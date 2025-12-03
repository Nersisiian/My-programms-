import telebot, random, json, os, threading, time
from telebot import types

TOKEN = "Bot_Token"
bot = telebot.TeleBot(TOKEN)

DATA = "stats.json"
TIME_LIMIT = 15

if not os.path.exists(DATA):
    with open(DATA, "w", encoding="utf8") as f:
        json.dump({}, f)

def load():
    with open(DATA, "r", encoding="utf8") as f:
        return json.load(f)

def save(d):
    with open(DATA, "w", encoding="utf8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

questions = {
    "easy": [
        ["5+5?", ["8","10","12","15"], 1],
        ["Столица Франции", ["Рим","Берлин","Париж","Мадрид"], 2],
        ["2*6?", ["10","12","14","8"], 1],
        ["Цвет неба?", ["красный","синий","зелёный","белый"], 1],
        ["Сколько дней в неделе?", ["5","6","7","8"], 2],
        ["3+4?", ["5","6","7","9"], 2],
        ["Сколько континентов?", ["5","6","7","8"], 2],
        ["Какой фрукт красный?", ["банан","яблоко","груша","дыня"], 1],
        ["1+9?", ["10","8","11","9"], 0],
        ["10-7?", ["1","2","3","4"], 2]
    ],
    "medium": [
        ["12*2?", ["14","20","24","22"], 2],
        ["Столица Японии", ["Осака","Токио","Киото","Пекин"], 1],
        ["Корень из 49?", ["5","6","7","8"], 2],
        ["Самая большая планета?", ["Земля","Марс","Юпитер","Сатурн"], 2],
        ["9^2?", ["81","72","64","90"], 0],
        ["Океан самый большой?", ["Красный","Атлант","Тихий","Северный"], 2],
        ["15+6?", ["19","20","21","22"], 2],
        ["Столица Италии?", ["Рим","Пиза","Неаполь","Милан"], 0],
        ["Сколько планет?", ["7","8","9","10"], 1],
        ["Температура замерз воды?", ["0","-5","5","10"], 0]
    ],
    "hard": [
        ["√144?", ["10","11","12","13"], 2],
        ["Самая длинная река?", ["Амазонка","Нил","Янцзы","Миссисипи"], 1],
        ["Год II Мировой?", ["1939","1941","1945","1918"], 0],
        ["P = U * ?", ["I","R","t","m"], 0],
        ["Столица Канады?", ["Оттава","Торонто","Ванкувер","Монреаль"], 0],
        ["7^2?", ["42","48","49","56"], 2],
        ["Хим. знак золота?", ["Ag","Au","Fe","Zn"], 1],
        ["Газ в воздухе больше?", ["O2","CO2","N2","H2"], 2],
        ["Самый твёрдый минерал?", ["Алмаз","Гранит","Кварц","Железо"], 0],
        ["Самая горячая планета?", ["Земля","Марс","Меркурий","Венера"], 3]
    ]
}

users = {}
timers = {}

langs_text = {
    "🇷🇺 Русский": {
        "start": "🎮 QUIZ BOT\n\nНажмите ▶️ Старт",
        "choose_lang": "🌍 Выберите язык:",
        "choose_level": "⚡ Выберите уровень сложности:",
        "timeup": "⏰ Время вышло!",
        "stop": "⛔ Игра остановлена.\nНажмите ▶️ Старт для начала.",
        "finish": "🏁 Игра окончена!\n\n✅ {score}/{total}",
        "stats": "📊 Статистика:\n\n🎮 Игр: {games}\n🏆 Лучший: {best}",
        "top": "🏆 ТОП-5 игроков:\n\n"
    },
    "🇬🇧 English": {
        "start": "🎮 QUIZ BOT\n\nPress ▶️ Start",
        "choose_lang": "🌍 Choose a language:",
        "choose_level": "⚡ Choose difficulty level:",
        "timeup": "⏰ Time is up!",
        "stop": "⛔ Game stopped.\nPress ▶️ Start to play.",
        "finish": "🏁 Game over!\n\n✅ {score}/{total}",
        "stats": "📊 Stats:\n\n🎮 Games: {games}\n🏆 Best: {best}",
        "top": "🏆 TOP-5 players:\n\n"
    },
    "🇦🇲 Հայերեն": {
        "start": "🎮 QUIZ BOT\n\nՍեղմեք ▶️ Սկսել",
        "choose_lang": "🌍 Ընտրեք լեզուն:",
        "choose_level": "⚡ Ընտրեք դժվարության մակարդակը:",
        "timeup": "⏰ Ժամանակն ավարտվել է!",
        "stop": "⛔ Խաղը կանգնեցվեց.\nՍեղմեք ▶️ Սկսել սկսելու համար.",
        "finish": "🏁 Խաղը ավարտվեց!\n\n✅ {score}/{total}",
        "stats": "📊 Статистика:\n\n🎮 Խաղեր: {games}\n🏆 Լավագույն: {best}",
        "top": "🏆 TOP-5 խաղացողներ:\n\n"
    }
}

@bot.message_handler(commands=["start"])
def start(m):
    cid = m.chat.id
    users.pop(cid, None)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("▶️ Старт")
    bot.send_message(cid, langs_text["🇷🇺 Русский"]["start"], reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == "▶️ Старт")
def choose_lang(m):
    cid = m.chat.id
    if cid not in users:
        users[cid] = {"score":0,"index":0,"level":None,"list":[],"answered":False,"lang":"🇷🇺 Русский","lang_chosen":False,"level_chosen":False}
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🇷🇺 Русский", "🇬🇧 English", "🇦🇲 Հայերեն")
    bot.send_message(cid, langs_text["🇷🇺 Русский"]["choose_lang"], reply_markup=kb)

@bot.message_handler(func=lambda m: m.text in ["🇷🇺 Русский","🇬🇧 English","🇦🇲 Հայերեն"])
def lang(m):
    cid = m.chat.id
    u = users[cid]
    if u.get("lang_chosen"): return
    u["lang_chosen"] = True
    u["lang"] = m.text
    choose_level(cid)

def choose_level(cid):
    u = users[cid]
    if u.get("level_chosen"): return
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🟢 easy", "🟡 medium", "🔴 hard", "⏹ Стоп")
    bot.send_message(cid, langs_text[u["lang"]]["choose_level"], reply_markup=kb)

@bot.message_handler(func=lambda m: m.text in ["🟢 easy","🟡 medium","🔴 hard"])
def level(m):
    cid = m.chat.id
    u = users[cid]
    if u.get("level_chosen"): return
    u["level_chosen"] = True
    lvl = m.text.split()[-1]
    u["level"] = lvl
    q = questions[lvl].copy()
    random.shuffle(q)
    u["list"] = q[:10]
    u["index"] = 0
    ask(cid)

@bot.message_handler(func=lambda m: m.text=="⏹ Стоп")
def stop_game(m):
    cid = m.chat.id
    u = users.pop(cid, None)
    timers.pop(cid, None)
    lang_choice = u["lang"] if u else "🇷🇺 Русский"
    bot.send_message(cid, langs_text[lang_choice]["stop"])

def ask(cid):
    u = users.get(cid)
    if not u: return
    u["answered"] = False
    q = u["list"][u["index"]]
    kb = types.InlineKeyboardMarkup()
    for i, ans in enumerate(q[1]):
        kb.add(types.InlineKeyboardButton(ans, callback_data=str(i)))
    bot.send_message(cid, f"❓ {q[0]}\n⏳ {TIME_LIMIT} сек", reply_markup=kb)
    animated_timer(cid, TIME_LIMIT)

def animated_timer(cid, sec):
    def run():
        for s in range(sec, 0, -1):
            u = users.get(cid)
            if not u or u["answered"]: return
            try:
                q = u["list"][u["index"]]
                bot.edit_message_text(f"❓ {q[0]}\n\n⏳ Осталось: {s} сек", cid, u.get("last_msg_id", None))
            except:
                pass
            time.sleep(1)
        if users.get(cid) and not users[cid]["answered"]:
            timeup(cid)
    t = threading.Thread(target=run)
    t.start()
    timers[cid] = t

def timeup(cid):
    u = users.get(cid)
    if not u or u["answered"]: return
    u["answered"] = True
    bot.send_message(cid, langs_text[u["lang"]]["timeup"])
    u["index"] += 1
    if u["index"] < len(u["list"]):
        ask(cid)
    else:
        finish(cid)

@bot.callback_query_handler(func=lambda c: True)
def check(c):
    cid = c.message.chat.id
    u = users.get(cid)
    if not u or u["answered"]:
        bot.answer_callback_query(c.id,"⏳ Уже отвечено")
        return
    u["answered"] = True
    q = u["list"][u["index"]]
    if int(c.data) == q[2]:
        u["score"] += 1
        bot.answer_callback_query(c.id,"✅ Верно")
    else:
        bot.answer_callback_query(c.id,"❌ Неверно")
    u["index"] += 1
    if u["index"] < len(u["list"]):
        ask(cid)
    else:
        finish(cid)

def finish(cid):
    u = users.get(cid)
    if not u: return
    score = u["score"]
    total = len(u["list"])
    data = load()
    uid = str(cid)
    if uid not in data: data[uid] = {"games":0,"best":0}
    data[uid]["games"] += 1
    data[uid]["best"] = max(data[uid]["best"], score)
    save(data)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("▶️ Старт","📊 Статистика","🏆 Рейтинг")
    bot.send_message(cid, langs_text[u["lang"]]["finish"].format(score=score,total=total), reply_markup=kb)

@bot.message_handler(func=lambda m: m.text=="📊 Статистика")
def stat(m):
    d = load().get(str(m.chat.id), {"games":0,"best":0})
    u = users.get(m.chat.id)
    lang_choice = u["lang"] if u else "🇷🇺 Русский"
    bot.send_message(m.chat.id, langs_text[lang_choice]["stats"].format(games=d["games"], best=d["best"]))

@bot.message_handler(func=lambda m: m.text=="🏆 Рейтинг")
def rank(m):
    data = load()
    top = sorted(data.items(), key=lambda x:x[1]["best"], reverse=True)[:5]
    u = users.get(m.chat.id)
    lang_choice = u["lang"] if u else "🇷🇺 Русский"
    txt = langs_text[lang_choice]["top"]
    for i, (_,v) in enumerate(top):
        txt += f"{i+1}. {v['best']} баллов\n"
    bot.send_message(m.chat.id, txt)

bot.polling(none_stop=True)


