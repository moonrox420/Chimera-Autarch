#!/usr/bin/env python3
"""
DroxAI Consumer - Single Double-Click Launcher
Handles all complexity behind the scenes
"""
import subprocess
import sys
import os
import webbrowser
import time
import threading
from pathlib import Path

def check_requirements():
    """Check if Python and required modules are available"""
    print("ðŸ” Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("âŒ Python 3.8+ required. Please upgrade Python.")
        input("Press Enter to exit...")
        return False
    
    print(f"âœ… Python {sys.version.split()[0]} detected")
    
    # Check required modules
    required_modules = ['websockets', 'aiohttp', 'numpy']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"âœ… {module} available")
        except ImportError:
            missing_modules.append(module)
            print(f"âŒ {module} missing")
    
    if missing_modules:
        print(f"\nðŸ“¦ Installing missing modules: {', '.join(missing_modules)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_modules)
            print("âœ… Modules installed successfully")
        except subprocess.CalledProcessError:
            print("âŒ Failed to install required modules")
            print("Please run: pip install websockets aiohttp numpy")
            input("Press Enter to exit...")
            return False
    
    return True

def start_droxai():
    """Start DroxAI system with consumer-friendly error handling"""
    print("\nðŸš€ Starting DroxAI...")
    
    try:
        # Start the main CHIMERA system
        chimera_process = subprocess.Popen([
            sys.executable, "chimera_autarch.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("âœ… CHIMERA system started")
        
        # Wait for system to initialize
        print("â³ Waiting for system to initialize...")
        time.sleep(5)
        
        # Check if process is still running
        if chimera_process.poll() is not None:
            stdout, stderr = chimera_process.communicate()
            print("âŒ CHIMERA system failed to start")
            if stderr:
                print(f"Error: {stderr.decode()}")
            return False
        
        # Open web interface
        print("ðŸŒ Opening web interface...")
        webbrowser.open("http://localhost:3000")
        
        print("\n" + "="*60)
        print("ðŸŽ‰ DroxAI is now running!")
        print("="*60)
        print("ðŸ“Š Web Dashboard: http://localhost:3000")
        print("ðŸ”Œ WebSocket API: ws://localhost:3001")
        print("\nâš ï¸  Keep this window open to keep DroxAI running")
        print("ðŸ”´ Close this window or press Ctrl+C to stop")
        print("="*60)
        
        # Monitor process
        try:
            chimera_process.wait()
        except KeyboardInterrupt:
            print("\nðŸ›‘ Shutting down DroxAI...")
            chimera_process.terminate()
            chimera_process.wait()
        
        return True
        
    except Exception as e:
        print(f"âŒ Failed to start DroxAI: {e}")
        print("\nðŸ”§ Troubleshooting:")
        print("1. Make sure all files are in the same folder")
        print("2. Check that Python 3.8+ is installed")
        print("3. Verify no antivirus is blocking the application")
        input("\nPress Enter to exit...")
        return False

def main():
    """Main consumer entry point"""
    print("=" * 60)
    print("    ðŸš€ DroxAI - Advanced AI Orchestration System")
    print("    Consumer Edition v1.0.0")
    print("=" * 60)
    print()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check requirements
    if not check_requirements():
        return
    
    # Start DroxAI
    start_droxai()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"âŒ Unexpected error: {e}")
        print("Please contact support with this error message.")
        input("Press Enter to exit...")

