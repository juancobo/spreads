#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import logging

# Add the current directory to Python path so we can import spreads modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spreads.config import Configuration
import spreads.plugin

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_chdkptp_simple():
    """Simple test to verify chdkptp integration works"""
    print("=== Testing CHDKCamera Plugin Integration ===")
    
    try:
        # Initialize configuration
        config = Configuration()
        print("✓ Configuration initialized successfully")
        
        # Set the driver to chdkcamera
        config['driver'] = 'chdkcamera'
        print("✓ Driver set to chdkcamera")
        
        # Get available plugins
        plugins = spreads.plugin.get_plugins()
        print(f"✓ Available plugins: {list(plugins.keys())}")
        
        # Check if chdkcamera plugin is available
        if 'chdkcamera' in plugins:
            print("✓ CHDKCamera plugin found!")
            plugin_class = plugins['chdkcamera']
            print(f"✓ Plugin class: {plugin_class}")
            
            # Try to get devices (this will test our chdkptp integration)
            try:
                devices = plugin_class.yield_devices(config)
                device_list = list(devices)
                print(f"✓ Found {len(device_list)} device(s)")
                
                for i, device in enumerate(device_list):
                    print(f"  Device {i+1}: {device}")
                    print(f"    Type: {type(device)}")
                    if hasattr(device, '_device'):
                        print(f"    Underlying device: {device._device}")
                
                # Test basic device properties
                if device_list:
                    device = device_list[0]
                    print(f"\n=== Testing Device Properties ===")
                    print(f"Device target page: {device.target_page}")
                    
                    # Test if device has the required methods
                    required_methods = ['prepare_capture', 'finish_capture', 'capture']
                    for method in required_methods:
                        if hasattr(device, method):
                            print(f"✓ Device has {method} method")
                        else:
                            print(f"✗ Device missing {method} method")
                
            except Exception as e:
                print(f"✗ Error testing devices: {e}")
                import traceback
                traceback.print_exc()
        
        else:
            print("✗ CHDKCamera plugin not found in available plugins")
            print("Available plugins:", list(plugins.keys()))
        
    except Exception as e:
        print(f"✗ Error during configuration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chdkptp_simple()