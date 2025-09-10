import pygame as pg
import time
import asyncio
pg.init()
clock = pg.time.Clock()

black = (0, 0, 0)
white = (255, 255, 255) 
font = pg.font.Font(None, 30)

win_width = 800
win_height = 600
screen = pg.display.set_mode((win_width, win_height))
pg.display.set_caption('Double Dodging')

running = True
max_projectiles = 10
p1_boost_active = False
p1_boost_timer = 0
p2_boost_active = False
p2_boost_timer = 0
original_max_projectiles = max_projectiles  # Store the original limit (3)
p1_objects = []
p2_objects = []
p1_shield = 100
p2_shield = 100
p1_speed = 10
p2_speed = 10
p1_vel_x = 0
p1_vel_y = 0
p2_vel_x = 0
p2_vel_y = 0
acceleration = 0.6  # How fast players speed up
friction = 0.1      # How fast players slow down
max_speed = 10   # Maximum speed (replacing p1_speed and p2_speed)

line = pg.Rect(win_width // 2 - 5, 0, 10, win_height)

bg_image = pg.image.load('./assets/images/spacebg.png')
bg_image = pg.transform.scale(bg_image, (win_width, win_height))

obj_size = 35
obj_image = pg.image.load('./assets/images/projectile.png')
obj_image = pg.transform.scale(obj_image, (obj_size, obj_size))

p1_super = []
p2_super = []
super_size = 24
super_image = pg.image.load('./assets/images/super.png')
super_image = pg.transform.scale(super_image, (super_size, super_size))

player_size = 50
p1_image = pg.image.load('./assets/images/p1.png')
p1_image = pg.transform.scale(p1_image, (player_size, player_size))
p1 = pg.Rect(600, 300, player_size, player_size)

p2_image = pg.image.load('./assets/images/p2.png')
p2_image = pg.transform.scale(p2_image, (player_size, player_size))
p2 = pg.Rect(100, 300, player_size, player_size)

def move_p1(keys_pressed, p1):
    global p1_vel_x, p1_vel_y
    
    # Apply acceleration based on input
    if keys_pressed[pg.K_LEFT] and p1.x > line.right:
        p1_vel_x -= acceleration
    if keys_pressed[pg.K_RIGHT] and p1.x + p1.width < win_width:
        p1_vel_x += acceleration
    if keys_pressed[pg.K_UP]:
        p1_vel_y -= acceleration
    if keys_pressed[pg.K_DOWN]:
        p1_vel_y += acceleration
    
    # Apply friction
    p1_vel_x *= (1 - friction)
    p1_vel_y *= (1 - friction)
    
    # Limit maximum speed
    p1_vel_x = max(-max_speed, min(max_speed, p1_vel_x))
    p1_vel_y = max(-max_speed, min(max_speed, p1_vel_y))
    
    # Update position
    p1.x += p1_vel_x
    p1.y += p1_vel_y
    
    # Teleport from bottom to top or top to bottom
    if p1.y + p1.height < 0:  # If player goes above the top
        p1.y = win_height  # Teleport to bottom
    elif p1.y > win_height:   # If player goes below the bottom
        p1.y = -p1.height  # Teleport to top


def move_p2(keys_pressed, p2):
    global p2_vel_x, p2_vel_y
    
    # Apply acceleration based on input
    if keys_pressed[pg.K_a] and p2.x > 0:
        p2_vel_x -= acceleration
    if keys_pressed[pg.K_d] and p2.x + p2.width < line.left:
        p2_vel_x += acceleration
    if keys_pressed[pg.K_w]:
        p2_vel_y -= acceleration
    if keys_pressed[pg.K_s]:
        p2_vel_y += acceleration
    
    # Apply friction
    p2_vel_x *= (1 - friction)
    p2_vel_y *= (1 - friction)
    
    # Limit maximum speed
    p2_vel_x = max(-max_speed, min(max_speed, p2_vel_x))
    p2_vel_y = max(-max_speed, min(max_speed, p2_vel_y))
    
    # Update position
    p2.x += p2_vel_x
    p2.y += p2_vel_y
    
    # Teleport from bottom to top or top to bottom
    if p2.y + p2.height < 0:  # If player goes above the top
        p2.y = win_height  # Teleport to bottom
    elif p2.y > win_height:   # If player goes below the bottom
        p2.y = -p2.height  # Teleport to top


def draw_window():
    
    screen.blit(bg_image, (0, 0))
    pg.draw.rect(screen, black, line)

    p1_text = font.render(f'Shield: {p1_shield}', True, white)
    p2_text = font.render(f'Shield: {p2_shield}', True, white)
    screen.blit(p1_text, (win_width - p1_text.get_width() - 10, 10))
    screen.blit(p2_text, (10, 10))

    screen.blit(p1_image, (p1.x, p1.y))
    screen.blit(p2_image, (p2.x, p2.y))

    for object in p1_objects:
        screen.blit(obj_image, object)

    for object in p2_objects:
        screen.blit(obj_image, object)

    for object in p1_super:
        screen.blit(super_image, object)

    for object in p2_super:
        screen.blit(super_image, object)

def collision_check():
    global p1_shield, p2_shield, p1_objects, p2_objects, max_projectiles
    global p1_boost_active, p1_boost_timer, p2_boost_active, p2_boost_timer
    
    for object in p1_objects:        
        object.x -= 10
        if p2.colliderect(object):
            p2_shield -= 1
            if not p2_boost_active:  # Only trigger if boost isn’t already active
                p2_boost_active = True
                p2_boost_timer = pg.time.get_ticks()  # Record the time when boost starts
                max_projectiles = original_max_projectiles + 5  # Increase to 15
            p1_objects.remove(object)
        elif object.x < 0:
            p1_objects.remove(object)
    
    for object in p2_objects:
        object.x += 10        
        if p1.colliderect(object):
            p1_shield -= 1
            if not p1_boost_active:  # Only trigger if boost isn’t already active
                p1_boost_active = True
                p1_boost_timer = pg.time.get_ticks()  # Record the time when boost starts
                max_projectiles = original_max_projectiles + 5  # Increase to 15
            p2_objects.remove(object)
        elif object.x > win_width:
            p2_objects.remove(object)

    # Super projectile collisions remain unchanged
    for object in p1_super:
        object.x -= 20
        if p2.colliderect(object):
            p2_shield -= 1
            if not p2_boost_active:
                p2_boost_active = True
                p2_boost_timer = pg.time.get_ticks()
                max_projectiles = original_max_projectiles + 5
            p1_super.remove(object)
        elif object.x < 0:
            p1_super.remove(object)

    for object in p2_super:
        object.x += 20
        if p1.colliderect(object):
            p1_shield -= 1
            if not p1_boost_active:
                p1_boost_active = True
                p1_boost_timer = pg.time.get_ticks()
                max_projectiles = original_max_projectiles + 5
            p2_super.remove(object)
        elif object.x > win_width:
            p2_super.remove(object)

def draw_win(text):
    global running
    bigfont = pg.font.Font(None, 50)
    label = bigfont.render(text, 1, white)
    screen.blit(label, (win_width / 2 - label.get_width() / 2, 10))
    pg.display.flip()
    time.sleep(2)
    running = False

async def main():
    global running, p1_boost_active, p2_boost_active, max_projectiles

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RCTRL and len(p1_objects) < max_projectiles:
                    object = pg.Rect(p1.centerx, p1.centery, obj_size, obj_size)
                    p1_objects.append(object)
                if event.key == pg.K_LCTRL and len(p2_objects) < max_projectiles:
                    object = pg.Rect(p2.centerx, p2.centery, obj_size, obj_size)
                    p2_objects.append(object)
                if event.key == pg.K_p and len(p1_super) < 1:
                    object = pg.Rect(p1.centerx, p1.centery, super_size, super_size)
                    p1_super.append(object)
                if event.key == pg.K_q and len(p2_super) < 1:
                    object = pg.Rect(p2.centerx, p2.centery, super_size, super_size)
                    p2_super.append(object)

        # Check and disable boosts after 5 seconds
        current_time = pg.time.get_ticks()
        if p1_boost_active and (current_time - p1_boost_timer >= 5000):
            p1_boost_active = False
            max_projectiles = original_max_projectiles  # Revert to 3
        if p2_boost_active and (current_time - p2_boost_timer >= 5000):
            p2_boost_active = False
            max_projectiles = original_max_projectiles  # Revert to 3

        keys_pressed = pg.key.get_pressed()
        move_p1(keys_pressed, p1)
        move_p2(keys_pressed, p2)

        collision_check()
        draw_window()
        
        if p1_shield <= 0:
            text = 'P2 Wins!'
            draw_win(text)
        if p2_shield <= 0:
            text = 'P1 Wins!'
            draw_win(text)
        
        clock.tick(60)
        pg.display.flip()

        await asyncio.sleep(0)

asyncio.run(main())