#!/usr/bin/env python3
"""
Reconstruct missing exits in ADVENT.DTA to make all rooms reachable.

This script:
1. Analyzes room connectivity
2. Adds bidirectional exits where one-way connections exist
3. Connects isolated room clusters to the main dungeon
4. Generates a manifest of all changes for transparency
5. Outputs a JSON map file for web visualization

Reconstructed exits are tracked separately from original data.
"""

import sys
import json
import struct
from pathlib import Path
from collections import defaultdict
from copy import deepcopy

RECORD_SIZE = 512
DIRECTIONS = ['N', 'E', 'S', 'W']
OPPOSITE = {'N': 'S', 'E': 'W', 'S': 'N', 'W': 'E'}
DIR_OFFSETS = {'N': 1, 'E': 5, 'S': 9, 'W': 13}  # Byte offset within record
DIR_NAMES = {'N': 'North', 'E': 'East', 'S': 'South', 'W': 'West'}


class RoomData:
    """Raw room data with modification tracking"""

    def __init__(self, number, raw_bytes):
        self.number = number
        self.raw = bytearray(raw_bytes)
        # Validation byte wraps at 256 (single byte storage)
        expected_validation = (number - 1) % 256
        self.valid = (raw_bytes[0] == expected_validation) if number > 0 else False
        self.original_exits = {}
        self.reconstructed_exits = {}

        if self.valid:
            self._parse_exits()
            self._parse_description()

    def _parse_exits(self):
        """Parse existing exits from raw data"""
        for direction in DIRECTIONS:
            offset = DIR_OFFSETS[direction]
            dir_char = chr(self.raw[offset]) if self.raw[offset] else ''
            # 16-bit little-endian destination at offset+1 and offset+2
            dest = self.raw[offset + 1] + (self.raw[offset + 2] << 8)

            if dir_char == direction:
                self.original_exits[direction] = dest  # 0 = exit dungeon, >0 = room number

    def _parse_description(self):
        """Extract room description"""
        desc_bytes = self.raw[200:512]
        desc = ""
        for b in desc_bytes:
            if b == ord('$') or b == 0:
                break
            if 32 <= b < 127:
                desc += chr(b)
            elif b == 10 or b == 13:
                desc += ' '
        self.description = ' '.join(desc.split())  # Normalize whitespace

    def get_all_exits(self):
        """Get combined original + reconstructed exits"""
        exits = dict(self.original_exits)
        exits.update(self.reconstructed_exits)
        return exits

    def get_useful_exits(self):
        """Get exits that lead to actual rooms (not dungeon exit)"""
        all_exits = self.get_all_exits()
        return {d: dest for d, dest in all_exits.items() if dest > 0}

    def get_free_directions(self):
        """Get directions that can be used for new exits"""
        used = set()
        for d, dest in self.original_exits.items():
            if dest > 0:  # Only count exits to actual rooms as "used"
                used.add(d)
        for d in self.reconstructed_exits:
            used.add(d)
        return [d for d in DIRECTIONS if d not in used]

    def add_exit(self, direction, destination, force=False):
        """Add a reconstructed exit

        Args:
            direction: N, E, S, or W
            destination: Room number to connect to (16-bit, up to 65535)
            force: If True, override exits that point to room 0
        """
        # Destination must fit in 16 bits
        if destination > 65535:
            return False

        # Check if this direction is available
        if direction in self.reconstructed_exits:
            return False
        if direction in self.original_exits:
            if not force or self.original_exits[direction] > 0:
                return False

        self.reconstructed_exits[direction] = destination
        # Write to raw bytes as 16-bit little-endian
        offset = DIR_OFFSETS[direction]
        self.raw[offset] = ord(direction)
        self.raw[offset + 1] = destination & 0xFF          # Low byte
        self.raw[offset + 2] = (destination >> 8) & 0xFF   # High byte
        self.raw[offset + 3] = 0  # Padding byte
        return True

    def get_bytes(self):
        """Return modified raw bytes"""
        return bytes(self.raw)


def load_rooms(filepath):
    """Load all rooms from ADVENT.DTA"""
    rooms = {}
    with open(filepath, 'rb') as f:
        data = f.read()

    num_records = len(data) // RECORD_SIZE

    for i in range(num_records):
        offset = i * RECORD_SIZE
        record = data[offset:offset + RECORD_SIZE]
        room_number = i + 1
        room = RoomData(room_number, record)
        if room.valid:
            rooms[room_number] = room

    return rooms, data


