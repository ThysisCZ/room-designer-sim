import pygame
from .sprite_sheet import SpriteSheet
import os

class IsometricUtils:
    """Utility class for isometric coordinate conversions and rendering"""
    
    def __init__(self, tile_width=64, tile_height=32):
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.half_tile_width = tile_width // 2
        self.half_tile_height = tile_height // 2
        self.sprites_loaded = False

        self.ITEM_TAB = 0
        self.FLOOR_TAB = 1
        self.WALL_TAB = 2
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.objects = pygame.sprite.Group()
    
    def load_sprite_sheets(self, selected, type):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)

        if type == self.ITEM_TAB:
            spritesheets_dir = os.path.join(project_root, "assets/", "spritesheets/", "items")
        elif type == self.FLOOR_TAB:
            spritesheets_dir = os.path.join(project_root, "assets/", "spritesheets/", "floors")
        else:
            spritesheets_dir = os.path.join(project_root, "assets/", "spritesheets/", "walls")

        spritesheets_path = os.path.join(spritesheets_dir, selected["spritesheet"])

        if type == self.ITEM_TAB:
            self.object_sheet = SpriteSheet(spritesheets_path)
        elif type == self.FLOOR_TAB:
            self.floor_sheet = SpriteSheet(spritesheets_path)
        else:
            self.wall_sheet = SpriteSheet(spritesheets_path)
            
        self.col = 0
        self.row = 0
        self.sprites_loaded = True
        
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
    
    def _load_object_spritesheet_by_id(self, object_id):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)

        spritesheets_dir = os.path.join(project_root, "assets/", "spritesheets/", "items")
        spritesheets_path = os.path.join(spritesheets_dir, f"{object_id}.png")

        if os.path.exists(spritesheets_path):
            self.object_sheet = SpriteSheet(spritesheets_path)
            self.sprites_loaded = True
    
    def create_object_sprite(self, c=0, r=0, alpha=255, object_id=None):
        """Create object sprite from sprite sheet"""
        col, row = c, r

        # Load sprite sheet if not already loaded
        if not self.sprites_loaded and object_id:
            self._load_object_spritesheet_by_id(object_id)

        if not hasattr(self, 'object_sheet'):
            raise RuntimeError("Object spritesheet not loaded or missing.")

        # Calculate sprite dimensions (assuming 10x10 grid)
        total_width = self.object_sheet.sheet.get_width()
        total_height = self.object_sheet.sheet.get_height()
        sprite_width = total_width // 10
        sprite_height = total_height // 10

        # Get sprite from position (col, row)
        sprite = self.object_sheet.get_sprite(
            col * sprite_width,
            row * sprite_height,
            sprite_width,
            sprite_height,
            scale=4
        )

        # Set opacity
        sprite.set_alpha(alpha)

        return sprite
    
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