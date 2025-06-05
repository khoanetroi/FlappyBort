import pygame
from pygame.locals import *
import random
import sys
import os

pygame.init()

clock = pygame.time.Clock()
fps = 60

# Screen setup
screen_width = 664
screen_height = 736
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# Font
font = pygame.font.SysFont('Bauhaus 93', 60)

# Colours
white = (255, 255, 255)

# Game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
main_menu = True
selected_skin = 1  # default skin index
shop_menu = False

# Load images
bg = pygame.image.load('img/bg.png').convert()
ground_img = pygame.image.load('img/ground.png').convert_alpha()
button_img = pygame.image.load('img/newgame_btn.png').convert_alpha()
new_game_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/quit_btn.png').convert_alpha()
menu_img = pygame.image.load('img/menu_btn.png').convert_alpha()
game_over_img = pygame.image.load('img/gameover.png').convert_alpha()
game_logo_img = pygame.image.load('img/flappy_logo.png').convert_alpha()
shop_img = pygame.image.load('img/shop_btn.png').convert_alpha()

# Load bird skins dynamically and resize all skins to the size of bird1.png
bird_skins = []

# Load bird1.png first to get base size
base_bird_img = pygame.image.load('img/bird1.png').convert_alpha()
base_size = base_bird_img.get_size()

# Now scan img folder for bird skins (bird1.png, bird2.png, bird3.png, etc.)
# You can add as many skins as you want with this naming pattern: birdX.png
skin_index = 1
while True:
    skin_path = f'img/bird{skin_index}.png'
    if not os.path.isfile(skin_path):
        break
    skin_img = pygame.image.load(skin_path).convert_alpha()
    skin_img = pygame.transform.scale(skin_img, base_size)  # resize to base size
    bird_skins.append(skin_img)
    skin_index += 1

# If no skins found, fallback to base bird1.png
if len(bird_skins) == 0:
    bird_skins.append(base_bird_img)

# draw center text
def draw_center_text(text, font, color, x, y):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(x, y))
    screen.blit(img, rect)

# Reset game
def reset_game():
    pipe_group.empty()
    global flappy
    flappy = Bird(100, screen_height // 2, selected_skin)
    bird_group.empty()
    bird_group.add(flappy)
    return 0

# Bird class
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y, skin_index):
        super().__init__()
        # Use the loaded skin images list to support animation if needed
        # For now, just single image for selected skin
        self.images = [bird_skins[skin_index - 1]]  # list of one image
        self.index = 0
        self.counter = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = 0
        self.clicked = False

    def update(self):
        if flying:
            self.vel += 0.5
            self.vel = min(self.vel, 8)
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if not game_over:
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            self.counter += 1
            if self.counter > 5:
                self.counter = 0
                self.index = (self.index + 1) % len(self.images)
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

# Pipe class
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        super().__init__()
        self.image = pygame.image.load('img/pipe.png').convert_alpha()
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - pipe_gap // 2]
        else:
            self.rect.topleft = [x, y + pipe_gap // 2]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

# Button class with hover effect
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.original_image = image.copy()
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            bright_image = pygame.Surface(self.image.get_size()).convert_alpha()
            bright_image.fill((40, 40, 40, 0))
            hover_img = self.original_image.copy()
            hover_img.blit(bright_image, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            screen.blit(hover_img, self.rect)
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        else:
            screen.blit(self.image, self.rect)

        return action


# Sprite groups
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, screen_height // 2, selected_skin)
bird_group.add(flappy)

# Buttons
restart_button = Button(screen_width // 2, screen_height // 2 + 20, button_img)
back_to_menu_button = Button(screen_width // 2, screen_height // 2 + 160, menu_img)
exit_button_gameover = Button(screen_width // 2, screen_height // 2 + 220, exit_img)
new_game_button = Button(screen_width // 2, screen_height // 2 - 70, new_game_img)
shop_button = Button(screen_width // 2, screen_height // 2 + 10, shop_img)
exit_button_mainmenu = Button(screen_width // 2, screen_height // 2 + 90, exit_img)
menu_button_gameover = Button(screen_width // 2, screen_height // 2 + 130, menu_img) 


# Main loop
run = True
while run:
    clock.tick(fps)

    screen.blit(bg, (0, 0))

    # Main Menu
    if main_menu and not shop_menu:
        screen.blit(ground_img, (0, 700))
        screen.blit(game_logo_img, game_logo_img.get_rect(center=(screen_width // 2, screen_height // 2 - 200)))

        if new_game_button.draw():
            main_menu = False
            shop_menu = False
            flying = False
            game_over = False
            score = reset_game()

        if shop_button.draw():
            shop_menu = True  # go to shop

        if exit_button_mainmenu.draw():
            run = False

    # Shop Menu
    elif shop_menu:
        screen.blit(ground_img, (0, 700))
        draw_center_text("Select a Bird Skin", font, white, screen_width // 2, 80)

        for i, skin in enumerate(bird_skins):
            skin_scaled = pygame.transform.scale(skin, (60, 60))
            rect = skin_scaled.get_rect(center=(150 + i * 100, 200))
            screen.blit(skin_scaled, rect)

            if rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                selected_skin = i + 1
                flappy = Bird(100, screen_height // 2, selected_skin)
                bird_group.empty()
                bird_group.add(flappy)

        if back_to_menu_button.draw():
            shop_menu = False
            main_menu = True

    # Gameplay
    else:
        bird_group.draw(screen)
        bird_group.update()
        pipe_group.draw(screen)
        screen.blit(ground_img, (ground_scroll, 700))  # Ground position fixed to 700, matches main menu

        if len(pipe_group) > 0:
            bird = bird_group.sprites()[0]
            pipe = pipe_group.sprites()[0]
            if bird.rect.left > pipe.rect.left and bird.rect.right < pipe.rect.right and not pass_pipe:
                pass_pipe = True
            if pass_pipe and bird.rect.left > pipe.rect.right:
                score += 1
                pass_pipe = False

        draw_center_text(str(score), font, white, screen_width // 2, 50)

        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
            game_over = True
        if flappy.rect.bottom >= 700:
            game_over = True
            flying = False

        if not game_over and flying:
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > pipe_frequency:
                pipe_height = random.randint(-100, 100)
                pipe_group.add(Pipe(screen_width, screen_height // 2 + pipe_height, -1))
                pipe_group.add(Pipe(screen_width, screen_height // 2 + pipe_height, 1))
                last_pipe = time_now

            ground_scroll -= scroll_speed
            if abs(ground_scroll) > 35:
                ground_scroll = 0

            pipe_group.update()

        if game_over:
            screen.blit(game_over_img, game_over_img.get_rect(center=(screen_width // 2, screen_height // 2 - 150)))
            
            if restart_button.draw():
                game_over = False
                flying = False
                score = reset_game()

            if menu_button_gameover.draw():
                game_over = False
                flying = False
                main_menu = True
                shop_menu = False

            if exit_button_gameover.draw():
                run = False

    # Global events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over and not main_menu:
            flying = True

    pygame.display.update()

pygame.quit()
sys.exit()
