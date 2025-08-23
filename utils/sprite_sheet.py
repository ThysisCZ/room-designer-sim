import pygame

class SpriteSheet:
    """"""
    
    def __init__(self, image_path):
        """Class for working with sprite sheets"""
        self.sheet = pygame.image.load(image_path)
    
    def get_sprite(self, x, y, width, height, scale):
        """Extracts a sprite from sheet at a given position"""
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        
        if scale != 1:
            sprite = pygame.transform.scale(sprite, (int(width * scale), int(height * scale)))
        
        return sprite