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
        "background": pygame.mixer.Sound("assets/sounds/background_melody.wav"),
        "object_place": pygame.mixer.Sound("assets/sounds/place.wav"),
        "object_rotate": pygame.mixer.Sound("assets/sounds/rotate.wav"),
        "ui_click" : pygame.mixer.Sound("assets/sounds/click.wav")
    }


def create_graphics():
    """Creates graphics for various UI components"""
    # Load inventory
    inventory = pygame.image.load("assets/graphics/inventory.png")
    inventory = pygame.transform.scale(inventory, (540, 346))
        
    return [inventory]