def find_reachable(rooms, start=2):
    """Find all rooms reachable from start"""
    reachable = set()
    to_visit = [start]

    while to_visit:
        current = to_visit.pop(0)
        if current in reachable or current not in rooms:
            continue
        reachable.add(current)

        for dest in rooms[current].get_useful_exits().values():
            if dest not in reachable:
                to_visit.append(dest)

    return reachable


def find_clusters(rooms):
    """Find all disconnected clusters of rooms"""
    unvisited = set(rooms.keys())
    clusters = []

    while unvisited:
        start = min(unvisited)
        cluster = set()
        to_visit = [start]

        while to_visit:
            current = to_visit.pop(0)
            if current in cluster or current not in rooms:
                continue
            cluster.add(current)
            unvisited.discard(current)

            for dest in rooms[current].get_useful_exits().values():
                if dest not in cluster and dest in unvisited:
                    to_visit.append(dest)

        clusters.append(sorted(cluster))

    return clusters


def reconstruct_exits(rooms):
    """
    Reconstruct missing exits to create a connected dungeon.

    Strategy:
    1. Add return paths for one-way connections
    2. Build chains connecting isolated rooms to the main cluster
    3. Use force=True to override exits that go to room 0 (dungeon exit)
    """
    changes = []

    # Step 1: Add bidirectional exits for existing connections
    print("Step 1: Adding bidirectional exits...")
    for num, room in list(rooms.items()):
        for direction, dest in list(room.original_exits.items()):
            if dest > 0 and dest in rooms:
                opposite = OPPOSITE[direction]
                dest_room = rooms[dest]

                # Check if return path exists (to any room, not just 0)
                dest_useful = dest_room.get_useful_exits()
                if opposite not in dest_useful:
                    # Try to add return path, forcing if needed
                    if dest_room.add_exit(opposite, num, force=True):
                        changes.append({
                            'type': 'bidirectional',
                            'room': dest,
                            'direction': opposite,
                            'destination': num,
                            'reason': f'Return path from room {num}'
                        })
                        print(f"  Room {dest}: Added {opposite} exit to room {num}")

    # Step 2: Iteratively connect isolated rooms
    print("\nStep 2: Building connected dungeon...")

    # Track what's reachable and what's not
    reachable = find_reachable(rooms, 2)
    all_rooms = set(rooms.keys())
    unreachable = sorted(all_rooms - reachable)

    print(f"  Initially reachable: {len(reachable)}")
    print(f"  Unreachable: {len(unreachable)}")

    # Build a list of rooms we can connect from (start with reachable rooms)
    frontier = list(reachable)
    iterations = 0
    max_iterations = len(rooms) + 10  # Safety limit

    while unreachable and iterations < max_iterations:
        iterations += 1
        connected_this_round = False

        # Try to connect unreachable rooms to the frontier
        for target_num in list(unreachable):
            target = rooms[target_num]
            target_free = target.get_free_directions()

            if not target_free:
                # All directions occupied by room-0 exits, try forcing
                for d in DIRECTIONS:
                    if d not in target.reconstructed_exits:
                        target_free.append(d)
                        break

            if not target_free:
                continue

            # Find a frontier room to connect to
            for source_num in frontier:
                source = rooms[source_num]
                source_free = source.get_free_directions()

                if not source_free:
                    continue

                # Find compatible directions
                for src_dir in source_free:
                    opposite = OPPOSITE[src_dir]
                    if opposite in target_free or opposite not in target.get_useful_exits():
                        # Create bidirectional connection
                        if source.add_exit(src_dir, target_num, force=True):
                            changes.append({
                                'type': 'chain_connection',
                                'room': source_num,
                                'direction': src_dir,
                                'destination': target_num,
                                'reason': f'Connect room {target_num} to main dungeon'
                            })

                        if target.add_exit(opposite, source_num, force=True):
                            changes.append({
                                'type': 'chain_connection',
                                'room': target_num,
                                'direction': opposite,
                                'destination': source_num,
                                'reason': f'Return path to room {source_num}'
                            })

                        # Update tracking
                        unreachable.remove(target_num)
                        frontier.append(target_num)
                        reachable.add(target_num)
                        connected_this_round = True
                        break

                if target_num not in unreachable:
                    break

            if target_num not in unreachable:
                continue

        if not connected_this_round and unreachable:
            # No progress made, try harder
            print(f"  Iteration {iterations}: Stuck with {len(unreachable)} unreachable rooms")
            break

        if iterations % 50 == 0:
            print(f"  Iteration {iterations}: {len(unreachable)} rooms remaining")

    print(f"  Final: {len(reachable)} reachable, {len(unreachable)} unreachable")

    # Step 3: Final verification
    print("\nStep 3: Final verification...")
    final_reachable = find_reachable(rooms, 2)
    all_rooms = set(rooms.keys())
    still_unreachable = all_rooms - final_reachable

    print(f"  Reachable from room 2: {len(final_reachable)}")
    print(f"  Still unreachable: {len(still_unreachable)}")

    if still_unreachable:
        print(f"  Unreachable rooms: {sorted(still_unreachable)[:20]}...")

    return changes


