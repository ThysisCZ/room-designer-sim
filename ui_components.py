import pygame
from pathlib import Path

from utils.sprite_sheet import SpriteSheet
from game_logic import create_graphics
import storage.inventory_abl as inventory_abl

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
    def __init__(self, items, floors, walls, item_size, tabs, x, y, cols, rows, total_balance,
                 selected_item=None, selected_floor=None, selected_wall=None, selected_tab=0):
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
        self.selected_item = selected_item
        self.selected_floor = selected_floor
        self.selected_wall = selected_wall
        self.selected_tab = selected_tab
        self.rect = pygame.Rect(self.x, self.y, self.cols * self.item_size, self.rows * self.item_size)
        self.total_balance = total_balance

        self.ITEM_TAB = 0
        self.FLOOR_TAB = 1
        self.WALL_TAB = 2
    
    def draw(self, screen):
        start = self.page * self.cols * self.rows
        end = start + self.cols * self.rows

        # Prepare 8x4 grid
        for col in range(self.cols):
            for row in range(self.rows):
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

                    # Show count
                    font = pygame.font.SysFont(None, 36)
                    count_str = str(item['count'])
                    label = font.render(count_str, True, (255, 255, 255))
                    label_rect = label.get_rect(bottomright=(x + self.item_size - 3, y + self.item_size))
                    
                    if item['count'] != 1:
                        screen.blit(label, label_rect)
                    
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
                    lambda i: setattr(self, "selected_item",
                    self.items[i] if self.selected_item != self.items[i] else None
                )
            )
        # Floors
        elif self.selected_tab == self.FLOOR_TAB:
            return handle_grid_selection(self.floors, lambda i: setattr(self, "selected_floor", self.floors[i]))
        # Walls
        else:
            return handle_grid_selection(self.walls, lambda i: setattr(self, "selected_wall", self.walls[i]))
        
    def attempt_item_sale(self):
        item = self.selected_item

        if item:
            price = item.get('price', 0)

        inventory = inventory_abl.load_inventory()
            
        for existing in inventory['item']:
            if existing.get('id') == item.get('id'):
                if existing['count'] > 1:
                    existing['count'] = existing.get('count', 1) - 1
                    self.total_balance += price
                    # Keep selection when more items remain
                    item['count'] = existing['count']
                    break
                elif existing['count'] == 1:
                    inventory['item'].remove(existing)
                    self.total_balance += price
                    # Only clear selection when no items remain
                    self.selected_item = None

        inventory_abl.save_inventory(inventory)
        return True
    
    def attempt_floor_sale(self):
        floor = self.selected_floor

        if floor:
            price = floor.get('price', 0)

        inventory = inventory_abl.load_inventory()
            
        for existing in inventory['floor']:
            if floor:
                if existing.get('id') == floor.get('id'):
                    inventory['floor'].remove(existing)
                    self.total_balance += price
                    self.selected_floor = None

        inventory_abl.save_inventory(inventory)
        return True
    
    def attempt_wall_sale(self):
        wall = self.selected_wall

        if wall:
            price = wall.get('price', 0)

        inventory = inventory_abl.load_inventory()
            
        for existing in inventory['wall']:
            if wall:
                if existing.get('id') == wall.get('id'):
                    inventory['wall'].remove(existing)
                    self.total_balance += price
                    self.selected_wall = None

        inventory_abl.save_inventory(inventory)
        return True

class MinigameUI:
    def __init__(self, thumbnail_size, x, y, cols, rows):
        self.thumbnail_size = thumbnail_size
        self.x = x
        self.y = y
        self.cols = cols
        self.rows = rows
        self.rect = pygame.Rect(self.x, self.y, self.cols * self.thumbnail_size, self.rows * self.thumbnail_size)
        self.minigames = ["Snake", "Catch the Fruit", "Bullet Hell"]
        self.selected_minigame = None
        self.graphics_collection = create_graphics()
        self.snake_thumbnail = self.graphics_collection[3]
        self.fruit_thumbnail = self.graphics_collection[9]
        self.bullet_thumbnail = self.graphics_collection[20]
    
    def draw(self, screen):
        # Prepare 4x2 grid
        for col in range(self.cols):
            for row in range(self.rows):
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

            if minigame == 'Snake':
                # Draw thumbnail
                screen.blit(self.snake_thumbnail, (x + 1, y + 2))

                # Draw minigame name text
                font = pygame.font.SysFont(None, 20)
                label = font.render(minigame, True, (255, 255, 255))
                screen.blit(label, (x + 44, y + 105))
            elif minigame == 'Catch the Fruit':
                screen.blit(self.fruit_thumbnail, (x + 1, y + 2))

                font = pygame.font.SysFont(None, 20)
                label = font.render(minigame, True, (255, 255, 255))
                screen.blit(label, (x + 15, y + 105))
            else:
                screen.blit(self.bullet_thumbnail, (x + 1, y + 2))

                font = pygame.font.SysFont(None, 20)
                label = font.render(minigame, True, (255, 255, 255))
                screen.blit(label, (x + 30, y + 105))
    
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
                self.selected_minigame = idx
                return 'minigame'

