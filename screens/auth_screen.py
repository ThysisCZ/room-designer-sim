import pygame
import sys
from storage.cloud_sync import login_user, register_user, request_password_reset, reset_password
from game_logic import create_background, create_sounds

class AuthScreen:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.clock = pygame.time.Clock()
        
        # Screen dimensions
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        self.bg_surface_collection = create_background(self.screen_width, self.screen_height)
        self.bg_surface = self.bg_surface_collection[0]
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (200, 200, 200)
        self.BLUE = (70, 130, 180)
        self.GREEN = (60, 179, 113)
        self.RED = (220, 20, 60)
        self.ORANGE = (255, 165, 0)
        
        # Input fields
        self.username_or_email = ""  
        self.password = ""
        self.email = "" 
        self.reset_code = ""
        self.new_password = ""
        self.password_visible = False
        self.new_password_visible = False
        
        # UI state
        self.active_field = None
        self.mode = "login"
        self.message = ""
        self.message_color = self.BLACK
        self.reset_email = ""
        
        # Input field rects - will be repositioned based on mode
        self.username_or_email_rect = pygame.Rect(self.screen_width // 2 - 165, 270, 300, 40)
        self.password_rect = pygame.Rect(self.screen_width // 2 - 165, 330, 300, 40)
        self.email_rect = pygame.Rect(self.screen_width // 2 - 165, 390, 300, 40)
        self.reset_code_rect = pygame.Rect(self.screen_width // 2 - 165, 330, 300, 40)
        self.new_password_rect = pygame.Rect(self.screen_width // 2 - 165, 390, 300, 40)
        
        # Button rects - will be repositioned based on mode
        self.show_hide_btn = pygame.Rect(self.screen_width // 2 + 145, 335, 52, 30)
        self.show_hide_new_btn = pygame.Rect(self.screen_width // 2 + 145, 395, 52, 30)
        self.login_register_btn = pygame.Rect(self.screen_width // 2 - 115, 470, 88, 40)
        self.continue_btn = pygame.Rect(self.screen_width // 2 + 5, 470, 88, 40)
        self.forgot_btn = pygame.Rect(self.screen_width // 2 - 87, 420, 150, 30)
        self.back_btn = pygame.Rect(self.screen_width // 2 - 115, 470, 88, 40)
        
        # Animation
        self.cursor_timer = 0
        self.show_cursor = True

        # Enable key repeat when typing
        pygame.key.set_repeat(250, 50)

        self.extended_text_rect = None

        self.sounds = create_sounds()
        self.sounds['ui_click'].set_volume(0.5)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                # Check input field clicks based on mode
                if self.mode in ["login", "register"]:
                    if self.username_or_email_rect.collidepoint(pos):
                        self.sounds['ui_click'].play()
                        self.active_field = "username_or_email"
                    elif self.password_rect.collidepoint(pos):
                        self.sounds['ui_click'].play()
                        self.active_field = "password"
                    elif self.email_rect.collidepoint(pos) and self.mode == "register":
                        self.sounds['ui_click'].play()
                        self.active_field = "email"
                        
                elif self.mode == "forgot_password":
                    if self.username_or_email_rect.collidepoint(pos):
                        self.sounds['ui_click'].play()
                        self.active_field = "username_or_email"
                        
                elif self.mode == "reset_password":
                    if self.reset_code_rect.collidepoint(pos):
                        self.sounds['ui_click'].play()
                        self.active_field = "reset_code"
                    elif self.new_password_rect.collidepoint(pos):
                        self.sounds['ui_click'].play()
                        self.active_field = "new_password"
                
                # Check button clicks based on mode
                if self.mode in ["login", "register"]:
                    if self.show_hide_btn.collidepoint(pos):
                        self.sounds['ui_click'].play()
                        self.password_visible = not self.password_visible
                    
                    elif self.login_register_btn.collidepoint(pos):
                        if self.mode == "login":
                            self.sounds['ui_click'].play()
                            self.mode = "register"
                            self.message = ""
                            self.active_field = None
                            self.username_or_email = ""  
                            self.password = ""
                            self.email = ""
                        else:
                            self.sounds['ui_click'].play()
                            self.mode = "login"
                            self.message = ""
                            self.active_field = None
                            self.username_or_email = ""  
                            self.password = ""
                    
                    elif self.continue_btn.collidepoint(pos):
                        if self.mode == "login":
                            self.sounds['ui_click'].play()
                            return self.attempt_login()
                        else:
                            self.sounds['ui_click'].play()
                            return self.attempt_register()
                    
                    elif self.forgot_btn.collidepoint(pos) and self.mode == "login":
                        self.sounds['ui_click'].play()
                        self.mode = "forgot_password"
                        self.message = ""
                        self.active_field = None
                        self.username_or_email = ""
                
                elif self.mode == "forgot_password":
                    if self.continue_btn.collidepoint(pos):
                        self.sounds['ui_click'].play()
                        return self.request_reset_code()
                    elif self.back_btn.collidepoint(pos):
                        self.sounds['ui_click'].play()
                        self.mode = "login"
                        self.message = ""
                        self.active_field = None
                        self.username_or_email = ""
                
                elif self.mode == "reset_password":
                    if self.show_hide_new_btn.collidepoint(pos):
                        self.sounds['ui_click'].play()
                        self.new_password_visible = not self.new_password_visible
                    elif self.continue_btn.collidepoint(pos):
                        self.sounds['ui_click'].play()
                        return self.attempt_password_reset()
                    elif self.back_btn.collidepoint(pos):
                        self.sounds['ui_click'].play()
                        self.mode = "forgot_password"
                        self.message = ""
                        self.active_field = None
                        self.reset_code = ""
                        self.new_password = ""
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.mode == "login":
                        return self.attempt_login()
                    elif self.mode == "register":
                        return self.attempt_register()
                    elif self.mode == "forgot_password":
                        return self.request_reset_code()
                    elif self.mode == "reset_password":
                        return self.attempt_password_reset()
                elif event.key == pygame.K_ESCAPE:
                    if self.mode in ["forgot_password", "reset_password"]:
                        self.mode = "login"
                        self.message = ""
                        self.active_field = None
                        self.username_or_email = ""
                        self.reset_code = ""
                        self.new_password = ""
                    else:
                        return "quit"
                elif event.key == pygame.K_BACKSPACE:
                    self.handle_backspace()
                else:
                    self.handle_text_input(event.unicode)
        
        return None

    def handle_backspace(self):
        """Handle backspace key"""
        if self.active_field == "username_or_email":
            self.username_or_email = self.username_or_email[:-1]
        elif self.active_field == "password":
            self.password = self.password[:-1]
        elif self.active_field == "email":
            self.email = self.email[:-1]
        elif self.active_field == "reset_code":
            self.reset_code = self.reset_code[:-1]
        elif self.active_field == "new_password":
            self.new_password = self.new_password[:-1]

    def handle_text_input(self, text):
        """Handle text input"""
        if text.isprintable():
            if self.active_field == "username_or_email":
                if len(self.username_or_email) < 50:
                    self.username_or_email += text
            elif self.active_field == "password":
                if len(self.password) < 20:
                    self.password += text
            elif self.active_field == "email":
                if len(self.email) < 50:
                    self.email += text
            elif self.active_field == "reset_code":
                if len(self.reset_code) < 10:  # Reset codes are usually 6-8 digits
                    self.reset_code += text
            elif self.active_field == "new_password":
                if len(self.new_password) < 20:
                    self.new_password += text

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
        
        success, message = register_user(self.username_or_email, self.email, self.password)
        self.message = message
        self.message_color = self.GREEN if success else self.RED
        
        if success:
            return "success"
        return None

    def request_reset_code(self):
        """Request password reset code"""
        if not self.username_or_email:
            self.message = "Please enter your email address"
            self.message_color = self.RED
            return None
        
        if "@" not in self.username_or_email or "." not in self.username_or_email:
            self.message = "Please enter a valid email address"
            self.message_color = self.RED
            return None
        
        success, message = request_password_reset(self.username_or_email)
        self.message = message
        self.message_color = self.GREEN if success else self.RED
        
        if success:
            self.reset_email = self.username_or_email
            self.mode = "reset_password"
            self.active_field = None
            self.reset_code = ""
            self.new_password = ""
        
        return None

    def attempt_password_reset(self):
        """Attempt to reset password with code"""
        if not self.reset_code or not self.new_password:
            self.message = "Please fill in all fields"
            self.message_color = self.RED
            return None
        
        if len(self.new_password) < 6:
            self.message = "Password must be at least 6 characters"
            self.message_color = self.RED
            return None
        
        success, message = reset_password(self.reset_email, self.reset_code, self.new_password)
        self.message = message
        self.message_color = self.GREEN if success else self.RED
        
        if success:
            # Reset successful, go back to login
            self.mode = "login"
            self.active_field = None
            self.username_or_email = ""
            self.password = ""
            self.reset_code = ""
            self.new_password = ""
            self.reset_email = ""
        
        return None

    def draw_input_field(self, rect, text, placeholder, is_active, hide_text=False):
        """Draw an input field"""
        # Field background
        color = self.WHITE if is_active else self.LIGHT_GRAY
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, self.BLACK, rect, 2)
        
        # Text content
        display_text = text if not hide_text else "•" * len(text)
        if not display_text and not is_active:
            display_text = placeholder
            text_color = self.GRAY
        else:
            text_color = self.BLACK
        
        text_surface = self.font.render(display_text, True, text_color)
        text_rect = text_surface.get_rect()
        text_rect.centery = rect.centery
        border_offset = 10
        text_rect.x = rect.x + border_offset
        
        # Handle longer input
        if text_rect.width > rect.width:
            self.extended_text_rect = pygame.Rect.inflate(text_rect, border_offset, border_offset)
            self.extended_text_rect.topleft = rect.topleft
            self.extended_text_rect.height = rect.height
            self.extended_text_rect.width += border_offset

            if self.username_or_email:
                self.username_or_email_rect.width = self.extended_text_rect.width
            elif self.email:
                self.email_rect.width = self.extended_text_rect.width

            pygame.draw.rect(self.screen, color, self.extended_text_rect)
            pygame.draw.rect(self.screen, self.BLACK, self.extended_text_rect, 2)

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
        self.screen.blit(self.bg_surface, (0, 0))
        
        # Title based on mode
        if self.mode == "login":
            title_text = "Log In"
        elif self.mode == "register":
            title_text = "Register"
        elif self.mode == "forgot_password":
            title_text = "Reset Password"
        else:  # reset_password
            title_text = "Enter Reset Code"
            
        title_surface = pygame.font.Font('ithaca.ttf', 48).render(title_text, True, self.WHITE)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2 - 15, 175))
        self.screen.blit(title_surface, title_rect)
        
        # Draw UI based on mode
        if self.mode in ["login", "register"]:
            self.draw_login_register_ui()
        elif self.mode == "forgot_password":
            self.draw_forgot_password_ui()
        else:  # reset_password
            self.draw_reset_password_ui()
        
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

    def draw_login_register_ui(self):
        """Draw login/register specific UI"""
        # Input fields
        login_placeholder = "Username / Email" if self.mode == "login" else "Username"
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
        
        # Forgot password
        if self.mode == "login":
            forgot_surface = self.font.render("Forgot password?", True, self.WHITE)
            forgot_rect = forgot_surface.get_rect(center=self.forgot_btn.center)
            self.screen.blit(forgot_surface, forgot_rect)
        
        # Action buttons
        if self.mode == "login":
            self.draw_button(self.login_register_btn, "Register", self.GREEN)
        else:
            self.draw_button(self.login_register_btn, "Log In", self.GREEN)
        
        self.draw_button(self.continue_btn, "Continue", self.BLUE)

    def draw_forgot_password_ui(self):
        """Draw forgot password UI"""
        # Instruction text
        instruction = "Enter your email address to receive a reset code"
        instruction_surface = self.font.render(instruction, True, self.WHITE)
        instruction_rect = instruction_surface.get_rect(center=(self.screen_width // 2 - 7, 230))
        self.screen.blit(instruction_surface, instruction_rect)
        
        # Email input field
        self.draw_input_field(self.username_or_email_rect, self.username_or_email, "Email", 
                             self.active_field == "username_or_email")
        
        # Buttons
        self.draw_button(self.continue_btn, " Send Code ", self.BLUE)
        self.draw_button(self.back_btn, "Back", self.GRAY)

    def draw_reset_password_ui(self):
        """Draw reset password UI"""
        # Instruction text
        instruction1 = f"Reset code sent to: {self.reset_email}"
        instruction2 = "Check your email and enter the code below"
        
        instruction1_surface = self.font.render(instruction1, True, self.WHITE)
        instruction1_rect = instruction1_surface.get_rect(center=(self.screen_width // 2 - 7, 220))
        self.screen.blit(instruction1_surface, instruction1_rect)
        
        instruction2_surface = self.font.render(instruction2, True, self.WHITE)
        instruction2_rect = instruction2_surface.get_rect(center=(self.screen_width // 2 - 7, 245))
        self.screen.blit(instruction2_surface, instruction2_rect)
        
        # Input fields
        self.draw_input_field(self.reset_code_rect, self.reset_code, "Reset Code", 
                             self.active_field == "reset_code")
        
        self.draw_input_field(self.new_password_rect, self.new_password, "New Password", 
                             self.active_field == "new_password", not self.new_password_visible)
        
        # Show/Hide new password button
        show_hide_text = "Hide" if self.new_password_visible else "Show"
        self.draw_button(self.show_hide_new_btn, show_hide_text, self.GRAY)
        
        # Buttons
        self.draw_button(self.continue_btn, "Reset", self.BLUE)
        self.draw_button(self.back_btn, "Back", self.GRAY)

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