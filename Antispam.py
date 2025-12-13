# -------------------- AntiSpam / AntiRaid / AntiAttack Bot --------------------
# Требования:
#   pip install aiogram aiosqlite aiolimiter

import asyncio
import re
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ChatPermissions, ChatMemberAdministrator, ChatMemberOwner
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

from aiolimiter import AsyncLimiter
import aiosqlite


# ---------------------- НАСТРОЙКИ ----------------------

TELEGRAM_TOKEN = ""

# Админы по username
ADMIN_USERNAMES = {"", ""}

# Чаты, где работает бот (username чата без @)
ALLOWED_CHATS = {
   "@",
    
}

# Пользователи, которых нельзя банить (username без @)
PROTECTED_USERS = {
    "",

DB_PATH = "antispam.db"

# Анти-флуд
MESSAGE_LIMIT = 5
PER_SECONDS = 7

# Супер-флуд (атака)
SUPER_FLOOD_LIMIT = 15
SUPER_FLOOD_WINDOW = 5

# Глобальная атака
GLOBAL_ATTACK_LIMIT = 50
GLOBAL_ATTACK_WINDOW = 3
GLOBAL_ATTACK_DURATION = 10

# Рейд
RAID_LIMIT = 3
RAID_WINDOW = 5

# Наказания
MUTE_SECONDS = 120

bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)

dp = Dispatcher()

limiter = AsyncLimiter(max_rate=MESSAGE_LIMIT, time_period=PER_SECONDS)

global_messages = []
new_users = []


# ----------------- ИНИЦ БАЗЫ -----------------

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                user_id INTEGER,
                timestamp INTEGER
            )
        """)
        await db.commit()


# ----------------- ПРОВЕРКА ЧАТА -----------------

def is_allowed_chat(message: Message) -> bool:
    if not message.chat.username:
        return False
    return message.chat.username.lower() in ALLOWED_CHATS


# ----------------- ПРОВЕРКА АДМИНА -----------------

async def is_admin(message: Message) -> bool:

    # username админа в списке
    if message.from_user.username and message.from_user.username.lower() in ADMIN_USERNAMES:
        return True

    # Telegram-админ
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    return isinstance(member, (ChatMemberAdministrator, ChatMemberOwner))


# ----------------- ПРОВЕРКА ЗАЩИЩЁННОСТИ -----------------

def is_protected_user(message: Message) -> bool:
    if not message.from_user.username:
        return False
    return message.from_user.username.lower() in PROTECTED_USERS


# ----------------- БАЗА: УЧЁТ СООБЩЕНИЙ -----------------

async def add_message(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO messages (user_id, timestamp) VALUES (?, ?)",
            (user_id, int(datetime.now(timezone.utc).timestamp()))
        )
        await db.commit()


async def get_recent_messages(user_id: int, sec: int) -> int:
    border = int((datetime.now(timezone.utc) - timedelta(seconds=sec)).timestamp())
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM messages WHERE user_id=? AND timestamp>?",
            (user_id, border)
        )
        (count,) = await cursor.fetchone()
        return count


# ----------------- АНТИ-АТАКА: ГЛОБАЛЬНЫЙ ФИЛЬТР -----------------

async def detect_global_attack(message: Message):
    global global_messages

    now = datetime.now(timezone.utc).timestamp()
    global_messages.append(now)

    global_messages = [t for t in global_messages if now - t < GLOBAL_ATTACK_WINDOW]

    if len(global_messages) > GLOBAL_ATTACK_LIMIT:

        await message.chat.send_message(
            "⚠️ <b>CHAT UNDER ATTACK!</b>\n"
            f"⛔ Все сообщения не-админов будут удаляться {GLOBAL_ATTACK_DURATION} секунд."
        )

        end = datetime.now(timezone.utc).timestamp() + GLOBAL_ATTACK_DURATION

        while datetime.now(timezone.utc).timestamp() < end:
            await asyncio.sleep(0.1)

        return True

    return False


# ----------------- АНТИ-АТАКА: СУПЕР-ФЛУД -----------------

async def detect_super_flood(message: Message):

    # защищённых пользователей не трогаем
    if is_protected_user(message):
        return False

    count = await get_recent_messages(message.from_user.id, SUPER_FLOOD_WINDOW)

    if count > SUPER_FLOOD_LIMIT:
        try:
            await message.chat.ban(message.from_user.id)
            await message.answer("🚫 <b>Super-Flood:</b> пользователь заблокирован.")
        except:
            pass
        return True

    return False


# ----------------- АНТИ-ССЫЛКИ -----------------

URL_REGEX = r"(http[s]?://|t\.me/|telegram\.me|discord\.gg)"

async def check_links(message: Message):
    if await is_admin(message):
        return False

    if is_protected_user(message):
        return False

    if re.search(URL_REGEX, message.text or "", re.IGNORECASE):
        await message.delete()
        return True

    return False


# ----------------- АНТИ-РЕЙД -----------------

async def detect_raid(message: Message):
    global new_users

    now = datetime.now(timezone.utc).timestamp()
    new_users.append(now)

    new_users = [t for t in new_users if now - t < RAID_WINDOW]

    return len(new_users) >= RAID_LIMIT


async def welcome_user_protect(message: Message):
    is_raid = await detect_raid(message)

    for user in message.new_chat_members:

        suspicious = False

        if not user.username:
            suspicious = True

        if user.username and re.match(r"[a-zA-Z]{5,}[0-9]{2,}", user.username):
            suspicious = True

        if user.first_name and len(user.first_name) < 2:
            suspicious = True

        try:
            if suspicious or is_raid:
                await message.chat.ban(user.id)
                await message.answer(
                    f"🚫 <b>Anti-Raid / Anti-Bot:</b> {user.full_name} заблокирован."
                )
            else:
                await message.chat.restrict(
                    user.id, ChatPermissions(can_send_messages=False)
                )
                await message.answer(
                    f"🛡 {user.mention_html()}, пройдите проверку (капча)."
                )
        except:
            pass


# ----------------- КОМАНДЫ -----------------

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("🛡 Анти-Спам / Анти-Атака бот активирован.")


# ----------------- ОБРАБОТКА ВСЕХ СООБЩЕНИЙ -----------------

@dp.message()
async def main_filter(message: Message):

    # работает только в указанных чатах
    if not is_allowed_chat(message):
        return

    # Новые пользователи
    if message.new_chat_members:
        return await welcome_user_protect(message)

    # защищённый пользователь
    if is_protected_user(message):
        return

    # Глобальная атака
    if await detect_global_attack(message):
        if not await is_admin(message):
            await message.delete()
        return

    # ссылки
    if await check_links(message):
        return

    # супер-флуд
    if await detect_super_flood(message):
        return

    # обычный анти-флуд
    await add_message(message.from_user.id)

    if await get_recent_messages(message.from_user.id, PER_SECONDS) > MESSAGE_LIMIT:

        try:
            await message.chat.restrict(
                message.from_user.id,
                ChatPermissions(can_send_messages=False),
                until_date=datetime.now(timezone.utc) + timedelta(seconds=MUTE_SECONDS)
            )
        except:
            pass

        await message.reply(f"⛔ Анти-флуд: мут {MUTE_SECONDS} сек.")
        return


# ------------------------ START ---------------------

async def main():
    await init_db()
    print("🚀 AntiAttack Bot запущен.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
