#!/usr/bin/env python3
"""
Test script to verify base_events.py works correctly
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_basic_functionality():
    """Test basic functionality without hanging"""
    try:
        logging.info("🧪 Testing base_events.py basic functionality...")
        
        # Import the module

        logging.info("✅ Import successful")
        
        # Create a simple test
        system = BaseEventSystem()
        logging.info("✅ BaseEventSystem created")
        
        # Test event generation (synchronous part)
        event_data = system._generate_event_data(EventType.NODE_REGISTERED)
        logging.info(f"✅ Event data generated: {event_data}")
        
        # Test broker creation
        broker = system.broker
        stats = broker.get_stats()
        logging.info(f"✅ Broker stats: {stats}")
        
        logging.info("\n🎉 All tests passed! base_events.py is working correctly.")
        return True
        
    except Exception as e:
        logging.info(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_basic_functionality())
    sys.exit(0 if success else 1)
