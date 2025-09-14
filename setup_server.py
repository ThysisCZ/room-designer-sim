#!/usr/bin/env python3
"""
Server Setup Script for Room Designer Simulator
This script ensures the server dependencies are installed before the game starts.
"""

import os
import sys
import subprocess

def setup_server_dependencies():
    """Set up server dependencies if needed"""
    print("Setting up server dependencies...")
    
    # Get the correct server directory
    if getattr(sys, 'frozen', False):
        # Running as executable
        if hasattr(sys, '_MEIPASS'):
            server_dir = os.path.join(sys._MEIPASS, 'server')
        else:
            server_dir = os.path.join(os.path.dirname(sys.executable), 'server')
    else:
        # Running from source
        server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server')
    
    print(f"Server directory: {server_dir}")
    
    # Check if package.json exists
    package_json = os.path.join(server_dir, 'package.json')
    if not os.path.exists(package_json):
        print(f"ERROR: package.json not found at {package_json}")
        return False
    
    # Check if node_modules exists
    node_modules_path = os.path.join(server_dir, 'node_modules')
    if not os.path.exists(node_modules_path):
        print("node_modules not found, installing dependencies...")
        
        # Find npm executable
        npm_path = None
        try:
            result = subprocess.run(['where', 'npm'], capture_output=True, text=True)
            if result.returncode == 0:
                npm_path = result.stdout.strip().split('\n')[0]
        except:
            pass
        
        if not npm_path:
            # Try to find npm in common locations (prioritize .cmd files on Windows)
            node_paths = [
                r'C:\Program Files\nodejs\npm.cmd',
                r'C:\Program Files (x86)\nodejs\npm.cmd',
                r'C:\Program Files\nodejs\npm',
                r'C:\Program Files (x86)\nodejs\npm'
            ]
            
            for path in node_paths:
                if os.path.exists(path):
                    npm_path = path
                    break
        
        # If still not found, try using node to run npm
        if not npm_path:
            try:
                result = subprocess.run(['where', 'node'], capture_output=True, text=True)
                if result.returncode == 0:
                    node_path = result.stdout.strip().split('\n')[0]
                    # Use node to run npm
                    npm_path = [node_path, os.path.join(os.path.dirname(node_path), 'node_modules', 'npm', 'bin', 'npm-cli.js')]
            except:
                pass
        
        if not npm_path:
            # Last resort: try to run the batch file
            batch_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'install_dependencies.bat')
            if os.path.exists(batch_file):
                print("Trying to run install_dependencies.bat...")
                try:
                    result = subprocess.run([batch_file], 
                                          cwd=os.path.dirname(batch_file),
                                          capture_output=True, 
                                          text=True, 
                                          timeout=120)
                    if result.returncode == 0:
                        print("Dependencies installed successfully via batch file!")
                        return True
                    else:
                        print(f"Batch file failed: {result.stderr}")
                except Exception as e:
                    print(f"Error running batch file: {e}")
            
            print("ERROR: npm not found. Please install Node.js.")
            return False
        
        print(f"Using npm at: {npm_path}")
        
        # Run npm install
        try:
            print("Running npm install...")
            if isinstance(npm_path, list):
                # npm_path is a list [node_path, npm_script_path]
                cmd = npm_path + ['install']
            else:
                # npm_path is a string
                cmd = [npm_path, 'install']
            
            result = subprocess.run(cmd, 
                                  cwd=server_dir, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=120)
            
            if result.returncode == 0:
                print("Dependencies installed successfully!")
                return True
            else:
                print(f"npm install failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("npm install timed out")
            return False
        except Exception as e:
            print(f"Error running npm install: {e}")
            return False
    else:
        print("Dependencies already installed")
        return True

if __name__ == "__main__":
    success = setup_server_dependencies()
    if success:
        print("Server setup completed successfully!")
    else:
        print("Server setup failed!")
        sys.exit(1)