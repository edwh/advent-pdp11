#!/usr/bin/env python3
"""
Analyze ADVENT.DTA room data to find connectivity issues and generate map data.

Room Record Format (512 bytes per room):
  Byte 0: Room validation (should equal room_number % 256)
  Bytes 1-16: Exits (4 bytes per direction: N=1-4, E=5-8, S=9-12, W=13-16)
    - Byte 0: Direction letter ('N','E','S','W') or null if no exit
    - Bytes 1-2: Destination room number as 16-bit little-endian (0 = exit dungeon)
    - Byte 3: unused
  Bytes 17-99: People/NPCs
  Bytes 100-199: Objects
  Bytes 200-511: Description (ends at '$')
"""

import sys
import json
from collections import defaultdict
from pathlib import Path

RECORD_SIZE = 512
DIRECTIONS = ['N', 'E', 'S', 'W']
OPPOSITE = {'N': 'S', 'E': 'W', 'S': 'N', 'W': 'E'}
DIR_NAMES = {'N': 'North', 'E': 'East', 'S': 'South', 'W': 'West'}

class Room:
    def __init__(self, number, data):
        self.number = number
        # Validation byte stores (room_number - 1) % 256
        expected_validation = (number - 1) % 256
        self.valid = (data[0] == expected_validation) if number > 0 else False
        self.exits = {}
        self.description = ""
        self.objects = ""
        self.people = ""

        if self.valid:
            # Parse exits (bytes 1-16, 4 bytes per direction)
            for i, direction in enumerate(DIRECTIONS):
                offset = 1 + (i * 4)
                dir_char = chr(data[offset]) if data[offset] else ''
                # 16-bit little-endian destination at offset+1 and offset+2
                dest = data[offset + 1] + (data[offset + 2] << 8)

                if dir_char in DIRECTIONS:
                    self.exits[direction] = dest  # 0 = exit dungeon, >0 = room number

            # Parse description (bytes 200-511)
            desc_bytes = data[200:512]
            desc = ""
            for b in desc_bytes:
                if b == ord('$') or b == 0:
                    break
                if 32 <= b < 127:
                    desc += chr(b)
                elif b == 13:
                    desc += '\n'
            self.description = desc.strip()

            # Parse objects (bytes 100-199)
            obj_bytes = data[100:200]
            self.objects = bytes(obj_bytes).decode('ascii', errors='ignore').rstrip('\x00')

            # Parse people (bytes 17-99)
            ppl_bytes = data[17:100]
            self.people = bytes(ppl_bytes).decode('ascii', errors='ignore').rstrip('\x00')

def load_rooms(filepath):
    """Load all rooms from ADVENT.DTA

    BASIC-PLUS uses 1-indexed records, so:
    - Record 1 (offset 0) = room 1 data, validation byte = 0
    - Record 2 (offset 512) = room 2 data, validation byte = 1
    - Record N = room N data, validation byte = N-1
    """
    rooms = {}
    with open(filepath, 'rb') as f:
        data = f.read()

    num_records = len(data) // RECORD_SIZE
    print(f"File size: {len(data)} bytes, {num_records} records")

    for i in range(num_records):
        offset = i * RECORD_SIZE
        record = data[offset:offset + RECORD_SIZE]
        room_number = i + 1  # BASIC records are 1-indexed
        room = Room(room_number, record)
        if room.valid:
            rooms[room_number] = room

    return rooms

def analyze_connectivity(rooms, start_room=2):
    """Analyze room connectivity from starting room"""

    # Find all reachable rooms from start
    reachable = set()
    to_visit = [start_room]

    while to_visit:
        current = to_visit.pop(0)
        if current in reachable or current not in rooms:
            continue
        reachable.add(current)

        for dest in rooms[current].exits.values():
            if dest > 0 and dest not in reachable:
                to_visit.append(dest)

    # Find unreachable rooms
    all_rooms = set(rooms.keys())
    unreachable = all_rooms - reachable

    # Find dead ends (rooms with only one exit or no working exits)
    dead_ends = []
    no_exits = []
    for num, room in rooms.items():
        working_exits = [d for d, dest in room.exits.items()
                        if dest > 0 and dest in rooms]
        if len(working_exits) == 0:
            no_exits.append(num)
        elif len(working_exits) == 1:
            dead_ends.append(num)

    # Find one-way connections (exit exists but no return path)
    one_way = []
    for num, room in rooms.items():
        for direction, dest in room.exits.items():
            if dest > 0 and dest in rooms:
                opposite_dir = OPPOSITE[direction]
                dest_room = rooms[dest]
                if opposite_dir not in dest_room.exits or dest_room.exits[opposite_dir] != num:
                    one_way.append((num, direction, dest))

    # Find broken exits (point to non-existent rooms)
    broken = []
    for num, room in rooms.items():
        for direction, dest in room.exits.items():
            if dest > 0 and dest not in rooms:
                broken.append((num, direction, dest))

    return {
        'reachable': sorted(reachable),
        'unreachable': sorted(unreachable),
        'dead_ends': sorted(dead_ends),
        'no_exits': sorted(no_exits),
        'one_way': one_way,
        'broken': broken
    }

