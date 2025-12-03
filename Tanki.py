# main.py
import pygame
import sys

# Initialize
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Mini FPS Shooter (Prototype)")

# Simple objects
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.speed = 5

    def update(self, keys):
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed

        # keep in bounds
        self.rect.clamp_ip(screen.get_rect())

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, dir_vec):
        super().__init__()
        self.image = pygame.Surface((6, 6))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=pos)
        self.vel = dir_vec.normalize() * 10

    def update(self):
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y
        if not screen.get_rect().collidepoint(self.rect.center):
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=pos)
        self.speed = 2

    def update(self, player_pos):
        # simple chase
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        dist = max(1, (dx*dx + dy*dy) ** 0.5)
        self.rect.x += int(self.speed * dx / dist)
        self.rect.y += int(self.speed * dy / dist)

# Groups
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Spawn a few enemies
for i in range(5):
    e = Enemy((100 + i*120, 100))
    all_sprites.add(e)
    enemies.add(e)

# Main loop
running = True
while running:
    dt = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left click to shoot
                # shoot toward mouse
                mouse = pygame.mouse.get_pos()
                dir_vec = pygame.math.Vector2(mouse) - pygame.math.Vector2(player.rect.center)
                bullet = Bullet(player.rect.center, dir_vec)
                all_sprites.add(bullet)
                bullets.add(bullet)

    keys = pygame.key.get_pressed()
    player.update(keys)

    for b in bullets:
        b.update()

    for e in enemies:
        e.update(player.rect.center)

    # collision
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    # remove and maybe respawn enemies
    for _ in hits:
        # spawn a new enemy to keep challenge
        en = Enemy((50, 50))
        all_sprites.add(en)
        enemies.add(en)

    # render
    screen.fill((30, 30, 30))
    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()