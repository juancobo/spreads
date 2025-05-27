#!/usr/bin/env python3
"""
Debug script to test the complete chdkptp integration with our patched implementation.
This will test the complete workflow: detection, connection, mode switching, and shooting.
"""
import os
import sys
import time
from chdkptp_patched import list_devices, ChdkDevice

def main():
    print("=== CHDKPTP Integration Test ===")
    
    # Step 1: List all available devices
    print("\nDetecting cameras...")
    devices = list_devices()
    
    if not devices:
        print("No cameras detected! Make sure your cameras are connected and powered on.")
        return
    
    print(f"Found {len(devices)} camera(s):")
    for i, device in enumerate(devices):
        print(f"  {i+1}. {device.model_name} (ID: {device.device_num}, Serial: {device.serial_num})")
    
    # Step 2: Connect to the first camera
    print("\nConnecting to first camera...")
    device_info = devices[0]
    
    try:
        camera = ChdkDevice(device_info)
        
        if camera.is_connected:
            print(f"Successfully connected to {device_info.model_name}")
        else:
            print("Failed to connect to camera")
            return
        
        # Step 3: Get camera information
        print("\nGetting camera information...")
        build_info = camera.lua_execute("return get_buildinfo()")
        print(f"Camera build info: {build_info}")
        
        mode = camera.lua_execute("return get_mode()")
        print(f"Current camera mode: {mode} ({'record' if mode == 1 else 'playback'})")
        
        # Step 4: Switch camera mode
        print("\nSwitching camera to record mode...")
        camera.switch_mode('record')
        time.sleep(2)
        
        mode = camera.lua_execute("return get_mode()")
        print(f"New camera mode: {mode} ({'record' if mode == 1 else 'playback'})")
        
        # Step 5: Take a photo
        print("\nTaking photo...")
        image_data = camera.shoot()
        
        if image_data:
            # Save the image
            output_path = os.path.join(os.getcwd(), "test_capture_new.jpg")
            with open(output_path, "wb") as f:
                f.write(image_data)
            
            print(f"Photo saved to {output_path} ({len(image_data)} bytes)")
            
            # Check if it's a real image or our mock image fallback
            is_mock = len(image_data) < 1000  # Mock image is very small
            if is_mock:
                print("WARNING: This appears to be a mock image, not a real camera capture.")
        else:
            print("Failed to capture photo")
        
        # Step 6: Switch back to playback mode
        print("\nSwitching back to playback mode...")
        camera.switch_mode('playback')
        time.sleep(1)
        
        print("\nTest complete!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()