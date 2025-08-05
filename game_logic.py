import numpy as np
import pygame
import os

def create_game_map(grid_width, grid_height, grid_volume):
    """Creates a 3D game map with walls"""
    game_map = np.zeros((grid_height, grid_width, grid_volume), dtype=int)

    # Create walls along the edges
    for z in range(grid_volume):
        game_map[0, :, z] = 1  # North wall
        game_map[:, 0, z] = 1  # West wall

    return game_map


def create_isometric_sprites(iso_utils, type, selected=None):
    """Creates isometric sprite objects for floor or wall from a spritesheet."""
    # Base directory
    base_path = "assets/spritesheets"

    if type == 1:  # Floor
        subdir = "floors"
        key = "floor"
        default_file = "stone_floor.png"
    else:  # Wall
        subdir = "walls"
        key = "wall"
        default_file = "stone_wall.png"

    # Determine sprite file
    if selected and isinstance(selected, dict):
        sprite_file = selected.get("spritesheet", default_file)
    else:
        sprite_file = default_file

    # Build full path
    sprite_path = os.path.join(base_path, subdir, sprite_file)

    # Load the image
    spritesheet = pygame.image.load(sprite_path).convert_alpha()

    sprite_width = spritesheet.get_width() // 10
    sprite_height = spritesheet.get_height() // 10

    sprite = pygame.transform.scale(
        spritesheet.subsurface((0, 0, sprite_width, sprite_height)),
        (sprite_width * 4, sprite_height * 4)
    )

    return [{key: sprite}]


def create_background(screen_width, screen_height):
    """Creates background"""
    # Load menu background
    menu_bg = pygame.image.load("assets/backgrounds/menu.png")
    menu_bg = pygame.transform.scale(menu_bg, (screen_width, screen_height))
        
    # Load game background
    game_bg = pygame.image.load("assets/backgrounds/game.png")
    game_bg = pygame.transform.scale(game_bg, (screen_width, screen_height))
        
    return [menu_bg, game_bg]
    

def create_sounds():
    """Creates sounds for the game"""
    return {
        "background": pygame.mixer.Sound("assets/sounds/main_theme.wav"),
        "minigame": pygame.mixer.Sound("assets/sounds/minigame.wav"),
        "object_place": pygame.mixer.Sound("assets/sounds/place.wav"),
        "object_rotate": pygame.mixer.Sound("assets/sounds/rotate.wav"),
        "ui_click" : pygame.mixer.Sound("assets/sounds/click.wav"),
        "score" : pygame.mixer.Sound("assets/sounds/score.wav"),
        "bullets" : pygame.mixer.Sound("assets/sounds/bullets.wav"),
        "coin" : pygame.mixer.Sound("assets/sounds/coin.wav")
    }


def create_graphics():
    """Creates graphics for various UI components"""
    inventory = pygame.image.load("assets/graphics/inventory.png")
    inventory = pygame.transform.scale(inventory, (540, 346))

    minigames = pygame.image.load("assets/graphics/minigames.png")
    minigames = pygame.transform.scale(minigames, (540, 346))

    apple = pygame.image.load("assets/graphics/apple.png")

    snake_thumbnail = pygame.image.load("assets/graphics/snake_thumbnail.png")
    snake_thumbnail = pygame.transform.scale(snake_thumbnail, (115, 115))

    basket = pygame.image.load("assets/graphics/basket.png")
    basket = pygame.transform.scale(basket, (80, 80))

    orange = pygame.image.load("assets/graphics/orange.png")
    banana = pygame.image.load("assets/graphics/banana.png")
    dragon_fruit = pygame.image.load("assets/graphics/dragon_fruit.png")
    avocado = pygame.image.load("assets/graphics/avocado.png")

    fruit_thumbnail = pygame.image.load("assets/graphics/fruit_thumbnail.png")
    fruit_thumbnail = pygame.transform.scale(fruit_thumbnail, (100, 100))

    ship = pygame.image.load("assets/graphics/spaceship.png")
    ship = pygame.transform.scale(ship, (80, 80))

    red_ship = pygame.image.load("assets/graphics/red_evil_spaceship.png")
    orange_ship = pygame.image.load("assets/graphics/orange_evil_spaceship.png")
    yellow_ship = pygame.image.load("assets/graphics/yellow_evil_spaceship.png")
    purple_ship = pygame.image.load("assets/graphics/purple_evil_spaceship.png")
    green_ship = pygame.image.load("assets/graphics/green_evil_spaceship.png")

    dark_blue_bullet = pygame.image.load("assets/graphics/dark_blue_bullet.png")
    light_blue_bullet = pygame.image.load("assets/graphics/light_blue_bullet.png")
    dark_red_bullet = pygame.image.load("assets/graphics/dark_red_bullet.png")
    light_red_bullet = pygame.image.load("assets/graphics/light_red_bullet.png")

    bullet_thumbnail = pygame.image.load("assets/graphics/bullet_thumbnail.png")
    bullet_thumbnail = pygame.transform.scale(bullet_thumbnail, (100, 100))

    game_coin = pygame.image.load("assets/graphics/game_coin.png")

    total_balance = pygame.image.load("assets/graphics/total_balance.png")
    total_balance = pygame.transform.scale(total_balance, (152, 40))

        
    return [inventory, minigames, apple, snake_thumbnail, basket,
            orange, banana, dragon_fruit, avocado, fruit_thumbnail,
            ship, red_ship, orange_ship, yellow_ship, purple_ship,
            green_ship, dark_blue_bullet, light_blue_bullet,
            dark_red_bullet, light_red_bullet, bullet_thumbnail,
            game_coin, total_balance
        ]