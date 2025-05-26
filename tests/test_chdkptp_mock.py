#!/usr/bin/env python3
"""
Test file for CHDK camera functionality using mocked chdkptp dependencies.
This allows testing the camera logic without requiring actual hardware or the
problematic chdkptp.py compilation.
"""

import sys
import mock
import pytest
from unittest.mock import MagicMock, patch

# Mock all the problematic imports before importing the CHDK camera module
mock_jpegtran = MagicMock()
mock_jpegtran.JPEGImage = MagicMock()
sys.modules['jpegtran'] = mock_jpegtran

mock_pyexiv2 = MagicMock()
mock_pyexiv2.ImageMetadata = MagicMock()
sys.modules['pyexiv2'] = mock_pyexiv2

# Create comprehensive mock for chdkptp module
class MockDeviceInfo:
    def __init__(self, name, bus, port, vendor_id, product_id, serial_num, device_id):
        self.name = name
        self.bus = bus
        self.port = port
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.serial_num = serial_num
        self.device_id = device_id

class MockPTPError(Exception):
    pass

class MockLuaError(Exception):
    pass

class MockChdkDevice:
    def __init__(self, info):
        self.info = info
        self.is_connected = True
        self.mode = 'record'
        self.lua_execute = MagicMock()
        self.reconnect = MagicMock()
        self.switch_mode = MagicMock()
        self.upload_file = MagicMock()
        self.download_file = MagicMock()
        self.get_frames = MagicMock()
        self.shoot = MagicMock()
        
        # Set up default return values
        self.lua_execute.side_effect = self._lua_execute_handler
        self.download_file.side_effect = self._download_file_handler
        self.get_frames.return_value = iter([b"mock_preview_data"])
        self.shoot.return_value = b"mock_image_data"
        
    def _lua_execute_handler(self, script, do_return=True):
        if "get_buildinfo" in script:
            return {'build_revision': 3000}
        elif "get_zoom_steps" in script:
            return 8
        elif "get_focus" in script:
            return 300
        return None if not do_return else True
        
    def _download_file_handler(self, filename):
        if filename == 'OWN.TXT':
            return "ODD\n"
        return ""

# Mock the chdkptp module structure
mock_chdkptp = MagicMock()
mock_chdkptp.DeviceInfo = MockDeviceInfo
mock_chdkptp.ChdkDevice = MockChdkDevice
mock_chdkptp.list_devices = MagicMock(return_value=[])

# Mock lua submodule
mock_lua = MagicMock()
mock_lua.PTPError = MockPTPError
mock_lua.lupa = MagicMock()
mock_lua.lupa.LuaError = MockLuaError
mock_chdkptp.lua = mock_lua

# Mock util submodule
mock_util = MagicMock()
mock_util.shutter_to_tv96 = lambda x: int(x * 96)
mock_chdkptp.util = mock_util

# Add mocks to sys.modules
sys.modules['chdkptp'] = mock_chdkptp
sys.modules['chdkptp.lua'] = mock_lua
sys.modules['chdkptp.util'] = mock_util

# Now we can import and test the CHDK camera module
import spreads.vendor.confit as confit
import spreadsplug.dev.chdkcamera as chdkcamera


@pytest.fixture
def config():
    config = confit.Configuration('test_chdkcamera')
    tmpl = chdkcamera.CHDKCameraDevice.configuration_template()
    for key, option in tmpl.items():
        if option.selectable:
            config[key] = option.value[0]
        else:
            config[key] = option.value
    # Set some specific test values
    config['zoom_level'] = 3
    config['focus_distance'] = 300
    config['focus_mode'] = 'manual'
    config['sensitivity'] = 100
    config['shutter_speed'] = '1/25'
    config['shoot_raw'] = False
    config['monochrome'] = False
    config['whitebalance'] = 'Auto'
    return config


@pytest.fixture
def mock_device():
    info = MockDeviceInfo('test', 0, 0, 0x1337, 0x1337, 'deadbeef', '1337')
    return MockChdkDevice(info)


@pytest.fixture  
def camera(config, mock_device):
    return chdkcamera.CHDKCameraDevice(config, mock_device)


def test_configuration_template():
    """Test that the configuration template includes expected options."""
    tmpl = chdkcamera.CHDKCameraDevice.configuration_template()
    
    # Check that required configuration options are present
    required_options = [
        'parallel_capture', 'flip_target_pages', 'sensitivity', 
        'shutter_speed', 'zoom_level', 'dpi', 'shoot_raw', 
        'monochrome', 'whitebalance'
    ]
    
    for option in required_options:
        assert option in tmpl, f"Missing configuration option: {option}"
    
    # Check whitebalance is selectable
    assert tmpl['whitebalance'].selectable
    assert 'Auto' in tmpl['whitebalance'].value


def test_yield_devices(config):
    """Test device discovery and instantiation."""
    # Mock device list with different camera types
    infos = [
        MockDeviceInfo('qualfix', 0, 0, 0x4a9, 0x31ef, 'deadbeef', '1337'),  # QualityFix
        MockDeviceInfo('a3300', 0, 1, 0x4a9, 0x3223, 'beefdead', '31337'),   # A3300
        MockDeviceInfo('other', 0, 2, 0x1337, 0x1337, 'feedbeef', '42')      # Regular
    ]
    
    with patch('spreadsplug.dev.chdkcamera.chdkptp.list_devices', return_value=infos):
        devices = list(chdkcamera.CHDKCameraDevice.yield_devices(config))
    
    assert len(devices) == 3
    assert isinstance(devices[0], chdkcamera.QualityFix)
    assert isinstance(devices[1], chdkcamera.A3300)  
    assert isinstance(devices[2], chdkcamera.CHDKCameraDevice)


