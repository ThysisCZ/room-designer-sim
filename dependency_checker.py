#!/usr/bin/env python3
"""
Automatic Dependency Checker for Room Designer Simulator
Checks for required dependencies and guides users through installation.
"""

import sys
import os
import subprocess
import tkinter as tk
from tkinter import ttk

class DependencyChecker:
    def __init__(self):
        self.missing_deps = []
        self.fix_attempts = {}
        
    def check_nodejs(self):
        """Check if Node.js is installed and working"""
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"[OK] Node.js found: {version}")
                return True, version
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            pass
        
        # Check common installation paths
        common_paths = [
            r'C:\Program Files\nodejs\node.exe',
            r'C:\Program Files (x86)\nodejs\node.exe',
            os.path.expanduser(r'~\AppData\Roaming\npm\node.exe')
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                try:
                    result = subprocess.run([path, '--version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        print(f"[OK] Node.js found at: {path} ({version})")
                        return True, version
                except:
                    continue
        
        print("[ERROR] Node.js not found")
        return False, None
    
    def check_visual_cpp(self):
        """Check for Visual C++ Redistributables"""
        vc_files = {
            'vcruntime140.dll': 'Visual C++ 2015-2022 Redistributable (x64)',
            'msvcp140.dll': 'Visual C++ 2015-2022 Redistributable (x64)',
            'ucrtbase.dll': 'Universal C Runtime'
        }
        
        system32 = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'System32')
        syswow64 = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'SysWOW64')
        
        missing_files = []
        
        for dll, description in vc_files.items():
            system32_path = os.path.join(system32, dll)
            syswow64_path = os.path.join(syswow64, dll)
            
            if not (os.path.exists(system32_path) or os.path.exists(syswow64_path)):
                missing_files.append(f"{dll} - {description}")
        
        if missing_files:
            print("[ERROR] Missing Visual C++ Redistributables:")
            for file in missing_files:
                print(f"  - {file}")
            print("  Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe")
            return False, missing_files
        else:
            print("[OK] Visual C++ Redistributables found")
            return True, []
    
    def check_python_packages(self):
        """Check if required Python packages are available (only when running from source)"""
        # Only check Python packages when running from source, not from executable
        if getattr(sys, 'frozen', False):
            print("[OK] Running as executable - Python packages are bundled")
            return True, []
        
        required_packages = ['pygame', 'requests', 'psutil']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"[OK] {package} is available")
            except ImportError:
                print(f"[ERROR] {package} is missing")
                missing_packages.append(package)
        
        return len(missing_packages) == 0, missing_packages
    
    def run_all_checks(self):
        """Run all dependency checks"""
        print("Running dependency checks...")
        
        # Check Node.js
        node_ok, node_version = self.check_nodejs()
        if not node_ok:
            self.missing_deps.append({
                'name': 'Node.js',
                'description': 'Required for the game server',
                'download_url': 'https://nodejs.org/',
                'install_instructions': 'Download and install the LTS version from nodejs.org'
            })
        
        # Check Visual C++ Redistributables
        vcpp_ok, missing_vcpp = self.check_visual_cpp()
        if not vcpp_ok:
            self.missing_deps.append({
                'name': 'Visual C++ Redistributables',
                'description': 'Required for Python packages to work properly',
                'download_url': 'https://aka.ms/vs/17/release/vc_redist.x64.exe',
                'install_instructions': 'Download and run the installer as Administrator'
            })
        
        # Check Python packages (only when running from source)
        packages_ok, missing_packages = self.check_python_packages()
        if not packages_ok:
            self.missing_deps.append({
                'name': 'Python Packages',
                'description': f'Missing packages: {", ".join(missing_packages)}',
                'download_url': None,
                'install_instructions': f'Run: pip install {" ".join(missing_packages)}'
            })
        
        return len(self.missing_deps) == 0
    
    def show_dependency_dialog(self):
        """Show a user-friendly dialog for missing dependencies"""
        if not self.missing_deps:
            return True
        
        root = tk.Tk()
        root.title("Missing Dependencies - Room Designer Simulator")
        root.geometry("600x500")
        root.resizable(False, False)
        
        # Make window stay on top
        root.attributes('-topmost', True)
        root.focus_force()
        
        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Icon
        exe_dir = os.path.dirname(sys.executable)
        icon = os.path.join(exe_dir, 'assets', 'icon.ico')
        root.iconbitmap(icon)
        
        # Title
        title_label = ttk.Label(main_frame, text="Missing Dependencies", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_text = ("The following components are required to run Room Designer Simulator:\n\n"
                    "Please install the missing components and restart the game.")
        desc_label = ttk.Label(main_frame, text=desc_text, wraplength=550)
        desc_label.pack(pady=(0, 20))
        
        # Missing dependencies list
        deps_frame = ttk.LabelFrame(main_frame, text="Missing Components", padding="10")
        deps_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        for i, dep in enumerate(self.missing_deps):
            dep_frame = ttk.Frame(deps_frame)
            dep_frame.pack(fill=tk.X, pady=5)
            
            # Dependency name
            name_label = ttk.Label(dep_frame, text=f"• {dep['name']}", 
                                 font=('Arial', 10, 'bold'))
            name_label.pack(anchor=tk.W)
            
            # Description
            desc_label = ttk.Label(dep_frame, text=dep['description'], 
                                 font=('Arial', 10, 'bold'), wraplength=500)
            desc_label.pack(anchor=tk.W, padx=(20, 0))
            
            # Download url
            download_label = ttk.Label(dep_frame, text=dep['download_url'], 
                                    font=('Arial', 10, 'bold'))
            download_label.pack(anchor=tk.W, padx=(20, 0))
        
        # Center the window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
        # Start the dialog
        root.mainloop()
        
        return False
    
    def auto_install_attempt(self):
        """Attempt to automatically install some dependencies"""
        print("Attempting automatic installation...")
        
        # Try to install Python packages automatically
        try:
            import pip
            missing_packages = []
            
            for package in ['pygame', 'requests', 'psutil']:
                try:
                    __import__(package)
                except ImportError:
                    missing_packages.append(package)
            
            if missing_packages:
                print(f"Installing missing Python packages: {missing_packages}")
                pip.main(['install'] + missing_packages)
                print("Python packages installed successfully")
                return True
        except Exception as e:
            print(f"Failed to auto-install Python packages: {e}")
        
        return False

def check_dependencies():
    """Main function to check dependencies and show dialog if needed"""
    print("Room Designer Simulator - Dependency Check")
    print("=" * 50)
    
    checker = DependencyChecker()
    
    # Run all checks
    all_good = checker.run_all_checks()
    
    if all_good:
        print("[OK] All dependencies satisfied!")
        return True
    else:
        print(f"[ERROR] Found {len(checker.missing_deps)} missing dependencies")
        
        # Try automatic installation first
        if checker.auto_install_attempt():
            # Re-check after auto-install
            all_good = checker.run_all_checks()
            if all_good:
                print("[OK] All dependencies satisfied after auto-install!")
                return True
        
        # Show user dialog
        return checker.show_dependency_dialog()

if __name__ == "__main__":
    # Test the dependency checker
    success = check_dependencies()
    if success:
        print("Dependencies check passed!")
    else:
        print("Dependencies check failed!")