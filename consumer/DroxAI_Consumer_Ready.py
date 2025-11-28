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

from pathlib import Path

def check_and_install_requirements():
    """Check and install required Python modules with better error handling"""
    logging.info("ðŸ” Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logging.info("âŒ Python 3.8+ required. Please upgrade Python.")
        input("Press Enter to exit...")
        return False
    
    logging.info(f"âœ… Python {sys.version.split()[0]} detected")
    
    # Check required modules with comprehensive error handling
    required_modules = ['websockets', 'aiohttp', 'numpy']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            logging.info(f"âœ… {module} available")
        except Exception as e:
            missing_modules.append(module)
            logging.info(f"âŒ {module} missing ({str(e)})")
    
    if missing_modules:
        logging.info(f"\nðŸ“¦ Installing missing modules: {', '.join(missing_modules)}")
        try:
            # Try installing with pip
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_modules)
            logging.info("âœ… Modules installed successfully")
            
            # Verify installation worked
            for module in missing_modules:
                try:
                    __import__(module)
                    logging.info(f"âœ… {module} verified installed")
                except Exception:
                    logging.info(f"âš ï¸  {module} installation may have failed")
        except subprocess.CalledProcessError as e:
            logging.info("âŒ Failed to install required modules automatically")
            logging.info(f"Error: {e}")
            logging.info("\nðŸ”§ Manual installation required:")
            logging.info("Please run: pip install websockets aiohttp numpy")
            logging.info("\nAlternatively, try installing them one by one:")
            for module in missing_modules:
                logging.info(f"  pip install {module}")
            input("\nPress Enter to exit...")
            return False
    
    return True

def start_droxai():
    """Start DroxAI system with consumer-friendly error handling"""
    logging.info("\nðŸš€ Starting DroxAI...")
    
    try:
        # Start the main CHIMERA system
        chimera_process = subprocess.Popen([
            sys.executable, "chimera_autarch.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        logging.info("âœ… CHIMERA system started")
        
        # Wait for system to initialize
        logging.info("â³ Waiting for system to initialize...")
        time.sleep(5)
        
        # Check if process is still running
        if chimera_process.poll() is not None:
            stdout, stderr = chimera_process.communicate()
            logging.info("âŒ CHIMERA system failed to start")
            if stderr:
                logging.info(f"Error: {stderr.decode()}")
            if stdout:
                logging.info(f"Output: {stdout.decode()}")
            return False
        
        # Open web interface
        logging.info("ðŸŒ Opening web interface...")
        try:
            webbrowser.open("http://127.0.0.1: 3000")
        except Exception as e:
            logging.info(f"âš ï¸  Could not open browser automatically: {e}")
            logging.info("   Please manually open http://127.0.0.1: 3000 in your browser")
        
        logging.info("\n" + "="*60)
        logging.info("ðŸŽ‰ DroxAI is now running!")
        logging.info("="*60)
        logging.info("ðŸ“Š Web Dashboard: http://127.0.0.1: 3000")
        logging.info("ðŸ”Œ WebSocket API: ws://127.0.0.1: 3000")
        logging.info("\nâš ï¸  Keep this window open to keep DroxAI running")
        logging.info("ðŸ”´ Close this window or press Ctrl+C to stop")
        logging.info("="*60)
        
        # Monitor process with user feedback
        try:
            chimera_process.wait()
        except KeyboardInterrupt:
            logging.info("\nðŸ›‘ Shutting down DroxAI...")
            chimera_process.terminate()
            chimera_process.wait()
            logging.info("âœ… DroxAI stopped gracefully")
        
        return True
        
    except FileNotFoundError:
        logging.info("âŒ Could not find chimera_autarch.py")
        logging.info("Please make sure all files are in the same folder")
        input("Press Enter to exit...")
        return False
    except Exception as e:
        logging.info(f"âŒ Failed to start DroxAI: {e}")
        logging.info("\nðŸ”§ Troubleshooting:")
        logging.info("1. Make sure all files are in the same folder")
        logging.info("2. Check that Python 3.8+ is installed")
        logging.info("3. Verify no antivirus is blocking the application")
        logging.info("4. Try running as administrator on Windows")
        input("\nPress Enter to exit...")
        return False

def main():
    """Main consumer entry point"""
    logging.info("=" * 60)
    logging.info("    ðŸš€ DroxAI - Advanced AI Orchestration System")
    logging.info("    Consumer Edition v1.0.0")
    logging.info("=" * 60)
    logging.info()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check requirements and install if needed
    if not check_and_install_requirements():
        return
    
    # Start DroxAI
    start_droxai()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("\nðŸ‘‹ Goodbye!")
    except Exception as e:
        logging.info(f"âŒ Unexpected error: {e}")
        logging.info("Please contact support with this error message.")
        input("Press Enter to exit...")