class ShopUI:
    def __init__(self, assets, thumbnail_size, x, y, cols, rows, total_balance):
        self.assets = assets
        self.thumbnail_size = thumbnail_size
        self.x = x
        self.y = y
        self.cols = cols
        self.rows = rows
        self.selected_asset = None
        self.hovered_asset = None
        self.rect = pygame.Rect(self.x, self.y, self.cols * self.thumbnail_size, self.rows * self.thumbnail_size)
        self.total_balance = total_balance
    
    def draw(self, screen):
        start = 0
        end = start + self.cols * self.rows

        # Prepare 2x4 grid
        for col in range(self.cols):
            for row in range(self.rows):
                grid_x = col
                grid_y = row
                x = self.x + grid_x * self.thumbnail_size
                y = self.y + grid_y * self.thumbnail_size

                # Draw cells
                cell_rect = pygame.Rect(x, y, self.thumbnail_size, self.thumbnail_size)
                pygame.draw.rect(screen, (214, 162, 104), cell_rect)

                # White border
                pygame.draw.rect(screen, (255, 255, 255), cell_rect, 1)
        
        # Draw asset icons
        for idx, asset in enumerate(self.assets[start:end]):
                grid_x = idx % self.cols
                grid_y = idx // self.cols
                x = self.x + grid_x * self.thumbnail_size
                y = self.y + grid_y * self.thumbnail_size

                # Determine the absolute path to this file
                this_file = Path(__file__).resolve()
                project_root = this_file.parents[0]
                spritesheets_dir = project_root / "assets" / "spritesheets" / "assets"

                # Load only the first tile of the spritesheet as an icon
                icon_path = spritesheets_dir / asset["spritesheet"]
                icon_sheet = SpriteSheet(str(icon_path))

                # Calculate tile size (10x10 grid)
                total_width = icon_sheet.sheet.get_width()
                total_height = icon_sheet.sheet.get_height()
                tile_w = total_width // 10
                tile_h = total_height // 10

                # Resize and center the icon
                icon_resize = 1.5
                icon_margin = self.thumbnail_size // 6

                # Extract the first tile
                icon = icon_sheet.get_sprite(0, 0, tile_w, tile_h,
                                             scale=self.thumbnail_size / tile_w / icon_resize)

                #Draw square behind icon
                cell_rect = pygame.Rect(x, y, self.thumbnail_size, self.thumbnail_size)
                pygame.draw.rect(screen, (214, 162, 104), cell_rect)

                # White border
                pygame.draw.rect(screen, (255, 255, 255), cell_rect, 1)

                # Show icons
                screen.blit(icon, (x + icon_margin, y + icon_margin))

                # Yellow border
                if self.selected_asset == asset:
                    pygame.draw.rect(screen, (255, 255, 0), cell_rect, 5)
    
    def handle_click(self, mouse_pos):
        mx, my = mouse_pos

        # Asset selection
        def handle_grid_selection(grid_list, set_selected_callback):
            for idx in range(self.cols * self.rows):
                grid_x = idx % self.cols
                grid_y = idx // self.cols
                x = self.x + grid_x * self.thumbnail_size
                y = self.y + grid_y * self.thumbnail_size

                rect = pygame.Rect(x, y, self.thumbnail_size, self.thumbnail_size)
                
                if rect.collidepoint(mx, my):
                    index = idx

                    if index < len(grid_list):
                        set_selected_callback(index)
                        return grid_list[index]
            return None
        
        return handle_grid_selection(
                    self.assets,
                    lambda i: setattr(self, "selected_asset",
                    self.assets[i] if self.selected_asset != self.assets[i] else None
                )
            )
    
    def handle_hover(self, mouse_pos):
        mx, my = mouse_pos
        self.hovered_asset = None

        for idx, asset in enumerate(self.assets):
            grid_x = idx % self.cols
            grid_y = idx // self.cols
            x = self.x + grid_x * self.thumbnail_size
            y = self.y + grid_y * self.thumbnail_size
            rect = pygame.Rect(x, y, self.thumbnail_size, self.thumbnail_size)

            if rect.collidepoint(mx, my):
                self.hovered_asset = asset
                return asset
    
    def attempt_purchase(self):
        asset = self.selected_asset
        price = asset.get('price', 0)

        if self.total_balance < price:
            return False

        self.total_balance -= price

        inventory = inventory_abl.load_inventory()
        asset_type = asset.get('type')

        # Disallow re-buying floors/walls
        if asset_type in ['floor', 'wall']:
            for existing in inventory[asset_type]:
                if existing.get("id") == asset.get('id'):
                    self.total_balance += price
                    return False
            inventory[asset_type].append(asset)

        elif asset_type == 'item':
            found = False
            for existing in inventory['item']:
                if existing.get('id') == asset.get('id'):
                    existing['count'] = existing.get('count', 1) + 1
                    found = True
                    break

            if not found:
                # Copy asset and add count field
                asset_copy = asset.copy()
                asset_copy['count'] = 1
                inventory['item'].append(asset_copy)

        inventory_abl.save_inventory(inventory)
        return True




