import pygame
import json
import random
from sys import exit

pygame.init()
pygame.mixer.init()

# ---------- CONSTANTS ----------
WIDTH, HEIGHT = 800, 600
GROUND_LEVEL = 430
GRAVITY = 1
JUMP_FORCE = -22
MAX_LIVES = 3
RIDDLE_TIME = 30
FEEDBACK_DURATION = 1200

# ---------- STATES ----------
MENU = "menu"
PLAYING = "playing"
PAUSED = "paused"
RIDDLE = "riddle"
GAME_OVER = "game over"
game_state = MENU

# ---------- LOAD RIDDLES ----------
with open("Desktop/Riddle game by nadriekoda/riddles.json", "r", encoding="utf-8") as f:
    riddles = json.load(f)

current_riddle = 0

# ---------- SCREEN ----------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bosh")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 64)

# ---------- ASSETS ----------
sky = pygame.transform.scale(pygame.image.load("Desktop/sky.JPG"), (WIDTH, HEIGHT))
ground = pygame.transform.scale(pygame.image.load("Desktop/ground.JPG"), (WIDTH, 200))

player = pygame.image.load("Desktop/perso.png").convert_alpha()
player_rect = player.get_rect(midbottom=(500, GROUND_LEVEL))
player_velocity = 0

enemy_img = pygame.image.load("Desktop/gary.png").convert_alpha()
flying_enemy_img = pygame.image.load("Desktop/flying.png").convert_alpha()

heart_img = pygame.transform.scale(
    pygame.image.load("Desktop/heart.png").convert_alpha(), (32, 32)
)

# ---------- SOUNDS ----------
jump_sound = pygame.mixer.Sound("Desktop/jump.wav")
hit_sound = pygame.mixer.Sound("Desktop/hit.wav")
correct_sound = pygame.mixer.Sound("Desktop/jump.wav")
pygame.mixer.music.load("Desktop/music.wav")
pygame.mixer.music.play(-1)

# ---------- GAME DATA ----------
lives = MAX_LIVES
start_time = pygame.time.get_ticks()
survival_time = 0
riddle_start_time = 0
collision_locked = False

feedback_text = ""
feedback_color = (255, 255, 255)
feedback_start_time = 0
show_feedback = False

# ---------- ENEMIES ----------
enemies = []
flying_enemies = []

ENEMY_EVENT = pygame.USEREVENT + 1
FLYING_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(ENEMY_EVENT, 2000)
pygame.time.set_timer(FLYING_EVENT, 3000)

# ---------- BUTTONS ----------
start_button = pygame.Rect(300, 260, 200, 60)
restart_button = pygame.Rect(300, 300, 200, 60)
pause_button = pygame.Rect(700, 20, 80, 40)
resume_button = pygame.Rect(300, 260, 200, 60)

# ---------- FUNCTIONS ----------
def reset_game():
    global lives, enemies, flying_enemies, current_riddle, start_time
    global game_state, collision_locked, show_feedback
    lives = MAX_LIVES
    enemies.clear()
    flying_enemies.clear()
    current_riddle = 0
    start_time = pygame.time.get_ticks()
    collision_locked = False
    show_feedback = False
    game_state = PLAYING

