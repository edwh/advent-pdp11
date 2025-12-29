#!/usr/bin/env python3
"""
Room Data Converter for Advent MUD
===================================

Converts text-format room exports (roomfil.fil) to binary RMS format
expected by ADVENT.B2S on RSTS/E.

Binary record format (512 bytes per room):
    Bytes 0:       Room number verification (1 byte)
    Bytes 1-16:    Exits as N####S####E####W#### (16 bytes)
    Bytes 17-99:   People/monsters (83 bytes)
    Bytes 100-199: Objects (100 bytes)
    Bytes 200-511: Description + special cases (312 bytes)

Written by Claude (an AI), December 2025.
"""

import re
import struct
import sys
from pathlib import Path
from typing import Optional


# Record field sizes (from ADVENT.B2S FIELD statement)
ROOM_SIZE = 1
EXIT_SIZE = 16
PEOPLE_SIZE = 83
OBJECT_SIZE = 100
DESC_SIZE = 312
RECORD_SIZE = 512  # Total


class Room:
    """Represents a single room in the dungeon."""

    def __init__(self, number: int):
        self.number = number
        self.exits = ""      # N####S####E####W####
        self.people = ""     # Monsters/NPCs separated by /
        self.objects = ""    # Objects separated by /
        self.description = ""  # Room description
        self.special = ""    # Special cases (puzzles, etc.)

    def to_binary(self) -> bytes:
        """Convert room to 512-byte binary record."""
        record = bytearray(RECORD_SIZE)

        # Byte 0: Room number (modulo 256 for single byte)
        record[0] = self.number % 256

        # Bytes 1-16: Exits
        exits = self.format_exits().encode('ascii', errors='replace')[:EXIT_SIZE]
        record[1:1+len(exits)] = exits

        # Bytes 17-99: People
        people = self.people.encode('ascii', errors='replace')[:PEOPLE_SIZE]
        record[17:17+len(people)] = people

        # Bytes 100-199: Objects
        objects = self.objects.encode('ascii', errors='replace')[:OBJECT_SIZE]
        record[100:100+len(objects)] = objects

        # Bytes 200-511: Description + special cases
        desc = (self.description + self.special).encode('ascii', errors='replace')[:DESC_SIZE]
        record[200:200+len(desc)] = desc

        return bytes(record)

    def format_exits(self) -> str:
        """Format exits as N####S####E####W####"""
        # Parse exits like "N740W700" or "N11E15S10W8"
        exits_dict = {'N': '0000', 'S': '0000', 'E': '0000', 'W': '0000'}

        # Find all direction+number pairs
        pattern = r'([NSEW])(\d+)'
        for match in re.finditer(pattern, self.exits):
            direction = match.group(1)
            room_num = match.group(2)
            exits_dict[direction] = room_num.zfill(4)[:4]

        return f"N{exits_dict['N']}S{exits_dict['S']}E{exits_dict['E']}W{exits_dict['W']}"


def parse_room_file(filepath: Path) -> dict[int, Room]:
    """Parse a text room file and return dictionary of rooms."""
    rooms = {}
    current_room: Optional[Room] = None
    state = 'header'  # header, people, objects, description
    desc_lines = []

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.rstrip('\r\n')

            # Check for room header (number,exits)
            match = re.match(r'^(\d+),(.*)$', line)
            if match:
                # Save previous room
                if current_room is not None:
                    current_room.description = '\n'.join(desc_lines)
                    # Check if last line is special cases
                    if desc_lines and desc_lines[-1].startswith('/'):
                        current_room.special = desc_lines[-1]
                        current_room.description = '\n'.join(desc_lines[:-1])
                    rooms[current_room.number] = current_room

                # Start new room
                room_num = int(match.group(1))
                current_room = Room(room_num)
                current_room.exits = match.group(2)
                state = 'people'
                desc_lines = []
                continue

            if current_room is None:
                continue  # Skip lines before first room

            # Handle different states
            if state == 'people':
                # People line (may be empty)
                current_room.people = line
                state = 'objects'
            elif state == 'objects':
                # Objects line (may be empty)
                current_room.objects = line
                state = 'description'
            elif state == 'description':
                # Description lines (may span multiple lines)
                desc_lines.append(line)

    # Save last room
    if current_room is not None:
        current_room.description = '\n'.join(desc_lines)
        if desc_lines and desc_lines[-1].startswith('/'):
            current_room.special = desc_lines[-1]
            current_room.description = '\n'.join(desc_lines[:-1])
        rooms[current_room.number] = current_room

    return rooms


def write_binary_file(rooms: dict[int, Room], filepath: Path, max_rooms: int = 2000):
    """Write rooms to binary file in RMS format."""
    with open(filepath, 'wb') as f:
        for room_num in range(1, max_rooms + 1):
            if room_num in rooms:
                record = rooms[room_num].to_binary()
            else:
                # Empty room - just room number verification byte
                record = bytearray(RECORD_SIZE)
                record[0] = room_num % 256
            f.write(record)

    print(f"Wrote {max_rooms} room records ({max_rooms * RECORD_SIZE} bytes)")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: convert_rooms.py <input.fil> [output.dta]")
        print()
        print("Converts text room exports to binary ADVENT.DTA format")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.with_suffix('.dta')

    print(f"Reading {input_file}...")
    rooms = parse_room_file(input_file)
    print(f"Found {len(rooms)} rooms")

    # Find highest room number
    max_room = max(rooms.keys()) if rooms else 0
    print(f"Highest room number: {max_room}")

    # Show some sample rooms
    print("\nSample rooms:")
    for room_num in sorted(rooms.keys())[:3]:
        room = rooms[room_num]
        print(f"  Room {room_num}: exits={room.exits}, people={room.people[:30]}...")

    print(f"\nWriting {output_file}...")
    write_binary_file(rooms, output_file, max(max_room, 2000))

    print("Done!")


if __name__ == '__main__':
    main()
