import pygame
import json
import random
from sys import exit

pygame.init()
pygame.mixer.init()

# ---------- AUDIO ----------
pygame.mixer.music.load("Desktop/music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

jump_sound = pygame.mixer.Sound("Desktop/jump.wav")
correct_sound = pygame.mixer.Sound("Desktop/correct.wav")
wrong_sound = pygame.mixer.Sound("Desktop/wrong.wav")


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
HOW_TO_PLAY = "how_to_play"
ABOUT = "about"
CONGRATS = "congrats"
game_state = MENU

# ---------- LOAD RIDDLES ----------
with open("Desktop/Riddle game by nadriekoda/riddles.json", "r", encoding="utf-8") as f:
    riddles = json.load(f)

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

# ---------- GAME DATA ----------
current_riddle = 0
lives = MAX_LIVES
start_time = 0
survival_time = 0
riddle_start_time = 0
collision_locked = False
show_feedback = False
feedback_text = ""
feedback_color = (255, 255, 255)
feedback_start_time = 0

# ---------- ENEMIES ----------
enemies = []
flying_enemies = []
ENEMY_EVENT = pygame.USEREVENT + 1
FLYING_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(ENEMY_EVENT, 2000)
pygame.time.set_timer(FLYING_EVENT, 3000)

# ---------- BUTTONS ----------
start_btn = pygame.Rect(300, 220, 200, 50)
how_btn = pygame.Rect(300, 280, 200, 50)
about_btn = pygame.Rect(300, 340, 200, 50)
back_btn = pygame.Rect(20, 20, 120, 40)
restart_btn = pygame.Rect(300, 320, 200, 50)

# ---------- FUNCTIONS ----------
def reset_game():
    global lives, enemies, flying_enemies, current_riddle
    global start_time, collision_locked, show_feedback, game_state

    lives = MAX_LIVES
    enemies.clear()
    flying_enemies.clear()
    current_riddle = 0
    collision_locked = False
    show_feedback = False
    start_time = pygame.time.get_ticks()
    game_state = PLAYING

# ---------- MAIN LOOP ----------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # ---------- MENU ----------
        if game_state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn.collidepoint(event.pos):
                    reset_game()
                if how_btn.collidepoint(event.pos):
                    game_state = HOW_TO_PLAY
                if about_btn.collidepoint(event.pos):
                    game_state = ABOUT

        # ---------- PLAYING ----------
        elif game_state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player_rect.bottom >= GROUND_LEVEL:
                    player_velocity = JUMP_FORCE
                    jump_sound.play()
                if event.key == pygame.K_p:
                    game_state = PAUSED

            if event.type == ENEMY_EVENT:
                enemies.append(enemy_img.get_rect(midbottom=(-50, GROUND_LEVEL)))

            if event.type == FLYING_EVENT:
                flying_enemies.append(
                    flying_enemy_img.get_rect(midleft=(WIDTH + 50, random.randint(200, 320)))
                )

        # ---------- RIDDLE ----------
        elif game_state == RIDDLE and not show_feedback:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    answer = event.key - pygame.K_1
                    correct = riddles[current_riddle]["answer"]

                    if answer == correct:
                        feedback_text = "CORRECT!"
                        feedback_color = (0, 255, 0)
                    else:
                        feedback_text = "WRONG!"
                        feedback_color = (255, 0, 0)
                        lives -= 1

                    show_feedback = True
                    feedback_start_time = pygame.time.get_ticks()
                    current_riddle += 1

        # ---------- GAME OVER ----------
        elif game_state == GAME_OVER:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_btn.collidepoint(event.pos):
                    game_state = MENU

        # ---------- BACK BUTTON ----------
        if event.type == pygame.MOUSEBUTTONDOWN:
            if back_btn.collidepoint(event.pos) and game_state in (HOW_TO_PLAY, ABOUT, CONGRATS):
                game_state = MENU

    # ---------- GAME LOGIC ----------
    if game_state == PLAYING:
        survival_time = (pygame.time.get_ticks() - start_time) // 1000

        player_velocity += GRAVITY
        player_rect.y += player_velocity
        if player_rect.bottom >= GROUND_LEVEL:
            player_rect.bottom = GROUND_LEVEL
            player_velocity = 0

        for enemy in enemies + flying_enemies:
            enemy.x -= 5
            if enemy.colliderect(player_rect) and not collision_locked:
                collision_locked = True
                enemies.clear()
                flying_enemies.clear()
                riddle_start_time = pygame.time.get_ticks()
                game_state = RIDDLE

    elif game_state == RIDDLE:
        if show_feedback and pygame.time.get_ticks() - feedback_start_time > FEEDBACK_DURATION:
            show_feedback = False
            collision_locked = False
            if current_riddle >= len(riddles):
                game_state = CONGRATS
            elif lives <= 0:
                game_state = GAME_OVER
            else:
                game_state = PLAYING

    # ---------- DRAW ----------
    screen.fill((0, 0, 0))

    if game_state == MENU:
        screen.blit(big_font.render("BOSH", True, (255, 255, 255)), (320, 120))
        pygame.draw.rect(screen, (0, 150, 255), start_btn)
        pygame.draw.rect(screen, (0, 150, 255), how_btn)
        pygame.draw.rect(screen, (0, 150, 255), about_btn)

        screen.blit(font.render("START GAME", True, (255, 255, 255)), (325, 235))
        screen.blit(font.render("HOW TO PLAY", True, (255, 255, 255)), (320, 295))
        screen.blit(font.render("ABOUT", True, (255, 255, 255)), (355, 355))

    elif game_state == PLAYING:
        screen.blit(sky, (0, 0))
        screen.blit(ground, (0, GROUND_LEVEL))
        screen.blit(player, player_rect)

        for enemy in enemies:
            screen.blit(enemy_img, enemy)
        for enemy in flying_enemies:
            screen.blit(flying_enemy_img, enemy)

        for i in range(lives):
            screen.blit(heart_img, (20 + i * 40, 20))

        time_text = font.render(f"Time: {survival_time}s", True, (255, 255, 255))
        screen.blit(time_text, (650, 20))

    elif game_state == HOW_TO_PLAY:
        screen.blit(big_font.render("HOW TO PLAY", True, (255, 255, 0)), (220, 80))
        lines = [
            "SPACE  - Jump",
            "P      - Pause game",
            "1-4    - Answer riddles",
            "Avoid enemies or answer riddles correctly!"
        ]
        for i, line in enumerate(lines):
            screen.blit(font.render(line, True, (255, 255, 255)), (200, 200 + i * 40))
        pygame.draw.rect(screen, (200, 200, 200), back_btn)
        screen.blit(font.render("BACK", True, (0, 0, 0)), (50, 28))

    elif game_state == ABOUT:
        screen.blit(big_font.render("ABOUT US", True, (255, 255, 0)), (260, 80))
        screen.blit(font.render("Educational Riddle Platformer", True, (255, 255, 255)), (200, 230))
        screen.blit(font.render("Created by: Nadrie Koda", True, (255, 255, 255)), (200, 270))
        pygame.draw.rect(screen, (200, 200, 200), back_btn)
        screen.blit(font.render("BACK", True, (0, 0, 0)), (50, 28))

    elif game_state == CONGRATS:
        screen.blit(big_font.render("CONGRATULATIONS!", True, (0, 255, 0)), (180, 220))
        screen.blit(font.render("You solved all riddles!", True, (255, 255, 255)), (260, 290))
        pygame.draw.rect(screen, (200, 200, 200), back_btn)
        screen.blit(font.render("MENU", True, (0, 0, 0)), (45, 28))

    elif game_state == GAME_OVER:
        screen.blit(big_font.render("GAME OVER", True, (255, 0, 0)), (260, 220))
        pygame.draw.rect(screen, (0, 150, 255), restart_btn)
        screen.blit(font.render("MENU", True, (255, 255, 255)), (360, 335))

    pygame.display.update()
    clock.tick(60)
