from game import RoomDesignerGame
from screens.auth_screen import AuthScreen
from storage.cloud_sync import (is_logged_in, get_current_user, sync_to_cloud, upload_to_cloud, wait_for_server_ready)
from server_launcher import ServerLauncher
from utils.path_utils import init_path_system

import pygame
import signal
import sys
import os
import time
import traceback

def game_startup():
    """Gets called when game starts"""
    try:
        if is_logged_in():
            print(f"Welcome back, {get_current_user()}!")
            # Try to sync data
            success, message = sync_to_cloud()
            if success:
                print(f"Sync: {message}")
            return True
        return True
    except Exception as e:
        print(f"Error in game_startup: {e}")
        traceback.print_exc()
        return False

def show_auth_screen():
    """Show the combined login/register screen"""
    try:
        pygame.init()
        # Set up fullscreen display
        display_info = pygame.display.Info()
        width = display_info.current_w
        height = display_info.current_h
        screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        pygame.display.set_caption("Room Designer Simulator")
        
        # Check if font file exists
        font_path = 'ithaca.ttf'
        if getattr(sys, 'frozen', False):
            # Running as executable
            font_path = os.path.join(sys._MEIPASS, 'ithaca.ttf')
        
        if not os.path.exists(font_path):
            print(f"Font file not found: {font_path}")
            font = pygame.font.Font(None, 24)  # Use default font
        else:
            font = pygame.font.Font(font_path, 24)
        
        auth_screen = AuthScreen(screen, font)
        logged_in = auth_screen.run()
        
        if logged_in:
            # Try to sync after successful login
            success, message = sync_to_cloud()
            print(f"Sync: {message}")
        
        return logged_in
    except Exception as e:
        print(f"Error in show_auth_screen: {e}")
        traceback.print_exc()
        return False

class GameManager:
    def __init__(self):
        self.server = ServerLauncher()
        self.game = None
        self._cleanup_done = False
        
    def __enter__(self):
        try:
            print(f"Running as executable: {getattr(sys, 'frozen', False)}")
            print(f"Base path: {os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)}")
            
            # Start server first
            print("Starting server...")
            if not self.server.start_server():
                print("Failed to start server.")
                return None
            print("Server started successfully")
            
            # Then handle authentication
            print("Showing auth screen...")
            authenticated = show_auth_screen()
            if authenticated:
                print("Authentication successful, initializing game...")
                self.game = RoomDesignerGame()
            else:
                print("Authentication failed or cancelled")
            return self.game
        except Exception as e:
            print(f"Error in GameManager.__enter__: {e}")
            traceback.print_exc()
            return None
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(f"Exception during game execution: {exc_type}, {exc_val}")
            traceback.print_exc()
        self._cleanup()
        
    def _cleanup(self):
        """Centralized cleanup method"""
        if self._cleanup_done:
            return
            
        print("Starting cleanup...")
        self._cleanup_done = True
        
        # Give any ongoing uploads a moment to complete
        print("Waiting for any ongoing operations to complete...")
        time.sleep(3)
        
        # Stop server after ensuring uploads are done
        try:
            if self.server:
                print("Stopping server...")
                self.server.stop_server()
                print("Server stopped")
        except Exception as e:
            print(f"Error stopping server: {e}")
            traceback.print_exc()

# Global game manager instance for signal handlers
game_manager = None

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"Received signal {signum}")
    if game_manager:
        game_manager._cleanup()
    pygame.quit()
    sys.exit(0)

def upload_on_game_end():
    """Upload data immediately after game ends, while server is still running"""
    print("Attempting to upload game data...")
    try:
        if is_logged_in():
            print(f"User is logged in as: {get_current_user()}")
            
            # Enhanced server readiness check before upload
            print("Ensuring server is ready for upload...")
            if not wait_for_server_ready(timeout=20, check_interval=0.5):
                print("Server is not ready for upload")
                return False
            
            print("Server is ready, proceeding with upload...")
            
            print("Calling upload_to_cloud()...")
            success, message = upload_to_cloud()
            print(f"Upload result - Success: {success}, Message: {message}")
            
            if success:
                print("Progress saved to cloud!")
                return True
            else:
                print(f"Cloud save failed: {message}")
                return False
        else:
            print("User not logged in, skipping cloud upload")
            return False
    except Exception as e:
        print(f"Error during immediate upload: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    init_path_system()
    
    # Enable console output for debugging when running as exe
    if getattr(sys, 'frozen', False):
        # Redirect stdout and stderr to files when running as exe
        log_dir = os.path.join(os.path.dirname(sys.executable), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        stdout_log = os.path.join(log_dir, 'game_stdout.log')
        stderr_log = os.path.join(log_dir, 'game_stderr.log')
        
        sys.stdout = open(stdout_log, 'w', buffering=1)
        sys.stderr = open(stderr_log, 'w', buffering=1)
        
        print(f"Game started as executable. Logs will be written to {log_dir}")
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    game_manager = None
    try:
        print("Initializing game manager...")
        game_manager = GameManager()
        
        with game_manager as game:
            if game:
                print("Starting game...")
                game.run()
                print("Game ended, uploading data...")
                
                # Enhanced upload retry logic with better server readiness checks
                upload_success = False
                max_retries = 5  # Increased from 3
                
                for attempt in range(max_retries):
                    print(f"Upload attempt {attempt + 1}/{max_retries}")
                    
                    # Wait longer between attempts for exe mode
                    if attempt > 0:
                        wait_time = min(5, 2 + attempt)  # Progressive delay: 2,3,4,5,5 seconds
                        print(f"Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                    
                    upload_success = upload_on_game_end()
                    
                    if upload_success:
                        print("Upload successful!")
                        break
                    else:
                        print(f"Upload attempt {attempt + 1} failed")
                        
                        # For exe mode, give the server more time to stabilize
                        if getattr(sys, 'frozen', False) and attempt < max_retries - 1:
                            print("Running as exe, giving server extra time to stabilize...")
                            time.sleep(2)
                
                print(f"Upload completed with success: {upload_success}")
                
                # Give more time for server operations to complete before cleanup
                time.sleep(3)
            else:
                print("Failed to initialize game")
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
    finally:
        # Ensure cleanup happens even if context manager fails
        if game_manager:
            print("Final cleanup...")
            game_manager._cleanup()
        
        pygame.quit()
        print("Game shutdown complete")