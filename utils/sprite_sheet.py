import pygame

class SpriteSheet:
    """"""
    
    def __init__(self, image_path):
        """Class for working with sprite sheets"""
        try:
            self.sheet = pygame.image.load(image_path)
        except pygame.error:
            print(f"Failed to load sprite sheet: {image_path}")
            # Create an empty surface as a fallback
            self.sheet = pygame.Surface((32, 32))
            self.sheet.fill((255, 0, 255))  # Magenta as error
    
    def get_sprite(self, x, y, width, height, scale=1):
        """Extracts a sprite from sheet at a given position"""
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        
        if scale != 1:
            sprite = pygame.transform.scale(sprite, (int(width * scale), int(height * scale)))
        
        return sprite