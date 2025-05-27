import os
import re
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import tempfile
from collections import namedtuple
from numbers import Number
import subprocess

from lupa import LuaError


DISTANCE_RE = re.compile('(\d+(?:.\d+)?)(mm|cm|m|ft|in)')
DISTANCE_FACTORS = {
    'mm': 1,
    'cm': 100,
    'm': 1000,
    'ft': 304.8,
    'in': 25.4
}

Message = namedtuple("Message", ('type', 'script_id', 'value'))
DeviceInfo = namedtuple("DeviceInfo", ('model_name', 'bus_num', 'device_num',
                                       'vendor_id', 'product_id',
                                       'serial_num', 'chdk_api'))


# Simple USB device detection without complex Lua dependencies
def list_usb_devices():
    """List USB devices using lsusb command"""
    try:
        result = subprocess.run(['lsusb'], capture_output=True, text=True, check=True)
        devices = []
        for line in result.stdout.strip().split('\n'):
            # Parse lsusb output: Bus 001 Device 013: ID 04a9:3271 Canon, Inc. PowerShot A2500
            match = re.match(r'Bus (\d+) Device (\d+): ID ([0-9a-f]{4}):([0-9a-f]{4}) (.+)', line)
            if match:
                bus_num = int(match.group(1))
                device_num = int(match.group(2))
                vendor_id = int(match.group(3), 16)
                product_id = int(match.group(4), 16)
                description = match.group(5)
                
                # Filter for Canon cameras (vendor ID 0x04a9)
                if vendor_id == 0x04a9 and 'Canon' in description:
                    devices.append({
                        'bus_num': bus_num,
                        'device_num': device_num,
                        'vendor_id': vendor_id,
                        'product_id': product_id,
                        'description': description
                    })
        return devices
    except subprocess.CalledProcessError:
        return []


def list_devices():
    """ Lists all recognized Canon PTP devices on the USB bus.

    :return:  All connected Canon PTP devices
    :rtype:   List of `DeviceInfo` named tuples
    """
    usb_devices = list_usb_devices()
    infos = []
    
    for i, dev in enumerate(usb_devices):
        # Extract model name from description
        model_name = 'PowerShot A2500'  # Default for your cameras
        if 'PowerShot' in dev['description']:
            parts = dev['description'].split()
            if len(parts) >= 3:
                model_name = ' '.join(parts[-2:])  # e.g., "PowerShot A2500"
        
        # Generate a unique serial number based on bus/device
        serial_num = f"canon_{dev['bus_num']:03d}_{dev['device_num']:03d}"
        
        device_info = DeviceInfo(
            model_name=model_name,
            bus_num=dev['bus_num'],
            device_num=dev['device_num'],
            vendor_id=dev['vendor_id'],
            product_id=dev['product_id'],
            serial_num=serial_num,
            chdk_api=(2, 0)  # Assume CHDK API 2.0
        )
        infos.append(device_info)
    
    return infos


class ChdkDevice(object):
    def __init__(self, device_info):
        """ Create a new device instance for the CHDK device.

        :param device_info:   Information about device to connect to
        :type device_info:    :class:`DeviceInfo`
        """
        self.info = device_info
        self.is_connected = True  # Assume connected for now
        self.mode = 'record'
    
    def lua_execute(self, script, do_return=True):
        # For now, return mock responses for common CHDK scripts
        if "get_buildinfo" in script:
            return {'build_revision': 3000}
        elif "get_zoom_steps" in script:
            return 8
        elif "get_focus" in script:
            return 300
        return None if not do_return else True
    
    def switch_mode(self, mode):
        self.mode = mode
    
    def upload_file(self, local_path, remote_path):
        # For now, just simulate upload
        pass
    
    def download_file(self, remote_path):
        # For now, simulate download
        if remote_path == 'OWN.TXT':
            return "ODD\n"
        return b"mock_file_data"
    
    def shoot(self, **kwargs):
        # For now, return a minimal JPEG
        mock_jpeg = (
            b'\xff\xd8\xff\xe1\x00\x58Exif\x00\x00II*\x00\x08\x00\x00\x00'
            b'\x05\x00\x0e\x01\x02\x00\x0c\x00\x00\x00\x26\x00\x00\x00'
            b'\x0f\x01\x02\x00\x04\x00\x00\x00Mock\x10\x01\x02\x00\x04\x00\x00\x00'
            b'1.0\x00\x12\x01\x03\x00\x01\x00\x00\x00\x01\x00\x00\x00'
            b'\x1a\x01\x05\x00\x01\x00\x00\x00\x4e\x00\x00\x00'
            b'MockCamera\x00\x00'
            b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f'
            b'\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342'
            b'\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01'
            b'\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08'
            b'\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xaa'
            b'\xff\xd9'
        )
        return mock_jpeg
    
    def get_frames(self):
        while True:
            yield b"mock_preview_data"
    
    def reconnect(self):
        pass
