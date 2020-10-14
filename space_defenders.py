import pygame
import os
import sys

BLACK = (0,0,0)

DISPLAY_WIDTH = 1000
DISPLAY_HEIGHT = 700

PLAYER_DISTANCE_FROM_BOTTOM = 100

BARRIER_DISTANCE_FROM_BOTTOM = 175
NUMBER_OF_BARRIERS = 4
BARRIER_WIDTH = 96
BARRIER_HEIGHT = 96
BARRIER_MAX_HP = 5

MOVEMENT_SPEED = 4
FRAME_RATE = 60

ALIEN_X_MOVEMENT_SPEED = 16
ALIEN_Y_MOVEMENT_SPEED = 30
ALIEN_FRAME_DELAY = 20
ALIEN_MOVEMENT_MAX_STEPS = 6
ALIEN_WIDTH = 96
ALIEN_HEIGHT = 96
NUMBER_OF_ALIEN_COLS = 8
NUMBER_OF_ALIEN_ROWS = 5

MISSILE_X_OFFSET = 42
MISSILE_Y_OFFSET = 48
MISSILE_MOVEMENT_SPEED = -16

def draw_alien(index, x, y):
    if index == 0:
        display.blit(alien1_images[alien_frame], (x, y))
    elif index == 1 or index == 2:
        display.blit(alien2_images[alien_frame], (x, y))
    elif index == 3 or index == 4:
        display.blit(alien3_images[alien_frame], (x, y))

def alien_bounds(row, col):
    x = alien_x + (col * alien_x_spacing)
    y = alien_y + (row * alien_y_spacing)
    return (x, y, ALIEN_WIDTH, ALIEN_HEIGHT)

def barrier_bounds(index):
    x = barrier_x + (index * barrier_x_spacing)
    return (x, barrier_y, BARRIER_WIDTH, BARRIER_HEIGHT)

def hit_barrier(missile_x, missile_y, index):
    x, y, width, hieght = barrier_bounds(index)
    return not (missile_x < x or missile_x > (x + width) or missile_y < y or missile_y > (y + height))

def hit_alien(missile_x, missile_y, row, col):
    x, y, width, height = alien_bounds(row, col)
    return not (missile_x < x or missile_x > (x + width) or missile_y < y or missile_y > (y + height))

def print_q_values():
    print('-------------------------------')
    print(f'[f] q_fast_player: {q_fast_player}')
    print(f'[u] q_unlimited_bullets: {q_unlimited_bullets}')
    print(f'[k] q_kind_aliens: {q_kind_aliens}')
    print('-------------------------------')

pygame.init()
display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption('Space Defenders')

clock = pygame.time.Clock()

player_image = pygame.image.load(os.path.join(sys.path[0], 'assets/player.png'))
player_x = DISPLAY_WIDTH // 2
player_y = DISPLAY_HEIGHT - PLAYER_DISTANCE_FROM_BOTTOM

missile_image = pygame.image.load(os.path.join(sys.path[0], 'assets/missile.png'))
missile_x = 0
missile_y = 0
show_missile = False

barrier_image = pygame.image.load(os.path.join(sys.path[0], 'assets/barrier.png'))
barrier_x = 150
barrier_x_spacing = 200
barrier_y = DISPLAY_HEIGHT - BARRIER_DISTANCE_FROM_BOTTOM
barriers_damage = [0, 0, 0, 0]
barriers_alive = [True, True, True, True]

alien1_images = [
    pygame.image.load(os.path.join(sys.path[0], 'assets/alien1-1.png')),
    pygame.image.load(os.path.join(sys.path[0], 'assets/alien1-2.png'))
]
alien2_images = [
    pygame.image.load(os.path.join(sys.path[0], 'assets/alien2-1.png')),
    pygame.image.load(os.path.join(sys.path[0], 'assets/alien2-2.png'))
]
alien3_images = [
    pygame.image.load(os.path.join(sys.path[0], 'assets/alien3-1.png')),
    pygame.image.load(os.path.join(sys.path[0], 'assets/alien3-2.png'))
]

aliens_alive = [
    [True, True, True, True, True, True, True, True],
    [True, True, True, True, True, True, True, True],
    [True, True, True, True, True, True, True, True],
    [True, True, True, True, True, True, True, True],
    [True, True, True, True, True, True, True, True],
]

