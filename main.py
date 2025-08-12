from game import RoomDesignerGame
from screens.auth_screen import AuthScreen
from storage.cloud_sync import (
    register_user, login_user, logout_user, is_logged_in, 
    get_current_user, sync_to_cloud, upload_to_cloud, download_from_cloud
)
import pygame

def game_startup():
    """Gets called when game starts"""
    if is_logged_in():
        print(f"Welcome back, {get_current_user()}!")
        # Try to sync data
        success, message = sync_to_cloud()
        if success:
            print(f"Sync: {message}")
        else:
            print(f"Sync failed: {message} (playing offline)")
        return show_auth_screen()
    else:
        print("Playing offline - login to sync progress")
        return show_auth_screen()

def show_auth_screen():
    """Show the combined login/register screen"""
    pygame.init()
    # Set up fullscreen display
    display_info = pygame.display.Info()
    screen = pygame.display.set_mode((display_info.current_w, display_info.current_w), pygame.FULLSCREEN)
    pygame.display.set_caption("Room Designer - Login")
    font = pygame.font.Font('ithaca.ttf', 24)
    
    auth_screen = AuthScreen(screen, font)
    logged_in = auth_screen.run()
    
    if logged_in:
        # Try to sync after successful login
        success, message = sync_to_cloud()
        print(f"Sync: {message}")
    
    return logged_in

def game_exit():
    """Gets called when game exits"""
    if is_logged_in():
        success, message = upload_to_cloud()
        if success:
            print("Progress saved to cloud!")
        else:
            print(f"Cloud save failed: {message}")

if __name__ == "__main__":
    # Show auth screen first if not logged in
    authenticated = game_startup()
    
    try:
        game = RoomDesignerGame()
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted")
    finally:
        game_exit()