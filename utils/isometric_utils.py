import math
import pygame
from .sprite_sheet import SpriteSheet


class IsometricUtils:
    """Utility class for isometric coordinate conversions and rendering"""
    
    def __init__(self, tile_width=64, tile_height=32):
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.half_tile_width = tile_width // 2
        self.half_tile_height = tile_height // 2
        
        # Načti sprite sheety
        self.load_sprite_sheets()
    
    def load_sprite_sheets(self):
        """Načte všechny sprite sheety"""
        import os
        # Dynamická cesta - assets složka relativně k tomuto souboru
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        assets_dir = os.path.join(project_root, "assets")
        spritesheets_dir = os.path.join(assets_dir, "spritesheets")
        
        self.object_sheet = SpriteSheet(os.path.join(spritesheets_dir, "test_block.png"))
        self.sprites_loaded = True
        print(f"Sprite sheet loaded successfully from: {spritesheets_dir}")
        
    def grid_to_screen(self, grid_x, grid_y, z=0):
        """Convert grid coordinates to screen coordinates"""
        screen_x = (grid_x - grid_y) * self.half_tile_width
        screen_y = (grid_x + grid_y) * self.half_tile_height - z * self.half_tile_height
        return int(screen_x), int(screen_y)
    
    def screen_to_grid(self, screen_x, screen_y):
        """Convert screen coordinates to grid coordinates"""
        grid_x = (screen_x / self.half_tile_width + screen_y / self.half_tile_height) / 2
        grid_y = (screen_y / self.half_tile_height - screen_x / self.half_tile_width) / 2
        return int(grid_x), int(grid_y)
    
    def create_isometric_tile(self, color, height=1, with_sides=True):
        """Create an isometric tile sprite"""
        # Calculate total height including 3D effect
        total_height = self.tile_height + (height - 1) * self.half_tile_height
        surface = pygame.Surface((self.tile_width, total_height), pygame.SRCALPHA)
        
        # Top face (diamond shape)
        top_points = [
            (self.half_tile_width, 0),  # top
            (self.tile_width, self.half_tile_height),  # right
            (self.half_tile_width, self.tile_height),  # bottom
            (0, self.half_tile_height)  # left
        ]
        
        # Draw top face
        pygame.draw.polygon(surface, color, top_points)
        
        if with_sides and height > 1:
            # Left side
            left_color = tuple(max(0, c - 40) for c in color[:3])
            left_points = [
                (0, self.half_tile_height),
                (self.half_tile_width, self.tile_height),
                (self.half_tile_width, total_height),
                (0, total_height - self.half_tile_height)
            ]
            pygame.draw.polygon(surface, left_color, left_points)
            
            # Right side
            right_color = tuple(max(0, c - 60) for c in color[:3])
            right_points = [
                (self.tile_width, self.half_tile_height),
                (self.half_tile_width, self.tile_height),
                (self.half_tile_width, total_height),
                (self.tile_width, total_height - self.half_tile_height)
            ]
            pygame.draw.polygon(surface, right_color, right_points)
        
        # Add outline
        pygame.draw.polygon(surface, (0, 0, 0), top_points, 2)
        
        return surface
    
    def create_isometric_cube(self, color, size=1):
        """Create a 3D cube in isometric view"""
        cube_height = size * self.tile_height
        surface = pygame.Surface((self.tile_width, cube_height + self.half_tile_height), pygame.SRCALPHA)
        
        # Top face
        top_points = [
            (self.half_tile_width, 0),
            (self.tile_width, self.half_tile_height),
            (self.half_tile_width, self.tile_height),
            (0, self.half_tile_height)
        ]
        pygame.draw.polygon(surface, color, top_points)
        
        # Left side
        left_color = tuple(max(0, c - 40) for c in color[:3])
        left_points = [
            (0, self.half_tile_height),
            (self.half_tile_width, self.tile_height),
            (self.half_tile_width, cube_height + self.half_tile_height),
            (0, cube_height)
        ]
        pygame.draw.polygon(surface, left_color, left_points)
        
        # Right side
        right_color = tuple(max(0, c - 60) for c in color[:3])
        right_points = [
            (self.tile_width, self.half_tile_height),
            (self.half_tile_width, self.tile_height),
            (self.half_tile_width, cube_height + self.half_tile_height),
            (self.tile_width, cube_height)
        ]
        pygame.draw.polygon(surface, right_color, right_points)
        
        # Outlines
        pygame.draw.polygon(surface, (0, 0, 0), top_points, 2)
        pygame.draw.polygon(surface, (0, 0, 0), left_points, 2)
        pygame.draw.polygon(surface, (0, 0, 0), right_points, 2)
        
        return surface
    
    def create_object_sprite(self, base_color, c=0, r=0):
        """Create object sprite from sprite sheet"""
        if self.sprites_loaded and hasattr(self, 'object_sheet'):
                # Calculate sprite dimensions based on spritesheet dimensions (10x10 grid)
                total_width = self.object_sheet.sheet.get_width()
                total_height = self.object_sheet.sheet.get_height()
                sprite_width = total_width // 10
                sprite_height = total_height // 10
                
                # Get sprite from position (col, row)
                col, row = c, r
                
                # Use the SpriteSheet's get_sprite method with scale=4
                sprite = self.object_sheet.get_sprite(
                    col * sprite_width,
                    row * sprite_height,
                    sprite_width,
                    sprite_height,
                    scale=4
                )
                
                return sprite

        # Fallback to procedural generation
        obj_width = self.tile_width // 2
        obj_height = int(self.tile_height * 1.5)
        surface = pygame.Surface((obj_width, obj_height), pygame.SRCALPHA)
        object_rect = pygame.Rect(obj_width//4, obj_height//3, obj_width//2, obj_height//2)
        pygame.draw.ellipse(surface, base_color, object_rect)
        return surface
    
    def get_render_order(self, entities):
        """Sort entities by their render order (back to front)"""
        def sort_key(entity):
            # Sort by grid_y first (back to front), then by grid_x, then by z if available
            z = getattr(entity, 'z', 0)
            return (entity.grid_y + entity.grid_x, -z)
        
        return sorted(entities, key=sort_key)
    
    def get_tile_center_offset(self):
        """Get offset to center objects on tiles"""
        return self.half_tile_width, self.tile_height