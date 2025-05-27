#!/usr/bin/env python3
"""
Debug script for CHDKPTP integration
"""
import os
import sys
import logging
import importlib.util

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('chdkptp_debug')

def check_environment():
    """Check the Python environment and system paths"""
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    # Check if chdkptp is installed globally
    try:
        import chdkptp as global_chdkptp
        logger.info(f"Found global chdkptp.py at: {global_chdkptp.__file__}")
    except ImportError:
        logger.info("No global chdkptp.py found")
    
    # Check the vendor module
    vendor_path = os.path.join(os.path.dirname(__file__), 'spreads', 'vendor', 'chdkptp')
    logger.info(f"Checking vendor path: {vendor_path}")
    if os.path.exists(vendor_path):
        logger.info(f"Vendor chdkptp directory exists: {os.listdir(vendor_path)}")
    else:
        logger.warning(f"Vendor chdkptp directory not found: {vendor_path}")

def setup_chdkptp_path():
    """Set up the CHDKPTP_PATH environment variable"""
    # Check if we have the library zip file
    lib_zip = os.path.join(os.path.dirname(__file__), 'chdkptp-Linux-aarch64-libs-20250228.zip')
    if os.path.exists(lib_zip):
        logger.info(f"Found CHDKPTP libraries zip: {lib_zip}")
        
        # Extract the libraries if needed
        import zipfile
        import tempfile
        
        extract_dir = os.path.join(tempfile.gettempdir(), 'chdkptp_libs')
        if not os.path.exists(extract_dir):
            os.makedirs(extract_dir)
            
        logger.info(f"Extracting libraries to: {extract_dir}")
        with zipfile.ZipFile(lib_zip, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Set library path
        lib_path = extract_dir
        if os.environ.get('LD_LIBRARY_PATH'):
            os.environ['LD_LIBRARY_PATH'] = f"{lib_path}:{os.environ['LD_LIBRARY_PATH']}"
        else:
            os.environ['LD_LIBRARY_PATH'] = lib_path
        logger.info(f"Set LD_LIBRARY_PATH to: {os.environ['LD_LIBRARY_PATH']}")
    
    # Find the chdkptp folder (either from vendor or from site-packages)
    chdkptp_path = None
    
    # First check the vendored version
    vendor_chdkptp = os.path.join(os.path.dirname(__file__), 'spreads', 'vendor', 'chdkptp', 'chdkptp')
    if os.path.exists(vendor_chdkptp):
        chdkptp_path = vendor_chdkptp
        logger.info(f"Using vendored chdkptp at: {chdkptp_path}")
    else:
        # Try to find the installed package
        try:
            import chdkptp
            chdkptp_path = os.path.dirname(chdkptp.__file__)
            logger.info(f"Using installed chdkptp at: {chdkptp_path}")
        except ImportError:
            logger.error("Could not find chdkptp module! Please install it or update the vendor copy.")
            return False
    
    # Set the CHDKPTP_PATH environment variable
    os.environ['CHDKPTP_PATH'] = chdkptp_path
    logger.info(f"Set CHDKPTP_PATH to: {os.environ['CHDKPTP_PATH']}")
    return True

def patch_chdkptp_lua():
    """Patch the chdkptp Lua module to fix path issues"""
    try:
        # First patch the global module if it exists
        try:
            import chdkptp.lua as lua_module
            lua_file = lua_module.__file__
        except ImportError:
            # Try the vendor module
            vendor_path = os.path.join(os.path.dirname(__file__), 'spreads', 'vendor', 'chdkptp')
            lua_file = os.path.join(vendor_path, 'chdkptp', 'lua.py')
            if not os.path.exists(lua_file):
                logger.error(f"Could not find lua.py at {lua_file}")
                return False
        
        logger.info(f"Patching lua module at: {lua_file}")
        
        # Read the file
        with open(lua_file, 'r') as f:
            content = f.read()
        
        # Check if patching is needed
        if "os.environ.get('CHDKPTP_PATH', '')" not in content:
            # Replace the problematic line with path detection
            content = content.replace(
                "CHDKPTP_PATH = ''",
                "CHDKPTP_PATH = os.environ.get('CHDKPTP_PATH', '')"
            )
            
            # Backup original file
            backup_file = lua_file + '.backup'
            if not os.path.exists(backup_file):
                with open(backup_file, 'w') as f:
                    f.write(content)
                    
            # Write patched file
            with open(lua_file, 'w') as f:
                f.write(content)
            
            logger.info(f"Patched {lua_file} to use environment variable CHDKPTP_PATH")
        else:
            logger.info(f"File {lua_file} already patched")
            
        return True
    except Exception as e:
        logger.exception(f"Error patching lua module: {e}")
        return False

def fix_init_files():
    """Ensure all __init__.py files are properly set up"""
    vendor_path = os.path.join(os.path.dirname(__file__), 'spreads', 'vendor', 'chdkptp')
    chdkptp_init = os.path.join(vendor_path, '__init__.py')
    
    # Check if the init file needs to be updated
    with open(chdkptp_init, 'r') as f:
        content = f.read()
    
    if "import os" not in content:
        logger.info("Updating chdkptp/__init__.py")
        with open(chdkptp_init, 'w') as f:
            f.write("""# Local copy of chdkptp.py from forked repository
import os
import sys

# Set the CHDKPTP_PATH environment variable to help locate Lua scripts
current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(current_dir, 'chdkptp')):
    os.environ['CHDKPTP_PATH'] = os.path.join(current_dir, 'chdkptp')

try:
    from .chdkptp import *  # noqa
except ImportError as e:
    print(f"Error importing chdkptp: {e}")
    # If there are no modules yet, don't fail on import
    # The update_chdkptp.py script will need to be run first
    pass
""")
        logger.info("Updated chdkptp/__init__.py successfully")
    else:
        logger.info("chdkptp/__init__.py already updated")
    
    return True

def test_chdkptp_import():
    """Try to import chdkptp and list devices"""
    logger.info("Testing chdkptp import...")
    try:
        # Try importing from vendor first
        import sys
        sys.path.insert(0, os.path.dirname(__file__))
        
        try:
            from spreads.vendor.chdkptp import chdkptp
            logger.info("Successfully imported from spreads.vendor.chdkptp")
        except ImportError as e:
            logger.warning(f"Could not import from vendor: {e}")
            import chdkptp
            logger.info("Successfully imported from system chdkptp")
        
        logger.info("Listing CHDK devices...")
        devices = list(chdkptp.list_devices())
        logger.info(f"Found {len(devices)} devices")
        for i, device in enumerate(devices):
            logger.info(f"Device {i+1}:")
            logger.info(f"  - Bus: {device.bus}")
            logger.info(f"  - Device address: {device.device_address}")
            logger.info(f"  - Vendor ID: 0x{device.vendor_id:04x}")
            logger.info(f"  - Product ID: 0x{device.product_id:04x}")
            logger.info(f"  - Serial number: {device.serial_num}")
        
        return True
    except Exception as e:
        logger.exception(f"Error testing chdkptp: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting CHDKPTP debugging...")
    check_environment()
    
    if setup_chdkptp_path() and patch_chdkptp_lua() and fix_init_files():
        logger.info("Setup completed successfully.")
        if test_chdkptp_import():
            logger.info("CHDKPTP is working correctly!")
        else:
            logger.error("CHDKPTP import test failed.")
    else:
        logger.error("Setup failed.")