import requests
import json
import os
from datetime import datetime
from typing import Dict, Optional, Tuple

# Import existing storage modules
from storage.inventory_abl import load_inventory, save_inventory
from storage.selection_abl import load_selected_assets, save_selected_assets
from storage.tile_abl import load_tiles, save_tiles

# API Configuration
API_BASE_URL = "http://localhost:8000"
SYNC_FILE = "storage/last_sync.json"
USER_FILE = "storage/user_session.json"

class CloudSyncManager:
    def __init__(self):
        self.api_base = API_BASE_URL
        self.user_id = None
        self.username = None
        self.load_user_session()

    def load_user_session(self):
        """Load saved user session if exists"""
        try:
            if os.path.exists(USER_FILE):
                with open(USER_FILE, "r") as f:
                    session = json.load(f)
                    self.user_id = session.get("user_id")
                    self.username = session.get("username")
        except:
            pass

    def save_user_session(self, user_id: str, username: str):
        """Save user session to file"""
        self.user_id = user_id
        self.username = username
        session_data = {
            "user_id": user_id,
            "username": username,
            "login_time": datetime.now().isoformat()
        }
        with open(USER_FILE, "w") as f:
            json.dump(session_data, f, indent=4)

    def clear_user_session(self):
        """Clear user session and local data"""
        self.user_id = None
        self.username = None
        
        # Clear all local data files
        files_to_clear = [
            USER_FILE,
            SYNC_FILE,
            os.path.join(os.path.dirname(__file__), "stats_data.json"),
            os.path.join(os.path.dirname(__file__), "inventory_data.json"),
            os.path.join(os.path.dirname(__file__), "selection_data.json"),
            os.path.join(os.path.dirname(__file__), "tile_data.json")
        ]
        
        for file in files_to_clear:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass

    def register_user(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        """Register new user"""
        try:
            response = requests.post(f"{self.api_base}/auth/register", json={
                "username": username,
                "email": email,
                "password": password
            })
            
            if response.status_code == 201:
                data = response.json()
                user_id = data["data"]["userId"]
                self.save_user_session(user_id, username)
                return True, "Registration successful!"
            else:
                error_msg = response.json().get("message", "Registration failed")
                return False, error_msg
                
        except requests.RequestException:
            return False, "Network error - check your connection"
        except Exception as e:
            return False, f"Registration error: {str(e)}"

    def login_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Login user and load their data"""
        try:
            response = requests.post(f"{self.api_base}/auth/login", json={
                "username": username,
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                user_id = data["data"]["userId"]
                username = data["data"]["username"]
                self.save_user_session(user_id, username)
                
                # Immediately download user's data from MongoDB
                success, msg = self.download_game_data()
                if not success:
                    return False, f"Login successful but failed to load game data: {msg}"
                
                return True, "Login successful!"
            else:
                error_msg = response.json().get("message", "Login failed")
                return False, error_msg
                
        except requests.RequestException:
            return False, "Network error - check your connection"
        except Exception as e:
            return False, f"Login error: {str(e)}"

    def request_password_reset(self, email: str) -> Tuple[bool, str]:
        """Request password reset code via email"""
        try:
            response = requests.post(f"{self.api_base}/auth/forgot-password", json={
                "email": email
            })
            
            if response.status_code == 200:
                return True, ""
            else:
                error_msg = response.json().get("message", "Failed to send reset code")
                return False, error_msg
                
        except requests.RequestException:
            return False, "Network error - check your connection"
        except Exception as e:
            return False, f"Password reset request error: {str(e)}"

    def reset_password(self, email: str, reset_code: str, new_password: str) -> Tuple[bool, str]:
        """Reset password using the code from email"""
        try:
            response = requests.post(f"{self.api_base}/auth/reset-password", json={
                "email": email,
                "resetCode": reset_code,
                "newPassword": new_password
            })
            
            if response.status_code == 200:
                return True, ""
            else:
                error_msg = response.json().get("message", "Password reset failed")
                return False, error_msg
                
        except requests.RequestException:
            return False, "Network error - check your connection"
        except Exception as e:
            return False, f"Password reset error: {str(e)}"

    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        return self.user_id is not None

    def get_local_game_data(self) -> Dict:
        """Collect all local game data"""
        # Load stats
        stats = {"total_balance": 0, "snake_hi_score": 0, "fruit_hi_score": 0, "bullet_hi_score": 0}
        stats_file = os.path.join(os.path.dirname(__file__), "stats_data.json")
        try:
            if os.path.exists(stats_file):
                with open(stats_file, "r") as f:
                    stats = json.load(f)
        except:
            pass

        # Get current selection
        selection = load_selected_assets()
        
        return {
            "inventory": load_inventory(),
            "selection": selection,
            "stats": stats,
            "tiles": load_tiles()
        }

    def save_local_game_data(self, game_data: Dict):
        """Save game data to local files"""
        # Save inventory
        if "inventory" in game_data:
            save_inventory(game_data["inventory"])
        
        # Save selection
        if "selection" in game_data:
            selection = game_data["selection"]
            floor_selection = selection.get("floor")
            wall_selection = selection.get("wall")
            save_selected_assets(floor_selection, wall_selection)
        
        # Save stats
        if "stats" in game_data:
            stats_file = os.path.join(os.path.dirname(__file__), "stats_data.json")
            with open(stats_file, "w") as f:
                json.dump(game_data["stats"], f, indent=4)
        
        # Save tiles
        if "tiles" in game_data:
            save_tiles(game_data["tiles"])

    def upload_game_data(self) -> Tuple[bool, str]:
        """Upload local game data to cloud"""
        if not self.is_logged_in():
            return False, "Not logged in"

        try:
            game_data = self.get_local_game_data()
            
            response = requests.post(
                f"{self.api_base}/gamedata/save/{self.user_id}",
                json=game_data
            )
            
            if response.status_code == 200:
                self.update_last_sync_time()
                return True, "Game data uploaded successfully!"
            else:
                return False, "Upload failed"
                
        except requests.RequestException:
            return False, "Network error - check your connection"
        except Exception as e:
            return False, f"Upload error: {str(e)}"

    def download_game_data(self) -> Tuple[bool, str]:
        """Download game data from cloud"""
        if not self.is_logged_in():
            return False, "Not logged in"

        try:
            response = requests.get(f"{self.api_base}/gamedata/load/{self.user_id}")
            
            if response.status_code == 200:
                cloud_data = response.json()["data"]
                self.save_local_game_data(cloud_data)
                self.update_last_sync_time()
                return True, "Game data downloaded successfully!"
            else:
                return False, "Download failed"
                
        except requests.RequestException:
            return False, "Network error - check your connection"
        except Exception as e:
            return False, f"Download error: {str(e)}"

    def sync_game_data(self) -> Tuple[bool, str]:
        """Smart sync - compares local vs cloud timestamps"""
        if not self.is_logged_in():
            return False, "Not logged in"

        try:
            game_data = self.get_local_game_data()
            last_sync = self.get_last_sync_time()
            
            response = requests.patch(
                f"{self.api_base}/gamedata/sync/{self.user_id}",
                json={
                    "gameData": game_data,
                    "lastSyncTime": last_sync
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                action = result["action"]
                
                if action == "download":
                    # Cloud data is newer, save it locally
                    cloud_data = result["data"]
                    self.save_local_game_data(cloud_data)
                    self.update_last_sync_time()
                    return True, "Downloaded newer data from cloud!"
                else:
                    # Local data was uploaded
                    self.update_last_sync_time()
                    return True, "Uploaded local data to cloud!"
            else:
                return False, "Sync failed"
                
        except requests.RequestException:
            return False, "Network error - check your connection"
        except Exception as e:
            return False, f"Sync error: {str(e)}"

    def get_last_sync_time(self) -> Optional[str]:
        """Get last sync timestamp"""
        try:
            if os.path.exists(SYNC_FILE):
                with open(SYNC_FILE, "r") as f:
                    data = json.load(f)
                    return data.get("last_sync")
        except:
            pass
        return None

    def update_last_sync_time(self):
        """Update last sync timestamp"""
        sync_data = {
            "last_sync": datetime.now().isoformat(),
            "user_id": self.user_id
        }
        with open(SYNC_FILE, "w") as f:
            json.dump(sync_data, f, indent=4)

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