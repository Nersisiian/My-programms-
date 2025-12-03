import pygame
import random
import sys

WIDTH, HEIGHT = 800, 600
BG_COLOR = (30, 30, 30)
PLAYER_SIZE = 40
PLAYER_COLOR = (255, 215, 0)  
BOMB_COLOR = (255, 0, 0)
CHERRY_COLOR = (220, 20, 60)
TEXT_COLOR = (255, 255, 255)

NUM_BOMBS = 6
NUM_CHERRIES = 8
PLAYER_SPEED = 5

def random_pos(margin=20):
    x = random.randint(margin, WIDTH - margin)
    y = random.randint(margin, HEIGHT - margin)
    return x, y

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Обезьянка: собирай вишню, избегай бомб")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    
    player_rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
    player_rect.center = (WIDTH // 2, HEIGHT // 2)

    
    bombs = []
    for _ in range(NUM_BOMBS):
        while True:
            pos = random_pos()
            r = pygame.Rect(pos[0]-12, pos[1]-12, 24, 24)
            if not r.colliderect(player_rect):
                bombs.append(r)
                break

   
    cherries = []
    for _ in range(NUM_CHERRIES):
        while True:
            pos = random_pos()
            r = pygame.Rect(pos[0]-10, pos[1]-10, 20, 20)
            if not r.colliderect(player_rect) and not any(b.colliderect(r) for b in bombs):
                cherries.append(r)
                break

    score = 0
    game_over = False
    win = False

    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (game_over or win):
                
                    main()
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        keys = pygame.key.get_pressed()
        if not game_over and not win:
            dx = dy = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = PLAYER_SPEED
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -PLAYER_SPEED
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = PLAYER_SPEED

            
            player_rect.x += dx
            player_rect.y += dy
            player_rect.clamp_ip(screen.get_rect())

            
            for bomb in bombs:
                if player_rect.colliderect(bomb):
                    game_over = True
                    break

            
            for cherry in cherries[:]:
                if player_rect.colliderect(cherry):
                    score += 1
                    cherries.remove(cherry)
                    # Новая вишня
                    while True:
                        pos = random_pos()
                        r = pygame.Rect(pos[0]-10, pos[1]-10, 20, 20)
                        if not any(b.colliderect(r) for b in bombs) and not r.colliderect(player_rect):
                            cherries.append(r)
                            break
                    break

            
            if score >= NUM_CHERRIES:
                win = True

        
        screen.fill(BG_COLOR)

        
        for bomb in bombs:
            pygame.draw.circle(screen, BOMB_COLOR, bomb.center, bomb.width // 2)

        
        for cherry in cherries:
            pygame.draw.rect(screen, CHERRY_COLOR, cherry)

       
        pygame.draw.rect(screen, PLAYER_COLOR, player_rect)

        
        score_text = font.render(f"Очки: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))

        if game_over:
            over_text = font.render("Поражение! Нажмите R чтобы перезапустить", True, TEXT_COLOR)
            screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 20))
        if win:
            win_text = font.render("Победа! Нажмите R чтобы сыграть снова", True, TEXT_COLOR)
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 20))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()

# Ներբեռնեք տեռմինալում pip install pygame 