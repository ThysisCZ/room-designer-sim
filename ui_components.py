import pygame
from pathlib import Path

from utils.sprite_sheet import SpriteSheet
from game_logic import create_graphics

class Button:
    def __init__(self, x, y, width, height, text, font, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.base_color = color
        self.text_color = text_color
        self.hover_color = (255, 255, 0)
        self.is_hovered = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            # Update hover state
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False
        
    def draw(self, screen):
        # Create centered button rectangle
        button_rect = pygame.Rect(
            self.rect.centerx - self.rect.width // 2,
            self.rect.centery - self.rect.height // 2,
            self.rect.width,
            self.rect.height
        )
        
        # Draw border with hover effect
        border_color = self.hover_color if self.is_hovered else self.base_color
        pygame.draw.rect(screen, border_color, button_rect, 2, border_radius=8)
        
        # Render text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)

class InventoryUI:
    def __init__(self, items, floors, walls, item_size, tabs, x=50, y=400, cols=8, rows=4):
        self.items = items
        self.floors = floors
        self.walls = walls
        self.tabs = tabs
        self.cols = cols
        self.rows = rows
        self.item_size = item_size
        self.x = x
        self.y = y
        self.page = 0
        self.selected_item = None
        self.selected_floor = None
        self.selected_wall = None
        self.selected_tab = 0
        self.rect = pygame.Rect(self.x, self.y, self.cols * self.item_size, self.rows * self.item_size)

        self.ITEM_TAB = 0
        self.FLOOR_TAB = 1
        self.WALL_TAB = 2
    
    def draw(self, screen):
        start = self.page * self.cols * self.rows
        end = start + self.cols * self.rows

        # Prepare 8x4 grid
        for col in range(8):
            for row in range(4):
                grid_x = col
                grid_y = row
                x = self.x + grid_x * self.item_size
                y = self.y + grid_y * self.item_size

                # Draw cells
                cell_rect = pygame.Rect(x, y, self.item_size, self.item_size)
                pygame.draw.rect(screen, (214, 162, 104), cell_rect)

                # White border
                pygame.draw.rect(screen, (255, 255, 255), cell_rect, 1)
        
        # Prepare tabs
        for idx, tab in enumerate(self.tabs):
            x = self.x + idx * self.item_size
            y = self.y - self.item_size
            
            # Adjust text position
            if idx == 0 or idx == 2:
                x_offset = 2
            else:
                x_offset = 0

            tab_rect = pygame.Rect(x, y, self.item_size, self.item_size)
            pygame.draw.rect(screen, (175, 86, 31), tab_rect)
            pygame.draw.rect(screen, (124, 67, 0), tab_rect, 1)

            if self.selected_tab == idx:
                pygame.draw.rect(screen, (124, 67, 0), tab_rect)
            
            # Draw tab name text
            font = pygame.font.SysFont(None, 20)
            label = font.render(tab, True, (255, 255, 255))
            screen.blit(label, (x + 12 + x_offset, y + 25))

            # Draw item icons
            if self.selected_tab == self.ITEM_TAB:   
                for idx, item in enumerate(self.items[start:end]):
                    grid_x = idx % self.cols
                    grid_y = idx // self.cols
                    x = self.x + grid_x * self.item_size
                    y = self.y + grid_y * self.item_size

                    # Determine the absolute path to this file
                    this_file = Path(__file__).resolve()
                    project_root = this_file.parents[0]
                    spritesheets_dir = project_root / "assets" / "spritesheets" / "items"

                    # Load only the first tile of the spritesheet as an icon
                    icon_path = spritesheets_dir / item["spritesheet"]
                    icon_sheet = SpriteSheet(str(icon_path))

                    # Calculate tile size (10x10 grid)
                    total_width = icon_sheet.sheet.get_width()
                    total_height = icon_sheet.sheet.get_height()
                    tile_w = total_width // 10
                    tile_h = total_height // 10

                    # Extract the first tile
                    icon = icon_sheet.get_sprite(0, 0, tile_w, tile_h, scale=self.item_size / tile_w)

                    #Draw square behind icon
                    cell_rect = pygame.Rect(x, y, self.item_size, self.item_size)
                    pygame.draw.rect(screen, (214, 162, 104), cell_rect)

                    # White border
                    pygame.draw.rect(screen, (255, 255, 255), cell_rect, 1)

                    # Show icons
                    screen.blit(icon, (x, y))

                    # Yellow border
                    if self.selected_item == item:
                        pygame.draw.rect(screen, (255, 255, 0), cell_rect, 5)

                # Show info
                info = [
                    ("INFO:"),
                    ("Click on the floor to start placing"),
                    ("Use arrow keys to adjust position"),
                    ("Click on the same icon again to deselect")
                ]

                big_font = pygame.font.SysFont(None, 24)
                y_offset = y + self.item_size * 5.7

                for row in info:
                    info_text = big_font.render(f"{row}", True, (255, 255, 255))
                    screen.blit(info_text, (x - self.item_size * 6.55, y_offset))
                    y_offset += 20
                    
            # Draw floor icons
            elif self.selected_tab == self.FLOOR_TAB:
                for idx, floor in enumerate(self.floors[start:end]):
                    grid_x = idx % self.cols
                    grid_y = idx // self.cols
                    x = self.x + grid_x * self.item_size
                    y = self.y + grid_y * self.item_size

                    # Determine the absolute path to this file
                    this_file = Path(__file__).resolve()
                    project_root = this_file.parents[0]
                    spritesheets_dir = project_root / "assets" / "spritesheets" / "floors"

                    # Load only the first tile of the spritesheet as an icon
                    icon_path = spritesheets_dir / floor["spritesheet"]
                    icon_sheet = SpriteSheet(str(icon_path))

                    # Calculate tile size (10x10 grid)
                    total_width = icon_sheet.sheet.get_width()
                    total_height = icon_sheet.sheet.get_height()
                    tile_w = total_width // 10
                    tile_h = total_height // 10

                    # Extract the first tile
                    icon = icon_sheet.get_sprite(0, 0, tile_w, tile_h, scale=self.item_size / tile_w)

                    #Draw square behind icon
                    cell_rect = pygame.Rect(x, y, self.item_size, self.item_size)
                    pygame.draw.rect(screen, (214, 162, 104), cell_rect)

                    # White border
                    pygame.draw.rect(screen, (255, 255, 255), cell_rect, 1)

                    # Show icons
                    screen.blit(icon, (x, y))

                    # Handle initial selection
                    if idx == 0 and self.selected_floor is None:
                        pygame.draw.rect(screen, (255, 255, 0), cell_rect, 5)

                    # Yellow border
                    if self.selected_floor == floor:
                        pygame.draw.rect(screen, (255, 255, 0), cell_rect, 5)
            # Draw wall icons
            else:
                for idx, wall in enumerate(self.walls[start:end]):
                    grid_x = idx % self.cols
                    grid_y = idx // self.cols
                    x = self.x + grid_x * self.item_size
                    y = self.y + grid_y * self.item_size

                    # Determine the absolute path to this file
                    this_file = Path(__file__).resolve()
                    project_root = this_file.parents[0]
                    spritesheets_dir = project_root / "assets" / "spritesheets" / "walls"

                    # Load only the first tile of the spritesheet as an icon
                    icon_path = spritesheets_dir / wall["spritesheet"]
                    icon_sheet = SpriteSheet(str(icon_path))

                    # Calculate tile size (10x10 grid)
                    total_width = icon_sheet.sheet.get_width()
                    total_height = icon_sheet.sheet.get_height()
                    tile_w = total_width // 10
                    tile_h = total_height // 10

                    # Extract the first tile
                    icon = icon_sheet.get_sprite(0, 0, tile_w, tile_h, scale=self.item_size / tile_w)

                    #Draw square behind icon
                    cell_rect = pygame.Rect(x, y, self.item_size, self.item_size)
                    pygame.draw.rect(screen, (214, 162, 104), cell_rect)

                    # White border
                    pygame.draw.rect(screen, (255, 255, 255), cell_rect, 1)

                    # Show icons
                    screen.blit(icon, (x, y))

                    # Handle initial selection
                    if idx == 0 and self.selected_wall is None:
                        pygame.draw.rect(screen, (255, 255, 0), cell_rect, 5)

                    # Yellow border
                    if self.selected_wall == wall:
                        pygame.draw.rect(screen, (255, 255, 0), cell_rect, 5)

    def next_page(self):
        if (self.page + 1) * self.cols * self.rows < len(self.items):
            self.page += 1
    
    def prev_page(self):
        if self.page > 0:
            self.page -= 1
    
    def handle_click(self, mouse_pos):
        mx, my = mouse_pos

        # Tab selection
        for idx, tab in enumerate(self.tabs):
            x = self.x + idx * self.item_size
            y = self.y - self.item_size
            rect = pygame.Rect(x, y, self.item_size, self.item_size)

            if rect.collidepoint(mx, my):
                self.selected_tab = idx
                return 'tab'

        # Cell selection in grid
        def handle_grid_selection(grid_list, set_selected_callback):
            for idx in range(self.cols * self.rows):
                grid_x = idx % self.cols
                grid_y = idx // self.cols
                x = self.x + grid_x * self.item_size
                y = self.y + grid_y * self.item_size

                rect = pygame.Rect(x, y, self.item_size, self.item_size)
                
                if rect.collidepoint(mx, my):
                    index = self.page * self.cols * self.rows + idx

                    if index < len(grid_list):
                        set_selected_callback(index)
                        return grid_list[index]
            return None
        
        # Items
        if self.selected_tab == self.ITEM_TAB:
            return handle_grid_selection(
                self.items,
                lambda i: setattr(self, "selected_item", self.items[i] if self.selected_item != self.items[i] else None)
            )
        # Floors
        elif self.selected_tab == self.FLOOR_TAB:
            return handle_grid_selection(self.floors, lambda i: setattr(self, "selected_floor", self.floors[i]))
        # Walls
        else:
            return handle_grid_selection(self.walls, lambda i: setattr(self, "selected_wall", self.walls[i]))

class MinigameUI:
    def __init__(self, thumbnail_size, x=50, y=400, cols=4, rows=2):
        self.thumbnail_size = thumbnail_size
        self.x = x
        self.y = y
        self.cols = cols
        self.rows = rows
        self.rect = pygame.Rect(self.x, self.y, self.cols * self.thumbnail_size, self.rows * self.thumbnail_size)
        self.minigames = ["Snake"]
        self.selected_minigame = None
        self.SNAKE = 0
        self.graphics_collection = create_graphics()
        self.snake_thumbnail = self.graphics_collection[3]
    
    def draw(self, screen):
        # Prepare 4x2 grid
        for col in range(4):
            for row in range(2):
                grid_x = col
                grid_y = row
                x = self.x + grid_x * self.thumbnail_size
                y = self.y + grid_y * self.thumbnail_size

                # Draw cells
                cell_rect = pygame.Rect(x, y, self.thumbnail_size, self.thumbnail_size)
                pygame.draw.rect(screen, (214, 162, 104), cell_rect)

                # White border
                pygame.draw.rect(screen, (255, 255, 255), cell_rect, 1)
        
        # Prepare minigame thumbnails
        for idx, minigame in enumerate(self.minigames):
            grid_x = idx % self.cols
            grid_y = idx // self.cols
            x = self.x + grid_x * self.thumbnail_size
            y = self.y + grid_y * self.thumbnail_size

            minigame_rect = pygame.Rect(x, y, self.thumbnail_size, self.thumbnail_size)
            pygame.draw.rect(screen, (0, 0, 0), minigame_rect)
            pygame.draw.rect(screen, (255, 255, 255), minigame_rect, 1)

            # Snake thumbnail
            screen.blit(self.snake_thumbnail, (x + 1, y + 2))

            # Draw minigame name text
            font = pygame.font.SysFont(None, 20)
            label = font.render(minigame, True, (255, 255, 255))
            screen.blit(label, (x + 44, y + 105))
    
    def handle_click(self, mouse_pos):
        mx, my = mouse_pos

        # Minigame selection
        for idx, minigame in enumerate(self.minigames):
            grid_x = idx % self.cols
            grid_y = idx // self.cols
            x = self.x + grid_x * self.thumbnail_size
            y = self.y + grid_y * self.thumbnail_size

            rect = pygame.Rect(x, y, self.thumbnail_size, self.thumbnail_size)

            if rect.collidepoint(mx, my):
                self.selected_tab = idx
                return 'minigame'




