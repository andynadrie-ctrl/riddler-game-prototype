import pygame
import json
import random
from sys import exit

pygame.init()
#try:
   # with open("best_time.txt", "r") as f:
   #     best_time = int(f.read())
#except:
#    best_time = 0

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
HOW_TO_PLAY = "how_to_play"
ABOUT = "about"
CONGRATS = "congrats"

game_state = MENU

# ---------- LOAD RIDDLES ----------
with open("Desktop/Riddle game by nadriekoda/riddles.json", "r", encoding="utf-8") as f:
    riddles = json.load(f)

current_riddle = 0
riddles_answered = 0
end_time = 0
correct_answers = 0
wrong_answers = 0
best_time = 0
#total_time = 0

# ---------- SCREEN ----------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bosh")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 64)

# ---------- ASSETS ----------
sky = pygame.transform.scale(pygame.image.load("Desktop/Riddle game by nadriekoda/assets/backgrounds/sky.JPG"), (WIDTH, HEIGHT))
ground = pygame.transform.scale(pygame.image.load("Desktop/Riddle game by nadriekoda/assets/backgrounds/ground.JPG"), (WIDTH, 200))

player = pygame.image.load("Desktop/Riddle game by nadriekoda/assets/player/perso.png").convert_alpha()
player_rect = player.get_rect(midbottom=(400, GROUND_LEVEL))
player_velocity = 0

enemy_img = pygame.image.load("Desktop/Riddle game by nadriekoda/assets/enemies/gary.png").convert_alpha()
flying_enemy_img = pygame.image.load("Desktop/Riddle game by nadriekoda/assets/enemies/flying.png").convert_alpha()

heart_img = pygame.transform.scale(
    pygame.image.load("Desktop/Riddle game by nadriekoda/assets/backgrounds/heart.png").convert_alpha(), (32, 32)
)

# ---------- SOUNDS ----------
jump_sound = pygame.mixer.Sound("Desktop/Riddle game by nadriekoda/assets/songs/jump.wav")
hit_sound = pygame.mixer.Sound("Desktop/Riddle game by nadriekoda/assets/songs/hit.wav")
correct_sound = pygame.mixer.Sound("Desktop/Riddle game by nadriekoda/assets/songs/jump.wav")
pygame.mixer.music.load("Desktop/Riddle game by nadriekoda/assets/songs/music.wav")
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
howto_button = pygame.Rect(300, 340, 200, 60)
about_button = pygame.Rect(300, 420, 200, 60)
restart_button = pygame.Rect(300, 300, 200, 60)
pause_button = pygame.Rect(700, 20, 80, 40)
resume_button = pygame.Rect(300, 260, 200, 60)
back_button = pygame.Rect(20, 20, 120, 40)


# ---------- FUNCTIONS ----------
def reset_game():
    global lives, enemies, flying_enemies, current_riddle
    global start_time, collision_locked, show_feedback, game_state
    global riddles_answered, correct_answers, wrong_answers, end_time


    lives = MAX_LIVES
    enemies.clear()
    flying_enemies.clear()
    current_riddle = 0
    riddles_answered = 0
    end_time = 0
    start_time = pygame.time.get_ticks()
    collision_locked = False
    show_feedback = False
    game_state = PLAYING
    correct_answers = 0
    wrong_answers = 0




