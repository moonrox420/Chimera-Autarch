#!/usr/bin/env python3
"""
Test script to verify DroxAI Consumer functionality
"""
import sys
import os
from pathlib import Path

def test_basic_imports():
    """Test basic Python functionality"""
    logging.info("ðŸ” Testing basic functionality...")
    
    try:

        from pathlib import Path
        logging.info("âœ… Basic imports successful")
        return True
    except Exception as e:
        logging.info(f"âŒ Basic imports failed: {e}")
        return False

def test_droxai_dependencies():
    """Test if DroxAI requirements can be found/installed"""
    logging.info("\nðŸ“¦ Testing DroxAI dependencies...")
    
    modules = ['websockets', 'aiohttp', 'numpy']
    available = []
    missing = []
    
    for module in modules:
        try:
            __import__(module)
            available.append(module)
            logging.info(f"âœ… {module} available")
        except Exception:
            missing.append(module)
            logging.info(f"âŒ {module} missing")
    
    if missing:
        logging.info(f"\nðŸ“¥ To install missing modules, run:")
        logging.info(f"pip install {' '.join(missing)}")
        logging.info("\nOr use the DroxAI Consumer - it will auto-install them!")
        return False
    else:
        logging.info("\nðŸŽ‰ All dependencies available!")
        return True

def test_chimera_availability():
    """Test if CHIMERA system is available"""
    logging.info("\nðŸš€ Testing CHIMERA availability...")
    
    chimera_path = Path("chimera_autarch.py")
    if chimera_path.exists():
        logging.info("âœ… CHIMERA system found")
        return True
    else:
        logging.info("âŒ CHIMERA system not found")
        logging.info("Please ensure chimera_autarch.py is in the same folder")
        return False

def main():
    """Run all tests"""
    logging.info("="*50)
    logging.info("    DroxAI Consumer - Test Suite")
    logging.info("="*50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    results = []
    results.append(test_basic_imports())
    results.append(test_droxai_dependencies())
    results.append(test_chimera_availability())
    
    logging.info("\n" + "="*50)
    if all(results):
        logging.info("ðŸŽ‰ ALL TESTS PASSED!")
        logging.info("DroxAI Consumer should work perfectly!")
    else:
        logging.info("âš ï¸  Some tests failed")
        logging.info("The DroxAI Consumer will try to fix issues automatically")
    logging.info("="*50)

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")

