import os
import sys
import logging

def get_base_path():
    """
    Get the base path for the application, handling both script and executable modes.
    This should work consistently across all environments.
    """
    if getattr(sys, 'frozen', False):
        # If running as exe, check if assets are in current directory first
        exe_dir = os.path.dirname(sys.executable)
        if os.path.exists(os.path.join(exe_dir, 'assets')):
            return exe_dir
        
        # Check parent directory as fallback
        parent_dir = os.path.dirname(exe_dir)
        if os.path.exists(os.path.join(parent_dir, 'assets')):
            return parent_dir
            
        # If assets not found, default to exe directory
        return exe_dir
    else:
        # Running as script
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def verify_assets_structure():
    """
    Verify that all required asset directories exist.
    """
    required_dirs = [
        ['assets'],
        ['assets', 'spritesheets'],
        ['assets', 'spritesheets', 'assets'],
        ['assets', 'spritesheets', 'floors'],
        ['assets', 'spritesheets', 'walls'],
        ['assets', 'spritesheets', 'items']
    ]
    
    base_path = get_base_path()
    missing = []
    
    for parts in required_dirs:
        path = os.path.join(base_path, *parts)
        if not os.path.exists(path):
            missing.append(path)
            logging.error(f"Missing required directory: {path}")
    
    if missing:
        raise FileNotFoundError(f"Missing required directories: {', '.join(missing)}")
    return True

def get_asset_path(*path_parts):
    """
    Get a path relative to the assets directory.
    Usage: get_asset_path('spritesheets', 'floors', 'stone_floor.png')
    """
    base = get_base_path()
    path = os.path.join(base, 'assets', *path_parts)
    return path

def get_spritesheet_path(category, filename):
    """
    Get path to a spritesheet file.
    Categories: 'assets', 'floors', 'walls', 'items'
    """
    if category not in ['assets', 'floors', 'walls', 'items']:
        raise ValueError(f"Invalid spritesheet category: {category}")
        
    path = get_asset_path('spritesheets', category, filename)
    if not os.path.exists(path):
        logging.error(f"Spritesheet not found: {path}")
        raise FileNotFoundError(f"Spritesheet not found: {path}")
    return path

def init_path_system():
    """
    Initialize and verify the path system at startup.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    try:
        verify_assets_structure()
        logging.info("Asset structure verified successfully")
    except FileNotFoundError as e:
        logging.error(f"Asset structure verification failed: {e}")
        raise

# Debug function to help troubleshoot path issues
def debug_paths():
    """Print debug information about current paths"""
    print(f"=== PATH DEBUG INFO ===")
    print(f"sys.frozen: {getattr(sys, 'frozen', False)}")
    print(f"sys.executable: {sys.executable}")
    print(f"os.getcwd(): {os.getcwd()}")
    print(f"Base path: {get_base_path()}")
    print(f"Assets path: {get_asset_path()}")
    
    # Check if assets directory exists
    assets_path = get_asset_path()
    print(f"Assets directory exists: {os.path.exists(assets_path)}")
    
    if os.path.exists(assets_path):
        try:
            contents = os.listdir(assets_path)
            print(f"Assets directory contents: {contents}")
        except Exception as e:
            print(f"Error listing assets directory: {e}")
    
    print(f"=====================")