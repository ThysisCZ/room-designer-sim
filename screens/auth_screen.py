import pygame
import sys
from storage.cloud_sync import login_user, register_user

class AuthScreen:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.clock = pygame.time.Clock()
        
        # Screen dimensions
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (200, 200, 200)
        self.BLUE = (70, 130, 180)
        self.GREEN = (60, 179, 113)
        self.RED = (220, 20, 60)
        
        # Input fields
        self.username_or_email = ""  
        self.password = ""
        self.email = "" 
        self.password_visible = False
        
        # UI state
        self.active_field = "username_or_email"
        self.mode = "login"  
        self.message = ""
        self.message_color = self.BLACK
        
        # Input field rects
        self.username_or_email_rect = pygame.Rect(self.screen_width // 2 - 165, 270, 300, 40)
        self.password_rect = pygame.Rect(self.screen_width // 2 - 165, 330, 300, 40)
        self.email_rect = pygame.Rect(self.screen_width // 2 - 165, 390, 300, 40)
        
        # Button rects
        self.show_hide_btn = pygame.Rect(self.screen_width // 2 + 145, 335, 60, 30)
        self.login_register_btn = pygame.Rect(self.screen_width // 2 - 110, 470, 85, 40)
        self.continue_btn = pygame.Rect(self.screen_width // 2 + 10, 470, 85, 40)
        self.forgot_btn = pygame.Rect(self.screen_width // 2 - 85, 420, 150, 30)
        
        # Animation
        self.cursor_timer = 0
        self.show_cursor = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                # Check input field clicks
                if self.username_or_email_rect.collidepoint(pos):
                    self.active_field = "username_or_email"
                elif self.password_rect.collidepoint(pos):
                    self.active_field = "password"
                elif self.email_rect.collidepoint(pos) and self.mode == "register":
                    self.active_field = "email"
                
                # Check button clicks
                elif self.show_hide_btn.collidepoint(pos):
                    self.password_visible = not self.password_visible
                
                elif self.login_register_btn.collidepoint(pos):
                    if self.mode == "login":
                        self.mode = "register"
                        self.message = ""
                    else:
                        self.mode = "login"
                        self.message = ""
                        self.email = ""
                
                elif self.continue_btn.collidepoint(pos):
                    if self.mode == "login":
                        return self.attempt_login()
                    return self.attempt_register()
                
                elif self.forgot_btn.collidepoint(pos):
                    self.message = "TODO"
                    self.message_color = self.GRAY
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.cycle_active_field()
                elif event.key == pygame.K_RETURN:
                    if self.mode == "login":
                        return self.attempt_login()
                    else:
                        return self.attempt_register()
                elif event.key == pygame.K_ESCAPE:
                    return "quit"
                elif event.key == pygame.K_BACKSPACE:
                    self.handle_backspace()
                else:
                    self.handle_text_input(event.unicode)
        
        return None

    def cycle_active_field(self):
        """Cycle through input fields with Tab"""
        if self.mode == "login":
            if self.active_field == "username_or_email":
                self.active_field = "password"
            else:
                self.active_field = "username_or_email"
        else:  # register mode
            if self.active_field == "username_or_email":
                self.active_field = "email"
            elif self.active_field == "email":
                self.active_field = "password"
            else:
                self.active_field = "username_or_email"

    def handle_backspace(self):
        """Handle backspace key"""
        if self.active_field == "username_or_email":
            self.username_or_email = self.username_or_email[:-1]
        elif self.active_field == "password":
            self.password = self.password[:-1]
        elif self.active_field == "email":
            self.email = self.email[:-1]

    def handle_text_input(self, text):
        """Handle text input"""
        if text.isprintable():
            if self.active_field == "username_or_email":
                if len(self.username_or_email) < 50:  # Increased for email length
                    self.username_or_email += text
            elif self.active_field == "password":
                if len(self.password) < 30:
                    self.password += text
            elif self.active_field == "email":
                if len(self.email) < 50:
                    self.email += text

    def attempt_login(self):
        """Attempt to login"""
        if not self.username_or_email or not self.password:
            self.message = "Please fill in all fields"
            self.message_color = self.RED
            return None
        
        # Try login with username or email
        success, message = login_user(self.username_or_email, self.password)
        self.message = message
        self.message_color = self.GREEN if success else self.RED
        
        if success:
            return "success"
        return None

    def attempt_register(self):
        """Attempt to register"""
        if not self.username_or_email or not self.password or not self.email:
            self.message = "Please fill in all fields"
            self.message_color = self.RED
            return None
        
        if "@" not in self.email or "." not in self.email:
            self.message = "Please enter a valid email address"
            self.message_color = self.RED
            return None
        
        # For registration, username_or_email field should be username only
        success, message = register_user(self.username_or_email, self.email, self.password)
        self.message = message
        self.message_color = self.GREEN if success else self.RED
        
        if success:
            return "success"
        return None

    def draw_input_field(self, rect, text, placeholder, is_active, hide_text=False):
        """Draw an input field"""
        # Field background
        color = self.WHITE if is_active else self.LIGHT_GRAY
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, self.BLACK, rect, 2)
        
        # Text content
        display_text = text if not hide_text else "*" * len(text)
        if not display_text and not is_active:
            display_text = placeholder
            text_color = self.GRAY
        else:
            text_color = self.BLACK
        
        text_surface = self.font.render(display_text, True, text_color)
        text_rect = text_surface.get_rect()
        text_rect.centery = rect.centery
        text_rect.x = rect.x + 10
        self.screen.blit(text_surface, text_rect)
        
        # Cursor
        if is_active and self.show_cursor:
            cursor_x = text_rect.right + 2
            cursor_y = rect.y + 5
            pygame.draw.line(self.screen, self.BLACK, 
                           (cursor_x, cursor_y), (cursor_x, rect.bottom - 5), 2)

    def draw_button(self, rect, text, color=None):
        """Draw a button"""
        if color is None:
            color = self.BLUE
        
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, self.BLACK, rect, 2)
        
        text_surface = self.font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def draw(self):
        """Draw the authentication screen"""
        self.screen.fill(self.WHITE)
        
        # Title
        title_text = "Log In" if self.mode == "login" else "Register"
        title_surface = pygame.font.Font(None, 48).render(title_text, True, self.BLACK)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2 - 15, 175))
        self.screen.blit(title_surface, title_rect)
        
        # Input fields
        login_placeholder = "Username or Email" if self.mode == "login" else "Username"
        self.draw_input_field(self.username_or_email_rect, self.username_or_email, login_placeholder, 
                             self.active_field == "username_or_email")
        
        if self.mode == "register":
            self.draw_input_field(self.email_rect, self.email, "Email", 
                                 self.active_field == "email")
        
        self.draw_input_field(self.password_rect, self.password, "Password", 
                             self.active_field == "password", not self.password_visible)
        
        # Show/Hide password button
        show_hide_text = "Hide" if self.password_visible else "Show"
        self.draw_button(self.show_hide_btn, show_hide_text, self.GRAY)
        
        # Forgot password (only in login mode)
        if self.mode == "login":
            forgot_surface = self.font.render("Forgot password?", True, self.BLUE)
            forgot_rect = forgot_surface.get_rect(center=self.forgot_btn.center)
            self.screen.blit(forgot_surface, forgot_rect)
        
        # Action buttons
        if self.mode == "login":
            self.draw_button(self.login_register_btn, "Register", self.GREEN)
        else:
            self.draw_button(self.login_register_btn, "Log In", self.GREEN)
        
        self.draw_button(self.continue_btn, "Continue", self.BLUE)
        
        # Message
        if self.message:
            message_surface = self.font.render(self.message, True, self.message_color)
            message_rect = message_surface.get_rect(center=(self.screen_width // 2 - 7, 550))
            self.screen.blit(message_surface, message_rect)
        
        # Update cursor blink
        self.cursor_timer += self.clock.get_time()
        if self.cursor_timer > 500:
            self.show_cursor = not self.show_cursor
            self.cursor_timer = 0

    def run(self):
        """Run the authentication screen"""
        running = True
        while running:
            result = self.handle_events()
            
            if result == "quit":
                pygame.quit()
                sys.exit()
            elif result == "success":
                return True  # Logged in successfully
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        return False