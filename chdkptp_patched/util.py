import os
import math


# Simple implementations that don't require Lua runtime
def iso_to_av96(iso):
    # Convert ISO to AV96 format
    # This is a simplified version that should work for most cases
    return int(math.log2(iso / 100.0) * 96)


def shutter_to_tv96(shutter_speed):
    # Convert shutter speed to TV96 format
    # TV96 = -log2(shutter_speed) * 96
    if shutter_speed <= 0:
        return 0
    return int(-math.log2(shutter_speed) * 96)


def aperture_to_av96(aperture):
    # Convert aperture (f-number) to AV96 format
    # AV96 = log2(f-number^2) * 96
    if aperture <= 0:
        return 0
    return int(math.log2(aperture * aperture) * 96)


def apex_to_apex96(apex):
    x = apex * 96
    return round(x) if x > 0 else -round(x)


def to_camerapath(path):
    if not path.lower().startswith("a/"):
        path = os.path.join("A", path)
    return path
