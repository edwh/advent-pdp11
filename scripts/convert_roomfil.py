#!/usr/bin/env python3
"""
Convert roomfil.fil text format to binary ADVENT.DTA format.

The text format is:
    <room_num>,<exits>
    <objects/monsters>
    <description>

Where exits are like: N740W700 meaning North->740, West->700

The binary format is:
    FIELD #3%, 1% AS ROOM$, 16% AS EX$, 83% AS PEOPLE$, 100% AS OBJECT$, 312% AS DESC$

That's 512 bytes per room, 2000 rooms total = 1,024,000 bytes.
"""

import re
import struct
import sys
import os

def parse_exits(exit_str):
    """Parse exit string like 'N740W700' into dict of direction->room_num."""
    exits = {}
    # Match direction letter followed by digits
    pattern = r'([NSEW])(\d+)'
    for match in re.finditer(pattern, exit_str):
        direction = match.group(1)
        room_num = int(match.group(2))
        exits[direction] = room_num
    return exits

def create_binary_exits(exits_dict):
    """Create 16-byte binary exit string.

    Format: 4 bytes per direction (N, S, E, W)
    - Byte 0: Direction letter if exit exists, else space (0x20)
    - Bytes 1-2: Room number as 16-bit little-endian
    - Byte 3: Padding (0x00)
    """
    result = bytearray(16)
    directions = ['N', 'S', 'E', 'W']

    for idx, d in enumerate(directions):
        pos = idx * 4
        room = exits_dict.get(d, 0)

        if room > 0:
            result[pos] = ord(d)
            result[pos+1] = room & 0xFF
            result[pos+2] = (room >> 8) & 0xFF
            result[pos+3] = 0
        else:
            result[pos] = ord(' ')
            result[pos+1] = 0
            result[pos+2] = 0
            result[pos+3] = 0

    return bytes(result)

def parse_roomfil(filepath):
    """Parse roomfil.fil and return dict of room_num -> room_data."""
    rooms = {}

    with open(filepath, 'r', encoding='latin-1') as f:
        content = f.read()

    # Skip first line (pip roomut.fil)
    lines = content.split('\n')
    if lines[0].startswith('pip'):
        lines = lines[1:]

    i = 0
    current_room = None
    current_data = {
        'exits': {},
        'people': '',
        'objects': '',
        'description': ''
    }

    while i < len(lines):
        line = lines[i].rstrip()

        # Check if this is a room header line (starts with number,)
        room_match = re.match(r'^(\d+),(.*)$', line)
        if room_match:
            # Save previous room if exists
            if current_room is not None:
                rooms[current_room] = current_data

            # Start new room
            current_room = int(room_match.group(1))
            exit_str = room_match.group(2)
            current_data = {
                'exits': parse_exits(exit_str),
                'people': '',
                'objects': '',
                'description': ''
            }
        elif current_room is not None:
            # Categorize this line
            if line.startswith('!') or line.startswith('*') or line.startswith('#'):
                # Monster or corpse line
                if current_data['people']:
                    current_data['people'] += ' '
                current_data['people'] += line
            elif line.startswith('./') or line.startswith('/'):
                # Script line or end marker - skip
                pass
            elif any(c in line for c in ['$', '~']) and not current_data['description']:
                # Object line (contains price markers)
                if current_data['objects']:
                    current_data['objects'] += '/'
                current_data['objects'] += line
            elif line.strip():
                # Description line
                if current_data['description']:
                    current_data['description'] += ' '
                current_data['description'] += line.strip()

        i += 1

    # Don't forget the last room
    if current_room is not None:
        rooms[current_room] = current_data

    return rooms

def create_binary_dta(rooms, output_path, total_rooms=2000):
    """Create binary ADVENT.DTA file.

    Format per room (512 bytes):
    - 1 byte: Room marker (0xC0 if room exists, 0x00 if empty)
    - 16 bytes: Exits
    - 83 bytes: People/monsters
    - 100 bytes: Objects
    - 312 bytes: Description
    """
    ROOM_SIZE = 512

    with open(output_path, 'wb') as f:
        for room_num in range(1, total_rooms + 1):
            if room_num in rooms:
                room = rooms[room_num]

                # Room marker
                room_marker = b'\xC0'

                # Exits (16 bytes)
                exits_bin = create_binary_exits(room['exits'])

                # People (83 bytes, space-padded)
                people = room['people'][:83].ljust(83)

                # Objects (100 bytes, space-padded)
                objects = room['objects'][:100].ljust(100)

                # Description (312 bytes, space-padded)
                desc = room['description'][:312].ljust(312)

                # Write room
                record = room_marker + exits_bin + people.encode('latin-1') + objects.encode('latin-1') + desc.encode('latin-1')

                # Ensure exactly 512 bytes
                if len(record) < ROOM_SIZE:
                    record += b'\x00' * (ROOM_SIZE - len(record))

                f.write(record[:ROOM_SIZE])
            else:
                # Empty room slot
                f.write(b'\x00' * ROOM_SIZE)

    print(f"Created {output_path} ({total_rooms * ROOM_SIZE} bytes)")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')

    roomfil_path = os.path.join(data_dir, 'roomfil.fil')
    output_path = os.path.join(script_dir, '..', 'build', 'data', 'ADVENT.DTA')

    if len(sys.argv) > 1:
        roomfil_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]

    print(f"Reading {roomfil_path}...")
    rooms = parse_roomfil(roomfil_path)
    print(f"Parsed {len(rooms)} rooms")

    # Show some stats
    rooms_with_exits = sum(1 for r in rooms.values() if r['exits'])
    print(f"Rooms with exits: {rooms_with_exits}")

    # Show room 449 for verification
    if 449 in rooms:
        r = rooms[449]
        print(f"\nRoom 449:")
        print(f"  Exits: {r['exits']}")
        print(f"  People: {r['people'][:50]}...")
        print(f"  Objects: {r['objects'][:50]}...")
        print(f"  Description: {r['description'][:80]}...")

    print(f"\nCreating {output_path}...")
    create_binary_dta(rooms, output_path)

    # Verify the output
    print("\nVerifying output...")
    with open(output_path, 'rb') as f:
        f.seek(448 * 512)  # Room 449
        data = f.read(512)

        print(f"Room 449 marker: 0x{data[0]:02x}")
        exits = data[1:17]
        print(f"Room 449 exits: {exits.hex()}")

        for idx, d in enumerate(['N', 'S', 'E', 'W']):
            pos = idx * 4
            dir_byte = chr(exits[pos]) if exits[pos] > 31 else '?'
            room = struct.unpack('<H', exits[pos+1:pos+3])[0]
            if room > 0:
                print(f"  {d}: {dir_byte} -> room {room}")
            else:
                print(f"  {d}: (no exit)")

if __name__ == '__main__':
    main()