def test_camera_initialization(camera):
    """Test camera initialization and basic properties."""
    assert camera._chdk_buildnum == 3000
    assert camera._zoom_steps == 8
    assert camera._can_remote is True
    assert camera.target_page == 'odd'  # From mock download_file


def test_camera_connection(camera):
    """Test camera connection status and reconnection."""
    # Test connected state
    camera._device.is_connected = True
    assert camera.connected() is True
    
    # Test reconnection when disconnected
    camera._device.is_connected = False
    assert camera.connected() is True  # Should reconnect successfully
    camera._device.reconnect.assert_called_once()
    
    # Test failed reconnection
    camera._device.is_connected = False
    camera._device.reconnect.side_effect = MockPTPError("Connection failed")
    assert camera.connected() is False


def test_set_target_page(camera):
    """Test setting target page functionality."""
    with patch('spreadsplug.dev.chdkcamera.tempfile.mkstemp') as mock_temp, \
         patch('spreadsplug.dev.chdkcamera.os.write') as mock_write, \
         patch('spreadsplug.dev.chdkcamera.os.remove') as mock_remove:
        
        mock_temp.return_value = (1, '/tmp/test')
        
        camera.set_target_page('even')
        
        # Verify the page was written and uploaded (expect string, not bytes)
        mock_write.assert_called_once_with(1, 'EVEN\n')
        camera._device.upload_file.assert_called_once_with('/tmp/test', 'OWN.TXT')
        assert camera.target_page == 'even'


def test_prepare_capture(camera):
    """Test camera preparation for capture."""
    camera.prepare_capture()
    
    # Verify camera preparation calls were made
    camera._device.lua_execute.assert_called()
    camera._device.switch_mode.assert_called_with('record')


def test_capture_functionality(camera):
    """Test image capture functionality."""
    # Mock path object
    mock_path = MagicMock()
    mock_file = MagicMock()
    mock_path.open.return_value.__enter__.return_value = mock_file
    
    camera._device.mode = 'record'
    camera.target_page = 'odd'
    
    with patch('spreadsplug.dev.chdkcamera.update_exif_orientation') as mock_exif:
        mock_exif.return_value = b"processed_image_data"
        
        camera.capture(mock_path)
        
        # Verify capture was called
        camera._device.shoot.assert_called_once()
        
        # Verify EXIF orientation was processed
        mock_exif.assert_called_once_with(b"mock_image_data", 6)  # 6 for odd page
        
        # Verify file was written
        mock_file.write.assert_called_once_with(b"processed_image_data")


def test_focus_functionality(camera):
    """Test focus acquisition and setting."""
    # Test manual focus
    camera.config['focus_mode'] = 'manual'
    camera.config['focus_distance'] = 250
    
    camera._set_focus()
    
    # Verify focus commands were executed
    assert camera._device.lua_execute.call_count > 0
    
    # Test focus acquisition
    focus_val = camera._acquire_focus()
    assert focus_val == 300  # From mock return value


def test_zoom_functionality(camera):
    """Test zoom level setting."""
    camera._zoom_steps = 8
    camera.config['zoom_level'] = 5
    
    camera._set_zoom()
    
    # Verify zoom command was called
    camera._device.lua_execute.assert_called_with("set_zoom(5)")
    
    # Test invalid zoom level
    camera.config['zoom_level'] = 10  # Exceeds max
    with pytest.raises(ValueError):
        camera._set_zoom()


def test_preview_image(camera):
    """Test preview image acquisition."""
    preview = camera.get_preview_image()
    assert preview == b"mock_preview_data"


def test_error_handling(camera):
    """Test error handling during capture."""
    camera._device.shoot.side_effect = Exception("Capture failed")
    camera._device.mode = 'record'
    
    with pytest.raises(Exception):
        camera.capture(MagicMock())


def test_quality_fix_camera():
    """Test QualityFix camera variant."""
    info = MockDeviceInfo('qualfix', 0, 0, 0x4a9, 0x31ef, 'deadbeef', '1337')
    mock_device = MockChdkDevice(info)
    config = confit.Configuration('test')
    
    camera = chdkcamera.QualityFix(config, mock_device)
        
    assert camera.MAX_RESOLUTION == 0
    assert camera.MAX_QUALITY == 1


def test_a3300_camera():
    """Test A3300 camera variant with RAW shooting limitation."""
    info = MockDeviceInfo('a3300', 0, 0, 0x4a9, 0x3223, 'beefdead', '31337')
    mock_device = MockChdkDevice(info)
    config = confit.Configuration('test')
    config['shoot_raw'] = False
    
    camera = chdkcamera.A3300(config, mock_device)
        
    # A3300 should not support remote shooting without RAW
    assert camera._can_remote is False
    
    # Enable RAW and test again
    config['shoot_raw'] = True
    camera = chdkcamera.A3300(config, mock_device)
        
    assert camera._can_remote is True


def test_whitebalance_modes():
    """Test whitebalance mode constants."""
    wb_modes = chdkcamera.WHITEBALANCE_MODES
    assert 'Auto' in wb_modes
    assert 'Daylight' in wb_modes
    assert 'Tungsten' in wb_modes
    assert wb_modes['Auto'] == 0


def test_show_textbox(camera):
    """Test textbox display functionality."""
    camera.show_textbox("Test\nMessage")
    
    # Verify lua_execute was called to display text
    camera._device.lua_execute.assert_called()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])