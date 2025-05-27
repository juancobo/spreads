#!/usr/bin/env python3
"""
Debug script to test direct chdkptp command-line integration.
This will help diagnose issues with the command syntax and parameter formatting.
"""
import os
import re
import subprocess
import time
import sys

def test_chdkptp_command(cmd, description):
    """Test a specific chdkptp command and print the result"""
    print(f"\n--- Testing: {description} ---")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print(f"SUCCESS (exit code: {result.returncode})")
            if result.stdout.strip():
                print(f"Output:\n{result.stdout.strip()}")
            else:
                print("No output")
        else:
            print(f"FAILED (exit code: {result.returncode})")
            if result.stderr.strip():
                print(f"Error:\n{result.stderr.strip()}")
            if result.stdout.strip():
                print(f"Output:\n{result.stdout.strip()}")
    except subprocess.TimeoutExpired:
        print("TIMEOUT: Command took too long to execute")
    except Exception as e:
        print(f"ERROR: {str(e)}")

def main():
    print("=== CHDKPTP Command-line Integration Test ===")
    
    # Test if chdkptp is installed and accessible
    print("\nChecking chdkptp installation...")
    try:
        result = subprocess.run(['which', 'chdkptp'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"chdkptp found at: {result.stdout.strip()}")
        else:
            print("chdkptp not found in PATH")
    except Exception as e:
        print(f"Error checking chdkptp: {e}")
    
    # Test basic chdkptp help
    test_chdkptp_command(['chdkptp', '-h'], "Basic help")
    
    # Test version information
    test_chdkptp_command(['chdkptp', '-e=ver'], "Version info")
    
    # Test alternate command formats
    print("\n--- Testing different command syntax formats ---")
    
    # Format 1: -e=command
    test_chdkptp_command(['chdkptp', '-e=list'], "Format 1: -e=list")
    
    # Format 2: -ecommand (no space or quotes)
    test_chdkptp_command(['chdkptp', '-elist'], "Format 2: -elist")
    
    # Format 3: -e command (with space)
    test_chdkptp_command(['chdkptp', '-e', 'list'], "Format 3: -e list")
    
    # Test connecting and executing multiple commands in one line
    test_chdkptp_command(['chdkptp', '-c', '-elist'], "Connect then list")
    
    # Test connecting to a specific camera index and running commands
    test_chdkptp_command(['chdkptp', '-c', '-e', 'list'], "Connect and list devices")
    test_chdkptp_command(['chdkptp', '-c', '-e', 'connect'], "Connect default")
    test_chdkptp_command(['chdkptp', '-c', '-e', 'connect 0'], "Connect to device 0")
    
    # Test Lua script execution
    test_chdkptp_command(['chdkptp', '-c', '-e', 'connect', '-e', 'lua print("Hello")'], 
                         "Connect and run Lua script")
    
    # Test mode switching
    test_chdkptp_command(['chdkptp', '-c', '-e', 'connect', '-e', 'rec'], "Switch to record mode")
    
    # Test camera information
    test_chdkptp_command(['chdkptp', '-c', '-e', 'connect', '-e', 'lua return get_buildinfo()'], 
                         "Get build info")
    
    # Test taking photo and saving to file
    photo_path = os.path.join(os.getcwd(), 'test_photo.jpg')
    test_chdkptp_command(['chdkptp', '-c', '-e', 'connect', '-e', 'rec', '-e', f'remoteshoot {photo_path}'], 
                         "Take photo with remoteshoot command")
    
    if os.path.exists('test_photo.jpg'):
        print("\nPhoto was successfully captured and saved to test_photo.jpg")
    else:
        print("\nNo photo was saved")

if __name__ == "__main__":
    main()