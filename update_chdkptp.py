#!/usr/bin/env python3
"""
Script to copy the forked chdkptp.py repository into spreads/vendor/chdkptp
"""
import os
import shutil
import sys

def copy_chdkptp():
    """Copy the chdkptp.py repository into the vendor directory."""
    source_path = '/home/pi/Bookshelf/chdkptp.py'
    target_path = os.path.join(os.path.dirname(__file__), 
                              'spreads', 'vendor', 'chdkptp')
    
    if not os.path.exists(source_path):
        print(f"Error: Source path {source_path} does not exist!")
        return 1
    
    # Clean the target directory
    if os.path.exists(target_path):
        print(f"Cleaning existing directory: {target_path}")
        for item in os.listdir(target_path):
            item_path = os.path.join(target_path, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.unlink(item_path)
    else:
        os.makedirs(target_path)
    
    # Copy all Python files from the source directory
    print(f"Copying files from {source_path} to {target_path}")
    for item in os.listdir(source_path):
        source_item = os.path.join(source_path, item)
        target_item = os.path.join(target_path, item)
        
        # Skip directories like .git, __pycache__, etc.
        if os.path.isdir(source_item) and item in ('.git', '__pycache__', '.github'):
            continue
        
        # Copy file or directory
        if os.path.isdir(source_item):
            shutil.copytree(source_item, target_item)
        else:
            shutil.copy2(source_item, target_item)
    
    # Create or update __init__.py in the target directory
    init_path = os.path.join(target_path, '__init__.py')
    if not os.path.exists(init_path):
        with open(init_path, 'w') as f:
            f.write('# Local copy of chdkptp.py from forked repository\n')
            f.write('from .chdkptp import *  # noqa\n')
    
    print("CHDKPTP.py has been successfully copied to spreads/vendor/chdkptp")
    return 0

if __name__ == '__main__':
    sys.exit(copy_chdkptp())