alien_x = 50
alien_x_spacing = 100
alien_y = 25
alien_y_spacing = 80
alien_count = 40

alien_frame = 0
frame_count = 0
alien_movement_steps = 0

q_command = False
q_fast_player = False;
q_unlimited_bullets = False;
q_kind_aliens = False

game_over = False
dx = 0
while not game_over:
    # check for user input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True

        if event.type == pygame.KEYDOWN:
            if q_command:
                if event.key == pygame.K_p:
                    print_q_values()
                elif event.key == pygame.K_f:
                    q_fast_player = not q_fast_player
                elif event.key == pygame.K_u:
                    q_unlimited_bullets = not q_unlimited_bullets
                elif event.key == pygame.K_k:
                    q_kind_aliens = not q_kind_aliens
            else:
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    dx = -MOVEMENT_SPEED
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    dx = MOVEMENT_SPEED
                elif event.key == pygame.K_SPACE and (not show_missile or q_unlimited_bullets):
                    show_missile = True
                    missile_x = player_x + MISSILE_X_OFFSET
                    missile_y = player_y + MISSILE_Y_OFFSET
                elif event.key == pygame.K_q:
                    q_command = True


        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                dx = 0
            elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                dx = 0
            elif event.key == pygame.K_q:
                q_command = False


    # update the game state

    player_speed_multiplier = 1
    if q_fast_player:
        player_speed_multiplier = 2
    player_x += dx * player_speed_multiplier

    # check if the missile hits the barriers
    for index in range(NUMBER_OF_BARRIERS):
        if show_missile and barriers_alive[index] and hit_barrier(missile_x, missile_y, index):
            show_missile = False
            missile_x = -1
            missile_y = -1
            barriers_damage[index] += 1
            if barriers_damage[index] >= BARRIER_MAX_HP:
                barriers_alive[index] = False

    # check if the missile hits the aliens
    for col in range(NUMBER_OF_ALIEN_COLS):
        for row in range(NUMBER_OF_ALIEN_ROWS):
            if show_missile and aliens_alive[row][col] and hit_alien(missile_x, missile_y, row, col):
                aliens_alive[row][col] = False
                show_missile = False
                missile_x = -1
                missile_y = -1
                alien_count -= 1

    # update the missile position
    if show_missile:
        missile_y += MISSILE_MOVEMENT_SPEED

        if missile_y < 0:
            show_missile = False

    # animate the aliens
    frame_count += 1
    if frame_count > ALIEN_FRAME_DELAY:
        frame_count = 0

        # move the aliens
        alien_x += ALIEN_X_MOVEMENT_SPEED
        alien_movement_steps += 1
        if alien_movement_steps >= ALIEN_MOVEMENT_MAX_STEPS:
            ALIEN_X_MOVEMENT_SPEED *= -1
            alien_movement_steps = 0
            if not q_kind_aliens:
                alien_y += ALIEN_Y_MOVEMENT_SPEED

        # change the animation frame
        alien_frame = (alien_frame + 1) % 2

    for col in range(NUMBER_OF_ALIEN_COLS):
        for row in range(NUMBER_OF_ALIEN_ROWS):
            if aliens_alive[row][col]:
                if alien_y + ((row + 1) * ALIEN_HEIGHT) > DISPLAY_HEIGHT:
                    game_over = True

    if alien_count < 1:
        game_over = True

    # display the graphical elements
    display.fill(BLACK)

    # draw the player
    display.blit(player_image, (player_x, player_y))

    # draw the barriers
    for index in range(NUMBER_OF_BARRIERS):
        if barriers_alive[index]:
            x, y, width, height = barrier_bounds(index)
            display.blit(barrier_image, (x, y))

    # draw the missile
    if show_missile:
        display.blit(missile_image, (missile_x, missile_y))

    # draw the aliens
    for col in range(NUMBER_OF_ALIEN_COLS):
        for row in range(NUMBER_OF_ALIEN_ROWS):
            if aliens_alive[row][col]:
                x, y, width, height = alien_bounds(row, col)
                draw_alien(row, x, y)

    pygame.display.update();
    clock.tick(FRAME_RATE);

pygame.quit()
quit()
