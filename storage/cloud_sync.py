import requests
import json
import os
import sys
import time
import traceback
from datetime import datetime
from typing import Dict, Optional, Tuple

# Import existing storage modules
from storage.inventory_abl import load_inventory, save_inventory
from storage.selection_abl import load_selected_assets, save_selected_assets
from storage.tile_abl import load_tiles, save_tiles

# API Configuration
API_BASE_URL = "http://localhost:8000"

def get_storage_path():
    """Get the correct storage path for both script and executable modes"""
    if getattr(sys, 'frozen', False):
        # Running as executable - use directory where exe is located
        # Since you move the exe to root folder, this will be the project root
        base_path = os.path.dirname(sys.executable)
        print(f"Running as executable, exe location: {base_path}")
    else:
        # Running as script - go up one level from storage/ to project root
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(current_file_dir)  # Go up from storage/ to project root
        print(f"Running as script, project root: {base_path}")
    
    storage_path = os.path.join(base_path, 'storage')
    # Ensure storage directory exists
    os.makedirs(storage_path, exist_ok=True)
    print(f"Using storage path: {storage_path}")
    return storage_path

# Dynamic file paths
def get_sync_file():
    return os.path.join(get_storage_path(), "last_sync.json")

def get_user_file():
    return os.path.join(get_storage_path(), "user_session.json")

def get_stats_file():
    return os.path.join(get_storage_path(), "stats_data.json")

def wait_for_server_ready(timeout=30, check_interval=1):
    """Wait for server to be fully ready with proper retry logic"""
    print(f"Waiting for server to be ready (timeout: {timeout}s)...")
    start_time = time.time()
    attempts = 0
    
    while time.time() - start_time < timeout:
        attempts += 1
        try:
            print(f"Server readiness check attempt {attempts}...")
            response = requests.get(f"{API_BASE_URL}/health", timeout=3)
            if response.status_code == 200:
                print("Server is ready!")
                return True
        except requests.exceptions.RequestException as e:
            print(f"Server not ready yet: {e}")
        
        time.sleep(check_interval)
    
    print(f"Server failed to become ready within {timeout} seconds")
    return False

