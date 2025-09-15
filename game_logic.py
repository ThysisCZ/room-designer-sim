import numpy as np
import pygame
import os
from utils.path_utils import get_asset_path, get_spritesheet_path, debug_paths

def create_game_map(grid_width, grid_height, grid_depth):
    """Creates a 3D game map with walls"""
    game_map = np.zeros((grid_width, grid_height, grid_depth), dtype=int)

    # Create walls along the edges
    for z in range(grid_depth):
        game_map[:, 0, z] = 1  # north wall
        game_map[0, :, z] = 1  # east wall

    return game_map


def create_isometric_sprites(iso_utils, type, selected=None):
    """Creates isometric sprite objects for floor or wall from a spritesheet."""
    if type == 1:
        subdir = "floors"
        key = "floor"
        default_file = "stone_floor.png"
    else:
        subdir = "walls"
        key = "wall"
        default_file = "stone_wall.png"

    # Determine sprite file
    if selected and isinstance(selected, dict):
        sprite_file = selected.get("spritesheet", default_file)
    else:
        sprite_file = default_file

    # Build full path using centralized path resolution
    sprite_path = get_spritesheet_path(subdir, sprite_file)
    
    # Debug: Check if the file exists
    if not os.path.exists(sprite_path):
        print(f"ERROR: Sprite file not found at: {sprite_path}")
        debug_paths()  # Print debug info
        raise FileNotFoundError(f"Sprite file not found: {sprite_path}")

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
    menu_bg = pygame.image.load(get_asset_path("backgrounds", "menu.png"))
    menu_bg = pygame.transform.scale(menu_bg, (screen_width, screen_height))
        
    game_bg = pygame.image.load(get_asset_path("backgrounds", "game.png"))
    game_bg = pygame.transform.scale(game_bg, (screen_width, screen_height))

    snake_bg = pygame.image.load(get_asset_path("backgrounds", "snake.png")).convert()
    snake_bg = pygame.transform.scale(snake_bg, (screen_width, screen_height))

    fruit_bg = pygame.image.load(get_asset_path("backgrounds", "fruit.png")).convert()
    fruit_bg = pygame.transform.scale(fruit_bg, (screen_width, screen_height))

    bullet_bg = pygame.image.load(get_asset_path("backgrounds", "bullet.png")).convert()
    bullet_bg = pygame.transform.scale(bullet_bg, (screen_width, screen_height))
        
    return [menu_bg, game_bg, snake_bg, fruit_bg, bullet_bg]
    

def create_sounds():
    """Creates sounds for the game"""
    return {
        "background": pygame.mixer.Sound(get_asset_path("sounds", "main_theme.wav")),
        "minigame": pygame.mixer.Sound(get_asset_path("sounds", "minigame.wav")),
        "object_place": pygame.mixer.Sound(get_asset_path("sounds", "place.wav")),
        "object_rotate": pygame.mixer.Sound(get_asset_path("sounds", "rotate.wav")),
        "ui_click": pygame.mixer.Sound(get_asset_path("sounds", "click.wav")),
        "score": pygame.mixer.Sound(get_asset_path("sounds", "score.wav")),
        "bullets": pygame.mixer.Sound(get_asset_path("sounds", "bullets.wav")),
        "coin": pygame.mixer.Sound(get_asset_path("sounds", "coin.wav")),
        "hit": pygame.mixer.Sound(get_asset_path("sounds", "hit.wav"))
    }


def create_graphics():
    """Creates graphics for various UI components"""
    inventory = pygame.image.load(get_asset_path("graphics", "inventory.png"))
    inventory = pygame.transform.scale(inventory, (540, 346))

    minigames = pygame.image.load(get_asset_path("graphics", "minigames.png"))
    minigames = pygame.transform.scale(minigames, (540, 346))

    apple = pygame.image.load(get_asset_path("graphics", "apple.png"))

    snake_thumbnail = pygame.image.load(get_asset_path("graphics", "snake_thumbnail.png"))
    snake_thumbnail = pygame.transform.scale(snake_thumbnail, (115, 115))

    basket = pygame.image.load(get_asset_path("graphics", "basket.png"))
    basket = pygame.transform.scale(basket, (80, 80))

    orange = pygame.image.load(get_asset_path("graphics", "orange.png"))
    banana = pygame.image.load(get_asset_path("graphics", "banana.png"))
    dragon_fruit = pygame.image.load(get_asset_path("graphics", "dragon_fruit.png"))
    avocado = pygame.image.load(get_asset_path("graphics", "avocado.png"))

    fruit_thumbnail = pygame.image.load(get_asset_path("graphics", "fruit_thumbnail.png"))
    fruit_thumbnail = pygame.transform.scale(fruit_thumbnail, (100, 100))

    ship = pygame.image.load(get_asset_path("graphics", "spaceship.png"))
    ship = pygame.transform.scale(ship, (80, 80))

    red_ship = pygame.image.load(get_asset_path("graphics", "red_evil_spaceship.png"))
    orange_ship = pygame.image.load(get_asset_path("graphics", "orange_evil_spaceship.png"))
    yellow_ship = pygame.image.load(get_asset_path("graphics", "yellow_evil_spaceship.png"))
    purple_ship = pygame.image.load(get_asset_path("graphics", "purple_evil_spaceship.png"))
    green_ship = pygame.image.load(get_asset_path("graphics", "green_evil_spaceship.png"))

    dark_blue_bullet = pygame.image.load(get_asset_path("graphics", "dark_blue_bullet.png"))
    light_blue_bullet = pygame.image.load(get_asset_path("graphics", "light_blue_bullet.png"))
    dark_red_bullet = pygame.image.load(get_asset_path("graphics", "dark_red_bullet.png"))
    light_red_bullet = pygame.image.load(get_asset_path("graphics", "light_red_bullet.png"))

    bullet_thumbnail = pygame.image.load(get_asset_path("graphics", "bullet_thumbnail.png"))
    bullet_thumbnail = pygame.transform.scale(bullet_thumbnail, (100, 100))

    game_coin = pygame.image.load(get_asset_path("graphics", "game_coin.png"))

    total_balance = pygame.image.load(get_asset_path("graphics", "total_balance.png"))
    total_balance = pygame.transform.scale(total_balance, (152, 40))

    left_arrow = pygame.image.load(get_asset_path("graphics", "left_arrow.png"))
    left_arrow = pygame.transform.scale(left_arrow, (60, 45))

    right_arrow = pygame.image.load(get_asset_path("graphics", "right_arrow.png"))
    right_arrow = pygame.transform.scale(right_arrow, (60, 45))

    shop = pygame.image.load(get_asset_path("graphics", "shop.png"))
    shop = pygame.transform.scale(shop, (346, 540))

    logo = pygame.image.load(get_asset_path("graphics", "logo.png"))
    logo = pygame.transform.scale(logo, (720, 138))

    damaged_ship = pygame.image.load(get_asset_path("graphics", "damaged_spaceship.png"))
        
    return [inventory, minigames, apple, snake_thumbnail, basket,
            orange, banana, dragon_fruit, avocado, fruit_thumbnail,
            ship, red_ship, orange_ship, yellow_ship, purple_ship,
            green_ship, dark_blue_bullet, light_blue_bullet,
            dark_red_bullet, light_red_bullet, bullet_thumbnail,
            game_coin, total_balance, left_arrow, right_arrow,
            shop, logo, damaged_ship
        ]