def generate_map_json(rooms, analysis):
    """Generate JSON data for web map visualization"""

    map_data = {
        'start_room': 2,
        'rooms': {},
        'connections': [],
        'issues': {
            'unreachable': analysis['unreachable'],
            'dead_ends': analysis['dead_ends'],
            'no_exits': analysis['no_exits'],
            'one_way': [(src, dir, dest) for src, dir, dest in analysis['one_way']],
            'broken': [(src, dir, dest) for src, dir, dest in analysis['broken']]
        }
    }

    for num, room in rooms.items():
        # Clean description for display
        desc = room.description[:200] + '...' if len(room.description) > 200 else room.description

        map_data['rooms'][str(num)] = {
            'number': num,
            'description': desc,
            'exits': room.exits,
            'reachable': num in analysis['reachable'],
            'has_objects': bool(room.objects.strip()),
            'has_npcs': bool(room.people.strip() and room.people[0] in '*#')
        }

        # Add connections (bidirectional as single entries)
        for direction, dest in room.exits.items():
            if dest > 0:
                # Only add if source < dest to avoid duplicates
                if num < dest:
                    map_data['connections'].append({
                        'from': num,
                        'to': dest,
                        'direction': direction,
                        'bidirectional': (dest in rooms and
                                         OPPOSITE[direction] in rooms[dest].exits and
                                         rooms[dest].exits[OPPOSITE[direction]] == num)
                    })

    return map_data

def print_room_details(rooms, room_nums):
    """Print detailed info about specific rooms"""
    for num in room_nums[:10]:  # Limit to first 10
        if num in rooms:
            room = rooms[num]
            print(f"\n=== Room {num} ===")
            print(f"Description: {room.description[:100]}...")
            print(f"Exits: {room.exits}")
            if room.objects:
                print(f"Objects: {room.objects[:50]}")
            if room.people:
                print(f"People: {room.people[:50]}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Analyze ADVENT.DTA room data')
    parser.add_argument('datafile', nargs='?', default='build/data/ADVENT.DTA',
                       help='Path to ADVENT.DTA')
    parser.add_argument('--json', '-j', help='Output JSON map file')
    parser.add_argument('--start', '-s', type=int, default=2,
                       help='Starting room number (default: 2)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed room info')
    args = parser.parse_args()

    # Find data file
    filepath = Path(args.datafile)
    if not filepath.exists():
        # Try relative to script location
        script_dir = Path(__file__).parent.parent
        filepath = script_dir / args.datafile

    if not filepath.exists():
        print(f"Error: Cannot find {args.datafile}")
        sys.exit(1)

    print(f"Loading rooms from {filepath}")
    rooms = load_rooms(filepath)
    print(f"Found {len(rooms)} valid rooms")

    print(f"\nAnalyzing connectivity from room {args.start}...")
    analysis = analyze_connectivity(rooms, args.start)

    print(f"\n=== Connectivity Analysis ===")
    print(f"Reachable rooms: {len(analysis['reachable'])}")
    print(f"Unreachable rooms: {len(analysis['unreachable'])}")
    print(f"Dead ends (1 exit): {len(analysis['dead_ends'])}")
    print(f"No exits: {len(analysis['no_exits'])}")
    print(f"One-way connections: {len(analysis['one_way'])}")
    print(f"Broken exits: {len(analysis['broken'])}")

    if analysis['no_exits']:
        print(f"\nRooms with NO exits: {analysis['no_exits'][:20]}")
        if args.verbose:
            print_room_details(rooms, analysis['no_exits'])

    if analysis['unreachable']:
        print(f"\nUnreachable rooms (first 20): {analysis['unreachable'][:20]}")
        if args.verbose:
            print_room_details(rooms, analysis['unreachable'])

    if analysis['broken']:
        print(f"\nBroken exits (first 10): {analysis['broken'][:10]}")

    if analysis['one_way'][:10]:
        print(f"\nOne-way exits (first 10):")
        for src, dir, dest in analysis['one_way'][:10]:
            print(f"  Room {src} -> {dir} -> Room {dest} (no return)")

    # Check starting room specifically
    start = args.start
    if start in rooms:
        print(f"\n=== Starting Room {start} ===")
        room = rooms[start]
        print(f"Description: {room.description[:150]}")
        print(f"Exits: {room.exits}")
        if not room.exits:
            print("WARNING: Starting room has NO exits! Players are trapped.")
    else:
        print(f"\nWARNING: Starting room {start} is invalid!")

    # Generate JSON if requested
    if args.json:
        map_data = generate_map_json(rooms, analysis)
        output_path = Path(args.json)
        with open(output_path, 'w') as f:
            json.dump(map_data, f, indent=2)
        print(f"\nMap data written to {output_path}")

if __name__ == '__main__':
    main()
