import pygame

from domain.entity.object import Object
from ui_components import GameState, Button, InventoryUI
from utils.isometric_utils import IsometricUtils
from game_logic import (create_game_map, create_isometric_sprites, create_sounds, create_background, create_graphics)
from storage.inventory_data import inventory_items

class RoomDesignerGame:
    """
    Main class containing the game
    """
    def __init__(self):
        """
        Initializes the game
        prepares map width and height, fps, welcome screen (with buttons)
        """
        pygame.init()
        # Get the display info to set up fullscreen dimensions
        display_info = pygame.display.Info()
        self.WIDTH = display_info.current_w
        self.HEIGHT = display_info.current_h
        self.FPS = 15
        
        # Set up fullscreen display
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Room Designer Simulator")
        self.clock = pygame.time.Clock()
        
        # Isometric setup - adjust tile size based on screen resolution
        self.base_tile_width = 64
        self.scale_factor = min(self.WIDTH / 1280, self.HEIGHT / 720)
        tile_width = int(self.base_tile_width * self.scale_factor)
        tile_height = int(tile_width * 0.5)
        self.iso_utils = IsometricUtils(tile_width=tile_width, tile_height=tile_height)
        self.camera_offset_x = self.WIDTH // 2
        self.camera_offset_y = int(self.HEIGHT * 0.38)
        
        self.game_state = GameState.MENU_SCREEN
        self.menu_screen_clicked = False

        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
        self.running = True
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.objects = pygame.sprite.Group()
        
        # UI buttons for menu
        self.play_button = Button(self.WIDTH//2 - 100, self.HEIGHT//2 - 30, 200, 50,
                                 "PLAY", self.font, (255, 255, 255), (255, 255, 255))
        self.quit_button = Button(self.WIDTH//2 - 100, self.HEIGHT//2 + 30, 200, 50,
                                 "QUIT", self.font, (255, 255, 255), (255, 255, 255))
        
        # UI buttons for game
        self.inventory_button = Button(self.WIDTH - 220, self.HEIGHT - 700, 200, 50,
                                 "Inventory", self.font, (255, 255, 255), (255, 255, 255))
        
        # No object at start
        self.object = None
        
        # Inventory
        self.show_inventory = False
        tabs = ["Items", "Floors", "Walls"]
        self.inventory_ui = InventoryUI(inventory_items, item_size=64, tabs=tabs, x=390, y=250)
        
        self.sprites_collection = create_isometric_sprites(self.iso_utils)
        self.bg_surface_collection = create_background(self.WIDTH, self.HEIGHT)
        self.ui_graphics_collection = create_graphics()
        self.sounds = create_sounds()
        self.init_game_world()

        self.inventory_border = self.ui_graphics_collection[0]
        
        self.sounds['background'].play(loops=-1).set_volume(0.7)
    
    def init_game_world(self):
        """
        generates the game map via create_game_map
        """
        self.grid_width = 12
        self.grid_height = 12
        self.grid_volume = 8
        
        # Create game map
        self.game_map = create_game_map(self.grid_width, self.grid_height, self.grid_volume)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if self.game_state == GameState.PLAYING:
                    if event.key == pygame.K_RETURN:
                        self.place_object()
                    elif event.key == pygame.K_r:
                        obj = next(iter(self.objects), None)
                        if obj:
                            obj.rotate()
                            obj.animate(True)  # Trigger animation for one frame
                            self.sounds['object_rotate'].play().set_volume(0.6)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_state == GameState.MENU_SCREEN:
                    if self.play_button.handle_event(event):
                        self.sounds['ui_click'].play().set_volume(1.0)
                        self.restart_game()
                    elif self.quit_button.handle_event(event):
                        self.running = False
                elif self.game_state == GameState.PLAYING:
                    if self.inventory_button.handle_event(event):
                        if self.show_inventory == True:
                            self.sounds['ui_click'].play().set_volume(1.0)
                            self.show_inventory = False
                        else:
                            self.sounds['ui_click'].play().set_volume(1.0)
                            self.show_inventory = True
                    elif self.show_inventory:
                        selected = self.inventory_ui.handle_click(pygame.mouse.get_pos())

                        # Handle tab and item click
                        if selected:
                            self.sounds['ui_click'].play().set_volume(1.0)

                            # Create an object
                            if isinstance(selected, dict):
                                self.iso_utils.load_sprite_sheets(selected)

                                # Default starting position
                                start_x, start_y = 1, 1

                                if hasattr(self, "object") and self.object:
                                    start_x = self.object.grid_x
                                    start_y = self.object.grid_y

                                    self.objects.remove(self.object)
                                    self.all_sprites.remove(self.object)

                                self.object = Object(x=start_x, y=start_y, c=0, r=0, iso_utils=self.iso_utils)
                                self.objects.add(self.object)
                                self.all_sprites.add(self.object)
                        # Close inventory
                        else:
                            self.sounds['ui_click'].play().set_volume(1.0)
                            self.show_inventory = False
                            
            elif event.type == pygame.MOUSEMOTION:
                if self.game_state == GameState.MENU_SCREEN:
                    self.play_button.handle_event(event)  # Handle hover effects
                    self.quit_button.handle_event(event)
                elif self.game_state == GameState.PLAYING:
                    self.inventory_button.handle_event(event)
    
    def update(self):
        if self.game_state == GameState.PLAYING:
            self.update_object_movement()
    
    def update_object_movement(self):
        """
        Processes the movements of the object being placed.
        """
        moving = False
        
        # Flickering effect
        if self.object:
            self.object.flicker()
        
        obj = self.object
        keys = pygame.key.get_pressed()
        if obj:
            if keys[pygame.K_LEFT]:
                if obj.move(-1, 0, self.game_map, self.grid_width, self.grid_height):
                    moving = True
            elif keys[pygame.K_RIGHT]:
                if obj.move(1, 0, self.game_map, self.grid_width, self.grid_height):
                    moving = True
            elif keys[pygame.K_UP]:
                if obj.move(0, -1, self.game_map, self.grid_width, self.grid_height):
                    moving = True
            elif keys[pygame.K_DOWN]:
                if obj.move(0, 1, self.game_map, self.grid_width, self.grid_height):
                    moving = True
        
            # Call animate on the object if it's moving
            obj.animate(moving)
    
    def place_object(self):
        """
        Processes the object placement. Creates a static copy at the current position
        and marks it as placed.
        """
        # Check if object exists
        if self.object:
            # Get the current position
            current_x = self.object.grid_x
            current_y = self.object.grid_y

            # Get the current sprite
            current_c = self.object.col
            current_r = self.object.row
        
            # Make sure the place is not occupied
            if self.game_map[current_y, current_x, 0] == 0:
                # Create a static copy of the object at the current position
                static_object = Object(current_x, current_y, current_c, current_r, self.iso_utils)
                static_object.create_sprite()
                self.all_sprites.add(static_object)
                
                self.sounds['object_place'].play().set_volume(1.0)

                # Mark the position in the game map as occupied
                self.game_map[current_y, current_x, 0] = 2
                self.object.set_object_placed_position(current_x, current_y)
    
    def draw(self):
        """Function drawing screen content according to the state of the game"""
        self.screen.fill((0, 0, 0))
        
        if self.game_state == GameState.MENU_SCREEN:
            self.draw_menu_screen()
        elif self.game_state == GameState.MENU:
            self.draw_menu()
        elif self.game_state == GameState.PLAYING:
            self.draw_game()
            if self.show_inventory:
                self.inventory_ui.draw(self.screen)

        pygame.display.flip()

    def change_used_sprites(self, is_menu=False):
        """Changes the sprite collection based on game state"""
        if is_menu:
            self.sprites = self.sprites_collection[0]
            self.bg_surface = self.bg_surface_collection[0]  # Menu background
        else:
            self.sprites = self.sprites_collection[0]
            self.bg_surface = self.bg_surface_collection[1]  # Game background

    def draw_menu_screen(self):
        """
        Draws menu screen.
        """
        self.change_used_sprites(is_menu=True)
        
        self.screen.blit(self.bg_surface, (0, 0))
        
        title_text = self.big_font.render("Room Designer Simulator", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.WIDTH // 2, 175))
        
        self.screen.blit(title_text, title_rect)
        
        self.play_button.draw(self.screen)
        self.quit_button.draw(self.screen)
        
        authors = [
            ("Thysis", "Game Development & Game Design"),
            ("Nene", "Main Music (Theme Song)"),
            ("Matthew Pablo", "Minigame Music (Space Dimensions)")
        ]

        controls = [
            ("Arrow keys", "Move"),
            ("R", "Rotate"),
            ("Enter", "Place"),
            ("Escape", "Quit game")
        ]
        
        small_font = pygame.font.Font(None, 30)
        y_offset = self.HEIGHT - 120
        
        # Draw authors on the left
        for author, roles in authors:
            author_text = small_font.render(f"{author}: {roles}", True, (255, 255, 255))
            self.screen.blit(author_text, (48, y_offset))
            y_offset += 30
        
        # Reset y_offset for controls and draw them on the right
        y_offset = self.HEIGHT - 150
        for control, action in controls:
            control_text = small_font.render(f"{control}: {action}", True, (255, 255, 255))
            self.screen.blit(control_text, (1053, y_offset))
            y_offset += 30
    
    def draw_game(self):
        """Draws room."""
        
        self.change_used_sprites()
        
        self.screen.blit(self.bg_surface, (0, 0))
        
        self.inventory_button.draw(self.screen)
        
        render_list = []
        
        # Collect all tiles and objects for proper depth sorting
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                # Calculate base position for the tile
                screen_x, screen_y = self.iso_utils.grid_to_screen(x, y)
                screen_x += self.camera_offset_x
                screen_y += self.camera_offset_y
                
                # Floor tile - render for empty spaces and spaces with objects
                if self.game_map[y, x, 0] == 0 or self.game_map[y, x, 0] == 2:
                    floor_rect = self.sprites['floor'].get_rect()
                    floor_rect.x = screen_x - self.iso_utils.half_tile_width
                    floor_rect.y = screen_y - self.iso_utils.half_tile_height + 15
                    render_list.append((y + x, 'floor', floor_rect))
                
                # Walls - render each layer
                if self.game_map[y, x, 0] == 1:
                    # Render each vertical layer of the wall
                    for z in range(self.grid_volume):
                        if self.game_map[y, x, z] == 1:
                            wall_rect = self.sprites['wall'].get_rect()
                            wall_rect.x = screen_x - self.iso_utils.half_tile_width
                            # Full tile height offset for each level to prevent merging
                            wall_rect.y = screen_y - self.iso_utils.half_tile_height - (z * self.iso_utils.tile_height + self.iso_utils.half_tile_height - 2.5)
                            render_list.append((y + x + z * 0.1, 'wall', wall_rect))
        
        all_entities = list(self.all_sprites) + list(self.iso_utils.all_sprites)

        if self.object:
            all_entities.append(self.object)

        sorted_entities = self.iso_utils.get_render_order(all_entities)
        
        for sprite in sorted_entities:
            adjusted_rect = sprite.rect.copy()
            screen_x, screen_y = self.iso_utils.grid_to_screen(sprite.grid_x, sprite.grid_y)
            adjusted_rect.x = screen_x - self.iso_utils.half_tile_width + self.camera_offset_x
            adjusted_rect.y = screen_y - self.iso_utils.tile_height + self.camera_offset_y
            render_depth = sprite.grid_y + sprite.grid_x + 0.5
            render_list.append((render_depth, 'sprite', sprite, adjusted_rect))
        
        # Sort and render everything
        render_list.sort(key=lambda item: item[0])
        
        for item in render_list:
            if item[1] == 'sprite':
                sprite, rect = item[2], item[3]
                self.screen.blit(sprite.image, rect)
            else:
                sprite_type, rect = item[1], item[2]
                self.screen.blit(self.sprites[sprite_type], rect)
        
        if self.show_inventory:
            self.screen.blit(self.inventory_border, (375, 170))
    
    def clear_sprites(self):
        """Deletes all sprite groups"""
        self.all_sprites.empty()
        self.objects.empty()

    def restart_game(self):
        """Restarts game"""
        self.clear_sprites()
        self.init_game_world()
        self.game_state = GameState.PLAYING

    def run(self):
        """
        Main loop of the game.

        1. events are handled.
        2. all sprites are updated
        3. screen is redrawn
        4. fixed FPS
        """
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.FPS)

        pygame.quit()