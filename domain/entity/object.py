import pygame


class Object(pygame.sprite.Sprite):
    """
    Class for object sprite

    object represents anything that is controlled by the player
    """
    def __init__(self, x, y, z, c, r, iso_utils, asset=None, obj_id=None):
        super().__init__()
        self.iso_utils = iso_utils
        self.grid_x = x
        self.grid_y = y
        self.grid_z = z
        self.col = c
        self.row = r
        self.animation_frame = 0
        self.animation_timer = 0
        self.flickering_timer = 0
        self.object_placed_position = None
        self.asset = asset
        self.obj_id = obj_id or (asset['id'] if asset else None)
        
        # Store camera offsets
        self.camera_offset_x = 0
        self.camera_offset_y = 0

        self.EMPTY_SPACE = 0
        self.WALL_TILE = 1
        self.TOP_SURFACE = 2
        self.NON_TOP_SURFACE = 3
        
        self.create_sprite()

    def create_sprite(self):
        # Flickering when moving the object
        if (self.flickering_timer // 3) % 2:
            self.image = self.iso_utils.create_object_sprite(self.col, self.row, 100, self.obj_id)
        else:
            self.image = self.iso_utils.create_object_sprite(self.col, self.row, 255, self.obj_id)
        
        self.rect = self.image.get_rect()
        self.update_position()

    def update_position(self, camera_offset_x=None, camera_offset_y=None):
        """Update position using the exact same logic as the render system"""
        if camera_offset_x is not None:
            self.camera_offset_x = camera_offset_x
        if camera_offset_y is not None:
            self.camera_offset_y = camera_offset_y
        
        screen_x, screen_y = self.iso_utils.grid_to_screen(self.grid_x, self.grid_y)
        self.rect.x = screen_x - self.iso_utils.half_tile_width + self.camera_offset_x
        
        # Apply z-positioning
        tile_spacing = 1.3
        base_y = screen_y - self.iso_utils.tile_height + self.camera_offset_y
        z_offset = self.grid_z * self.iso_utils.tile_height * tile_spacing
        self.rect.y = base_y - z_offset

    def move(self, dx, dy, dz, game_map, grid_width, grid_height, grid_volume):
        """
        Function for moving the object.
        It checks if the move is valid.
        Object cannot be moved out of the map, through the wall and through another object

        Inputs:
        -------
        dx : int
            x change from current position
        dy : int
            y change from current position
        dz : int
            z change from current position
        game_map : 3D array
            entire isometric room
        grid_width : int
            width of the map
        grid_height : int
            height of the map
        """

        # Store new position and check map border
        new_x = min(grid_width - 1, self.grid_x + dx)
        new_y = min(grid_height - 1, self.grid_y + dy)
        new_z = max(0, min(grid_volume - 1, self.grid_z + dz))

        # Check walls and objects
        if not self.asset.get('type') == 'surface item':
            if game_map[new_x, new_y, new_z] in (self.WALL_TILE, self.TOP_SURFACE, self.NON_TOP_SURFACE):
                return False
        else:
            if game_map[new_x, new_y, new_z] in (self.WALL_TILE, self.NON_TOP_SURFACE):
                return False
            elif game_map[new_x, new_y, new_z] == self.TOP_SURFACE:
                new_z += 1
            elif game_map[new_x, new_y, new_z - 1] == self.EMPTY_SPACE and new_z == 1:
                new_z -= 1
            elif game_map[new_x, new_y, new_z - 1] == self.NON_TOP_SURFACE and new_z == 1:
                return False

        # Apply movement
        self.grid_x, self.grid_y, self.grid_z = new_x, new_y, new_z
        self.update_position()
        return True
    
    def rotate(self):
        """
        Function for rotating the object.
        """
        current_c = self.col

        current_c += 1

        # Return to the first sprite
        if current_c == 4:
            current_c = 0
        
        self.col = current_c

        return True
    
    def flicker(self):
        """
        Function for object flickering.
        """
        self.flickering_timer += 1
        # Update sprite for flickering
        self.create_sprite()

    def animate(self, moving):
        """
        Updates the animation state of the object.

        Parameters:
        -----------
        moving : bool
            Whether the object is currently moving
        """
        self.animation_timer += 1
        if moving and self.animation_timer > 5:
            self.animation_frame = (self.animation_frame + 1) % 4
            self.animation_timer = 0
            self.create_sprite()  # Update the sprite for the new animation frame
    
    def set_object_placed_position(self, x, y):
        """Sets the position where an object has been placed"""
        self.object_placed_position = (x, y)