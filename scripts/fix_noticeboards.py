#!/usr/bin/env python3
"""
Fix noticeboard data to ensure rooms mentioning noticeboards have working ones.

This script:
1. Reads the original BOARD.NTC from tape
2. Identifies rooms that mention "noticeboard" in descriptions but aren't indexed
3. Adds those rooms to the INDEX array
4. Extends the BOARD data with entries for the new rooms

File format:
- First 1024 bytes: INDEX%(0-511) - array of 512 2-byte little-endian room numbers
- Remaining bytes: BOARD$(0-N) - 512 bytes per indexed room for noticeboard text
"""

import struct
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Rooms that explicitly mention "noticeboard" or "notice board" in descriptions
# These were found by searching ADVENT.DTA for noticeboard text
NOTICEBOARD_ROOMS = [
    33,   # "a neat notice board" - floor and a neat notice on the wall
    40,   # "There is a notice board here" - large corridor
    89,   # "There is a notice board on one wall" - roughly hewn arch to east
    350,  # "crude wooden noticeboard" - webbed footprints in mud
    399,  # "There is a noticeboard on the wall" - Trolls' Den entrance
    443,  # "a large noticeboard on one wall" - ornate office
    # Note: Can't easily verify these without full room search, but from original list:
    # 944  - trek noticeboard
    # 1549 - SHRINE, SHOP, BELL, NOTICEBOARD
    # 1592 - a room containing a NOTICEBOARD
]

# Additional rooms to add (from original investigation)
ADDITIONAL_ROOMS = [944, 1549, 1592]


def fix_board_ntc():
    """Fix BOARD.NTC to include all noticeboard rooms."""

    tape_path = BASE_DIR / "tape" / "BOARD.NTC"
    output_path = BASE_DIR / "build" / "data" / "BOARD.NTC"

    if not tape_path.exists():
        print(f"ERROR: {tape_path} not found!")
        return False

    # Read original file
    with open(tape_path, 'rb') as f:
        data = bytearray(f.read())

    print(f"Read {len(data)} bytes from {tape_path}")

    # Parse INDEX array (first 1024 bytes = 512 x 2-byte integers)
    indexed_rooms = {}
    index_count = 0
    for i in range(512):
        offset = i * 2
        room_num = struct.unpack('<H', data[offset:offset+2])[0]
        if room_num > 0 and room_num < 2000:
            indexed_rooms[room_num] = i
            index_count = i + 1
            print(f"  INDEX[{i}] = Room {room_num}")

    print(f"\nCurrently indexed rooms ({index_count} total): {sorted(indexed_rooms.keys())}")

    # Calculate current BOARD data size
    board_offset_start = 1024  # INDEX is 512 x 2 = 1024 bytes
    board_entry_size = 512
    current_board_entries = (len(data) - board_offset_start) // board_entry_size
    print(f"Current BOARD entries: {current_board_entries}")

    # Combine room lists and find missing ones
    all_rooms_to_add = set(NOTICEBOARD_ROOMS + ADDITIONAL_ROOMS)
    missing_rooms = sorted(all_rooms_to_add - set(indexed_rooms.keys()))

    if not missing_rooms:
        print("\nAll noticeboard rooms already indexed!")
    else:
        print(f"\nMissing rooms to add: {missing_rooms}")

    # Add missing rooms
    for room in missing_rooms:
        # Find next empty INDEX slot
        next_slot = index_count

        # Write room number to INDEX
        idx_offset = next_slot * 2
        data[idx_offset:idx_offset+2] = struct.pack('<H', room)

        # Create new BOARD entry with default message
        default_msg = f"[Room {room} Noticeboard]\n\nNo messages have been posted here yet.\n"
        board_bytes = default_msg.encode('ascii', errors='replace')
        board_bytes = board_bytes[:board_entry_size].ljust(board_entry_size, b'\x00')

        # Extend data with new BOARD entry
        data.extend(board_bytes)

        indexed_rooms[room] = next_slot
        index_count += 1

        print(f"  Added room {room} at INDEX[{next_slot}]")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write fixed file
    with open(output_path, 'wb') as f:
        f.write(data)

    print(f"\nWrote fixed BOARD.NTC ({len(data)} bytes) to {output_path}")
    print(f"Final indexed rooms ({len(indexed_rooms)}): {sorted(indexed_rooms.keys())}")

    return True


if __name__ == '__main__':
    fix_board_ntc()