# ---------- MAIN LOOP ----------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # ----- MENU -----
        if game_state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    reset_game()

        # ----- PLAYING -----
        elif game_state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player_rect.bottom >= GROUND_LEVEL:
                    player_velocity = JUMP_FORCE
                    jump_sound.play()
                if event.key == pygame.K_p:
                    game_state = PAUSED

            if event.type == pygame.MOUSEBUTTONDOWN:
                if pause_button.collidepoint(event.pos):
                    game_state = PAUSED

            if event.type == ENEMY_EVENT and len(enemies) < 3:
                rect = enemy_img.get_rect(midbottom=(random.randint(-150, -50), GROUND_LEVEL))
                enemies.append(rect)

            if event.type == FLYING_EVENT and len(flying_enemies) < 2:
                rect = flying_enemy_img.get_rect(
                    midleft=(WIDTH + 50, random.randint(200, 320))
                )
                flying_enemies.append(rect)

        # ----- PAUSED -----
        elif game_state == PAUSED:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                game_state = PLAYING
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume_button.collidepoint(event.pos):
                    game_state = PLAYING

        # ----- RIDDLE INPUT -----
        elif game_state == RIDDLE and not show_feedback:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    selected = event.key - pygame.K_1
                    correct = riddles[current_riddle]["answer"]

                    if selected == correct:
                        feedback_text = "CORRECT!"
                        feedback_color = (0, 255, 0)
                        correct_sound.play()
                    else:
                        feedback_text = "WRONG!"
                        feedback_color = (255, 0, 0)
                        lives -= 1
                        hit_sound.play()

                    show_feedback = True
                    feedback_start_time = pygame.time.get_ticks()
                    collision_locked = False
                    current_riddle += 1

        # ----- GAME OVER -----
        elif game_state == GAME_OVER:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    reset_game()

    # ---------- GAME LOGIC ----------
    if game_state == PLAYING:
        survival_time = (pygame.time.get_ticks() - start_time) // 1000

        player_velocity += GRAVITY
        player_rect.y += player_velocity
        if player_rect.bottom >= GROUND_LEVEL:
            player_rect.bottom = GROUND_LEVEL
            player_velocity = 0

        for enemy in enemies[:]:
            enemy.x += 6
            if enemy.left > WIDTH:
                enemies.remove(enemy)
            if enemy.colliderect(player_rect) and not collision_locked:
                collision_locked = True
                enemies.clear()
                flying_enemies.clear()
                riddle_start_time = pygame.time.get_ticks()
                game_state = RIDDLE

        for f_enemy in flying_enemies[:]:
            f_enemy.x -= 5
            if f_enemy.right < 0:
                flying_enemies.remove(f_enemy)
            if f_enemy.colliderect(player_rect) and not collision_locked:
                collision_locked = True
                enemies.clear()
                flying_enemies.clear()
                riddle_start_time = pygame.time.get_ticks()
                game_state = RIDDLE

    elif game_state == RIDDLE:
        if not show_feedback:
            if (pygame.time.get_ticks() - riddle_start_time) // 1000 >= RIDDLE_TIME:
                lives -= 1
                show_feedback = True
                feedback_text = "TIME UP!"
                feedback_color = (255, 165, 0)
                feedback_start_time = pygame.time.get_ticks()
                collision_locked = False
        else:
            if pygame.time.get_ticks() - feedback_start_time >= FEEDBACK_DURATION:
                show_feedback = False
                game_state = GAME_OVER if lives <= 0 else PLAYING

    # ---------- DRAW ----------
    screen.fill((0, 0, 0))

    if game_state == MENU:
        pygame.draw.rect(screen, (0, 150, 255), start_button)
        screen.blit(font.render("START", True, (255, 255, 255)), (350, 275))

    elif game_state == PLAYING:
        screen.blit(sky, (0, 0))
        screen.blit(ground, (0, 400))
        screen.blit(player, player_rect)

        for enemy in enemies:
            screen.blit(enemy_img, enemy)

        for f_enemy in flying_enemies:
            screen.blit(flying_enemy_img, f_enemy)

        for i in range(lives):
            screen.blit(heart_img, (20 + i * 36, 20))

        screen.blit(font.render(f"Time: {survival_time}s", True, (255, 255, 255)), (20, 60))

        pygame.draw.rect(screen, (200, 200, 0), pause_button)
        screen.blit(font.render("PAUSE", True, (0, 0, 0)), (710, 28))

    elif game_state == PAUSED:
        screen.blit(sky, (0, 0))
        pause_text = big_font.render("PAUSED", True, (255, 255, 0))
        screen.blit(pause_text, pause_text.get_rect(center=(WIDTH // 2, 180)))
        pygame.draw.rect(screen, (0, 150, 255), resume_button)
        screen.blit(font.render("RESUME", True, (255, 255, 255)), (345, 275))

    elif game_state == RIDDLE:
        if show_feedback:
            txt = big_font.render(feedback_text, True, feedback_color)
            screen.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        else:
            r = riddles[current_riddle % len(riddles)]
            screen.blit(font.render(r["question"], True, (255, 255, 255)), (60, 80))
            for i, choice in enumerate(r["choices"]):
                screen.blit(font.render(f"{i + 1}. {choice}", True, (200, 200, 200)),
                            (80, 160 + i * 50))

            remaining = RIDDLE_TIME - ((pygame.time.get_ticks() - riddle_start_time) // 1000)
            screen.blit(font.render(f"Time Left: {remaining}", True, (255, 255, 0)), (20, 20))

    elif game_state == GAME_OVER:
        screen.blit(big_font.render("GAME OVER", True, (255, 0, 0)), (260, 220))
        pygame.draw.rect(screen, (0, 150, 255), restart_button)
        screen.blit(font.render("RESTART", True, (255, 255, 255)), (335, 315))

    pygame.display.update()
    clock.tick(60)