# ---------- MAIN LOOP ----------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if game_state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    reset_game()
                elif howto_button.collidepoint(event.pos):
                    game_state = HOW_TO_PLAY
                elif about_button.collidepoint(event.pos):
                    game_state = ABOUT

        elif game_state in (HOW_TO_PLAY, ABOUT):
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    game_state = MENU

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
                enemies.append(enemy_img.get_rect(midbottom=(random.randint(-150, -50), GROUND_LEVEL)))

            if event.type == FLYING_EVENT and len(flying_enemies) < 2:
                flying_enemies.append(
                    flying_enemy_img.get_rect(midleft=(WIDTH + 50, random.randint(200, 320)))
                )

        elif game_state == PAUSED:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                game_state = PLAYING
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume_button.collidepoint(event.pos):
                    game_state = PLAYING

        elif game_state == RIDDLE and not show_feedback:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    selected = event.key - pygame.K_1
                    correct = riddles[current_riddle]["answer"]
                    
                    riddles_answered += 1

                    if selected == correct:
                        feedback_text = "CORRECT!"
                        feedback_color = (0, 255, 0)
                        correct_sound.play()
                        correct_answers += 1

                    else:
                        feedback_text = "WRONG!"
                        feedback_color = (255, 0, 0)
                        lives -= 1
                        hit_sound.play()
                        wrong_answers += 1


                    show_feedback = True
                    feedback_start_time = pygame.time.get_ticks()
                    collision_locked = False
                    current_riddle += 1
                    riddles_answered += 1

        elif game_state == GAME_OVER:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    game_state = MENU

          # ---------- BACK BUTTON ----------
        if event.type == pygame.MOUSEBUTTONDOWN:
            if back_button.collidepoint(event.pos) and game_state in (HOW_TO_PLAY, ABOUT, CONGRATS):
                game_state = MENU

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
                feedback_text = "TIME UP!"
                feedback_color = (255, 165, 0)
                show_feedback = True
                feedback_start_time = pygame.time.get_ticks()
                collision_locked = False
            if current_riddle >= len(riddles):
                game_state = CONGRATS
                end_time = pygame.time.get_ticks()
           #     survival_time = (end_time - start_time) // 1000

         #   if best_time == 0 or survival_time < best_time:
         #      best_time = survival_time
          #     with open("best_time.txt", "w") as f:
            #        f.write(str(best_time))
            #        game_state = CONGRATS

            elif lives <= 0:
                end_time = pygame.time.get_ticks()
               # survival_time = (end_time - start_time) // 1000

           # if survival_time == 0 or survival_time < best_time:
              # best_time = survival_time
              # with open("best_time.txt", "w") as f:
               #  f.write(str(best_time))
           # game_state = GAME_OVER
                
        else:
            if pygame.time.get_ticks() - feedback_start_time >= FEEDBACK_DURATION:
                show_feedback = False
                game_state = GAME_OVER if lives <= 0 else PLAYING

    # ---------- DRAW ----------
    screen.fill((0, 0, 0))

    if game_state == MENU:
        screen.blit(sky, (0, 0))
        screen.blit(big_font.render("BOSH", True, (255, 255, 0)), (330, 150))

        pygame.draw.rect(screen, (0, 150, 255), start_button)
        pygame.draw.rect(screen, (0, 180, 120), howto_button)
        pygame.draw.rect(screen, (180, 120, 180), about_button)

        screen.blit(font.render("START", True, (255, 255, 255)), (350, 275))
        screen.blit(font.render("HOW TO PLAY", True, (255, 255, 255)), (315, 355))
        screen.blit(font.render("ABOUT US", True, (255, 255, 255)), (330, 435))

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
        pygame.draw.rect(screen, (200, 200, 200), back_button)
        screen.blit(font.render("BACK", True, (0, 0, 0)), (50, 28))


    elif game_state == ABOUT:
        screen.blit(big_font.render("ABOUT US", True, (255, 255, 0)), (260, 80))
        screen.blit(font.render("Educational Riddle Platformer", True, (255, 255, 255)), (200, 230))
        screen.blit(font.render("Created by: Nadrie Koda", True, (255, 255, 255)), (200, 270))
        pygame.draw.rect(screen, (200, 200, 200), back_button)
        screen.blit(font.render("BACK", True, (0, 0, 0)), (50, 28))

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
        screen.blit(big_font.render("PAUSED", True, (255, 255, 0)), (300, 180))
        pygame.draw.rect(screen, (0, 150, 255), resume_button)
        screen.blit(font.render("RESUME", True, (255, 255, 255)), (345, 275))
    
    elif game_state == CONGRATS:
        screen.blit(big_font.render("CONGRATULATIONS!", True, (0, 255, 0)), (180, 220))
        screen.blit(font.render("You solved all riddles!", True, (255, 255, 255)), (260, 290))
        screen.blit(font.render(f"Correct: {correct_answers}", True, (0, 255, 0)), (260, 340))
        screen.blit(font.render(f"Wrong: {wrong_answers}", True, (255, 0, 0)), (260, 360))
        screen.blit(font.render(f"Time Spent: {survival_time} seconds", True, (255, 255, 255)),(250, 400))
    #    if best_time > 0:
       #     screen.blit(font.render(f"Best Time: {best_time}s", True, (255, 215, 0)), (260, 390))

        pygame.draw.rect(screen, (200, 200, 200), back_button)
        screen.blit(font.render("MENU", True, (0, 0, 0)), (45, 28))


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
        screen.blit(font.render(f"Time Spent: {survival_time} seconds", True, (255, 255, 255)),(250, 400))
        screen.blit(font.render(f"Riddles Answered: {riddles_answered}", True, (255, 255, 255)),(250, 460))
        screen.blit(font.render(f"Correct: {correct_answers}", True, (0, 255, 0)), (260, 310))
        screen.blit(font.render(f"Wrong: {wrong_answers}", True, (255, 0, 0)), (260, 350))
        
    #    if best_time > 0:
     #       screen.blit(font.render(f"Best Time: {best_time}s", True, (255, 215, 0)), (260, 390))

        pygame.draw.rect(screen, (0, 150, 255), restart_button)
        screen.blit(font.render("MENU", True, (255, 255, 255)), (350, 315))

    pygame.display.update()
    clock.tick(60)
