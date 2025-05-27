#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/home/pi/Bookshelf/spreads')

from spreads import plugin
from spreads.config import Configuration

def test_plugin_loading():
    """Test if CHDK plugin is properly loaded and accessible."""
    
    # Create a configuration object
    config = Configuration()
    
    print("Available device plugins:")
    devices = plugin.get_devices(config)
    for device in devices:
        print(f"- {device.__class__.__name__} from {device.__class__.__module__}")
    
    print("\nTesting CHDK plugin specifically:")
    try:
        from spreadsplug.dev.chdkcamera import CHDKCameraDevice
        print(f"✓ Successfully imported CHDKCameraDevice")
        
        # Check if CHDK devices are in the available devices
        chdk_devices = [d for d in devices if isinstance(d, CHDKCameraDevice)]
        print(f"✓ Found {len(chdk_devices)} CHDK camera devices")
        
        if chdk_devices:
            for i, device in enumerate(chdk_devices):
                print(f"  Device {i+1}: {device}")
                
    except ImportError as e:
        print(f"✗ Failed to import CHDKCameraDevice: {e}")

if __name__ == "__main__":
    test_plugin_loading()