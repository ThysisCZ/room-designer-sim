import pygame


class Object(pygame.sprite.Sprite):
    """
    Class for object sprite

    object represents anything that is controlled by the player
    """
    def __init__(self, x, y, c, r, iso_utils):
        super().__init__()
        self.iso_utils = iso_utils
        self.grid_x = x
        self.grid_y = y
        self.col = c
        self.row = r
        self.z = 0
        self.animation_frame = 0
        self.animation_timer = 0
        self.object_placed_position = None
        
        self.create_sprite()

    def create_sprite(self):
        self.image = self.iso_utils.create_object_sprite((0, 150, 255), self.col, self.row)
        
        self.rect = self.image.get_rect()
        self.update_position()

    def update_position(self):
        screen_x, screen_y = self.iso_utils.grid_to_screen(self.grid_x, self.grid_y, self.z)
        offset_x, offset_y = self.iso_utils.get_tile_center_offset()
        self.rect.centerx = screen_x + offset_x
        self.rect.bottom = screen_y + offset_y

    def move(self, dx, dy, game_map, grid_width, grid_height, objects=None):
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
        game_map : 3d array
            map of the game, used for determining valid moves
        grid_width : int
            width of the map, used for determining valid moves
        grid_height : int
            height of the map, used for determining valid moves
        objects, default None
            other objects placed on the map
        """
        new_x = max(0, min(grid_width - 1, self.grid_x + dx))
        new_y = max(0, min(grid_height - 1, self.grid_y + dy))

        # Kontrola stěn a položených objektů (2 je kód pro položený objekt)
        if game_map[new_y, new_x, 0] == 1 or game_map[new_y, new_x, 0] == 2:
            return False
        
        # Kontrola objektů
        if objects:
            for object in objects:
                if object.grid_x == new_x and object.grid_y == new_y:
                    # Pokud se snažíme jít na objekt a není to objekt, který jsme právě položili
                    if self.object_placed_position != (new_x, new_y):
                        return False
        
        # Pokud se pohybujeme, zkontroluj jestli opouštíme pozici s položeným objektem
        if self.object_placed_position and (self.grid_x, self.grid_y) == self.object_placed_position:
            # Opouštíme pozici s položeným objektem - už se na ni nemůžeme vrátit
            self.object_placed_position = None
        
        self.grid_x = new_x
        self.grid_y = new_y

        self.update_position()
        return True
    
    def rotate(self):
        """
        Function for rotating the object.
        """
        current_c = self.col

        current_c += 1

        if current_c == 4:
            current_c = 0
        
        self.col = current_c

        return True

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
        """Nastaví pozici kde hráč položil objekt"""
        self.object_placed_position = (x, y)