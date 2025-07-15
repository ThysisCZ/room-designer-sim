import pygame
import math
import time
from enum import Enum


class GameState(Enum):
    MENU_SCREEN = 1
    MENU = 2
    PLAYING = 3

class Button:
    def __init__(self, x, y, width, height, text, font, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.base_color = color  # Store the original color
        self.text_color = text_color
        self.hover_color = (255, 255, 0)  # Yellow hover color
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