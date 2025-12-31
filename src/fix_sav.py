#!/usr/bin/env python3
"""
Fix SAV file header - set stack to 0 (let system decide) or to a safe value
"""
import sys
import struct

def fix_sav(infile, outfile):
    with open(infile, 'rb') as f:
        data = bytearray(f.read())
    
    # Read current header values (little-endian)
    begin = struct.unpack_from('<H', data, 0x20)[0]
    stack = struct.unpack_from('<H', data, 0x22)[0]
    jsw = struct.unpack_from('<H', data, 0x24)[0]
    high = struct.unpack_from('<H', data, 0x28)[0]
    
    print(f"Current: BEGIN=0x{begin:04x} ({begin}) STACK=0x{stack:04x} ({stack}) JSW=0x{jsw:04x} HIGH=0x{high:04x} ({high})")
    
    # Set stack to 0 - let the RT-11 RTS decide
    # Or set to high value like 0xE000 (56K area) if that's needed
    new_stack = 0x0000  # Let system manage stack
    
    struct.pack_into('<H', data, 0x22, new_stack)
    
    print(f"Fixed: BEGIN=0x{begin:04x} STACK=0x{new_stack:04x} JSW=0x{jsw:04x} HIGH=0x{high:04x}")
    
    with open(outfile, 'wb') as f:
        f.write(data)
    
    print(f"Wrote to {outfile}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: fix_sav.py input.sav output.sav")
        sys.exit(1)
    fix_sav(sys.argv[1], sys.argv[2])
