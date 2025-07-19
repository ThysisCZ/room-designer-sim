import pygame
from enum import Enum
from pathlib import Path
from utils.sprite_sheet import SpriteSheet


class GameState(Enum):
    MENU_SCREEN = 1
    MENU = 2
    PLAYING = 3

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
    def __init__(self, items, item_size, tabs, x=50, y=400, cols=8, rows=4):
        self.items = items
        self.tabs = tabs
        self.cols = cols
        self.rows = rows
        self.item_size = item_size
        self.x = x
        self.y = y
        self.page = 0
        self.selected_item = None
        self.selected_tab = 0
    
    def draw(self, screen):
        item_start = self.page * self.cols * self.rows
        item_end = item_start + self.cols * self.rows

        # Prepare 8x4 grid
        for row in range(8):
            for col in range(4):
                grid_x = row
                grid_y = col
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
        
        # Add objects to the inventory
        for idx, item in enumerate(self.items[item_start:item_end]):
            grid_x = idx % self.cols
            grid_y = idx // self.cols
            x = self.x + grid_x * self.item_size
            y = self.y + grid_y * self.item_size

            # Determine the absolute path to this file
            this_file = Path(__file__).resolve()
            project_root = this_file.parents[0]
            spritesheets_dir = project_root / "assets" / "spritesheets"

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

            # Draw square behind icon
            cell_rect = pygame.Rect(x, y, self.item_size, self.item_size)
            pygame.draw.rect(screen, (214, 162, 104), cell_rect)

            # White border
            pygame.draw.rect(screen, (255, 255, 255), cell_rect, 1)

            # Show icons
            screen.blit(icon, (x, y))

            # Yellow border
            if self.selected_item == item:
                pygame.draw.rect(screen, (255, 255, 0), cell_rect, 5)
        
    def next_page(self):
        if (self.page + 1) * self.cols * self.rows < len(self.items):
            self.page += 1
    
    def prev_page(self):
        if self.page > 0:
            self.page -= 1
    
    def handle_click(self, mouse_pos):
        mx, my = mouse_pos

        # Handle tab clicks
        for idx, tab in enumerate(self.tabs):
            x = self.x + idx * self.item_size
            y = self.y - self.item_size - 10
            rect = pygame.Rect(x, y, self.item_size, self.item_size)

            if rect.collidepoint(mx, my):
                self.selected_tab = idx
                return "tab"

        # Handle item selection
        for idx in range(self.cols * self.rows):
            grid_x = idx % self.cols
            grid_y = idx // self.cols
            x = self.x + grid_x * self.item_size
            y = self.y + grid_y * self.item_size

            rect = pygame.Rect(x, y, self.item_size, self.item_size)
            if rect.collidepoint(mx, my):
                index = self.page * self.cols * self.rows + idx
                if index < len(self.items):
                    self.selected_item = self.items[index]
                    return self.selected_item
        
        return None




