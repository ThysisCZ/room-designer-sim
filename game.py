import pygame, time, random

from domain.entity.object import Object
from ui_components import Button, InventoryUI, MinigameUI
from domain.state.states import GameState
from utils.isometric_utils import IsometricUtils
from game_logic import (create_game_map, create_isometric_sprites, create_sounds, create_background, create_graphics)
from storage.inventory_data import (inventory_items, inventory_floors, inventory_walls)

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

        # Set up tile types
        self.EMPTY_SPACE = 0
        self.WALL_TILE = 1
        self.STATIC_OBJECT = 2

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
        self.camera_offset_y = self.HEIGHT * 0.37 # Center room vertically
        
        self.game_state = GameState.MENU

        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
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
        
        # No object at start
        self.object = None
        
        # Inventory
        self.show_inventory = False
        tabs = ["Items", "Floors", "Walls"]
        self.inventory_ui = InventoryUI(inventory_items,
                                        inventory_floors, 
                                        inventory_walls, 
                                        item_size=64, 
                                        tabs=tabs, 
                                        x=390, 
                                        y=250
                                    )

        selected_tab = self.inventory_ui.selected_tab
        self.selected_item_data = None

        # Minigames
        self.show_minigames = False
        self.minigame_ui = MinigameUI(thumbnail_size=128, 
                                        x=390,
                                        y=250
                                    )

        # Determine asset type based on selected tab
        if selected_tab == self.FLOOR_TAB:
            self.sprites_collection = create_isometric_sprites(self.iso_utils, self.FLOOR_TAB)
        elif selected_tab == self.WALL_TAB:
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
        
        self.sounds['background'].play(loops=-1).set_volume(0.8)
    
    def init_game_world(self):
        """
        generates the game map via create_game_map
        """
        self.grid_width = 12
        self.grid_height = 12
        self.grid_volume = 6
        
        # Create game map
        self.game_map = create_game_map(self.grid_width, self.grid_height, self.grid_volume)
    
    def init_snake_game(self):
        self.game_state = GameState.SNAKE
        self.sounds = create_sounds()
        self.sounds['minigame'].play(loops=-1).set_volume(0.4)

        pygame.mouse.set_visible(False)

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
        self.score_offset = 0
        self.coins_offset = 0

        self.growth_counter = 0
        self.block_counter = 0

        def show_score():
            font = pygame.font.SysFont(None, 30)

            score_text = font.render('Score: ' + str(self.score), True, 'white')
            score_rect = score_text.get_rect()
            score_rect.midtop = (self.WIDTH//3.25 + 455 - self.score_offset, self.HEIGHT//6 - 23)
            self.screen.blit(score_text, score_rect)
        
        def show_coins():
            font = pygame.font.SysFont(None, 30)

            coin_text = font.render('Gamecoins: ' + str(self.coins), True, 'white')
            coin_rect = coin_text.get_rect()
            coin_rect.midtop = (self.WIDTH//3.25 + 70 + self.coins_offset, self.HEIGHT//6 - 23)
            self.screen.blit(coin_text, coin_rect)

        def game_over():
            # Keep border and score on the screen
            border_rect = pygame.Rect(self.WIDTH//3.25, self.HEIGHT//6, self.area_size, self.area_size)
            pygame.draw.rect(self.screen, (255, 255, 255), border_rect, 3)
            show_score()

            font = pygame.font.SysFont(None, 50)

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

            pygame.display.flip()
            time.sleep(2)
            self.restart_game()

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

            if snake_rect.colliderect(food_rect):
                self.sounds['score'].play().set_volume(1)
                self.score += 10
                self.food_eaten = True
                self.growth_counter += 7

                if self.score == 10 or self.score == 100 or self.score == 1000 or self.score == 10000:
                    self.score_offset += 6
            elif snake_rect.colliderect(coin_rect):
                self.sounds['coin'].play().set_volume(0.2)
                self.coins += 1
                self.coin_picked = True

                if self.coins == 10 or self.coins == 100 or self.coins == 1000:
                    self.coins_offset += 5
            # If snake doesn't meet food or coin
            else:
                if self.growth_counter > 0:
                    self.growth_counter -= 1 
                else:
                    self.snake_body.pop()

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
            self.screen.fill('black')

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

        pygame.mouse.set_visible(False)

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

        self.food_speed = 3

        self.food_count = 1

        self.coin_image = pygame.transform.scale(self.graphics_collection[21], (50, 50))

        self.coin_size = 50

        self.coin_pos = [0, 0]

        self.coins = []

        self.score = 0
        self.coin_count = 0
        self.score_offset = 0
        self.coins_offset = 0
        self.timer = 0

        background_rect = pygame.Rect(0, 0, self.WIDTH, self.HEIGHT)
        pygame.draw.rect(self.screen, (0, 0, 0), background_rect)

        self.score_font = pygame.font.SysFont(None, 30)
        self.info_font = pygame.font.SysFont(None, 24)

        def show_score():
            font = pygame.font.SysFont(None, 30)

            score_text = font.render('Score: ' + str(self.score), False, 'white')
            score_rect = score_text.get_rect()
            score_rect.midtop = (self.WIDTH - 7 * self.basket_size//4 - 8 + self.score_offset, self.border_offset)
            self.screen.blit(score_text, score_rect)

        def show_coins():
            font = pygame.font.SysFont(None, 30)

            coin_text = font.render('Gamecoins: ' + str(self.coin_count), False, 'white')
            coin_rect = coin_text.get_rect()
            coin_rect.midtop = (self.WIDTH - 3 * self.basket_size//2 + self.coins_offset, 30)
            self.screen.blit(coin_text, coin_rect)
        
        def show_info():
            info = [
                    ("INFO:"),
                    ("Hold left SHIFT to dash")
                ]

            font = pygame.font.SysFont(None, 24)
            y_offset = self.HEIGHT - 45

            for row in info:
                info_text = font.render(f"{row}", False, (255, 255, 255))
                self.screen.blit(info_text, (15, y_offset))
                y_offset += 20

        # Game loop
        while self.game_state == GameState.CATCH_THE_FRUIT:
            # Clear the screen each frame to prevent trails
            self.screen.fill('black')

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    # Quit
                    if event.key == pygame.K_ESCAPE:
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
                self.sounds['score'].play().set_volume(1)
                self.score += 10
            
            # Generate new fruit
            def generate_food():
                # Random position
                new_food_pos = [random.randrange(self.WIDTH//5, self.WIDTH - self.WIDTH//5 - self.food_size), 0]
                
                # Random image
                random_food_image = random.randint(1, 5)
                
                if random_food_image == 1:
                    new_food_image = pygame.transform.scale(self.graphics_collection[2], (50, 50))
                elif random_food_image == 2:
                    new_food_image = pygame.transform.scale(self.graphics_collection[5], (50, 50))
                elif random_food_image == 3:
                    new_food_image = pygame.transform.scale(self.graphics_collection[6], (50, 50))
                elif random_food_image == 4:
                    new_food_image = pygame.transform.scale(self.graphics_collection[7], (50, 50))
                else:
                    new_food_image = pygame.transform.scale(self.graphics_collection[8], (50, 50))
                
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
                    self.sounds['score'].play().set_volume(1)
                    self.score += 10
                    self.foods.remove(food)

                    if self.score == 10 or self.score == 100 or self.score == 1000 or self.score == 10000:
                        self.score_offset += 6

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

                    font = pygame.font.SysFont(None, 50)

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

                    pygame.display.flip()
                    time.sleep(2)
                    self.restart_game()
            
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
                    self.sounds['coin'].play().set_volume(0.2)
                    self.coin_count += 1
                    self.coins.remove(coin)

                    if self.coin_count == 10 or self.coin_count == 100 or self.coin_count == 1000:
                        self.coins_offset += 6

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

        pygame.mouse.set_visible(False)

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

        self.coin_image = pygame.transform.scale(self.graphics_collection[21], (50, 50))

        self.coin_size = 50

        self.coin_pos = [0, 0]

        self.coins = []

        self.score = 0

        self.sounds['score'].set_volume(1)
        self.sounds['bullets'].set_volume(0.3)
        self.sounds['coin'].set_volume(0.2)

        self.score = 0
        self.coin_count = 0
        self.score_offset = 0
        self.coins_offset = 0
        self.timer = 0

        background_rect = pygame.Rect(0, 0, self.WIDTH, self.HEIGHT)
        pygame.draw.rect(self.screen, (0, 0, 0), background_rect)

        self.score_font = pygame.font.SysFont(None, 30)
        self.info_font = pygame.font.SysFont(None, 24)

        def show_score():
            font = pygame.font.SysFont(None, 30)

            score_text = font.render('Score: ' + str(self.score), False, 'white')
            score_rect = score_text.get_rect()
            score_rect.midtop = (self.WIDTH - 7 * self.player_size//4 - 8 + self.score_offset, self.border_offset)
            self.screen.blit(score_text, score_rect)

        def show_coins():
            font = pygame.font.SysFont(None, 30)

            coin_text = font.render('Gamecoins: ' + str(self.coin_count), False, 'white')
            coin_rect = coin_text.get_rect()
            coin_rect.midtop = (self.WIDTH - 3 * self.player_size//2 + self.coins_offset, 30)
            self.screen.blit(coin_text, coin_rect)
        
        def show_info():
            info = [
                    ("INFO:"),
                    ("Hold Y/Z key to shoot"),
                    ("Hold left SHIFT to focus")
                ]

            font = pygame.font.SysFont(None, 24)
            y_offset = self.HEIGHT - 65

            for row in info:
                info_text = font.render(f"{row}", False, (255, 255, 255))
                self.screen.blit(info_text, (15, y_offset))
                y_offset += 20

        # Game loop
        while self.game_state == GameState.BULLET_HELL:
            # Clear the screen each frame to prevent trails
            self.screen.fill('black')

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    # Quit
                    if event.key == pygame.K_ESCAPE:
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
            enemy_rect = pygame.Rect(self.enemy_pos[0], self.enemy_pos[1], self.enemy_size, self.enemy_size)
            
            # Generate new player bullet
            def generate_player_bullet():
                # Random position
                new_bullet_pos = [random.randrange(self.player_pos[0], self.player_pos[0] + self.player_size),
                                  self.player_pos[1]
                                ]
                
                # Random image
                random_bullet_image = random.randint(1, 5)
                
                if random_bullet_image == 1:
                    new_bullet_image = pygame.transform.scale(self.graphics_collection[16], (self.bullet_size, self.bullet_size))
                else:
                    new_bullet_image = pygame.transform.scale(self.graphics_collection[17], (self.bullet_size, self.bullet_size))
                
                self.player_bullets.append({"pos": new_bullet_pos, "image": new_bullet_image})

            # Shoot bullets
            if keys[pygame.K_y] or keys[pygame.K_z]:
                self.sounds['bullets'].play(loops=-1)
                if self.timer % 3 == 0:
                    generate_player_bullet()
            elif not keys[pygame.K_y] or not keys[pygame.K_z]:
                self.sounds['bullets'].stop()

            # Draw player bullets
            for bullet in self.player_bullets[:]:
                bullet_pos = bullet["pos"]
                bullet_image = bullet["image"]

                # Falling
                self.screen.blit(bullet_image, (bullet_pos[0], bullet_pos[1]))
                
                bullet_pos[1] -= self.bullet_speed
            
            player_rect = pygame.Rect(self.player_pos[0], self.player_pos[1], self.player_size, self.player_size//6)
            
            # Generate new enemy
            def generate_enemy():
                # Random position
                new_enemy_pos = [random.randrange(self.WIDTH//5, self.WIDTH - self.WIDTH//5 - self.enemy_size), 0]
                
                # Random image
                random_enemy_image = random.randint(1, 5)
                
                if random_enemy_image == 1:
                    new_enemy_image = pygame.transform.scale(self.graphics_collection[11], (self.enemy_size, self.enemy_size))
                elif random_enemy_image == 2:
                    new_enemy_image = pygame.transform.scale(self.graphics_collection[12], (self.enemy_size, self.enemy_size))
                elif random_enemy_image == 3:
                    new_enemy_image = pygame.transform.scale(self.graphics_collection[13], (self.enemy_size, self.enemy_size))
                elif random_enemy_image == 4:
                    new_enemy_image = pygame.transform.scale(self.graphics_collection[14], (self.enemy_size, self.enemy_size))
                else:
                    new_enemy_image = pygame.transform.scale(self.graphics_collection[15], (self.enemy_size, self.enemy_size))
                
                self.enemies.append({"pos": new_enemy_pos, 
                                   "image": new_enemy_image, 
                                   "last_shot": self.timer})
                self.enemy_count += 1
            
            # Spawn enemy bullets periodically
            for enemy in self.enemies:
                if self.timer - enemy["last_shot"] >= 30:
                    enemy_x, enemy_y = enemy["pos"]
                    bullet_x = random.randint(enemy_x, enemy_x + self.enemy_size)
                    bullet_y = enemy_y + self.enemy_size

                    # Create bullet image
                    random_bullet_image = random.randint(1, 2)

                    if random_bullet_image == 1:
                        bullet_image = pygame.transform.scale(self.graphics_collection[18], (self.bullet_size, self.bullet_size))
                    else:
                        bullet_image = pygame.transform.scale(self.graphics_collection[19], (self.bullet_size, self.bullet_size))

                    # Append bullet
                    self.enemy_bullets.append({
                        "pos": [bullet_x, bullet_y],
                        "image": bullet_image
                    })

                    enemy["last_shot"] = self.timer  # Reset shot timer

            #Change enemy spawn frequency
            if self.enemy_count <= 15:
                if self.timer % 30 == 0:
                    generate_enemy()
            elif self.enemy_count > 15 and self.enemy_count <= 30:
                if self.timer % 15 == 0:
                    generate_enemy()
            elif self.enemy_count > 30:
                if self.timer % 7 == 0:
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
                # Random position
                new_coin_pos = [random.randrange(self.WIDTH//5, self.WIDTH - self.WIDTH//5 - self.coin_size), 0]
                
                self.coins.append({"pos": new_coin_pos})

            # Coin spawn frequency
            if self.timer % 480 == 0:
                generate_coin()

            # Draw the coins
            for coin in self.coins[:]:
                coin_pos = coin["pos"]

                coin_rect = pygame.Rect(coin_pos[0], coin_pos[1], self.coin_size, self.coin_size)

                if player_rect.colliderect(coin_rect):
                    self.sounds['bullets'].stop()
                    self.sounds['coin'].play()
                    self.coin_count += 1
                    self.coins.remove(coin)

                    if self.coin_count == 10 or self.coin_count == 100 or self.coin_count == 1000:
                        self.coins_offset += 6

                if coin_pos[1] > self.HEIGHT:
                    self.coins.remove(coin)

                # Falling
                self.screen.blit(self.coin_image, (coin_pos[0], coin_pos[1]))
                
                coin_pos[1] += self.enemy_speed

            def game_over():
                border_rect = pygame.Rect(self.WIDTH//5, 0, self.WIDTH - 2 * (self.WIDTH//5), self.HEIGHT)
                pygame.draw.rect(self.screen, (255, 255, 255), border_rect, 3)

                show_score()
                show_coins()
                show_info()

                font = pygame.font.SysFont(None, 50)

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

                pygame.display.flip()
                time.sleep(2)
                self.restart_game()

            player_bullets_to_remove = []
            enemies_to_remove = []

            # Handle enemy-bullet collisions
            for bullet in self.player_bullets:
                bullet_pos = bullet["pos"]
                bullet_rect = pygame.Rect(bullet_pos[0], bullet_pos[1], self.bullet_size, self.bullet_size)

                for enemy in self.enemies:
                    enemy_pos = enemy["pos"]
                    enemy_rect = pygame.Rect(enemy_pos[0], enemy_pos[1], self.enemy_size, self.enemy_size)

                    if bullet_rect.colliderect(enemy_rect):
                        if enemy_pos[1] > 3 * self.player_size:
                            self.sounds['bullets'].stop()
                            self.sounds['score'].play()
                            self.score += 10
                            player_bullets_to_remove.append(bullet)
                            enemies_to_remove.append(enemy)
                            
                            if self.score == 10 or self.score == 100 or self.score == 1000 or self.score == 10000:
                                self.score_offset += 6
                            break  # One bullet hits one enemy only
                
                # Clean up unused player bullets
                if bullet["pos"][1] < 0:
                    self.player_bullets.remove(bullet)
                
            # Clean up player bullets and enemies
            for bullet in player_bullets_to_remove:
                if bullet in self.player_bullets:
                    self.player_bullets.remove(bullet)

            for enemy in enemies_to_remove:
                if enemy in self.enemies:
                    self.enemies.remove(enemy)

            # Draw enemy bullets
            for bullet in self.enemy_bullets[:]:
                bullet_pos = bullet["pos"]
                bullet_image = bullet["image"]

                self.screen.blit(bullet_image, (bullet_pos[0], bullet_pos[1]))
                bullet_pos[1] += self.bullet_speed

                # Clean up enemy bullets
                if bullet_pos[1] > self.HEIGHT:
                    self.enemy_bullets.remove(bullet)

            # Handle player-bullet collisions
            for bullet in self.enemy_bullets:
                bullet_pos = bullet["pos"]
                bullet_rect = pygame.Rect(bullet_pos[0], bullet_pos[1], self.bullet_size, self.bullet_size)

                if hitbox_rect.colliderect(bullet_rect):
                    self.sounds['bullets'].stop()
                    game_over()

            # Draw enemies and handle collisions
            for enemy in self.enemies[:]:
                enemy_pos = enemy["pos"]
                enemy_image = enemy["image"]

                enemy_rect = pygame.Rect(enemy_pos[0], enemy_pos[1], self.enemy_size, self.enemy_size)

                if hitbox_rect.colliderect(enemy_rect):
                    self.sounds['bullets'].stop()
                    game_over()

                # Falling
                self.screen.blit(enemy_image, (enemy_pos[0], enemy_pos[1]))
                enemy_pos[1] += self.enemy_speed
                
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
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if self.game_state == GameState.PLAYING:
                    if event.key == pygame.K_RETURN:
                        self.place_object()
                    elif event.key == pygame.K_r:
                        if self.object:
                            self.object.rotate()
                            self.object.animate(True)  # Trigger animation for one frame
                            self.sounds['object_rotate'].play().set_volume(0.6)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_state == GameState.MENU:
                    if self.play_button.handle_event(event):
                        self.sounds['ui_click'].play().set_volume(1.0)
                        self.restart_game()
                    elif self.quit_button.handle_event(event):
                        self.running = False
                elif self.game_state == GameState.PLAYING:
                    if self.inventory_button.handle_event(event):
                        self.show_minigames = False
                        if self.show_inventory == True:
                            self.sounds['ui_click'].play().set_volume(1.0)
                            self.show_inventory = False
                        else:
                            self.sounds['ui_click'].play().set_volume(1.0)
                            self.show_inventory = True
                    elif self.minigame_button.handle_event(event):
                        self.show_inventory = False
                        if self.show_minigames == True:
                            self.sounds['ui_click'].play().set_volume(1.0)
                            self.show_minigames = False
                        else:
                            self.sounds['ui_click'].play().set_volume(1.0)
                            self.show_minigames = True
                    elif self.show_inventory:
                        selected = self.inventory_ui.handle_click(pygame.mouse.get_pos())

                        # Prevent inventory from closing
                        inner_click = self.inventory_ui.rect.collidepoint(pygame.mouse.get_pos())
                        
                        # Tab selection
                        if selected:
                            self.sounds['ui_click'].play().set_volume(1.0)
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

                            # Floor selection
                            elif selected_tab == self.FLOOR_TAB:
                                self.sprites["floor"] = create_isometric_sprites(
                                    self.iso_utils, self.FLOOR_TAB, self.inventory_ui.selected_floor
                                )[0]["floor"]

                            # Wall selection
                            else:
                                self.sprites["wall"] = create_isometric_sprites(
                                    self.iso_utils, self.WALL_TAB, self.inventory_ui.selected_wall
                                )[0]["wall"]

                        # Close inventory
                        elif not inner_click:
                            self.sounds['ui_click'].play().set_volume(1.0)
                            self.show_inventory = False
                    
                    # Handle ghost object placement
                    elif self.selected_item_data and self.object is None and not self.show_minigames:
                        mx, my = pygame.mouse.get_pos()

                        def get_floor_surface(px, py, cx, cy, w, h):
                            dx = abs(px - cx)
                            dy = abs(py - cy)
                            return (dx / (w / 2) + dy / (h / 2)) <= 1
                        
                        # Prepare clickable floor
                        for y in range(self.grid_height):
                            for x in range(self.grid_width):
                                screen_x, screen_y = self.iso_utils.grid_to_screen(x, y)
                                screen_x += self.camera_offset_x
                                screen_y += self.camera_offset_y

                                if 'floor' in self.sprites and self.game_map[y, x, 0] == self.EMPTY_SPACE:
                                    floor_rect = self.sprites['floor'].get_rect()
                                    floor_rect.x = screen_x - self.iso_utils.half_tile_width
                                    floor_rect.y = screen_y - self.iso_utils.half_tile_height + 15

                                    tile_width = self.iso_utils.tile_width
                                    tile_height = self.iso_utils.tile_height

                                    center_x = screen_x
                                    center_y = screen_y + 20

                                    # Handle floor click
                                    if get_floor_surface(mx, my, center_x, center_y, tile_width, tile_height):
                                        # Remove duplicate sprites
                                        if self.object:
                                            self.objects.remove(self.object)
                                            self.all_sprites.remove(self.object)

                                        # Create ghost object again
                                        self.object = Object(x=x, y=y, c=0, r=0, iso_utils=self.iso_utils)
                                        self.objects.add(self.object)
                                        self.all_sprites.add(self.object) 
                    elif self.show_minigames:
                        selected = self.minigame_ui.handle_click(pygame.mouse.get_pos())

                        # Prevent minigames selection from closing
                        inner_click = self.minigame_ui.rect.collidepoint(pygame.mouse.get_pos())

                        # Minigame selection
                        if selected:
                            self.sounds['ui_click'].play().set_volume(1.0)
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
                            self.sounds['ui_click'].play().set_volume(1.0)
                            self.show_minigames = False
            elif event.type == pygame.MOUSEMOTION:
                if self.game_state == GameState.MENU:
                    self.play_button.handle_event(event)  # Handle hover effects
                    self.quit_button.handle_event(event)
                elif self.game_state == GameState.PLAYING:
                    self.inventory_button.handle_event(event)
                    self.minigame_button.handle_event(event)
    
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
            if keys[pygame.K_LEFT]:
                if self.object.move(-1, 0, self.game_map, self.grid_width, self.grid_height):
                    moving = True
            elif keys[pygame.K_RIGHT]:
                if self.object.move(1, 0, self.game_map, self.grid_width, self.grid_height):
                    moving = True
            elif keys[pygame.K_UP]:
                if self.object.move(0, -1, self.game_map, self.grid_width, self.grid_height):
                    moving = True
            elif keys[pygame.K_DOWN]:
                if self.object.move(0, 1, self.game_map, self.grid_width, self.grid_height):
                    moving = True
        
            # Call animate on the object if it's moving
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

            # Get the current sprite
            current_c = self.object.col
            current_r = self.object.row
        
            # Make sure the place is not occupied
            if self.game_map[current_y, current_x, 0] == self.EMPTY_SPACE:
                # Create a static copy of the object at the current position
                static_object = Object(current_x, current_y, current_c, current_r, self.iso_utils)
                static_object.create_sprite()
                self.all_sprites.add(static_object)
                
                self.sounds['object_place'].play().set_volume(1.0)

                # Mark the position in the game map as occupied
                self.game_map[current_y, current_x, 0] = self.STATIC_OBJECT
                self.object.set_object_placed_position(current_x, current_y)
    
    def draw(self):
        """Function drawing screen content according to the state of the game"""
        self.screen.fill((0, 0, 0))
        
        if self.game_state == GameState.MENU:
            self.draw_menu_screen()
        elif self.game_state == GameState.PLAYING:
            self.draw_game()
            if self.show_inventory:
                self.inventory_ui.draw(self.screen)
            if self.show_minigames:
                self.minigame_ui.draw(self.screen)

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
        
        # Reset offset for controls and draw them on the right
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
        self.minigame_button.draw(self.screen)
        
        render_list = []
        
        # Collect all tiles and objects for proper depth sorting
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                # Calculate base position for the tile
                screen_x, screen_y = self.iso_utils.grid_to_screen(x, y)
                screen_x += self.camera_offset_x
                screen_y += self.camera_offset_y
                
                # Floor tile - render for empty spaces and spaces with objects
                if 'floor' in self.sprites and (
                    self.game_map[y, x, 0] == self.EMPTY_SPACE or self.game_map[y, x, 0] == self.STATIC_OBJECT):
                    floor_rect = self.sprites['floor'].get_rect()
                    floor_rect.x = screen_x - self.iso_utils.half_tile_width
                    floor_rect.y = screen_y - self.iso_utils.half_tile_height + 15
                    render_list.append((y + x, 'floor', floor_rect))
                
                # Walls - render each layer
                if 'wall' in self.sprites and self.game_map[y, x, 0] == self.WALL_TILE:
                    # Render each vertical layer of the wall
                    for z in range(self.grid_volume):
                        if self.game_map[y, x, z] == self.WALL_TILE:
                            wall_rect = self.sprites['wall'].get_rect()
                            wall_rect.x = screen_x - self.iso_utils.half_tile_width
                            # Full tile height offset for each level to prevent merging
                            wall_rect.y = screen_y - self.iso_utils.half_tile_height - (z * self.iso_utils.tile_height * 1.3 + 13.5)
                            render_list.append((y + x + z, 'wall', wall_rect))
        
        all_entities = list(self.all_sprites)

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
            self.screen.blit(self.inventory_border, (376, 172))
        elif self.show_minigames:
            self.screen.blit(self.minigames_border, (376, 172))
    
    def clear_sprites(self):
        """Deletes all sprite groups"""
        self.all_sprites.empty()
        self.objects.empty()

    def restart_game(self):
        """Restarts game"""
        self.sounds['minigame'].stop()

        # Only refresh main theme song if not switching from menu
        if not self.game_state == GameState.MENU:
            self.sounds['background'].play(loops=-1).set_volume(0.8)

        pygame.mouse.set_visible(True)
        
        self.clear_sprites()
        self.init_game_world()
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