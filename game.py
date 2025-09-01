import pygame, time, random, json, os

from domain.entity.object import Object
from ui_components import Button, InventoryUI, MinigameUI, ShopUI
from domain.state.states import GameState
from utils.isometric_utils import IsometricUtils
from game_logic import (create_game_map, create_isometric_sprites, create_sounds, create_background, create_graphics)
import storage.inventory_abl as inventory_abl
from storage.shop_data import shop_assets
import storage.selection_abl as selection_abl
import storage.tile_abl as tile_abl

class RoomDesignerGame:
    """
    Main class containing the game
    """
    def __init__(self):
        """
        Initializes the game
        prepares menu screen and game map
        """
        pygame.init()
        # Set up fullscreen dimensions
        display_info = pygame.display.Info()
        self.WIDTH = display_info.current_w
        self.HEIGHT = display_info.current_h
        self.FPS = 15
        
        # Set up fullscreen display
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Room Designer Simulator")
        self.clock = pygame.time.Clock()

        # Set up tile types
        self.EMPTY_SPACE = 0
        self.WALL_TILE = 1
        self.TOP_SURFACE = 2
        self.NON_TOP_SURFACE = 3

        # Set up tab types
        self.ITEM_TAB = 0
        self.FLOOR_TAB = 1
        self.WALL_TAB = 2

        # Set up minigame types
        self.SNAKE = 0
        self.CATCH_THE_FRUIT = 1
        self.BULLET_HELL = 2
        
        # Isometric setup - adjust tile size based on screen resolution
        self.base_tile_width = 64
        self.scale_factor = min(self.WIDTH / 1280, self.HEIGHT / 720)
        tile_width = int(self.base_tile_width * self.scale_factor)
        tile_height = int(tile_width * 0.5)
        self.iso_utils = IsometricUtils(tile_width=tile_width, tile_height=tile_height)
        self.camera_offset_x = self.WIDTH // 2 # Center room horizontally
        self.camera_offset_y = self.HEIGHT * 0.35 # Center room vertically
        
        self.game_state = GameState.MENU

        self.font = pygame.font.Font('ithaca.ttf', 36)
        self.big_font = pygame.font.Font('ithaca.ttf', 72)
        
        self.running = True
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.objects = pygame.sprite.Group()
        self.sprites = {
            "floor": create_isometric_sprites(self.iso_utils, 1)[0]["floor"],
            "wall": create_isometric_sprites(self.iso_utils, 2)[0]["wall"]
        }
        
        # UI buttons for menu
        self.play_button = Button(self.WIDTH//2 - 100, self.HEIGHT//2 - 30, 200, 50,
                                 "PLAY", self.font, (255, 255, 255), (255, 255, 255))
        self.quit_button = Button(self.WIDTH//2 - 100, self.HEIGHT//2 + 30, 200, 50,
                                 "QUIT", self.font, (255, 255, 255), (255, 255, 255))
        
        # UI buttons for game
        self.inventory_button = Button(self.WIDTH - 220, self.HEIGHT - 700, 200, 50,
                                 "Inventory", self.font, (255, 255, 255), (255, 255, 255))
        self.minigame_button = Button(self.WIDTH - 220, self.HEIGHT - 640, 200, 50,
                                 "Minigames", self.font, (255, 255, 255), (255, 255, 255))
        self.shop_button = Button(self.WIDTH - 220, self.HEIGHT - 580, 200, 50,
                                 "Shop", self.font, (255, 255, 255), (255, 255, 255))
        self.buy_button = Button(20, self.HEIGHT - 640, 200, 50,
                                 "Buy", self.font, (255, 255, 255), (255, 255, 255))
        self.sell_button = Button(20, self.HEIGHT - 640, 200, 50,
                                 "Sell", self.font, (255, 255, 255), (255, 255, 255))
        
        self.show_buy_button = False
        self.show_sell_button = False
        
        # No object at start
        self.object = None

        self.total_balance, self.snake_hi_score, self.fruit_hi_score, self.bullet_hi_score = self.load_stats_data()

        # Inventory
        self.show_inventory = False
        inventory = inventory_abl.load_inventory()

        self.selected_item_data = None
        self.selected_tab = 0
        
        selected_assets = selection_abl.load_selected_assets()
        self.selected_floor_data = selected_assets['floor']
        self.selected_wall_data = selected_assets['wall']

        self.inventory_ui = InventoryUI(inventory['item'],
                                        inventory['floor'], 
                                        inventory['wall'], 
                                        item_size=64, 
                                        tabs=["Items", "Floors", "Walls"], 
                                        x=385, 
                                        y=250,
                                        cols=8,
                                        rows=4,
                                        selected_item=self.selected_item_data,
                                        selected_floor=self.selected_floor_data,
                                        selected_wall=self.selected_wall_data,
                                        selected_tab=self.selected_tab,
                                        total_balance=self.total_balance
                                    )

        # Minigames
        self.show_minigames = False
        self.minigame_ui = MinigameUI(thumbnail_size=128, 
                                        x=385,
                                        y=250,
                                        cols=4,
                                        rows=2
                                    )
        
        # Shop
        self.show_shop = False
        self.shop_ui = ShopUI(shop_assets,
                              thumbnail_size=128, 
                              x=517,
                              y=105,
                              cols=2,
                              rows=4,
                              total_balance=self.total_balance
                            )
        
        self.hovered_asset = None

        # Determine asset type based on selected tab
        if self.selected_tab == self.FLOOR_TAB:
            self.sprites_collection = create_isometric_sprites(self.iso_utils, self.FLOOR_TAB)
        elif self.selected_tab == self.WALL_TAB:
            self.sprites_collection = create_isometric_sprites(self.iso_utils, self.WALL_TAB)
        else:
            # Default floor and wall
            floor = create_isometric_sprites(self.iso_utils, self.FLOOR_TAB)[0]
            wall = create_isometric_sprites(self.iso_utils, self.WALL_TAB)[0]
            self.sprites_collection = [{**floor, **wall}]
        
        self.bg_surface_collection = create_background(self.WIDTH, self.HEIGHT)
        self.ui_graphics_collection = create_graphics()
        self.sounds = create_sounds()
        self.init_game_world()

        self.inventory_border = self.ui_graphics_collection[0]
        self.minigames_border = self.ui_graphics_collection[1]
        self.balance_border = self.ui_graphics_collection[22]
        self.shop_border = self.ui_graphics_collection[25]
        
        self.sounds['background'].play(loops=-1).set_volume(0.8)
        self.sounds['object_rotate'].set_volume(0.6)
        self.sounds['ui_click'].set_volume(0.6)
    
    def init_game_world(self):
        """
        generates the game map via create_game_map
        """
        self.grid_width = 12
        self.grid_height = 12
        self.grid_depth = 5
        
        # Create game map
        self.game_map = create_game_map(self.grid_width, self.grid_height, self.grid_depth)
    
    def init_snake_game(self):
        self.game_state = GameState.SNAKE
        self.sounds = create_sounds()
        self.sounds['minigame'].play(loops=-1).set_volume(0.4)
        self.sounds['score'].set_volume(1)
        self.sounds['coin'].set_volume(0.2)

        pygame.mouse.set_visible(False)

        self.bg_surface = self.bg_surface_collection[2]

        self.area_size = 500

        # Snake start position
        self.snake_pos = [self.WIDTH//3 + 100, self.HEIGHT//2]
        self.snake_speed = 10

        # Set framerate
        self.clock = pygame.time.Clock()

        self.snake_body = [[self.WIDTH//3 + 100, self.HEIGHT//2], [self.WIDTH//3 + 90, self.HEIGHT//2]]
        self.snake_size = 40

        self.graphics_collection = create_graphics()
        self.food_image = self.graphics_collection[2]

        # Area for random generation
        self.food_pos = [random.randrange(int(self.WIDTH//3.25), (int(self.HEIGHT//3.25) + self.area_size - self.snake_size)),
                            random.randrange(int(self.WIDTH//6), (int(self.HEIGHT//6) + self.area_size - self.snake_size))
                        ]
        
        self.food_size = 30

        self.food_eaten = False

        self.coin_image = pygame.transform.scale(self.graphics_collection[21], (30, 30))

        self.coin_pos = [random.randrange(int(self.WIDTH//3.25), (int(self.HEIGHT//3.25) + self.area_size - self.snake_size)),
                            random.randrange(int(self.WIDTH//6), (int(self.HEIGHT//6) + self.area_size - self.snake_size))
                        ]
        
        self.coin_size = 30

        self.coin_picked = False

        self.coin_spawn_rate = None

        self.coin_pause = False

        self.score = 0
        self.coins = 0

        self.growth_counter = 0
        self.block_counter = 0

        def show_score():
            font = pygame.font.Font('ithaca.ttf', 30)

            score_text = font.render('Score: ' + str(self.score), True, 'white')
            score_rect = score_text.get_rect()
            score_rect.bottomright = (self.WIDTH - self.WIDTH//3.25, self.HEIGHT//6 - 10)
            self.screen.blit(score_text, score_rect)

            current_hs = self.snake_hi_score if self.snake_hi_score > self.score else self.score

            hi_score_text = font.render('Hi-Score: ' + str(current_hs), True, 'white')
            hi_score_rect = hi_score_text.get_rect()
            hi_score_rect.bottomright = (self.WIDTH - self.WIDTH//3.25, self.HEIGHT//6 - 30)
            self.screen.blit(hi_score_text, hi_score_rect)
        
        def show_coins():
            font = pygame.font.Font('ithaca.ttf', 30)

            coin_text = font.render('Gamecoins: ' + str(self.coins), True, 'white')
            coin_rect = coin_text.get_rect()
            coin_rect.bottomleft = (self.WIDTH//3.25, self.HEIGHT//6 - 10)
            self.screen.blit(coin_text, coin_rect)

        def game_over():
            # Keep border and score on the screen
            border_rect = pygame.Rect(self.WIDTH//3.25, self.HEIGHT//6, self.area_size, self.area_size)
            pygame.draw.rect(self.screen, (255, 255, 255), border_rect, 3)
            show_score()

            font = pygame.font.Font('ithaca.ttf', 50)

            game_over_text = font.render(
                'GAME OVER', True, 'white')
            game_over_rect = game_over_text.get_rect()
            game_over_rect.midtop = (self.WIDTH/2, self.HEIGHT/4)
            self.screen.blit(game_over_text, game_over_rect)

            score_text = font.render(
                'Score: ' + str(self.score), True, 'white')
            score_rect = score_text.get_rect()
            score_rect.midtop = (self.WIDTH/2, self.HEIGHT/3)
            self.screen.blit(score_text, score_rect)

            show_score()
            show_coins()

            self.total_balance += self.coins
            self.save_stats_data(
                                    balance=self.total_balance,
                                    snake_hs=self.snake_hi_score,
                                    fruit_hs=self.fruit_hi_score,
                                    bullet_hs=self.bullet_hi_score
                                )

            # Handle new hi-score
            if self.score > self.snake_hi_score:
                self.snake_hi_score = self.score
                self.save_stats_data(
                                    balance=self.total_balance,
                                    snake_hs=self.snake_hi_score,
                                    fruit_hs=self.fruit_hi_score,
                                    bullet_hs=self.bullet_hi_score
                                )
            
            selection_abl.save_selected_assets(
                                self.selected_floor_data,
                                self.selected_wall_data
                            )

            pygame.display.flip()
            time.sleep(2)
            self.restart_game()
            self.sounds['ui_click'].set_volume(0.6)

        # Handle snake movements
        dir = 'RIGHT'
        next_dir = dir

        # Game loop
        while self.game_state == GameState.SNAKE:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        # If UP is pressed, next_dir becomes UP
                        next_dir = 'UP'
                    if event.key == pygame.K_DOWN:
                        next_dir = 'DOWN'
                    if event.key == pygame.K_LEFT:
                        next_dir = 'LEFT'
                    if event.key == pygame.K_RIGHT:
                        next_dir = 'RIGHT'
                    # Quit
                    if event.key == pygame.K_ESCAPE:
                        self.total_balance += self.coin_count
                        self.save_stats_data(
                                    balance=self.total_balance,
                                    snake_hs=self.snake_hi_score,
                                    fruit_hs=self.fruit_hi_score,
                                    bullet_hs=self.bullet_hi_score
                                )
                        
                        selection_abl.save_selected_assets(
                                self.selected_floor_data,
                                self.selected_wall_data
                            )
                        
                        self.restart_game()
            
            # Update the movements with input in next_dir
            if next_dir == 'UP' and dir != 'DOWN':
                # If DOWN is pressed while snake goes UP, no changes occur
                dir = 'UP'
            if next_dir == 'DOWN' and dir != 'UP':
                dir = 'DOWN'
            if next_dir == 'LEFT' and dir != 'RIGHT':
                dir = 'LEFT'
            if next_dir == 'RIGHT' and dir != 'LEFT':
                dir = 'RIGHT'

            # Change snake's position
            if dir == 'UP':
                self.snake_pos[1] -= 10
            if dir == 'DOWN':
                self.snake_pos[1] += 10
            if dir == 'LEFT':
                self.snake_pos[0] -= 10
            if dir == 'RIGHT':
                self.snake_pos[0] += 10

            # Insert every coordinate the snake passes through
            self.snake_body.insert(0, list(self.snake_pos))

            snake_rect = pygame.Rect(self.snake_pos[0], self.snake_pos[1], self.snake_size, self.snake_size)
            food_rect = pygame.Rect(self.food_pos[0], self.food_pos[1], self.food_size, self.food_size)
            coin_rect = pygame.Rect(self.coin_pos[0], self.coin_pos[1], self.coin_size, self.coin_size)

            # Prevent snake from growing
            def stop_growth():
                if self.growth_counter > 0:
                    self.growth_counter -= 1 
                else:
                    self.snake_body.pop()

            # Handle food and coin collisions
            if snake_rect.colliderect(food_rect):
                self.sounds['score'].play()
                self.score += 10
                self.food_eaten = True
                self.growth_counter += 7
            elif snake_rect.colliderect(coin_rect):
                self.sounds['coin'].play()
                self.coins += 1
                self.coin_picked = True
                
                stop_growth()
            else:
                stop_growth()

            self.coin_spawn_rate = random.randint(1, 12)

            # Assign a new coordinate to food/coin position
            if self.food_eaten:
                self.food_pos = [random.randrange(int(self.WIDTH//3.25), (int(self.HEIGHT//3.25) + self.area_size - self.snake_size)),
                            random.randrange(int(self.WIDTH//6), (int(self.HEIGHT//6) + self.area_size - self.snake_size))
                        ]
                
                # Randomly spawn new coin when food is eaten
                if self.coin_pause and self.coin_spawn_rate <= 3:
                    self.coin_pos = [random.randrange(int(self.WIDTH//3.25), (int(self.HEIGHT//3.25) + self.area_size - self.snake_size)),
                        random.randrange(int(self.WIDTH//6), (int(self.HEIGHT//6) + self.area_size - self.snake_size))
                    ]

                    self.coin_pause = False
            elif self.coin_picked:
                if self.coin_spawn_rate <= 3:
                    self.coin_pos = [random.randrange(int(self.WIDTH//3.25), (int(self.HEIGHT//3.25) + self.area_size - self.snake_size)),
                        random.randrange(int(self.WIDTH//6), (int(self.HEIGHT//6) + self.area_size - self.snake_size))
                    ]

                    self.coin_pause = False
                else:
                    self.coin_pos = [-self.coin_size, 0]

                    self.coin_pause = True
            
            self.food_eaten = False
            self.coin_picked = False
            self.screen.blit(self.bg_surface, (0, 0))

            # Draw the snake
            for pos in self.snake_body:
                self.block_counter += 1

                if self.block_counter % 2 == 0:
                    pygame.draw.rect(self.screen, 'dark green', (pos[0], pos[1], self.snake_size, self.snake_size), 30, 5)
                else:
                    pygame.draw.rect(self.screen, 'green', (pos[0], pos[1], self.snake_size, self.snake_size), 30, 5)

            self.screen.blit(self.food_image, (self.food_pos[0], self.food_pos[1]))
            self.screen.blit(self.coin_image, (self.coin_pos[0], self.coin_pos[1]))

            # Game over conditions
            if self.snake_pos[0] < self.WIDTH//3.25 or self.snake_pos[0] > self.WIDTH//3.25 + self.area_size - self.snake_size:
                game_over()
            elif self.snake_pos[1] < self.HEIGHT//6 or self.snake_pos[1] > self.HEIGHT//6 + self.area_size - self.snake_size:
                game_over()
            # Snake bites itself
            for block in self.snake_body[1:]:
                if self.snake_pos[0] == block[0] and self.snake_pos[1] == block[1]:
                    game_over()
            
            border_rect = pygame.Rect(self.WIDTH//3.25, self.HEIGHT//6, self.area_size, self.area_size)
            pygame.draw.rect(self.screen, (255, 255, 255), border_rect, 3)

            show_score()
            show_coins()

            pygame.display.update()
            self.clock.tick(self.snake_speed)
        
    def init_catch_the_fruit(self):
        self.game_state = GameState.CATCH_THE_FRUIT
        self.sounds = create_sounds()
        self.sounds['minigame'].play(loops=-1).set_volume(0.4)
        self.sounds['score'].set_volume(1)
        self.sounds['coin'].set_volume(0.2)

        pygame.mouse.set_visible(False)

        self.bg_surface = self.bg_surface_collection[3]

        self.basket_size = 80

        self.border_offset = 3

        # Basket start position
        self.basket_pos = [self.WIDTH//2 - self.basket_size//2, self.HEIGHT - self.basket_size - self.border_offset]

        self.basket_speed = 50

        self.graphics_collection = create_graphics()

        self.basket_image = self.graphics_collection[4]

        # Set framerate
        self.clock = pygame.time.Clock()
        self.minigame_FPS = 60

        self.food_image = None

        self.food_size = 50

        # Area for random generation
        self.food_pos = [0, 0]
        
        # List of food positions
        self.foods = []

        self.food_images = [
            pygame.transform.scale(self.graphics_collection[2], (self.food_size, self.food_size)),
            pygame.transform.scale(self.graphics_collection[5], (self.food_size, self.food_size)),
            pygame.transform.scale(self.graphics_collection[6], (self.food_size, self.food_size)),
            pygame.transform.scale(self.graphics_collection[7], (self.food_size, self.food_size)),
            pygame.transform.scale(self.graphics_collection[8], (self.food_size, self.food_size)),
        ]

        self.food_speed = 3

        self.food_count = 1

        self.coin_image = pygame.transform.scale(self.graphics_collection[21], (50, 50))

        self.coin_size = 50

        self.coin_pos = [0, 0]

        self.coins = []

        self.score = 0
        self.coin_count = 0
        self.timer = 0

        self.score_font = pygame.font.Font('ithaca.ttf', 30)
        self.info_font = pygame.font.Font('ithaca.ttf', 24)

        def show_score():
            font = pygame.font.Font('ithaca.ttf', 30)

            score_text = font.render('Score: ' + str(self.score), False, 'white')
            score_rect = score_text.get_rect()
            score_rect.bottomleft = (self.WIDTH - self.WIDTH//5 + 25, 60)
            self.screen.blit(score_text, score_rect)

            current_hs = self.fruit_hi_score if self.fruit_hi_score > self.score else self.score

            hi_score_text = font.render('Hi-Score: ' + str(current_hs), False, 'white')
            hi_score_rect = hi_score_text.get_rect()
            hi_score_rect.bottomleft = (self.WIDTH - self.WIDTH//5 + 25, 40)
            self.screen.blit(hi_score_text, hi_score_rect)

        def show_coins():
            font = pygame.font.Font('ithaca.ttf', 30)

            coin_text = font.render('Gamecoins: ' + str(self.coin_count), False, 'white')
            coin_rect = coin_text.get_rect()
            coin_rect.bottomleft = (self.WIDTH - self.WIDTH//5 + 25, 80)
            self.screen.blit(coin_text, coin_rect)
        
        def show_info():
            info = [
                    ("INFO:"),
                    ("Hold left SHIFT to dash")
                ]

            font = pygame.font.Font('ithaca.ttf', 24)
            y_offset = self.HEIGHT - 55

            for row in info:
                info_text = font.render(f"{row}", False, (255, 255, 255))
                self.screen.blit(info_text, (20, y_offset))
                y_offset += 20

        # Game loop
        while self.game_state == GameState.CATCH_THE_FRUIT:
            # Clear the screen each frame to prevent trails
            self.screen.blit(self.bg_surface, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    # Quit
                    if event.key == pygame.K_ESCAPE:
                        self.total_balance += self.coin_count
                        self.save_stats_data(
                                    balance=self.total_balance,
                                    snake_hs=self.snake_hi_score,
                                    fruit_hs=self.fruit_hi_score,
                                    bullet_hs=self.bullet_hi_score
                                )
                        
                        selection_abl.save_selected_assets(
                                self.selected_floor_data,
                                self.selected_wall_data
                            )
                        
                        self.restart_game()

            self.timer += 1

            def basket_dash():
                if self.basket_speed < 275:
                    if keys[pygame.K_LSHIFT]:
                        self.basket_speed += 45
                        
            # Handle movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.basket_pos[0] -= self.basket_speed // 10
                basket_dash()
            if keys[pygame.K_RIGHT]:
                self.basket_pos[0] += self.basket_speed // 10
                basket_dash()
            
            # Border detection
            if self.basket_pos[0] < self.WIDTH//5 + self.border_offset:
                self.basket_pos[0] = self.WIDTH//5 + self.border_offset
            elif self.basket_pos[0] > self.WIDTH - self.WIDTH//5 - self.basket_size - self.border_offset:
                self.basket_pos[0] = self.WIDTH - self.WIDTH//5 - self.basket_size - self.border_offset
            
            # Reset basket speed
            if self.basket_speed == 275 and not keys[pygame.K_LSHIFT]:
                self.basket_speed = 50

            basket_rect = pygame.Rect(self.basket_pos[0], self.basket_pos[1], self.basket_size, self.basket_size//6)
            food_rect = pygame.Rect(self.food_pos[0], self.food_pos[1], self.food_size, self.food_size)

            if basket_rect.colliderect(food_rect):
                self.sounds['score'].play()
                self.score += 10
            
            # Generate new fruit
            def generate_food():
                # Random position
                new_food_pos = [random.randrange(self.WIDTH//5, self.WIDTH - self.WIDTH//5 - self.food_size), 0]
                
                # Random new image
                new_food_image = random.choice(self.food_images)
                
                self.foods.append({"pos": new_food_pos, "image": new_food_image})
                self.food_count += 1

            # Change food spawn frequency
            if self.food_speed == 3:
                if self.timer % 120 == 0:
                    generate_food()
            elif self.food_speed == 6:
                if self.timer % 60 == 0:
                    generate_food()
            elif self.food_speed == 8:
                if self.timer % 30 == 0:
                    generate_food()

            # Draw the basket
            self.screen.blit(self.basket_image, (self.basket_pos[0], self.basket_pos[1]))

            # Draw the food
            for food in self.foods[:]:
                food_pos = food["pos"]
                food_image = food["image"]

                food_rect = pygame.Rect(food_pos[0], food_pos[1], self.food_size, self.food_size)

                if basket_rect.colliderect(food_rect):
                    self.sounds['score'].play()
                    self.score += 10
                    self.foods.remove(food)

                if food_pos[1] > self.HEIGHT:
                    self.foods.remove(food)

                # Falling
                self.screen.blit(food_image, (food_pos[0], food_pos[1]))

                if self.food_count >= 15 and self.food_count < 30:
                    self.food_speed = 6
                elif self.food_count >= 30:
                    self.food_speed = 8
                
                food_pos[1] += self.food_speed

                # Game over
                if food_pos[1] > self.HEIGHT:
                    border_rect = pygame.Rect(self.WIDTH//5, 0, self.WIDTH - 2 * (self.WIDTH//5), self.HEIGHT)
                    pygame.draw.rect(self.screen, (255, 255, 255), border_rect, 3)

                    show_score()
                    show_coins()
                    show_info()

                    font = pygame.font.Font('ithaca.ttf', 50)

                    game_over_text = font.render(
                        'GAME OVER', True, 'white')
                    game_over_rect = game_over_text.get_rect()
                    game_over_rect.midtop = (self.WIDTH/2, self.HEIGHT/4)
                    self.screen.blit(game_over_text, game_over_rect)

                    score_text = font.render(
                        'Score: ' + str(self.score), True, 'white')
                    score_rect = score_text.get_rect()
                    score_rect.midtop = (self.WIDTH/2, self.HEIGHT/3)
                    self.screen.blit(score_text, score_rect)

                    self.total_balance += self.coin_count
                    self.save_stats_data(
                                            balance=self.total_balance,
                                            snake_hs=self.snake_hi_score,
                                            fruit_hs=self.fruit_hi_score,
                                            bullet_hs=self.bullet_hi_score
                                        )

                    # Handle new hi-score
                    if self.score > self.fruit_hi_score:
                        self.fruit_hi_score = self.score
                        self.save_stats_data(
                                            balance=self.total_balance,
                                            snake_hs=self.snake_hi_score,
                                            fruit_hs=self.fruit_hi_score,
                                            bullet_hs=self.bullet_hi_score
                                        )
                    
                    selection_abl.save_selected_assets(
                                self.selected_floor_data,
                                self.selected_wall_data
                            )

                    pygame.display.flip()
                    time.sleep(2)
                    self.restart_game()
                    self.sounds['ui_click'].set_volume(0.6)
            
            # Generate new coin
            def generate_coin():
                # Random position
                new_coin_pos = [random.randrange(self.WIDTH//5, self.WIDTH - self.WIDTH//5 - self.food_size),
                                -2 * self.basket_size
                            ]
                
                self.coins.append({"pos": new_coin_pos})

            # Change coin spawn frequency
            if self.food_speed == 3:
                if self.timer % 960 == 0:
                    generate_coin()
            elif self.food_speed == 6:
                if self.timer % 480 == 0:
                    generate_coin()
            elif self.food_speed == 8:
                if self.timer % 240 == 0:
                    generate_coin()

            # Draw the coins
            for coin in self.coins[:]:
                coin_pos = coin["pos"]

                coin_rect = pygame.Rect(coin_pos[0], coin_pos[1], self.coin_size, self.coin_size)

                if basket_rect.colliderect(coin_rect):
                    self.sounds['coin'].play()
                    self.coin_count += 1
                    self.coins.remove(coin)

                if coin_pos[1] > self.HEIGHT:
                    self.coins.remove(coin)

                # Falling
                self.screen.blit(self.coin_image, (coin_pos[0], coin_pos[1]))
                
                coin_pos[1] += self.food_speed
            
            # Draw border
            border_rect = pygame.Rect(self.WIDTH//5, 0, self.WIDTH - 2 * (self.WIDTH//5), self.HEIGHT)
            pygame.draw.rect(self.screen, (255, 255, 255), border_rect, 3)

            show_score()
            show_coins()
            show_info()

            pygame.display.update()
            self.clock.tick(self.minigame_FPS)
    
    def init_bullet_hell(self):
        self.game_state = GameState.BULLET_HELL
        self.sounds = create_sounds()
        self.sounds['minigame'].play(loops=-1).set_volume(0.4)
        self.sounds['score'].set_volume(1.5)
        self.sounds['bullets'].set_volume(0.3)
        self.sounds['coin'].set_volume(0.2)
        self.sounds['hit'].set_volume(0.125)

        pygame.mouse.set_visible(False)

        self.bg_surface = self.bg_surface_collection[4]

        self.player_size = 80

        self.border_offset = 3

        # Player start position
        self.player_pos = [self.WIDTH//2 - self.player_size//2, self.HEIGHT - self.player_size]

        self.player_speed = 100

        self.graphics_collection = create_graphics()

        self.player_image = self.graphics_collection[10]

        self.hitbox_size = 15

        self.hitbox_pos = [self.player_pos[0] + self.player_size//2, self.player_pos[1] + self.player_size//2]

        self.player_bullet_pos = [0, 0]

        self.player_bullets = []

        self.bullet_size = 15

        self.bullet_speed = 9

        # Set framerate
        self.clock = pygame.time.Clock()
        self.minigame_FPS = 60

        self.enemy_image = None

        self.enemy_size = 80

        # Area for random generation
        self.enemy_pos = [0, 0]
        
        # List of enemy positions
        self.enemies = []

        self.enemy_speed = 6

        self.enemy_count = 1

        self.enemy_bullet_pos = [0, 0]

        self.enemy_bullets = []

        self.coin_size = 50

        self.coin_image = pygame.transform.scale(self.graphics_collection[21], (self.coin_size, self.coin_size))

        self.coin_pos = [0, 0]

        self.coins = []

        self.score = 0
        self.coin_count = 0
        self.timer = 0

        self.player_bullet_images = [
            pygame.transform.scale(self.graphics_collection[16], (self.bullet_size, self.bullet_size)),
            pygame.transform.scale(self.graphics_collection[17], (self.bullet_size, self.bullet_size))
        ]
        
        self.enemy_bullet_images = [
            pygame.transform.scale(self.graphics_collection[18], (self.bullet_size, self.bullet_size)),
            pygame.transform.scale(self.graphics_collection[19], (self.bullet_size, self.bullet_size))
        ]
        
        self.enemy_images = [
            pygame.transform.scale(self.graphics_collection[11], (self.enemy_size, self.enemy_size)),
            pygame.transform.scale(self.graphics_collection[12], (self.enemy_size, self.enemy_size)),
            pygame.transform.scale(self.graphics_collection[13], (self.enemy_size, self.enemy_size)),
            pygame.transform.scale(self.graphics_collection[14], (self.enemy_size, self.enemy_size)),
            pygame.transform.scale(self.graphics_collection[15], (self.enemy_size, self.enemy_size))
        ]

        self.damage_image = pygame.transform.scale(self.graphics_collection[27], (self.enemy_size, self.enemy_size))

        self.MAX_PLAYER_BULLETS = 150
        self.MAX_ENEMY_BULLETS = 300
        self.MAX_ENEMIES = 50
        self.ENEMY_HEALTH = 10

        background_rect = pygame.Rect(0, 0, self.WIDTH, self.HEIGHT)
        pygame.draw.rect(self.screen, (0, 0, 0), background_rect)

        self.score_font = pygame.font.Font('ithaca.ttf', 30)
        self.info_font = pygame.font.Font('ithaca.ttf', 24)

        def show_score():
            font = pygame.font.Font('ithaca.ttf', 30)

            score_text = font.render('Score: ' + str(self.score), False, 'white')
            score_rect = score_text.get_rect()
            score_rect.bottomleft = (self.WIDTH - self.WIDTH//5 + 25, 60)
            self.screen.blit(score_text, score_rect)

            current_hs = self.bullet_hi_score if self.bullet_hi_score > self.score else self.score

            hi_score_text = font.render('Hi-Score: ' + str(current_hs), False, 'white')
            hi_score_rect = hi_score_text.get_rect()
            hi_score_rect.bottomleft = (self.WIDTH - self.WIDTH//5 + 25, 40)
            self.screen.blit(hi_score_text, hi_score_rect)

        def show_coins():
            font = pygame.font.Font('ithaca.ttf', 30)

            coin_text = font.render('Gamecoins: ' + str(self.coin_count), False, 'white')
            coin_rect = coin_text.get_rect()
            coin_rect.bottomleft = (self.WIDTH - self.WIDTH//5 + 25, 80)
            self.screen.blit(coin_text, coin_rect)
        
        def show_info():
            info = [
                    ("INFO:"),
                    ("Hold Y/Z key to shoot"),
                    ("Hold left SHIFT to focus")
                ]

            font = pygame.font.Font('ithaca.ttf', 24)
            y_offset = self.HEIGHT - 75

            for row in info:
                info_text = font.render(f"{row}", False, (255, 255, 255))
                self.screen.blit(info_text, (20, y_offset))
                y_offset += 20

        # Game loop
        while self.game_state == GameState.BULLET_HELL:
            # Clear the screen each frame to prevent trails
            self.screen.blit(self.bg_surface, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.total_balance += self.coin_count
                        self.save_stats_data(
                                    balance=self.total_balance,
                                    snake_hs=self.snake_hi_score,
                                    fruit_hs=self.fruit_hi_score,
                                    bullet_hs=self.bullet_hi_score
                                )
                        
                        selection_abl.save_selected_assets(
                                self.selected_floor_data,
                                self.selected_wall_data
                            )
                        
                        self.restart_game()

            self.timer += 1

            def player_focus():
                if self.player_speed > 50:
                    if keys[pygame.K_LSHIFT]:
                        self.player_speed -= 50
            
            # Handle movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player_pos[0] -= self.player_speed // 10
                player_focus()
            if keys[pygame.K_RIGHT]:
                self.player_pos[0] += self.player_speed // 10
                player_focus()
            if keys[pygame.K_DOWN]:
                self.player_pos[1] += self.player_speed // 10
                player_focus()
            if keys[pygame.K_UP]:
                self.player_pos[1] -= self.player_speed // 10
                player_focus()
            
            # Border detection
            if self.player_pos[0] < self.WIDTH//5 + self.border_offset:
                self.player_pos[0] = self.WIDTH//5 + self.border_offset
            elif self.player_pos[0] > self.WIDTH - self.WIDTH//5 - self.player_size - self.border_offset:
                self.player_pos[0] = self.WIDTH - self.WIDTH//5 - self.player_size - self.border_offset
            elif self.player_pos[1] < 0:
                self.player_pos[1] = 0
            elif self.player_pos[1] > self.HEIGHT - self.player_size:
                self.player_pos[1] = self.HEIGHT - self.player_size
            
            # Handle position conflicts
            if (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) and keys[pygame.K_UP]:
                if self.player_pos[1] < 0:
                    self.player_pos[1] = 0
            elif (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) and keys[pygame.K_DOWN]:
                if self.player_pos[1] > self.HEIGHT - self.player_size:
                    self.player_pos[1] = self.HEIGHT - self.player_size
            
            # Reset player speed
            if self.player_speed == 50 and not keys[pygame.K_LSHIFT]:
                self.player_speed = 100

            hitbox_rect = pygame.Rect(self.player_pos[0] + self.player_size//2, self.player_pos[1] + self.player_size//2,
                                    self.hitbox_size, self.hitbox_size)
            
            # Generate new player bullet
            def generate_player_bullet():
                if len(self.player_bullets) >= self.MAX_PLAYER_BULLETS:
                    return 
                
                new_bullet_pos = [random.randrange(self.player_pos[0], self.player_pos[0] + self.player_size),
                                self.player_pos[1]]
                
                bullet_image = random.choice(self.player_bullet_images)
                
                self.player_bullets.append({"pos": new_bullet_pos, "image": bullet_image})

            # Shoot bullets
            if keys[pygame.K_y] or keys[pygame.K_z]:
                self.sounds['bullets'].play(loops=-1)
                if self.timer % 3 == 0:
                    generate_player_bullet()
            elif not keys[pygame.K_y] or not keys[pygame.K_z]:
                self.sounds['bullets'].stop()

            # Update and draw player bullets
            idx = 0
            while idx < len(self.player_bullets):
                bullet = self.player_bullets[idx]
                bullet_pos = bullet["pos"]
                bullet_image = bullet["image"]

                bullet_pos[1] -= self.bullet_speed
                
                if bullet_pos[1] < -self.bullet_size:
                    del self.player_bullets[idx]
                    continue
                    
                self.screen.blit(bullet_image, (bullet_pos[0], bullet_pos[1]))
                idx += 1
            
            player_rect = pygame.Rect(self.player_pos[0], self.player_pos[1], self.player_size, self.player_size//6)
            
            # Generate new enemy
            def generate_enemy():
                if len(self.enemies) >= self.MAX_ENEMIES:
                    return
                    
                new_enemy_pos = [random.randrange(self.WIDTH//5, self.WIDTH - self.WIDTH//5 - self.enemy_size), 0]
                
                enemy_image = random.choice(self.enemy_images)

                hit_count = 0
                
                self.enemies.append({"pos": new_enemy_pos, 
                                "image": enemy_image, 
                                "last_shot": self.timer,
                                "hit_count": hit_count})
                
                self.enemy_count += 1
            
            # Spawn enemy bullets periodically
            for enemy in self.enemies:
                if len(self.enemy_bullets) >= self.MAX_ENEMY_BULLETS:
                    break
                    
                if self.timer - enemy["last_shot"] >= 15:
                    enemy_x, enemy_y = enemy["pos"]
                    bullet_x = random.randint(enemy_x, enemy_x + self.enemy_size)
                    bullet_y = enemy_y + self.enemy_size

                    bullet_image = random.choice(self.enemy_bullet_images)

                    self.enemy_bullets.append({
                        "pos": [bullet_x, bullet_y],
                        "image": bullet_image
                    })

                    enemy["last_shot"] = self.timer  # reset shot timer

            #Change enemy spawn frequency
            if self.enemy_count <= 15:
                if self.timer % 30 == 0:
                    generate_enemy()
            elif self.enemy_count > 15 and self.enemy_count <= 30:
                if self.timer % 25 == 0:
                    generate_enemy()
            elif self.enemy_count > 30:
                if self.timer % 13 == 0:
                    generate_enemy()

            # Draw the player and hitbox
            self.screen.blit(self.player_image, (self.player_pos[0], self.player_pos[1]))
            pygame.draw.circle(self.screen, 'black',
                            (self.player_pos[0] + self.player_size//2,
                                self.player_pos[1] + self.player_size//2), 12)
            pygame.draw.circle(self.screen, 'white',
                            (self.player_pos[0] + self.player_size//2,
                                self.player_pos[1] + self.player_size//2), 7.5)
            
            # Generate new coin
            def generate_coin():
                new_coin_pos = [random.randrange(self.WIDTH//5, self.WIDTH - self.WIDTH//5 - self.coin_size), 0]
                
                self.coins.append({"pos": new_coin_pos})

            # Coin spawn frequency
            if self.timer % 240 == 0:
                generate_coin()

            # Update and draw coins
            idx = 0
            while idx < len(self.coins):
                coin = self.coins[idx]
                coin_pos = coin["pos"]

                coin_rect = pygame.Rect(coin_pos[0], coin_pos[1], self.coin_size, self.coin_size)

                if player_rect.colliderect(coin_rect):
                    self.sounds['bullets'].stop()
                    self.sounds['coin'].play()
                    self.coin_count += 1
                    del self.coins[idx]
                    continue

                coin_pos[1] += self.enemy_speed
                
                if coin_pos[1] > self.HEIGHT:
                    del self.coins[idx]
                    continue

                self.screen.blit(self.coin_image, (coin_pos[0], coin_pos[1]))
                idx += 1

            def game_over():
                border_rect = pygame.Rect(self.WIDTH//5, 0, self.WIDTH - 2 * (self.WIDTH//5), self.HEIGHT)
                pygame.draw.rect(self.screen, (255, 255, 255), border_rect, 3)

                show_score()
                show_coins()
                show_info()

                font = pygame.font.Font('ithaca.ttf', 50)

                game_over_text = font.render(
                    'GAME OVER', True, 'white')
                game_over_rect = game_over_text.get_rect()
                game_over_rect.midtop = (self.WIDTH/2, self.HEIGHT/4)
                self.screen.blit(game_over_text, game_over_rect)

                score_text = font.render(
                    'Score: ' + str(self.score), True, 'white')
                score_rect = score_text.get_rect()
                score_rect.midtop = (self.WIDTH/2, self.HEIGHT/3)
                self.screen.blit(score_text, score_rect)

                self.total_balance += self.coin_count
                self.save_stats_data(
                                        balance=self.total_balance,
                                        snake_hs=self.snake_hi_score,
                                        fruit_hs=self.fruit_hi_score,
                                        bullet_hs=self.bullet_hi_score
                                    )
                
                # Handle new hi-score
                if self.score > self.bullet_hi_score:
                    self.bullet_hi_score = self.score
                    self.save_stats_data(
                                            balance=self.total_balance,
                                            snake_hs=self.snake_hi_score,
                                            fruit_hs=self.fruit_hi_score,
                                            bullet_hs=self.bullet_hi_score
                                        )
                
                selection_abl.save_selected_assets(
                                self.selected_floor_data,
                                self.selected_wall_data
                            )

                pygame.display.flip()
                time.sleep(2)
                self.restart_game()
                self.sounds['ui_click'].set_volume(0.6)

            # Update and draw enemies
            idx = 0
            while idx < len(self.enemies):
                enemy = self.enemies[idx]
                enemy_pos = enemy["pos"]
                enemy_image = enemy["image"]

                enemy_pos[1] += self.enemy_speed
                
                if enemy_pos[1] > self.HEIGHT + self.enemy_size:
                    del self.enemies[idx]
                    continue

                # Check hitbox-enemy collisions
                enemy_rect = pygame.Rect(enemy_pos[0], enemy_pos[1], self.enemy_size, self.enemy_size)
                
                if hitbox_rect.colliderect(enemy_rect):
                    self.sounds['bullets'].stop()
                    game_over()
                    return
                
                self.screen.blit(enemy_image, (enemy_pos[0], enemy_pos[1]))
                idx += 1
            
            bullets_to_remove = []
            enemies_to_remove = []

            # Handle enemy-bullet collisions
            for bullet in self.player_bullets:
                if bullet in bullets_to_remove:
                    continue
                    
                bullet_pos = bullet["pos"]
                bullet_rect = pygame.Rect(bullet_pos[0], bullet_pos[1], self.bullet_size, self.bullet_size)

                for enemy in self.enemies:
                    if enemy in enemies_to_remove:
                        continue
                        
                    enemy_pos = enemy["pos"]
                    enemy_rect = pygame.Rect(enemy_pos[0], enemy_pos[1], self.enemy_size, self.enemy_size)
                    enemy_image = self.damage_image

                    # Enemy hit
                    if bullet_rect.colliderect(enemy_rect):
                        enemy["hit_count"] += 1
                        self.sounds['bullets'].stop()
                        self.sounds['hit'].play()
                        self.screen.blit(enemy_image, enemy_rect)

                        bullets_to_remove.append(bullet)
                    # Enemy death
                    elif enemy["hit_count"] > self.ENEMY_HEALTH:
                        self.sounds['bullets'].stop()
                        self.sounds['hit'].stop()
                        self.sounds['score'].play()
                        self.score += 10

                        enemies_to_remove.append(enemy)
            
            # Remove bullets
            for bullet in bullets_to_remove:
                if bullet in self.player_bullets:
                    self.player_bullets.remove(bullet)

            # Remove enemies
            for enemy in enemies_to_remove:
                if enemy in self.enemies:
                    self.enemies.remove(enemy)

            # Update and draw enemy bullets
            idx = 0
            while idx < len(self.enemy_bullets):
                bullet = self.enemy_bullets[idx]
                bullet_pos = bullet["pos"]
                bullet_image = bullet["image"]

                bullet_pos[1] += self.bullet_speed

                if bullet_pos[1] > self.HEIGHT + self.bullet_size:
                    del self.enemy_bullets[idx]
                    continue

                # Check hitbox-bullet collisions
                bullet_rect = pygame.Rect(bullet_pos[0], bullet_pos[1], self.bullet_size, self.bullet_size)
                if hitbox_rect.colliderect(bullet_rect):
                    self.sounds['bullets'].stop()
                    game_over()
                    return

                self.screen.blit(bullet_image, (bullet_pos[0], bullet_pos[1]))
                idx += 1
            
            # Draw border
            border_rect = pygame.Rect(self.WIDTH//5, 0, self.WIDTH - 2 * (self.WIDTH//5), self.HEIGHT)
            pygame.draw.rect(self.screen, (255, 255, 255), border_rect, 3)

            show_score()
            show_coins()
            show_info()

            pygame.display.update()
            self.clock.tick(self.minigame_FPS)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if self.game_state == GameState.MENU:
                    if event.key == pygame.K_ESCAPE:
                        selection_abl.save_selected_assets(
                                self.selected_floor_data,
                                self.selected_wall_data
                            )
                        
                        self.running = False
                elif self.game_state == GameState.PLAYING:
                    if event.key == pygame.K_SPACE:
                        self.place_object()
                    elif event.key == pygame.K_ESCAPE:
                        selection_abl.save_selected_assets(
                                self.selected_floor_data,
                                self.selected_wall_data
                            )

                        self.game_state = GameState.MENU

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_r:
                    if self.object:
                        asset_type = self.selected_item_data.get('type')

                        if not asset_type == 'wall item':
                            self.object.rotate()
                            self.object.animate(True)
                            self.sounds['object_rotate'].play()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_state == GameState.MENU:
                    if self.play_button.handle_event(event):
                        self.sounds['ui_click'].play()
                        self.restart_game()
                    elif self.quit_button.handle_event(event):
                        selection_abl.save_selected_assets(
                                self.selected_floor_data,
                                self.selected_wall_data
                            )
                        
                        self.running = False
                
                elif self.game_state == GameState.PLAYING:
                    if self.inventory_button.handle_event(event):
                        self.show_minigames = False
                        self.show_shop = False
                        self.show_buy_button = False

                        if self.show_inventory:
                            self.sounds['ui_click'].play()
                            self.show_inventory = False
                            self.show_sell_button = False
                        else:
                            self.sounds['ui_click'].play()
                            self.show_inventory = True

                            selected_tab = self.inventory_ui.selected_tab
                            
                            # Handle sell button display
                            if selected_tab == self.ITEM_TAB:
                                self.show_sell_button = self.inventory_ui.selected_item is not None
                            elif selected_tab == self.FLOOR_TAB:
                                self.show_sell_button = self.selected_floor_data['id'] != 'stone_floor'
                            else:
                                self.show_sell_button = self.selected_wall_data['id'] != 'stone_wall'
                    
                    elif self.minigame_button.handle_event(event):
                        self.show_inventory = False
                        self.show_shop = False
                        self.show_buy_button = False
                        self.show_sell_button = False

                        # Reset item selection to avoid conflicts
                        self.inventory_ui.selected_item = None
                        self.selected_item_data = None
                        self.shop_ui.selected_asset = None

                        if self.object:
                            self.objects.remove(self.object)
                            self.all_sprites.remove(self.object)
                            self.object = None
                        
                        if self.show_minigames:
                            self.sounds['ui_click'].play()
                            self.show_minigames = False
                        else:
                            self.sounds['ui_click'].play()
                            self.show_minigames = True
                    
                    elif self.shop_button.handle_event(event):
                        self.show_inventory = False
                        self.show_minigames = False
                        self.show_sell_button = False

                        self.inventory_ui.selected_item = None
                        self.selected_item_data = None
                        
                        if self.object:
                            self.objects.remove(self.object)
                            self.all_sprites.remove(self.object)
                            self.object = None

                        if self.show_shop:
                            self.sounds['ui_click'].play()
                            self.show_shop = False
                        else:
                            self.sounds['ui_click'].play()
                            self.show_shop = True
                            self.show_buy_button = self.shop_ui.selected_asset is not None
                    
                    elif self.show_inventory:
                        selected = self.inventory_ui.handle_click(pygame.mouse.get_pos())

                        # Prevent inventory from closing
                        inner_click = self.inventory_ui.rect.collidepoint(pygame.mouse.get_pos())
                        
                        # Tab selection
                        if selected:
                            self.sounds['ui_click'].play()
                            selected_tab = self.inventory_ui.selected_tab

                            # Item selection
                            if selected_tab == self.ITEM_TAB:
                                if isinstance(selected, dict):
                                    if selected != self.selected_item_data:
                                        self.iso_utils.load_sprite_sheets(selected, selected_tab)

                                        if self.object:
                                            self.objects.remove(self.object)
                                            self.all_sprites.remove(self.object)

                                        self.selected_item_data = selected
                                        self.object = None
                                    else:
                                        self.selected_item_data = None

                                        # Remove ghost object
                                        if self.object:
                                            self.objects.remove(self.object)
                                            self.all_sprites.remove(self.object)
                                            self.object = None

                                self.show_sell_button = self.inventory_ui.selected_item is not None

                            # Floor selection
                            elif selected_tab == self.FLOOR_TAB:
                                self.selected_floor_data = self.inventory_ui.selected_floor

                                self.sprites["floor"] = create_isometric_sprites(
                                    self.iso_utils, self.FLOOR_TAB, self.selected_floor_data
                                )[0]["floor"]

                                self.show_sell_button = self.selected_floor_data['id'] != 'stone_floor'

                            # Wall selection
                            else:
                                self.selected_wall_data = self.inventory_ui.selected_wall

                                self.sprites["wall"] = create_isometric_sprites(
                                    self.iso_utils, self.WALL_TAB, self.selected_wall_data
                                )[0]["wall"]
                                
                                self.show_sell_button = self.selected_wall_data['id'] != 'stone_wall'

                        # Close inventory
                        elif not inner_click and not self.sell_button.handle_event(event):
                            self.sounds['ui_click'].play()
                            self.show_inventory = False
                            self.show_sell_button = False
                        # Handle sell button click
                        elif self.show_sell_button and self.sell_button.handle_event(event):
                            selected_tab = self.inventory_ui.selected_tab

                            if selected_tab == self.ITEM_TAB:
                                self.sounds['ui_click'].play()

                                success = self.inventory_ui.attempt_item_sale()

                                if success:
                                    self.total_balance = self.inventory_ui.total_balance
                                    
                                    # Handle no amount
                                    if not self.inventory_ui.selected_item:
                                        self.selected_item_data = None
                                        self.show_sell_button = None

                                        # Remove ghost object
                                        if self.object:
                                            self.objects.remove(self.object)
                                            self.all_sprites.remove(self.object)
                                            self.object = None

                                    self.reload_inventory()
                                    self.save_stats_data(
                                            balance=self.total_balance,
                                            snake_hs=self.snake_hi_score,
                                            fruit_hs=self.fruit_hi_score,
                                            bullet_hs=self.bullet_hi_score
                                        )
                                    
                                    self.shop_ui.total_balance = self.total_balance
                            
                            elif selected_tab == self.FLOOR_TAB:
                                self.sounds['ui_click'].play()

                                success = self.inventory_ui.attempt_floor_sale()

                                if success:
                                    self.total_balance = self.inventory_ui.total_balance
                                    
                                    # Default to stone floor after sale
                                    if not self.inventory_ui.selected_floor:
                                        self.selected_floor_data = self.inventory_ui.floors[0]

                                        self.sprites['floor'] = create_isometric_sprites(
                                            self.iso_utils, self.FLOOR_TAB, self.selected_floor_data
                                        )[0]['floor']

                                        self.show_sell_button = False

                                    self.reload_inventory()
                                    self.save_stats_data(
                                            balance=self.total_balance,
                                            snake_hs=self.snake_hi_score,
                                            fruit_hs=self.fruit_hi_score,
                                            bullet_hs=self.bullet_hi_score
                                        )
                                    
                                    self.inventory_ui.selected_tab = self.FLOOR_TAB
                                    self.shop_ui.total_balance = self.total_balance
                            else:
                                self.sounds['ui_click'].play()

                                success = self.inventory_ui.attempt_wall_sale()

                                if success:
                                    self.total_balance = self.inventory_ui.total_balance

                                    # Default to stone wall after sale
                                    if not self.inventory_ui.selected_wall:
                                        self.selected_wall_data = self.inventory_ui.walls[0]

                                        self.sprites['wall'] = create_isometric_sprites(
                                            self.iso_utils, self.WALL_TAB, self.selected_wall_data
                                        )[0]['wall']

                                    self.show_sell_button = False

                                    self.reload_inventory()
                                    self.save_stats_data(
                                            balance=self.total_balance,
                                            snake_hs=self.snake_hi_score,
                                            fruit_hs=self.fruit_hi_score,
                                            bullet_hs=self.bullet_hi_score
                                        )
                                    
                                    self.inventory_ui.selected_tab = self.WALL_TAB
                                    self.shop_ui.total_balance = self.total_balance
                    
                    # Handle ghost object placement
                    elif self.selected_item_data:
                        # Verify that inventory has items
                        item_exists = False
                        for item in self.inventory_ui.items:
                            if item.get('id') == self.selected_item_data.get('id') and item.get('count', 0) > 0:
                                item_exists = True
                                break
                        
                        if not item_exists:
                            # Clear selection if we have no items left
                            self.selected_item_data = None
                            self.inventory_ui.selected_item = None
                            continue

                        # Create ghost object if it doesn't exist
                        if not self.object:
                            mx, my = pygame.mouse.get_pos()

                            item_type = self.selected_item_data.get('type')

                            if item_type == 'floor item' or item_type == 'non top floor item':
                                def get_floor_surface(px, py, cx, cy, w, h):
                                    """Check if click point is on floor."""
                                    dx = abs(px - cx)
                                    dy = abs(py - cy)
                                    return (dx / (w / 2) + dy / (h / 2)) <= 1
                                
                                # Prepare clickable floor
                                for y in range(self.grid_height):
                                    for x in range(self.grid_width):
                                        screen_x, screen_y = self.iso_utils.grid_to_screen(x, y)
                                        screen_x += self.camera_offset_x
                                        screen_y += self.camera_offset_y

                                        # Handle floor click
                                        if self.game_map[x, y, 0] == self.EMPTY_SPACE:
                                            floor_rect = self.sprites['floor'].get_rect()
                                            floor_rect.x = screen_x - self.iso_utils.half_tile_width
                                            floor_rect.y = screen_y - self.iso_utils.half_tile_height

                                            tile_width = self.iso_utils.tile_width
                                            tile_height = self.iso_utils.tile_height

                                            center_x = screen_x
                                            y_offset = 35
                                            center_y = screen_y + y_offset

                                            if get_floor_surface(mx, my, center_x, center_y, tile_width, tile_height):
                                                # Prevent duplicit sprites
                                                if self.object:
                                                    self.objects.remove(self.object)
                                                    self.all_sprites.remove(self.object)
                                                    self.object = None

                                                # Create ghost object at clicked position
                                                self.object = Object(x=x, y=y, z=0, c=0, r=0, iso_utils=self.iso_utils, asset=self.selected_item_data)
                                                self.objects.add(self.object)
                                                self.all_sprites.add(self.object)
                            elif item_type == 'wall item':
                                def point_in_polygon(px, py, polygon):
                                    """Check if point is inside a polygon by using ray casting."""
                                    inside = False
                                    n = len(polygon)
                                    
                                    for i in range(n):
                                        x1, y1 = polygon[i]
                                        x2, y2 = polygon[(i + 1) % n]
                                        
                                        if ((y1 > py) != (y2 > py)) and \
                                        (px < (x2 - x1) * (py - y1) / (y2 - y1 + 1e-9) + x1):
                                            inside = not inside
                                    
                                    return inside

                                def build_wall_quads(cx, cy, half_w, half_h, z, tile_height, tile_spacing):
                                    """
                                    Precise wall quad calculation that matches rendering exactly.
                                    """
                                    
                                    wall_render_y = cy - (z * tile_height * tile_spacing + half_h)
                                    
                                    # Top seam of the wal
                                    seam = (cx, wall_render_y)
                                    
                                    # Bottom of the wall
                                    wall_bottom_y = wall_render_y + tile_height * tile_spacing
                                    bottom_center = (cx, wall_bottom_y)

                                    # Left sides of wall tiles
                                    top_left = (seam[0] - half_w, seam[1] + half_h)
                                    bottom_left = (bottom_center[0] - half_w, bottom_center[1] + half_h)
                                    east_quad = [seam, top_left, bottom_left, bottom_center]
                                    
                                    # Right sides of wall tiles
                                    top_right = (seam[0] + half_w, seam[1] + half_h)
                                    bottom_right = (bottom_center[0] + half_w, bottom_center[1] + half_h)
                                    north_quad = [seam, top_right, bottom_right, bottom_center]

                                    return east_quad, north_quad


                                def find_adjacent_floor_position(wall_x, wall_y, wall_z, side, game_map, grid_width, grid_height, grid_depth, objects, EMPTY_SPACE):
                                    """
                                    Adjacent floor position calculation.
                                    """
                                    
                                    if side == "east":
                                        # East side
                                        adj_x, adj_y = wall_x, wall_y + 1
                                    elif side == "north":
                                        # North side
                                        adj_x, adj_y = wall_x + 1, wall_y
                                    else:
                                        return None
                                    
                                    # Clamp to grid bounds
                                    if not (0 <= adj_x < grid_width and 0 <= adj_y < grid_height):
                                        return None

                                    # Place object at the same z-level as the wall
                                    target_z = wall_z
                                    
                                    # Ensure target z is within bounds
                                    if not (0 <= target_z < grid_depth):
                                        return None
                                    
                                    # Check if the target cell is empty
                                    cell_content = game_map[adj_x, adj_y, target_z]
                                    
                                    if cell_content != EMPTY_SPACE:
                                        return None
                                    
                                    # Check for existing objects at this position
                                    for obj in objects:
                                        if obj.grid_x == adj_x and obj.grid_y == adj_y and obj.grid_z == target_z:
                                            return None
                                    
                                    return (adj_x, adj_y, target_z)

                                object_placed = False
                                wall_candidates = []

                                # Collect all walls
                                for x in range(self.grid_width):
                                    for y in range(self.grid_height):
                                        for z in range(self.grid_depth):
                                            if self.game_map[x, y, z] == self.WALL_TILE:
                                                screen_x, screen_y = self.iso_utils.grid_to_screen(x, y)
                                                screen_x += self.camera_offset_x
                                                screen_y += self.camera_offset_y

                                                tile_spacing = 1.375
                                                wall_screen_y = screen_y - self.iso_utils.half_tile_height - (z * self.iso_utils.tile_height * tile_spacing + self.iso_utils.half_tile_height)

                                                wall_candidates.append({
                                                    'x': x, 'y': y, 'z': z,
                                                    'screen_x': screen_x, 'screen_y': screen_y,
                                                    'wall_screen_y': wall_screen_y,
                                                    'sort_key': (wall_screen_y, screen_x, z)
                                                })

                                # Sort walls front to back
                                wall_candidates.sort(key=lambda w: w['sort_key'])

                                # Test each wall for clicks
                                clicked_walls = []
                                for idx, wall in enumerate(wall_candidates):
                                    cx, cy = wall['screen_x'], wall['screen_y']
                                    x, y, z = wall['x'], wall['y'], wall['z']
                                    
                                    half_w = self.iso_utils.half_tile_width
                                    half_h = self.iso_utils.half_tile_height
                                    tile_h = self.iso_utils.tile_height
                                    tile_spacing = 1.375

                                    east_quad, north_quad = build_wall_quads(cx, cy, half_w, half_h, z, tile_h, tile_spacing)

                                    # Check click detection
                                    side = None
                                    if point_in_polygon(mx, my, east_quad):
                                        side = "east"
                                    elif point_in_polygon(mx, my, north_quad):
                                        side = "north"

                                    if side:
                                        clicked_walls.append((x, y, z, side))
                                        
                                        # Only place object for the first valid wall
                                        if not object_placed:
                                            placement_pos = find_adjacent_floor_position(
                                                x, y, z, side,
                                                self.game_map, self.grid_width, self.grid_height, self.grid_depth,
                                                self.objects, self.EMPTY_SPACE
                                            )

                                            if placement_pos:
                                                obj_x, obj_y, obj_z = placement_pos
                                                
                                                # Initial facing direction
                                                if side == "east":
                                                    obj_c = 0
                                                else:
                                                    obj_c = 1

                                                # Create and place the object
                                                self.object = Object(
                                                    x=obj_x, y=obj_y, z=obj_z,
                                                    c=obj_c, r=0,
                                                    iso_utils=self.iso_utils,
                                                    asset=self.selected_item_data
                                                )

                                                self.object.update_position(self.camera_offset_x, self.camera_offset_y)
                                                self.objects.add(self.object)
                                                self.all_sprites.add(self.object)
                                                object_placed = True
                            else:
                                def get_floor_surface(px, py, cx, cy, w, h):
                                    """Check if click point is on floor."""
                                    dx = abs(px - cx)
                                    dy = abs(py - cy)
                                    return (dx / (w / 2) + dy / (h / 2)) <= 1
                                
                                # Prepare clickable floor
                                for y in range(self.grid_height):
                                    for x in range(self.grid_width):
                                        screen_x, screen_y = self.iso_utils.grid_to_screen(x, y)
                                        screen_x += self.camera_offset_x
                                        screen_y += self.camera_offset_y

                                        # Handle static object top surface click
                                        if self.game_map[x, y, 0] == self.TOP_SURFACE and self.game_map[x, y, 1] == self.EMPTY_SPACE:
                                            floor_rect = self.sprites['floor'].get_rect()
                                            floor_rect.x = screen_x - self.iso_utils.half_tile_width
                                            floor_rect.y = screen_y - self.iso_utils.half_tile_height

                                            tile_width = self.iso_utils.tile_width
                                            tile_height = self.iso_utils.tile_height

                                            center_x = screen_x
                                            center_y = screen_y

                                            if get_floor_surface(mx, my, center_x, center_y, tile_width, tile_height):
                                                # Prevent duplicit sprites
                                                if self.object:
                                                    self.objects.remove(self.object)
                                                    self.all_sprites.remove(self.object)
                                                    self.object = None

                                                # Create ghost object at clicked position
                                                self.object = Object(x=x, y=y, z=1, c=0, r=0, iso_utils=self.iso_utils, asset=self.selected_item_data)
                                                self.objects.add(self.object)
                                                self.all_sprites.add(self.object)

                                        # Handle floor click
                                        elif self.game_map[x, y, 0] == self.EMPTY_SPACE:
                                            floor_rect = self.sprites['floor'].get_rect()
                                            floor_rect.x = screen_x - self.iso_utils.half_tile_width
                                            floor_rect.y = screen_y - self.iso_utils.half_tile_height

                                            tile_width = self.iso_utils.tile_width
                                            tile_height = self.iso_utils.tile_height

                                            center_x = screen_x
                                            y_offset = 35
                                            center_y = screen_y + y_offset

                                            if get_floor_surface(mx, my, center_x, center_y, tile_width, tile_height):
                                                # Prevent duplicit sprites
                                                if self.object:
                                                    self.objects.remove(self.object)
                                                    self.all_sprites.remove(self.object)
                                                    self.object = None

                                                # Create ghost object at clicked position
                                                self.object = Object(x=x, y=y, z=0, c=0, r=0, iso_utils=self.iso_utils, asset=self.selected_item_data)
                                                self.objects.add(self.object)
                                                self.all_sprites.add(self.object)

                    elif self.show_minigames:
                        selected = self.minigame_ui.handle_click(pygame.mouse.get_pos())

                        inner_click = self.minigame_ui.rect.collidepoint(pygame.mouse.get_pos())

                        # Minigame selection
                        if selected:
                            self.sounds['ui_click'].play()
                            selected_minigame = self.minigame_ui.selected_minigame

                            # Stop previous background music
                            self.sounds['background'].stop()

                            if selected_minigame == self.SNAKE:
                                self.init_snake_game()
                            elif selected_minigame == self.CATCH_THE_FRUIT:
                                self.init_catch_the_fruit()
                            else:
                                self.init_bullet_hell()

                        if not inner_click:
                            self.sounds['ui_click'].play()
                            self.show_minigames = False
                    elif self.show_shop:
                        selected = self.shop_ui.handle_click(pygame.mouse.get_pos())

                        if selected:
                            self.sounds['ui_click'].play()

                            # Show or hide buy button
                            self.show_buy_button = self.shop_ui.selected_asset is not None
                        
                        inner_click = self.shop_ui.rect.collidepoint(pygame.mouse.get_pos())
                        left_arrow_click = self.shop_ui.left_arrow_rect.collidepoint(pygame.mouse.get_pos())
                        right_arrow_click = self.shop_ui.right_arrow_rect.collidepoint(pygame.mouse.get_pos())

                        if not inner_click and not left_arrow_click and not right_arrow_click and not self.buy_button.handle_event(event):
                            self.sounds['ui_click'].play()
                            self.show_shop = False
                            self.show_buy_button = False
                        # Handle buy button click
                        elif self.show_buy_button and self.buy_button.handle_event(event):
                            self.sounds['ui_click'].play()

                            success = self.shop_ui.attempt_purchase()

                            if success:
                                self.total_balance = self.shop_ui.total_balance
                                self.reload_inventory()
                                self.save_stats_data(
                                            balance=self.total_balance,
                                            snake_hs=self.snake_hi_score,
                                            fruit_hs=self.fruit_hi_score,
                                            bullet_hs=self.bullet_hi_score
                                        )
                    # Handle static object removal
                    else:
                        mx, my = pygame.mouse.get_pos()

                        def pickup_object():
                            def get_object_surface(px, py, cx, cy, w, h):
                                """Check if click point is on any object surface."""
                                dx = abs(px - cx)
                                dy = abs(py - cy)
                                return (dx / (w / 2) + dy / h) <= 1
                            
                            # Prepare clickable objects
                            for x in reversed(range(self.grid_width)):
                                for y in reversed(range(self.grid_height)):
                                    for z in reversed(range(self.grid_depth)):
                                        screen_x, screen_y = self.iso_utils.grid_to_screen(x, y)
                                        screen_x += self.camera_offset_x
                                        screen_y += self.camera_offset_y

                                        # Adjust vertical screen position based on z-level
                                        tile_spacing = 1.375
                                        screen_y = screen_y - (z * self.iso_utils.tile_height * tile_spacing + self.iso_utils.half_tile_height)

                                        if self.game_map[x, y, z] == self.TOP_SURFACE or self.game_map[x, y, z] == self.NON_TOP_SURFACE:
                                            object_rect = self.sprites['floor'].get_rect()
                                            object_rect.x = screen_x - self.iso_utils.half_tile_width
                                            object_rect.y = screen_y - self.iso_utils.half_tile_height

                                            tile_width = self.iso_utils.tile_width
                                            tile_height = self.iso_utils.tile_height

                                            objects = tile_abl.load_tiles()

                                            # Adjust offset based on item type
                                            for object in objects:
                                                if object.get('grid_x') == x and object.get('grid_y') == y and object.get('grid_z') == z:
                                                    obj_id = object.get('id')

                                                    for asset in shop_assets:
                                                        if asset.get('id') == obj_id:
                                                            if asset.get('type') == 'wall item' and object.get('col') == 0:
                                                                x_offset = 14
                                                                y_offset = 20
                                                            elif asset.get('type') == 'wall item' and object.get('col') == 1:
                                                                x_offset = -6
                                                                y_offset = 20
                                                            elif asset.get('type') == 'surface item':
                                                                x_offset = 2
                                                                y_offset = 55
                                                            else:
                                                                x_offset = 2
                                                                y_offset = 35

                                            center_x = screen_x + x_offset
                                            center_y = screen_y + y_offset

                                            # Handle object click
                                            if get_object_surface(mx, my, center_x, center_y, tile_width, tile_height):
                                                objects = tile_abl.load_tiles()
                                                inventory = inventory_abl.load_inventory()
                                                objects_to_remove = []  

                                                for object in objects:
                                                    if object.get('grid_x') == x and object.get('grid_y') == y and object.get('grid_z') == z:
                                                        obj_id = object.get('id')
                                                        added = False

                                                        for item in inventory['item']:
                                                            if item.get('id') == obj_id:
                                                                item['count'] = item.get('count', 1) + 1
                                                                added = True
                                                                break

                                                        if not added:
                                                            # Get full item data from shop assets
                                                            for item in shop_assets:
                                                                if item.get('id') == obj_id:
                                                                    item_copy = item.copy()
                                                                    item_copy['count'] = 1
                                                                    inventory['item'].append(item_copy)
                                                                    break

                                                        objects_to_remove.append(object)

                                                # Check for surface objects on top of floor tile
                                                for object in objects:
                                                    if object.get('grid_x') == x and object.get('grid_y') == y and object.get('grid_z') == z + 1:
                                                        for asset in shop_assets:
                                                            if asset.get('id') == object.get('id'):
                                                                item_type = asset.get('type')
                                                                break

                                                        if item_type == 'surface item':
                                                            obj_id = object.get('id')
                                                            added = False

                                                            for item in inventory['item']:
                                                                if item.get('id') == obj_id:
                                                                    item['count'] = item.get('count', 1) + 1
                                                                    added = True
                                                                    break

                                                            if not added:
                                                                # Get full item data from shop assets
                                                                for item in shop_assets:
                                                                    if item.get('id') == obj_id:
                                                                        item_copy = item.copy()
                                                                        item_copy['count'] = 1
                                                                        inventory['item'].append(item_copy)
                                                                        break

                                                            objects_to_remove.append(object)

                                                # Remove all collected objects
                                                for removable in objects_to_remove:
                                                    if removable in objects:
                                                        objects.remove(removable)

                                                tile_abl.save_tiles(objects)
                                                inventory_abl.save_inventory(inventory)
                                                
                                                self.clear_sprites()
                                                self.init_game_world()
                                                self.load_placed_objects()
                                                self.reload_inventory()
                                                return

                        pickup_object()
            elif event.type == pygame.MOUSEMOTION:
                if self.game_state == GameState.MENU:
                    self.play_button.handle_event(event)  # Handle hover effects
                    self.quit_button.handle_event(event)
                elif self.game_state == GameState.PLAYING:
                    self.inventory_button.handle_event(event)
                    self.minigame_button.handle_event(event)
                    self.shop_button.handle_event(event)
                    self.buy_button.handle_event(event)
                    self.sell_button.handle_event(event)

                    if self.show_shop:
                        self.hovered_asset = self.shop_ui.handle_hover(pygame.mouse.get_pos())
    
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
        
        keys = pygame.key.get_pressed()
        if self.object:

            item_type = self.selected_item_data.get('type')

            # Movement on the floor
            if item_type == 'floor item' or item_type == 'non top floor item' or item_type == 'surface item':
                if keys[pygame.K_LEFT]:
                    if self.object.move(-1, 0, 0, self.game_map, self.grid_width, self.grid_height, self.grid_depth):
                        moving = True
                elif keys[pygame.K_RIGHT]:
                    if self.object.move(1, 0, 0, self.game_map, self.grid_width, self.grid_height, self.grid_depth):
                        moving = True
                elif keys[pygame.K_UP]:
                    if self.object.move(0, -1, 0, self.game_map, self.grid_width, self.grid_height, self.grid_depth):
                        moving = True
                elif keys[pygame.K_DOWN]:
                    if self.object.move(0, 1, 0, self.game_map, self.grid_width, self.grid_height, self.grid_depth):
                        moving = True
        
                self.object.animate(moving)

            else:
                # Movement on the east wall
                if self.object.grid_y == 1 and self.object.grid_x > 1:
                    if keys[pygame.K_LEFT]:
                        if self.object.move(-1, 0, 0, self.game_map, self.grid_width, self.grid_height, self.grid_depth):
                            moving = True
                    elif keys[pygame.K_RIGHT]:
                        if self.object.move(1, 0, 0, self.game_map, self.grid_width, self.grid_height, self.grid_depth):
                            moving = True
                    elif keys[pygame.K_UP]:
                        if self.object.move(0, 0, 1, self.game_map, self.grid_width, self.grid_height, self.grid_depth):
                                moving = True
                    elif keys[pygame.K_DOWN]:
                        if self.object.move(0, 0, -1, self.game_map, self.grid_width, self.grid_height, self.grid_depth):
                            moving = True
                    
                        self.object.animate(moving)
                        self.object.col = 0

                # Movement on the north wall
                elif self.object.grid_x == 1 and self.object.grid_y > 1:
                    if keys[pygame.K_LEFT]:
                        if self.object.move(0, 1, 0, self.game_map, self.grid_width, self.grid_height, self.grid_depth):
                            moving = True
                    elif keys[pygame.K_RIGHT]:
                        if self.object.move(0, -1, 0, self.game_map, self.grid_width, self.grid_height, self.grid_depth):
                            moving = True
                    elif keys[pygame.K_UP]:
                        if self.object.move(0, 0, 1, self.game_map, self.grid_width, self.grid_height, self.grid_depth):
                            moving = True
                    elif keys[pygame.K_DOWN]:
                        if self.object.move(0, 0, -1, self.game_map, self.grid_width, self.grid_height, self.grid_depth):
                            moving = True
                    
                    self.object.animate(moving)
                    self.object.col = 1
                
                # Movement in the corner
                elif self.object.grid_x == 1 and self.object.grid_y == 1 and self.object.col == 0:
                    if keys[pygame.K_LEFT]:
                        self.object.col = 1
                        moving = True
                    elif keys[pygame.K_RIGHT]:
                        if self.object.move(1, 0, 0, self.game_map, self.grid_width, self.grid_height, self.grid_depth):
                            moving = True
                    elif keys[pygame.K_UP]:
                        if self.object.move(0, 0, 1, self.game_map, self.grid_width, self.grid_height, self.grid_depth):
                            moving = True
                    elif keys[pygame.K_DOWN]:
                        if self.object.move(0, 0, -1, self.game_map, self.grid_width, self.grid_height, self.grid_depth):
                            moving = True
                    
                    self.object.animate(moving)

                elif self.object.grid_x == 1 and self.object.grid_y == 1 and self.object.col == 1:
                    if keys[pygame.K_LEFT]:
                        if self.object.move(0, 1, 0, self.game_map, self.grid_width, self.grid_height, self.grid_depth):
                            moving = True
                    elif keys[pygame.K_RIGHT]:
                        self.object.col = 0
                        moving = True
                    elif keys[pygame.K_UP]:
                        if self.object.move(0, 0, 1, self.game_map, self.grid_width, self.grid_height, self.grid_depth):
                            moving = True
                    elif keys[pygame.K_DOWN]:
                        if self.object.move(0, 0, -1, self.game_map, self.grid_width, self.grid_height, self.grid_depth):
                            moving = True
                    
                    self.object.animate(moving)
                
    
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
            current_z = self.object.grid_z

            # Get the current sprite
            current_c = self.object.col
            current_r = self.object.row
        
            # Make sure the place is not occupied
            if self.game_map[current_x, current_y, current_z] == self.EMPTY_SPACE:
                # Create a static copy of the object at the current position
                static_object = Object(current_x, current_y, current_z, current_c, current_r,
                                       self.iso_utils, asset=self.selected_item_data
                                    )
                static_object.create_sprite()
                self.all_sprites.add(static_object)
                
                self.sounds['object_place'].play()

                item_type = self.selected_item_data.get('type')

                # Mark the position in the game map as occupied
                if item_type == 'floor item':
                    self.game_map[current_x, current_y, current_z] = self.TOP_SURFACE
                else:
                    self.game_map[current_x, current_y, current_z] = self.NON_TOP_SURFACE
                    
                self.save_placed_object(
                    self.object.asset['id'],
                    current_x,
                    current_y,
                    current_z,
                    current_c,
                    current_r
                )

                # Load inventory and subtract count
                inventory = inventory_abl.load_inventory()

                selected_id = self.selected_item_data.get('id') if self.selected_item_data else None

                # Subtract or remove from inventory
                for existing in inventory['item']:
                    if existing.get('id') == static_object.obj_id:
                        if existing.get('count') > 1:
                            existing['count'] -= 1
                        elif existing.get('count') == 1:
                            inventory['item'].remove(existing)
                        break

                # Update selection state
                for item in self.inventory_ui.items:
                    if item.get('id') == selected_id:
                        if item.get('count') == 1:
                            self.selected_item_data = None
                            self.inventory_ui.selected_item = None
                        else:
                            # Keep both data and visual selection state
                            self.selected_item_data = item
                            self.inventory_ui.selected_item = item
                        break
                
                # Save inventory
                inventory_abl.save_inventory(inventory)
                self.reload_inventory()

                # Remove ghost object
                if self.object:
                    self.objects.remove(self.object)
                    self.all_sprites.remove(self.object)
                    self.object = None
    
    def reload_inventory(self):
        inventory = inventory_abl.load_inventory()
        # Update selected item if it exists in the new inventory
        if self.selected_item_data:
            for item in inventory['item']:
                if item.get('id') == self.selected_item_data.get('id'):
                    self.selected_item_data = item
                    break

        self.inventory_ui = InventoryUI(
            inventory['item'],
            inventory['floor'],
            inventory['wall'],
            item_size=64, 
            tabs=["Items", "Floors", "Walls"], 
            x=385, 
            y=250,
            cols=8,
            rows=4,
            selected_item=self.selected_item_data,
            selected_floor=self.selected_floor_data,
            selected_wall=self.selected_wall_data,
            selected_tab=self.selected_tab,
            total_balance=self.total_balance
        )

        # Restore current floor/wall sprites
        if self.selected_floor_data:
            self.sprites['floor'] = create_isometric_sprites(
                self.iso_utils, self.FLOOR_TAB, self.selected_floor_data
            )[0]['floor']

        if self.selected_wall_data:
            self.sprites['wall'] = create_isometric_sprites(
                self.iso_utils, self.WALL_TAB, self.selected_wall_data
            )[0]['wall']
    
    def load_stats_data(self):
            file_path = os.path.join('storage', 'stats_data.json')

            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    balance = data.get('total_balance', 0)
                    snake_hs = data.get('snake_hi_score', 0)
                    fruit_hs = data.get('fruit_hi_score', 0)
                    bullet_hs = data.get('bullet_hi_score', 0)
                    return balance, snake_hs, fruit_hs, bullet_hs
            except FileNotFoundError:
                return 0
    
    def save_stats_data(self, balance, snake_hs, fruit_hs, bullet_hs):
        file_path = os.path.join('storage', 'stats_data.json')

        data = {
            "total_balance": balance,
            "snake_hi_score": snake_hs,
            "fruit_hi_score": fruit_hs,
            "bullet_hi_score": bullet_hs
        }

        with open(file_path, 'w') as f:
            json.dump(data, f)
    
    def save_placed_object(self, obj_id, grid_x, grid_y, grid_z, col, row):
        file_path = os.path.join('storage', 'tile_data.json')

        # Load existing placed objects
        try:
            with open(file_path, 'r') as f:
                placed_objects = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            placed_objects = []

        data = {
            "grid_x": grid_x,
            "grid_y": grid_y,
            "grid_z": grid_z,
            "col": col,
            "row": row,
            "id": obj_id
        }

        # Add the new object
        placed_objects.append(data)

        # Save back to file
        with open(file_path, 'w') as f:
            json.dump(placed_objects, f, indent=4)
    
    def load_placed_objects(self):
        file_path = os.path.join('storage', 'tile_data.json')

        try:
            with open(file_path, 'r') as f:
                placed_objects = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            placed_objects = []

        for obj in placed_objects:
            grid_x = obj["grid_x"]
            grid_y = obj["grid_y"]
            grid_z = obj["grid_z"]
            col = obj["col"]
            row = obj["row"]
            obj_id = obj["id"]

            # Find item type from shop assets
            for asset in shop_assets:
                if asset.get("id") == obj_id:
                    # Update map
                    if asset.get("type") == 'floor item':
                        self.game_map[grid_x, grid_y, grid_z] = self.TOP_SURFACE
                    else:
                        self.game_map[grid_x, grid_y, grid_z] = self.NON_TOP_SURFACE

            # Recreate the static object
            static_object = Object(grid_x, grid_y, grid_z, col, row, self.iso_utils, obj_id=obj_id,
                                        asset=self.selected_item_data
                                    )
            static_object.create_sprite()
            self.all_sprites.add(static_object)

    def apply_selected_assets(self):
        if self.selected_floor_data:
            self.sprites['floor'] = create_isometric_sprites(
                self.iso_utils, self.FLOOR_TAB, self.selected_floor_data
            )[0]['floor']

        if self.selected_wall_data:
            self.sprites['wall'] = create_isometric_sprites(
                self.iso_utils, self.WALL_TAB, self.selected_wall_data
            )[0]['wall']
    
    def draw(self):
        """Function drawing screen content according to the state of the game"""
        self.screen.fill((0, 0, 0))
        
        if self.game_state == GameState.MENU:
            self.draw_menu_screen()
        elif self.game_state == GameState.PLAYING:
            self.draw_game()
            if self.show_inventory:
                self.inventory_ui.draw(self.screen)
            elif self.show_minigames:
                self.minigame_ui.draw(self.screen)
            elif self.show_shop:
                self.shop_ui.draw(self.screen)

                # Asset hover
                if self.hovered_asset:
                    mx, my = pygame.mouse.get_pos()
                    font = pygame.font.Font('ithaca.ttf', 24)
                    
                    name = font.render(self.hovered_asset['name'], True, (255, 255, 0))  
                    name_rect = name.get_rect()
                    name_rect.topleft = (mx + 20, my - 10)

                    description = font.render(self.hovered_asset['description'], True, (255, 255, 255))  
                    description_rect = description.get_rect()
                    description_rect.topleft = (mx + 20, my - 10 + name_rect.height)

                    price = font.render(str(self.hovered_asset['price']), True, (0, 255, 88))  
                    price_rect = price.get_rect()
                    price_rect.topleft = (mx + 20, my - 10 + name_rect.height + description_rect.height)

                    currency = font.render(" GMC", True, (0, 255, 88))  
                    currency_rect = currency.get_rect()
                    currency_rect.topleft = (mx + 20 + price_rect.width, my - 10 + name_rect.height + description_rect.height)

                    # Draw background behind text
                    bg_rect = pygame.Rect(name_rect.x - 6, name_rect.y - 6, description_rect.width + 12,
                                          name_rect.height + description_rect.height + price_rect.height + 10)
                    bg_rect_center = pygame.Rect(name_rect.x - 6, name_rect.y - 6, description_rect.width + 12,
                                          name_rect.height + description_rect.height + 2)
                    pygame.draw.rect(self.screen, (255, 70, 0), bg_rect, 29, 5)
                    pygame.draw.rect(self.screen, (255, 70, 0), bg_rect_center, 15, 5)
                    pygame.draw.rect(self.screen, (255, 120, 0), bg_rect, 3, 5)

                    self.screen.blit(name, name_rect)
                    self.screen.blit(description, description_rect)
                    self.screen.blit(price, price_rect)
                    self.screen.blit(currency, currency_rect)

        pygame.display.flip()

    def change_used_sprites(self, is_menu=False):
        """Changes the sprite collection based on game state"""
        if is_menu:
            self.sprites = self.sprites_collection[0]
            self.bg_surface = self.bg_surface_collection[0]
        else:
            self.sprites.update(self.sprites_collection[0])
            self.bg_surface = self.bg_surface_collection[1]

    def draw_menu_screen(self):
        """
        Draws menu screen.
        """
        self.change_used_sprites(is_menu=True)
        
        self.screen.blit(self.bg_surface, (0, 0))
        
        logo = self.ui_graphics_collection[26]
        
        self.screen.blit(logo, (self.WIDTH // 4 - 35, self.HEIGHT // 6))
        
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
            ("Space", "Place"),
            ("Escape", "Quit game")
        ]
        
        small_font = pygame.font.Font('ithaca.ttf', 30)
        y_offset = self.HEIGHT - 120
        
        # Draw authors on the left
        for author, roles in authors:
            author_text = small_font.render(f"{author}: {roles}", True, (255, 255, 255))
            self.screen.blit(author_text, (48, y_offset))
            y_offset += 30
        
        # Reset offset for controls and draw them on the right
        y_offset = self.HEIGHT - 150
        for control, action in controls:
            control_text = small_font.render(f"{control}: {action}", True, (255, 255, 255))
            self.screen.blit(control_text, (1053, y_offset))
            y_offset += 30

        copyright = "©2025 | Thysis | All rights reserved"
        copyright_text = small_font.render(copyright, True, (255, 255, 255))
        self.screen.blit(copyright_text, (self.WIDTH // 3 + 40, 30))
    
    def draw_game(self):
        """Draws room."""
        self.change_used_sprites()
        
        self.screen.blit(self.bg_surface, (0, 0))
        
        self.inventory_button.draw(self.screen)
        self.minigame_button.draw(self.screen)
        self.shop_button.draw(self.screen)

        if self.show_buy_button == True:
            self.buy_button.draw(self.screen)
        elif self.show_sell_button == True:
            self.sell_button.draw(self.screen)

        self.screen.blit(self.balance_border, (20, 20))

        font = pygame.font.Font('ithaca.ttf', 30)

        balance_text = font.render(str(self.total_balance), True, 'white')
        balance_rect = balance_text.get_rect()
        balance_rect.bottomleft = (65, 53)
        self.screen.blit(balance_text, balance_rect)
        
        render_list = []

        # Collect all tiles and objects for proper depth sorting
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                for z in range(self.grid_depth):
                    
                    # Calculate base position for the tile
                    screen_x, screen_y = self.iso_utils.grid_to_screen(x, y)
                    screen_x += self.camera_offset_x
                    screen_y += self.camera_offset_y

                    # Floors - render for empty spaces and spaces with objects
                    if self.game_map[x, y, 0] == self.EMPTY_SPACE or self.game_map[x, y, 0] == self.TOP_SURFACE \
                    or self.game_map[x, y, 0] == self.NON_TOP_SURFACE:
                        floor_rect = self.sprites['floor'].get_rect()
                        floor_rect.x = screen_x - self.iso_utils.half_tile_width
                        y_offset = 30
                        floor_rect.y = screen_y - self.iso_utils.half_tile_height + y_offset
                        render_offset = 2
                        render_list.append((x + y - render_offset, 'floor', floor_rect))

                    # Walls - render each layer
                    if self.game_map[x, y, z] == self.WALL_TILE:
                        wall_rect = self.sprites['wall'].get_rect()
                        wall_rect.x = screen_x - self.iso_utils.half_tile_width
                        tile_spacing = 1.5
                        y_offset = 3
                        wall_rect.y = screen_y - self.iso_utils.half_tile_height - (z * self.iso_utils.tile_height
                                        * tile_spacing + self.iso_utils.half_tile_height - y_offset)
                        render_list.append((x + y + z, 'wall', wall_rect))

        all_entities = list(self.all_sprites)

        if self.object:
            all_entities.append(self.object)

        sorted_entities = self.iso_utils.get_render_order(all_entities)

        for sprite in sorted_entities:
            adjusted_rect = sprite.rect.copy()
            screen_x, screen_y = self.iso_utils.grid_to_screen(sprite.grid_x, sprite.grid_y)
            adjusted_rect.x = screen_x - self.iso_utils.half_tile_width + self.camera_offset_x

            y_offset = 10
            base_y = screen_y - self.iso_utils.half_tile_height + self.camera_offset_y + y_offset
            tile_spacing = 1.5
            z_offset = sprite.grid_z * self.iso_utils.tile_height * tile_spacing + self.iso_utils.half_tile_height
            adjusted_rect.y = base_y - z_offset

            render_depth = sprite.grid_x + sprite.grid_y + sprite.grid_z
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
            self.screen.blit(self.inventory_border, (371, 172))
            
            selected_tab = self.inventory_ui.selected_tab
            
            # Show info
            if selected_tab == self.ITEM_TAB:
                info = [
                    ("INFO:"),
                    ("Click on the floor or wall to start placing"),
                    ("Click on an icon again to stop placing"),
                    ("Use arrow keys to adjust position"),
                    ("Click on a placed item to pick it up")
                ]

                font = pygame.font.Font('ithaca.ttf', 24)
                y_offset = self.HEIGHT - 115

                for row in info:
                    info_text = font.render(f"{row}", True, (255, 255, 255))
                    self.screen.blit(info_text, (20, y_offset))
                    y_offset += 20
        elif self.show_minigames:
            self.screen.blit(self.minigames_border, (371, 172))
        elif self.show_shop:
            self.screen.blit(self.shop_border, (504, 91))
    
    def clear_sprites(self):
        """Deletes all sprite groups"""
        self.all_sprites.empty()
        self.objects.empty()

    def restart_game(self):
        """Starts a fresh game when switching from menu or minigames"""
        self.sounds['minigame'].stop()

        # Handle sound refresh after exiting a minigame
        if not self.game_state == GameState.MENU:
            self.sounds['background'].play(loops=-1).set_volume(0.8)
            self.sounds['ui_click'].set_volume(0.6)
        
        pygame.mouse.set_visible(True)
        
        self.clear_sprites()
        
        # Reset item selection state
        self.inventory_ui.selected_item = None
        self.selected_item_data = None

        if self.object:
            self.objects.remove(self.object)
            self.all_sprites.remove(self.object)
            self.object = None

        # Load existing selections
        selected_assets = selection_abl.load_selected_assets()
        selected_floor = selected_assets['floor']
        selected_wall = selected_assets['wall']
            
        # Update game state
        self.selected_floor_data = selected_floor
        self.selected_wall_data = selected_wall
        self.shop_ui.total_balance = self.total_balance
        
        # Reload game state with defaults
        self.reload_inventory()
        self.load_placed_objects()
        self.apply_selected_assets()
        self.game_state = GameState.PLAYING

    def run(self):
        """
        Main loop of the game.
        """
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.FPS)

        pygame.quit()