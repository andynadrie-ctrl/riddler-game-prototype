import pygame
from sys import exit
import json

#------GAME STATES------
MENU="menu"
PLAYING="playing"
RIDDLE="riddle"
GAME_OVER="game over"

game_state=MENU
#----------------------

pygame.init()

# -------- LOAD RIDDLES --------
with open("Desktop/Riddle game by nadriekoda/riddles.json", "r", encoding="utf-8") as file:
    riddles = json.load(file)

current_riddle = 0
selected_answer = None
# ----------------------------


screen= pygame.display.set_mode((800,600))
pygame.display.set_caption("bosh")
clock= pygame.time.Clock()
test_font=pygame.font.Font(None,50)
#game_active=False
groundLevel = 430
#sky
sky_surface=pygame.image.load("Desktop/sky.JPG")
sky_surface=pygame.transform.scale(sky_surface,(800,600))#before putting the sizes of an image call it back and add a ",", after you set the sizes
#ground
ground_surface=pygame.image.load("Desktop/ground.JPG")
ground_surface=pygame.transform.scale(ground_surface,(800,200))
#text
#text_surface=test_font.render("Nadrie's Game",False,(104,180,200))
#text_rect=text_surface.get_rect(center=(400,50))

#snail/obstacle
snail_surface=pygame.image.load("Desktop/gary.png").convert_alpha()
snail_rect=snail_surface.get_rect(midbottom=(-100,groundLevel))

obstacle_rect_list=[]

#perso
perso_surface=pygame.image.load("Desktop/perso.png").convert_alpha()
perso_rect=perso_surface.get_rect(midbottom=(500,groundLevel))
perso_gravity=0
#intro screen
intro=pygame.image.load("Desktop/intro.png")
intro_rect= intro.get_rect(center=(400,200))
intro=pygame.transform.scale(intro,(800,600))

start_time = pygame.time.get_ticks()
survival_time = 0

#timer
obstacle_timer=pygame.USEREVENT+1
pygame.time.set_timer(obstacle_timer,900)

while True:
    for event in pygame.event.get():
        if event.type ==pygame.QUIT:
            pygame.quit(  )
            exit()
        if  game_state == PLAYING:        
            #using mouse button to make him jump
         if event.type==pygame.MOUSEBUTTONDOWN:
             if perso_rect.bottom >= groundLevel:
                  perso_gravity=-25

            #using the space button
        keys=pygame.key.get_pressed()
        if game_state == PLAYING:
          if keys[pygame.K_SPACE]:
            if perso_rect.bottom >= groundLevel:
                perso_gravity=-25
        else:
           if event.type==pygame.KEYUP and event.key== pygame.K_BACKSPACE:
            if game_state==MENU:
                game_state==PLAYING
           # game_active=True 
            snail_rect.right=-100
            start_time = pygame.time.get_ticks()  # RESET TIMER

       # if pygame.event == obstacle_timer and game_active:
           # obstacle_rect_list.append(snail_surface.get_rect(midbottom=(-100,groundLevel))
    if game_state == RIDDLE:
     if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_1:
            selected_answer = 0
        elif event.key == pygame.K_2:
            selected_answer = 1
        elif event.key == pygame.K_3:
            selected_answer = 2
        elif event.key == pygame.K_4:
            selected_answer = 3

        if selected_answer is not None:
            correct = riddles[current_riddle]["answer"]

            current_riddle += 1
            selected_answer = None
            snail_rect.right = -100
            game_state = PLAYING


    # ---------- GAME STATE LOGIC ----------

    if game_state == MENU:
       screen.fill((25,25,25))
      #screen.blit(intro, (0,0))


    elif game_state == PLAYING:
    # 1. update timer
      current_time = pygame.time.get_ticks()
      survival_time = (current_time - start_time) // 1000

    # 2. draw background
      screen.blit(sky_surface, (0,0))
      screen.blit(ground_surface, (0,400))

    # 3. move & draw snail
      snail_rect.left += 5
      if snail_rect.left > 800:
        snail_rect.right = 0
      screen.blit(snail_surface, snail_rect)

    # 4. player physics
      perso_gravity += 1
      perso_rect.y += perso_gravity
      if perso_rect.bottom >= groundLevel:
        perso_rect.bottom = groundLevel
      screen.blit(perso_surface, perso_rect)

    # 5. collision → go to riddle
      if snail_rect.colliderect(perso_rect):
        game_state = RIDDLE
        selected_answer = None
     


    elif game_state == RIDDLE:
     screen.fill((20, 20, 20))

    r = riddles[current_riddle]

    question = test_font.render(r["question"], True, (255,255,255))
    screen.blit(question, (80,100))

    for i, choice in enumerate(r["choices"]):
     option = test_font.render(f"{i+1}. {choice}", True, (200,200,200))
    screen.blit(option, (100, 200 + i*60))


        
    timer_surface = test_font.render(f"Score: {survival_time}s", True, (255, 255, 255))
    screen.blit(timer_surface, (20, 20))

        


    pygame.display.update()
    clock.tick(60)