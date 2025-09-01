import subprocess
import sys
import os
import time
import psutil
import threading
import requests
import traceback

class ServerLauncher:
    def __init__(self):
        self.server_process = None
        self.server_port = 8000
        self.server_start_timeout = 45  # Increased timeout for exe mode
        self.stdout_thread = None
        self.stderr_thread = None

    def find_node_executable(self):
        """Find the Node.js executable"""
        print("Searching for Node.js executable...")
        
        try:
            if sys.platform == 'win32':
                result = subprocess.run(['where', 'node'], capture_output=True, text=True)
                if result.returncode == 0:
                    node_path = result.stdout.strip().split('\n')[0]
                    print(f"Found Node.js at: {node_path}")
                    return node_path         
        except Exception as e:
            print(f"Error finding Node.js: {e}")
            
        # Fallback to checking standard paths
        standard_paths = [
            r'C:\Program Files\nodejs\node.exe',
            r'C:\Program Files (x86)\nodejs\node.exe',
        ]
        
        for path in standard_paths:
            if os.path.exists(path):
                print(f"Found Node.js at: {path}")
                return path

        print("Node.js executable not found!")
        return None

    def _read_output(self, pipe, pipe_name):
        """Read output from server process in a separate thread"""
        try:
            for line in iter(pipe.readline, b''):
                try:
                    # Try UTF-8 first, then fallback to other encodings
                    decoded_line = line.decode('utf-8', errors='ignore').strip()
                except UnicodeDecodeError:
                    try:
                        decoded_line = line.decode('cp1252', errors='ignore').strip()
                    except:
                        decoded_line = line.decode('ascii', errors='ignore').strip()
                
                if decoded_line:  # Only print non-empty lines
                    print(f"Server {pipe_name}: {decoded_line}")
                    
                    # Look for server ready indicators
                    if "Server is running on port" in decoded_line or "listening" in decoded_line.lower():
                        print("Server startup message detected!")
                        
        except Exception as e:
            print(f"Error reading {pipe_name}: {e}")

    def wait_for_server_health(self, max_attempts=15, initial_delay=2):
        """Enhanced server health checking with progressive delays"""
        print(f"Starting server health checks (max attempts: {max_attempts})...")
        
        # Give server initial time to start
        print(f"Initial delay: {initial_delay}s")
        time.sleep(initial_delay)
        
        for attempt in range(max_attempts):
            # Check if process is still running
            if self.server_process and self.server_process.poll() is not None:
                print(f"Server process died with return code: {self.server_process.poll()}")
                return False
            
            try:
                print(f"Health check attempt {attempt + 1}/{max_attempts}...")
                response = requests.get(f'http://localhost:{self.server_port}/health', timeout=3)
                if response.status_code == 200:
                    print("Server health check passed!")
                    # Give it a moment to fully stabilize
                    time.sleep(1)
                    return True
                else:
                    print(f"Server responded with status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Health check failed: {e}")
            
            # Progressive delay: start with 1s, then 2s, then 3s, max 4s
            delay = min(4, 1 + (attempt // 3))
            print(f"Waiting {delay}s before next attempt...")
            time.sleep(delay)
        
        print("Server health checks exhausted")
        return False

    def start_server(self):
        try:
            print("Starting server...")
            
            # Get the correct path whether running as exe or script
            if getattr(sys, 'frozen', False):
                # Running as executable
                base_path = os.path.dirname(sys.executable)
                if hasattr(sys, '_MEIPASS'):
                    # When running from PyInstaller bundle
                    server_dir = os.path.join(sys._MEIPASS, 'server')
                else:
                    # When running as standalone exe
                    server_dir = os.path.join(base_path, 'server')
                print(f"Running as executable, base path: {base_path}")
                print(f"Server directory: {server_dir}")
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
                server_dir = os.path.join(base_path, 'server')
                print(f"Running as script, server dir: {server_dir}")
            
            # Verify server directory exists and list contents for debugging
            if not os.path.exists(server_dir):
                print(f"Server directory not found: {server_dir}")
                print(f"Current directory contents: {os.listdir(os.getcwd())}")
                return False
                
            print(f"Server directory contents: {os.listdir(server_dir)}")
            
            # Verify app.js exists
            app_js_path = os.path.join(server_dir, 'app.js')
            if not os.path.exists(app_js_path):
                print(f"app.js not found at: {app_js_path}")
                return False
                
            # Verify node_modules exists
            node_modules_path = os.path.join(server_dir, 'node_modules')
            if not os.path.exists(node_modules_path):
                print(f"node_modules not found at: {node_modules_path}")
                print("Attempting npm install...")
                try:
                    subprocess.run(['npm', 'install'], cwd=server_dir, check=True, timeout=60)
                except subprocess.CalledProcessError as e:
                    print(f"Failed to run npm install: {e}")
                    return False
                except subprocess.TimeoutExpired:
                    print("npm install timed out")
                    return False
            else:
                print(f"node_modules found at: {node_modules_path}")

            # Find node executable
            node_path = self.find_node_executable()
            if not node_path:
                print("Could not find Node.js executable")
                return False

            app_path = os.path.join(server_dir, 'app.js')
            if not os.path.exists(app_path):
                print(f"app.js not found at: {app_path}")
                return False
            else:
                print(f"app.js found at: {app_path}")
            
            # Create startup info to hide console window
            startupinfo = None
            creation_flags = 0
            
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creation_flags = subprocess.CREATE_NO_WINDOW
            
            print(f"Starting Node.js server with command: {node_path} {app_path}")
            print(f"Working directory: {server_dir}")
            
            # Enhanced environment setup for server process
            env = os.environ.copy()
            env['NODE_ENV'] = 'production'  # Ensure production mode
            
            # Start server with enhanced configuration
            self.server_process = subprocess.Popen(
                [node_path, app_path],
                cwd=server_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                creationflags=creation_flags,
                bufsize=0,  # Unbuffered for immediate output
                universal_newlines=False,
                env=env
            )
            
            print(f"Server process started with PID: {self.server_process.pid}")
            
            # Start threads to read output so buffers don't fill up
            self.stdout_thread = threading.Thread(
                target=self._read_output, 
                args=(self.server_process.stdout, "STDOUT"),
                daemon=True
            )
            self.stderr_thread = threading.Thread(
                target=self._read_output, 
                args=(self.server_process.stderr, "STDERR"),
                daemon=True
            )
            
            self.stdout_thread.start()
            self.stderr_thread.start()
            
            # Enhanced server readiness checking
            if not self.wait_for_server_health():
                print("Server failed to become ready")
                # Cleanup failed server process
                if self.server_process and self.server_process.poll() is None:
                    print("Terminating failed server process...")
                    try:
                        self.server_process.terminate()
                        self.server_process.wait(timeout=5)
                    except:
                        self.server_process.kill()
                return False
            
            print("Server started and ready!")
            return True

        except Exception as e:
            print(f"Error starting server: {e}")
            traceback.print_exc()
            return False

    def wait_for_server_health(self):
        """Wait for server to become healthy with enhanced logic"""
        print("Waiting for server to become healthy...")
        start_time = time.time()
        
        # Adaptive timeout based on execution mode
        if getattr(sys, 'frozen', False):
            # Running as exe - give more time
            timeout = self.server_start_timeout
            initial_delay = 3  # Extra initial delay for exe
        else:
            # Running as script
            timeout = 20
            initial_delay = 1
        
        print(f"Using timeout: {timeout}s, initial delay: {initial_delay}s")
        time.sleep(initial_delay)
        
        attempts = 0
        consecutive_failures = 0
        max_consecutive_failures = 3
        
        while time.time() - start_time < timeout:
            attempts += 1
            
            # Check if process is still running
            if self.server_process.poll() is not None:
                print(f"Server process died with return code: {self.server_process.poll()}")
                return False
            
            try:
                print(f"Health check attempt {attempts} (elapsed: {time.time() - start_time:.1f}s)")
                response = requests.get(f'http://localhost:{self.server_port}/health', timeout=4)
                
                if response.status_code == 200:
                    print(f"Server health check passed after {attempts} attempts!")
                    
                    # Do a few more quick checks to ensure stability
                    print("Performing stability verification...")
                    stable = True
                    for i in range(3):
                        time.sleep(0.5)
                        try:
                            verify_response = requests.get(f'http://localhost:{self.server_port}/health', timeout=2)
                            if verify_response.status_code != 200:
                                stable = False
                                break
                        except:
                            stable = False
                            break
                    
                    if stable:
                        print("Server is stable and ready!")
                        return True
                    else:
                        print("Server stability check failed, continuing to wait...")
                        consecutive_failures += 1
                else:
                    print(f"Health check failed with status code: {response.status_code}")
                    consecutive_failures += 1
                    
            except requests.exceptions.RequestException as e:
                print(f"Health check attempt failed: {e}")
                consecutive_failures += 1
                
            # If we have too many consecutive failures, something might be wrong
            if consecutive_failures >= max_consecutive_failures:
                print(f"Too many consecutive failures ({consecutive_failures}), resetting counter")
                consecutive_failures = 0
                # Give a longer pause
                time.sleep(2)
            else:
                # Standard retry delay
                time.sleep(1.5)
        
        print(f"Server health check timed out after {timeout} seconds")
        return False

    def is_server_responsive(self):
        """Check if server is currently responsive"""
        try:
            response = requests.get(f'http://localhost:{self.server_port}/health', timeout=2)
            return response.status_code == 200
        except:
            return False
            
    def stop_server(self):
        """Enhanced server stop with better process cleanup"""
        if self.server_process:
            print(f"Stopping server process (PID: {self.server_process.pid})")
            try:
                # First, try graceful shutdown
                parent = psutil.Process(self.server_process.pid)
                children = parent.children(recursive=True)
                print(f"Found {len(children)} child processes")
                
                # Terminate children first
                for child in children:
                    try:
                        print(f"Terminating child process: {child.pid}")
                        child.terminate()
                    except psutil.NoSuchProcess:
                        pass
                
                # Give children time to terminate gracefully
                gone, alive = psutil.wait_procs(children, timeout=3)
                
                # Force kill any remaining children
                for proc in alive:
                    try:
                        print(f"Force killing child process: {proc.pid}")
                        proc.kill()
                    except psutil.NoSuchProcess:
                        pass
                
                # Now terminate parent
                try:
                    print(f"Terminating parent process: {parent.pid}")
                    parent.terminate()
                    parent.wait(timeout=5)
                except psutil.TimeoutExpired:
                    print(f"Force killing parent process: {parent.pid}")
                    parent.kill()
                except psutil.NoSuchProcess:
                    print("Parent process already terminated")
                
                print("Server stopped successfully")
                
            except psutil.NoSuchProcess:
                print("Server process was already terminated")
            except Exception as e:
                print(f"Error stopping server: {e}")
                traceback.print_exc()
                
            # Clean up threads
            self.server_process = None
            
        else:
            print("No server process to stop")