def generate_map_json(rooms, changes):
    """Generate JSON map data for web visualization"""

    # Create change lookup
    change_lookup = defaultdict(list)
    for change in changes:
        change_lookup[change['room']].append(change)

    map_data = {
        'metadata': {
            'total_rooms': len(rooms),
            'total_changes': len(changes),
            'generated_by': 'reconstruct_rooms.py'
        },
        'start_room': 2,
        'rooms': {},
        'connections': [],
        'reconstruction_log': changes
    }

    reachable = find_reachable(rooms, 2)

    for num, room in rooms.items():
        all_exits = room.get_all_exits()

        map_data['rooms'][str(num)] = {
            'number': num,
            'description': room.description,
            'original_exits': room.original_exits,
            'reconstructed_exits': room.reconstructed_exits,
            'all_exits': all_exits,
            'reachable': num in reachable
        }

        # Add connections
        for direction, dest in all_exits.items():
            if dest > 0 and num < dest:  # Avoid duplicates
                is_reconstructed = (
                    direction in room.reconstructed_exits or
                    (dest in rooms and OPPOSITE[direction] in rooms[dest].reconstructed_exits)
                )
                map_data['connections'].append({
                    'from': num,
                    'to': dest,
                    'direction': direction,
                    'reconstructed': is_reconstructed
                })

    return map_data


def save_modified_data(rooms, original_data, output_path):
    """Save modified ADVENT.DTA"""
    data = bytearray(original_data)

    for num, room in rooms.items():
        offset = (num - 1) * RECORD_SIZE
        data[offset:offset + RECORD_SIZE] = room.get_bytes()

    with open(output_path, 'wb') as f:
        f.write(data)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Reconstruct missing room exits')
    parser.add_argument('--input', '-i', default='build/data/ADVENT.DTA',
                       help='Input ADVENT.DTA file')
    parser.add_argument('--output', '-o',
                       help='Output modified ADVENT.DTA (default: overwrite input)')
    parser.add_argument('--map-json', '-m', default='build/data/dungeon_map.json',
                       help='Output JSON map file')
    parser.add_argument('--dry-run', '-n', action='store_true',
                       help='Show changes without modifying files')
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        script_dir = Path(__file__).parent.parent
        input_path = script_dir / args.input

    if not input_path.exists():
        print(f"Error: Cannot find {args.input}")
        sys.exit(1)

    print(f"Loading rooms from {input_path}")
    rooms, original_data = load_rooms(input_path)
    print(f"Found {len(rooms)} valid rooms")

    # Check initial state
    initial_reachable = find_reachable(rooms, 2)
    print(f"Initially reachable from room 2: {len(initial_reachable)}")

    # Reconstruct exits
    changes = reconstruct_exits(rooms)

    print(f"\nTotal changes made: {len(changes)}")

    # Generate map JSON
    map_data = generate_map_json(rooms, changes)

    if args.dry_run:
        print("\n[DRY RUN - no files modified]")
        print(f"\nMap data preview:")
        print(json.dumps(map_data['metadata'], indent=2))
    else:
        # Save modified data
        output_path = Path(args.output) if args.output else input_path
        print(f"\nSaving modified data to {output_path}")
        save_modified_data(rooms, original_data, output_path)

        # Save map JSON
        map_path = Path(args.map_json)
        map_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Saving map JSON to {map_path}")
        with open(map_path, 'w') as f:
            json.dump(map_data, f, indent=2)

    print("\nDone!")


if __name__ == '__main__':
    main()
