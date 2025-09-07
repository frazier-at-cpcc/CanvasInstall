#!/usr/bin/env python3
"""
Canvas LMS Installer Entry Point
Run this script to start the Canvas LMS installation process
"""

import sys
import os
import subprocess

def check_and_install_dependencies():
    """Check and install required dependencies"""
    # Check if running with sudo
    if os.geteuid() != 0 and not os.environ.get('SUDO_USER'):
        print("ERROR: This installer requires sudo privileges.")
        print("Please run with: sudo python3 install_canvas.py")
        sys.exit(1)
    
    # Configure Git globally to prevent ownership issues
    try:
        print("Configuring Git for installation...")
        subprocess.run(["git", "config", "--global", "--add", "safe.directory", "*"],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "config", "--global", "user.name", "Canvas Installer"],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "config", "--global", "user.email", "installer@canvas.local"],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass  # Git config is not critical for dependency installation
    
    # Try to import rich
    try:
        import rich
        return True
    except ImportError:
        pass
    
    print("Installing required dependencies...")
    
    # Try different methods to install rich
    methods = [
        # Method 1: Install pip and then rich
        ["apt", "update"],
        ["apt", "install", "-y", "python3-pip"],
        [sys.executable, "-m", "pip", "install", "rich"],
        
        # Method 2: Use apt package directly (fallback)
        ["apt", "install", "-y", "python3-rich"]
    ]
    
    # Try pip installation first
    try:
        print("Updating package lists...")
        subprocess.check_call(["apt", "update"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("Installing pip...")
        subprocess.check_call(["apt", "install", "-y", "python3-pip"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("Installing Rich library...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Test import
        import rich
        print("Dependencies installed successfully!")
        return True
        
    except (subprocess.CalledProcessError, ImportError):
        print("Pip installation failed, trying apt package...")
        try:
            subprocess.check_call(["apt", "install", "-y", "python3-rich"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Test import
            import rich
            print("Dependencies installed successfully!")
            return True
        except (subprocess.CalledProcessError, ImportError):
            print("\nERROR: Failed to install Rich library automatically.")
            print("\nPlease install manually with one of these commands:")
            print("  sudo apt update && sudo apt install -y python3-pip && pip3 install rich")
            print("  sudo apt install -y python3-rich")
            print("\nThen run the installer again.")
            sys.exit(1)

def main():
    """Main entry point"""
    # Check and install dependencies first
    check_and_install_dependencies()
    
    # Add the canvas_installer package to the path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import and run the main installer
    try:
        from canvas_installer.installer import main as installer_main
        installer_main()
    except ImportError as e:
        print(f"ERROR: Failed to import installer: {e}")
        print("Please ensure all files are present and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()