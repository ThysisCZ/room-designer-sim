import pygame
import time
import random

from game_logic import (create_graphics, create_sounds)

#import and initialize pygame module
pygame.init()

display_info = pygame.display.Info()
width = display_info.current_w
height = display_info.current_h
screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)

#set up screen and caption
pygame.display.set_caption('Snake Game')

sounds = create_sounds()
sounds['minigame'].play(loops=-1).set_volume(0.4)

#snake start position
snake_pos = [width//3 + 100, height//2]
snake_speed = 10

#object to set framerate
clock = pygame.time.Clock()

snake_body = [[width//3 + 100, height//2], [width//3 + 90, height//2 - 10]]

graphics_collection = create_graphics()
food_image = graphics_collection[2]

#area for random generation
food_pos = [random.randrange(int(width//3.25), (int(width//3.25 + 460))),
                    random.randrange(int(height//6), (int(height//6 + 460)))
                ]

#boolean for food position change
food = True

score = 0
growth_counter = 0
segment_counter = 0

def show_score():
    font = pygame.font.SysFont(None, 30)

    score_text = font.render('Score: ' + str(score), True, 'white')
    score_rect = score_text.get_rect()
    score_rect.midtop = (width//3.25 + 430, height//6 - 23)
    screen.blit(score_text, score_rect)

def game_over():
    font = pygame.font.SysFont(None, 50)

    game_over_text = font.render(
        'GAME OVER', True, 'white')
    game_over_rect = game_over_text.get_rect()
    game_over_rect.midtop = (width/2, height/4)
    screen.blit(game_over_text, game_over_rect)

    score_text = font.render(
        'Score: ' + str(score), True, 'white')
    score_rect = score_text.get_rect()
    score_rect.midtop = (width/2, height/3)
    screen.blit(score_text, score_rect)

    pygame.display.flip()
    #pause for 2 seconds and quit auotmatically
    time.sleep(2)
    pygame.quit()
    quit()

#handle snake movements
dir = 'RIGHT'
next_dir = dir

#game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                #if UP is pressed, next_dir becomes UP
                next_dir = 'UP'
            if event.key == pygame.K_DOWN:
                next_dir = 'DOWN'
            if event.key == pygame.K_LEFT:
                next_dir = 'LEFT'
            if event.key == pygame.K_RIGHT:
                next_dir = 'RIGHT'
    
    #update the movements with input in next_dir
    if next_dir == 'UP' and dir != 'DOWN':
        #if DOWN is pressed while snake goes UP, no changes occur
        dir = 'UP'
    if next_dir == 'DOWN' and dir != 'UP':
        dir = 'DOWN'
    if next_dir == 'LEFT' and dir != 'RIGHT':
        dir = 'LEFT'
    if next_dir == 'RIGHT' and dir != 'LEFT':
        dir = 'RIGHT'

    #change snake's position
    if dir == 'UP':
        snake_pos[1] -= 10
    if dir == 'DOWN':
        snake_pos[1] += 10
    if dir == 'LEFT':
        snake_pos[0] -= 10
    if dir == 'RIGHT':
        snake_pos[0] += 10

    #insert every coordinate the snake passes through
    snake_body.insert(0, list(snake_pos))

    snake_rect = pygame.Rect(snake_pos[0], snake_pos[1], 40, 40)
    food_rect = pygame.Rect(food_pos[0], food_pos[1], 30, 30)

    if snake_rect.colliderect(food_rect):
        sounds['snake_eat'].play().set_volume(1)
        score += 10
        food = False
        growth_counter += 7
    #if snake doesn't meet the food
    else:
        if growth_counter > 0:
            growth_counter -= 1 
        else:
            snake_body.pop()
    
    #assign a new coordinate to food position
    if not food:
        food_pos = [random.randrange(int(width//3.25), (int(width//3.25 + 460))),
                    random.randrange(int(height//6), (int(height//6 + 460)))
                ]
    
    food = True
    screen.fill('black')

    #draw the snake
    for pos in snake_body:
        segment_counter += 1

        if segment_counter % 2:
            pygame.draw.rect(screen, 'dark green', (pos[0], pos[1], 40, 40), 30, 5)
        else:
            pygame.draw.rect(screen, 'green', (pos[0], pos[1], 40, 40), 30, 5)


    #draw the food
    screen.blit(food_image, (food_pos[0], food_pos[1]))

    #game over conditions
    if snake_pos[0] < width//3.25 or snake_pos[0] > width//3.25 + 460:
        game_over()
    if snake_pos[1] < height//6 or snake_pos[1] > height//6 + 460:
        game_over()
    #snake bites itself
    for block in snake_body[1:]:
        if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
            game_over()
    
    #draw border
    border_rect = pygame.Rect(width//3.25, height//6, 500, 500)
    pygame.draw.rect(screen, (255, 255, 255), border_rect, 3)

    #see score all the time on screen
    show_score()

    pygame.display.update()
    clock.tick(snake_speed)