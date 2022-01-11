import struct

def bitMapper(value, button_type, button_number):
    return struct.pack("hBB", value, button_type, button_number)