class CloudSyncManager:
    def __init__(self):
        self.api_base = API_BASE_URL
        self.user_id = None
        self.username = None
        print("Initializing CloudSyncManager...")
        self.load_user_session()

    def load_user_session(self):
        """Load saved user session if exists"""
        try:
            user_file = get_user_file()
            print(f"Loading user session from: {user_file}")
            if os.path.exists(user_file):
                with open(user_file, "r") as f:
                    session = json.load(f)
                    self.user_id = session.get("user_id")
                    self.username = session.get("username")
                    print(f"Loaded session for user: {self.username}")
            else:
                print("No existing user session found")
        except Exception as e:
            print(f"Error loading user session: {e}")
            traceback.print_exc()

    def save_user_session(self, user_id: str, username: str):
        """Save user session to file"""
        try:
            self.user_id = user_id
            self.username = username
            session_data = {
                "user_id": user_id,
                "username": username,
                "login_time": datetime.now().isoformat()
            }
            user_file = get_user_file()
            print(f"Saving user session to: {user_file}")
            with open(user_file, "w") as f:
                json.dump(session_data, f, indent=4)
            print("User session saved successfully")
        except Exception as e:
            print(f"Error saving user session: {e}")
            traceback.print_exc()

    def clear_user_session(self):
        """Clear user session and local data"""
        print("Clearing user session and local data...")
        self.user_id = None
        self.username = None
        
        # Clear all local data files
        files_to_clear = [
            get_user_file(),
            get_sync_file(),
            get_stats_file(),
            os.path.join(get_storage_path(), "inventory_data.json"),
            os.path.join(get_storage_path(), "selection_data.json"),
            os.path.join(get_storage_path(), "tile_data.json")
        ]
        
        for file in files_to_clear:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    print(f"Removed file: {file}")
                except Exception as e:
                    print(f"Error removing file {file}: {e}")

    def register_user(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        """Register new user"""
        try:
            print(f"Registering user: {username}")
            # Wait for server to be ready before attempting registration
            if not wait_for_server_ready(timeout=15):
                return False, "Server is not responding"
                
            response = requests.post(f"{self.api_base}/auth/register", json={
                "username": username,
                "email": email,
                "password": password
            }, timeout=15)
            
            if response.status_code == 201:
                data = response.json()
                user_id = data["data"]["userId"]
                self.save_user_session(user_id, username)
                print("Registration successful")
                return True, "Registration successful!"
            else:
                error_msg = response.json().get("message", "Registration failed")
                print(f"Registration failed: {error_msg}")
                return False, error_msg
                
        except requests.RequestException as e:
            print(f"Network error during registration: {e}")
            return False, "Network error - check your connection"
        except Exception as e:
            print(f"Registration error: {e}")
            traceback.print_exc()
            return False, f"Registration error: {str(e)}"

    def login_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Login user and load their data"""
        try:
            print(f"Logging in user: {username}")
            # Wait for server to be ready before attempting login
            if not wait_for_server_ready(timeout=15):
                return False, "Server is not responding"
                
            response = requests.post(f"{self.api_base}/auth/login", json={
                "username": username,
                "password": password
            }, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                user_id = data["data"]["userId"]
                username = data["data"]["username"]
                self.save_user_session(user_id, username)
                print("Login successful")
                
                # Immediately download user's data from MongoDB
                print("Downloading user data...")
                success, msg = self.download_game_data()
                if not success:
                    print(f"Failed to load game data: {msg}")
                    return False, f"Login successful but failed to load game data: {msg}"
                
                return True, "Login successful!"
            else:
                error_msg = response.json().get("message", "Login failed")
                print(f"Login failed: {error_msg}")
                return False, error_msg
                
        except requests.RequestException as e:
            print(f"Network error during login: {e}")
            return False, "Network error - check your connection"
        except Exception as e:
            print(f"Login error: {e}")
            traceback.print_exc()
            return False, f"Login error: {str(e)}"

    def request_password_reset(self, email: str) -> Tuple[bool, str]:
        """Request password reset code via email"""
        try:
            print(f"Requesting password reset for: {email}")
            if not wait_for_server_ready(timeout=15):
                return False, "Server is not responding"
                
            response = requests.post(f"{self.api_base}/auth/forgot-password", json={
                "email": email
            }, timeout=15)
            
            if response.status_code == 200:
                print("Password reset request successful")
                return True, ""
            else:
                error_msg = response.json().get("message", "Failed to send reset code")
                print(f"Password reset request failed: {error_msg}")
                return False, error_msg
                
        except requests.RequestException as e:
            print(f"Network error during password reset request: {e}")
            return False, "Network error - check your connection"
        except Exception as e:
            print(f"Password reset request error: {e}")
            traceback.print_exc()
            return False, f"Password reset request error: {str(e)}"

    def reset_password(self, email: str, reset_code: str, new_password: str) -> Tuple[bool, str]:
        """Reset password using the code from email"""
        try:
            print(f"Resetting password for: {email}")
            if not wait_for_server_ready(timeout=15):
                return False, "Server is not responding"
                
            response = requests.post(f"{self.api_base}/auth/reset-password", json={
                "email": email,
                "resetCode": reset_code,
                "newPassword": new_password
            }, timeout=15)
            
            if response.status_code == 200:
                print("Password reset successful")
                return True, ""
            else:
                error_msg = response.json().get("message", "Password reset failed")
                print(f"Password reset failed: {error_msg}")
                return False, error_msg
                
        except requests.RequestException as e:
            print(f"Network error during password reset: {e}")
            return False, "Network error - check your connection"
        except Exception as e:
            print(f"Password reset error: {e}")
            traceback.print_exc()
            return False, f"Password reset error: {str(e)}"

    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        logged_in = self.user_id is not None
        print(f"Login check: {logged_in}")
        return logged_in

    def get_local_game_data(self) -> Dict:
        """Collect all local game data"""
        print("Collecting local game data...")
        
        # Load stats
        stats = {"total_balance": 0, "snake_hi_score": 0, "fruit_hi_score": 0, "bullet_hi_score": 0}
        stats_file = get_stats_file()
        try:
            if os.path.exists(stats_file):
                print(f"Loading stats from: {stats_file}")
                with open(stats_file, "r") as f:
                    stats = json.load(f)
                print(f"Loaded stats: {stats}")
            else:
                print(f"Stats file not found: {stats_file}")
        except Exception as e:
            print(f"Error loading stats: {e}")

        # Get current data
        print("Loading inventory...")
        inventory = load_inventory()
        
        print("Loading selected assets...")
        selection = load_selected_assets()
        
        print("Loading tiles...")
        tiles = load_tiles()
        
        game_data = {
            "inventory": inventory,
            "selection": selection,
            "stats": stats,
            "tiles": tiles
        }
        
        print(f"Local game data collected: {list(game_data.keys())}")
        return game_data

    def save_local_game_data(self, game_data: Dict):
        """Save game data to local files"""
        print("Saving local game data...")
        
        try:
            # Save inventory
            if "inventory" in game_data:
                print("Saving inventory...")
                save_inventory(game_data["inventory"])
            
            # Save selection
            if "selection" in game_data:
                print("Saving selection...")
                selection = game_data["selection"]
                floor_selection = selection.get("floor")
                wall_selection = selection.get("wall")
                save_selected_assets(floor_selection, wall_selection)
            
            # Save stats
            if "stats" in game_data:
                print("Saving stats...")
                stats_file = get_stats_file()
                with open(stats_file, "w") as f:
                    json.dump(game_data["stats"], f, indent=4)
            
            # Save tiles
            if "tiles" in game_data:
                print("Saving tiles...")
                save_tiles(game_data["tiles"])
                
            print("Local game data saved successfully")
            
        except Exception as e:
            print(f"Error saving local game data: {e}")
            traceback.print_exc()

    def upload_game_data(self) -> Tuple[bool, str]:
        """Upload local game data to cloud with improved reliability"""
        print("Starting upload_game_data...")
        
        if not self.is_logged_in():
            print("User not logged in")
            return False, "Not logged in"

        try:
            # Enhanced server readiness check with longer timeout and retries
            print("Ensuring server is ready for upload...")
            if not wait_for_server_ready(timeout=20, check_interval=0.5):
                print("Server is not ready for upload")
                return False, "Server is not responding"
            
            print("Gathering local game data...")
            game_data = self.get_local_game_data()
            
            print(f"Making POST request to: {self.api_base}/gamedata/save/{self.user_id}")
            
            # Multiple upload attempts with exponential backoff
            max_attempts = 3
            base_delay = 1
            
            for attempt in range(max_attempts):
                try:
                    print(f"Upload attempt {attempt + 1}/{max_attempts}")
                    
                    # Additional health check before each attempt
                    health_response = requests.get(f"{self.api_base}/health", timeout=5)
                    if health_response.status_code != 200:
                        print(f"Health check failed on attempt {attempt + 1}")
                        if attempt < max_attempts - 1:
                            delay = base_delay * (2 ** attempt)
                            print(f"Waiting {delay}s before retry...")
                            time.sleep(delay)
                            continue
                        else:
                            return False, "Server health check failed"
                    
                    response = requests.post(
                        f"{self.api_base}/gamedata/save/{self.user_id}",
                        json=game_data,
                        timeout=90  # Increased timeout for slower environments
                    )
                    
                    print(f"Response status code: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("Upload successful, updating sync time...")
                        self.update_last_sync_time()
                        return True, "Game data uploaded successfully!"
                    else:
                        error_msg = f"Upload failed with status code: {response.status_code}"
                        try:
                            error_data = response.json()
                            error_msg += f", message: {error_data.get('message', 'Unknown error')}"
                        except:
                            error_msg += f", response: {response.text}"
                        print(error_msg)
                        
                        # Don't retry on client errors (4xx)
                        if 400 <= response.status_code < 500:
                            return False, error_msg
                        
                        # Retry on server errors (5xx) or other issues
                        if attempt < max_attempts - 1:
                            delay = base_delay * (2 ** attempt)
                            print(f"Server error, waiting {delay}s before retry...")
                            time.sleep(delay)
                            continue
                        else:
                            return False, error_msg
                            
                except requests.ConnectionError as e:
                    print(f"Connection error on attempt {attempt + 1}: {e}")
                    if attempt < max_attempts - 1:
                        delay = base_delay * (2 ** attempt)
                        print(f"Connection failed, waiting {delay}s before retry...")
                        time.sleep(delay)
                        continue
                    else:
                        return False, "Could not connect to server - server may have stopped"
                        
                except requests.Timeout as e:
                    print(f"Timeout on attempt {attempt + 1}: {e}")
                    if attempt < max_attempts - 1:
                        delay = base_delay * (2 ** attempt)
                        print(f"Request timed out, waiting {delay}s before retry...")
                        time.sleep(delay)
                        continue
                    else:
                        return False, "Upload timed out - check your connection"
                        
                except requests.RequestException as e:
                    print(f"Request error on attempt {attempt + 1}: {e}")
                    if attempt < max_attempts - 1:
                        delay = base_delay * (2 ** attempt)
                        print(f"Request failed, waiting {delay}s before retry...")
                        time.sleep(delay)
                        continue
                    else:
                        return False, f"Network error: {str(e)}"
            
            return False, "All upload attempts failed"
                
        except Exception as e:
            print(f"Upload error: {e}")
            traceback.print_exc()
            return False, f"Upload error: {str(e)}"

    def download_game_data(self) -> Tuple[bool, str]:
        """Download game data from cloud"""
        print("Starting download_game_data...")
        
        if not self.is_logged_in():
            print("User not logged in")
            return False, "Not logged in"

        try:
            print(f"Making GET request to: {self.api_base}/gamedata/load/{self.user_id}")
            response = requests.get(f"{self.api_base}/gamedata/load/{self.user_id}", timeout=15)
            
            print(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                cloud_data = response.json()["data"]
                print("Download successful, saving local data...")
                self.save_local_game_data(cloud_data)
                self.update_last_sync_time()
                return True, "Game data downloaded successfully!"
            else:
                error_msg = f"Download failed with status code: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f", message: {error_data.get('message', 'Unknown error')}"
                except:
                    error_msg += f", response: {response.text}"
                print(error_msg)
                return False, error_msg
                
        except requests.Timeout:
            print("Download request timed out")
            return False, "Download timed out - check your connection"
        except requests.RequestException as e:
            print(f"Network error during download: {e}")
            return False, "Network error - check your connection"
        except Exception as e:
            print(f"Download error: {e}")
            traceback.print_exc()
            return False, f"Download error: {str(e)}"

    def sync_game_data(self) -> Tuple[bool, str]:
        """Smart sync - compares local vs cloud timestamps"""
        print("Starting sync_game_data...")
        
        if not self.is_logged_in():
            print("User not logged in")
            return False, "Not logged in"

        try:
            # Wait for server readiness
            if not wait_for_server_ready(timeout=15):
                return False, "Server is not responding"
                
            print("Gathering data for sync...")
            game_data = self.get_local_game_data()
            last_sync = self.get_last_sync_time()
            print(f"Last sync time: {last_sync}")
            
            print(f"Making PATCH request to: {self.api_base}/gamedata/sync/{self.user_id}")
            response = requests.patch(
                f"{self.api_base}/gamedata/sync/{self.user_id}",
                json={
                    "gameData": game_data,
                    "lastSyncTime": last_sync
                },
                timeout=20
            )
            
            print(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                action = result["action"]
                print(f"Sync action: {action}")
                
                if action == "download":
                    # Cloud data is newer, save it locally
                    cloud_data = result["data"]
                    print("Saving newer cloud data locally...")
                    self.save_local_game_data(cloud_data)
                    self.update_last_sync_time()
                    return True, "Downloaded newer data from cloud!"
                else:
                    # Local data was uploaded
                    print("Local data was uploaded to cloud")
                    self.update_last_sync_time()
                    return True, "Uploaded local data to cloud!"
            else:
                error_msg = f"Sync failed with status code: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f", message: {error_data.get('message', 'Unknown error')}"
                except:
                    error_msg += f", response: {response.text}"
                print(error_msg)
                return False, error_msg
                
        except requests.Timeout:
            print("Sync request timed out")
            return False, "Sync timed out - check your connection"
        except requests.RequestException as e:
            print(f"Network error during sync: {e}")
            return False, "Network error - check your connection"
        except Exception as e:
            print(f"Sync error: {e}")
            traceback.print_exc()
            return False, f"Sync error: {str(e)}"

    def get_last_sync_time(self) -> Optional[str]:
        """Get last sync timestamp"""
        try:
            sync_file = get_sync_file()
            if os.path.exists(sync_file):
                print(f"Loading sync time from: {sync_file}")
                with open(sync_file, "r") as f:
                    data = json.load(f)
                    return data.get("last_sync")
            else:
                print(f"Sync file not found: {sync_file}")
        except Exception as e:
            print(f"Error loading sync time: {e}")
        return None

    def update_last_sync_time(self):
        """Update last sync timestamp"""
        try:
            sync_data = {
                "last_sync": datetime.now().isoformat(),
                "user_id": self.user_id
            }
            sync_file = get_sync_file()
            print(f"Updating sync time in: {sync_file}")
            with open(sync_file, "w") as f:
                json.dump(sync_data, f, indent=4)
            print("Sync time updated successfully")
        except Exception as e:
            print(f"Error updating sync time: {e}")
            traceback.print_exc()

# Global instance
cloud_sync = CloudSyncManager()

def register_user(username: str, email: str, password: str) -> Tuple[bool, str]:
    return cloud_sync.register_user(username, email, password)

def login_user(username: str, password: str) -> Tuple[bool, str]:
    return cloud_sync.login_user(username, password)

def logout_user():
    cloud_sync.clear_user_session()

def is_logged_in() -> bool:
    return cloud_sync.is_logged_in()

def get_current_user() -> Optional[str]:
    return cloud_sync.username

def sync_to_cloud() -> Tuple[bool, str]:
    return cloud_sync.sync_game_data()

def upload_to_cloud() -> Tuple[bool, str]:
    return cloud_sync.upload_game_data()

def download_from_cloud() -> Tuple[bool, str]:
    return cloud_sync.download_game_data()

def request_password_reset(email: str) -> Tuple[bool, str]:
    return cloud_sync.request_password_reset(email)

def reset_password(email: str, reset_code: str, new_password: str) -> Tuple[bool, str]:
    return cloud_sync.reset_password(email, reset_code, new_password)