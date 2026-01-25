#!/usr/bin/env python3
"""
Advent MUD Data Migration Script

Converts salvage data files (roomfil.fil, monfil.fil, REFRSH.CTL) into
proper RSTS/E binary format files for the Advent game.

Output files:
- ADVENT.DTA: 2000 rooms × 512 bytes (room data with binary exits)
- ADVENT.MON: 10000 × 20 bytes (monster spawn data)
- ADVENT.CHR: 100 × 512 bytes (character saves - empty)
- BOARD.NTC: 512 × 512 bytes (noticeboard - empty)
- MESSAG.NPC: 1000 × 60 bytes (NPC messages - empty)

Record structure for ADVENT.DTA (512 bytes per room):
- Byte 0 (1 byte): Validation byte = room_num & 0xFF
- Bytes 1-16 (16 bytes): Exits - 4 bytes each for N,S,E,W
  - Byte 0: Direction letter (N/S/E/W) or space if no exit
  - Bytes 1-2: Room number as 16-bit big-endian (for CVT$% compatibility)
  - Byte 3: Padding (0)
- Bytes 17-99 (83 bytes): Monsters/NPCs
- Bytes 100-199 (100 bytes): Objects
- Bytes 200-511 (312 bytes): Room description
"""

import os
import re
import struct
import sys
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "build" / "data"


def parse_exits(exit_string):
    """
    Parse exit string like 'N740W700' or 'N11E15S10W8' into a dictionary.

    Returns dict like {'N': 740, 'W': 700}
    """
    exits = {'N': 0, 'S': 0, 'E': 0, 'W': 0}

    if not exit_string:
        return exits

    # Parse exit format: direction followed by room number
    # Pattern: letter followed by digits
    pattern = r'([NSEW])(\d+)'
    matches = re.findall(pattern, exit_string.upper())

    for direction, room_num in matches:
        try:
            exits[direction] = int(room_num)
        except ValueError:
            pass

    return exits


def create_binary_exits(exits):
    """
    Create 16-byte binary exit string from exits dictionary.

    Format: 4 bytes per direction (N, S, E, W)
    - Byte 0: Direction letter if exit exists, else space
    - Bytes 1-2: Room number as 16-bit big-endian (for CVT$% compatibility)
    - Byte 3: Padding (0)
    """
    result = bytearray(16)
    directions = ['N', 'S', 'E', 'W']

    for idx, d in enumerate(directions):
        pos = idx * 4
        room = exits.get(d, 0)

        if room > 0:
            # Valid exit - direction letter and room number
            # NOTE: CVT$% in BASIC-PLUS-2 interprets bytes as big-endian
            # so we store high byte first, low byte second
            result[pos] = ord(d)
            result[pos+1] = (room >> 8) & 0xFF # High byte (for CVT$%)
            result[pos+2] = room & 0xFF        # Low byte
            result[pos+3] = 0                  # Padding
        else:
            # No exit - space character
            result[pos] = ord(' ')
            result[pos+1] = 0
            result[pos+2] = 0
            result[pos+3] = 0

    return bytes(result)


def parse_roomfil(filepath):
    """
    Parse roomfil.fil and return dictionary of room data.

    Room format:
    - Line 1: room_number,exits (e.g., "21,W20E601")
    - Line 2: monsters (e.g., "*A cave lizard/!corpse")
    - Line 3: objects (e.g., "A chest~50/A dagger$5")
    - Lines 4+: description (until next room number)
    - Optional: /special codes/ at end
    """
    rooms = {}

    with open(filepath, 'r', encoding='latin-1') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n\r')

        # Skip header line
        if line.startswith('pip '):
            i += 1
            continue

        # Try to parse as room header (number,exits)
        match = re.match(r'^(\d+),(.*)$', line)
        if match:
            room_num = int(match.group(1))
            exit_str = match.group(2).strip()

            # Parse exits
            exits = parse_exits(exit_str)

            # Next line should be monsters
            i += 1
            monsters = lines[i].rstrip('\n\r') if i < len(lines) else ''

            # Next line should be objects
            i += 1
            objects = lines[i].rstrip('\n\r') if i < len(lines) else ''

            # Remaining lines until next room are description
            i += 1
            desc_lines = []
            while i < len(lines):
                next_line = lines[i].rstrip('\n\r')
                # Check if this is the start of a new room
                if re.match(r'^\d+,', next_line):
                    break
                desc_lines.append(next_line)
                i += 1

            description = '\n'.join(desc_lines).strip()

            # Extract special codes from description if present
            # Special codes start with / and can span multiple lines
            # Find the FIRST line that starts with / and treat everything
            # from there as special codes
            special = ''
            desc_split_lines = description.split('\n')
            for idx, line in enumerate(desc_split_lines):
                if line.startswith('/'):
                    # Everything from this line onwards is special codes
                    special = '\n'.join(desc_split_lines[idx:])
                    description = '\n'.join(desc_split_lines[:idx]).strip()
                    break

            rooms[room_num] = {
                'exits': exits,
                'monsters': monsters,
                'objects': objects,
                'description': description,
                'special': special
            }
        else:
            i += 1

    return rooms


def create_room_record(room_num, room_data):
    """
    Create a 512-byte room record for ADVENT.DTA.

    Layout:
    - Byte 0: Room number low byte
    - Bytes 1-16: Exits (4 bytes each: dir, room_lo, room_hi, pad)
    - Bytes 17-99: Monsters (83 bytes)
    - Bytes 100-199: Objects (100 bytes)
    - Bytes 200-511: Description (312 bytes)
    """
    record = bytearray(512)

    # Byte 0: Room number verification
    # ADVNOR.SUB (navigation) checks: CHR$(ROOM%(USER%))=ROOM$ so validation byte = room_num & 0xFF
    # Note: ADVENT.B2S uses room_num-1, but ADVNOR.SUB (and ADVTDY.SUB) use room_num
    # We prioritize navigation working over avoiding cosmetic errors in main loop
    record[0] = room_num & 0xFF

    # Bytes 1-16: Exits
    exits = create_binary_exits(room_data.get('exits', {}))
    record[1:17] = exits

    # Bytes 17-99: Monsters (83 bytes)
    # Monster entries require trailing '/' for display code to iterate
    # Display code (ADVDSP.SUB:59): GOTO 15030 UNLESS INSTR(1%,PEO$,"/")
    # Without '/', monsters block GET but are invisible to the player
    monsters = room_data.get('monsters', '')
    if monsters and not monsters.endswith('/'):
        monsters = monsters + '/'
    monsters = monsters[:83]
    monsters_bytes = monsters.encode('ascii', errors='replace')
    record[17:17+len(monsters_bytes)] = monsters_bytes

    # Bytes 100-199: Objects (100 bytes)
    objects = room_data.get('objects', '')[:100]
    objects_bytes = objects.encode('ascii', errors='replace')
    record[100:100+len(objects_bytes)] = objects_bytes

    # Bytes 200-511: Description (312 bytes)
    # Description followed by $ terminator and special codes
    # Game uses: DES$=LEFT(DES$,INSTR(1%,DES$,"$")-1%) to truncate at $
    desc = room_data.get('description', '')
    special = room_data.get('special', '')
    if special:
        desc = desc + '$' + special
    else:
        desc = desc + '$'  # Always add terminator
    desc = desc[:312]
    desc_bytes = desc.encode('ascii', errors='replace')
    record[200:200+len(desc_bytes)] = desc_bytes

    return bytes(record)


def generate_advent_dta(rooms, output_path):
    """Generate ADVENT.DTA file with 2000 room records.

    IMPORTANT: BASIC-PLUS-2 uses 1-based record indexing:
    - GET #3%, RECORD 1 reads file offset 0
    - GET #3%, RECORD N reads file offset (N-1)*512

    So room N must be written at file index N-1.
    """
    print(f"Generating ADVENT.DTA...")

    record_count = 2000
    record_size = 512

    with open(output_path, 'wb') as f:
        # Write records 1 through record_count (1-based room numbers)
        # File index 0 = BASIC's RECORD 1 = room 1
        # File index N-1 = BASIC's RECORD N = room N
        for room_num in range(1, record_count + 1):
            if room_num in rooms:
                record = create_room_record(room_num, rooms[room_num])
            else:
                # Empty room record
                record = bytes(512)
            f.write(record)

    file_size = os.path.getsize(output_path)
    populated = len([r for r in rooms.keys() if 1 <= r <= record_count])
    print(f"  Created ADVENT.DTA: {file_size:,} bytes")
    print(f"  Populated {populated} rooms out of {record_count}")


def parse_refrsh_ctl(filepath):
    """Parse REFRSH.CTL to extract monster spawn data."""
    monsters = []

    with open(filepath, 'r', encoding='latin-1') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(';'):
                continue

            if line.startswith('M,'):
                # Monster: M,room,chance,name,attack,defense,hp,damage,special,xp
                parts = line.split(',')
                if len(parts) >= 10:
                    try:
                        room = int(parts[1])
                        chance = int(parts[2])
                        name = parts[3]
                        attack = int(parts[4])
                        defense = int(parts[5])
                        hp = int(parts[6])
                        damage = int(parts[7])
                        special = parts[8] if len(parts) > 8 else ""
                        xp = int(parts[9]) if len(parts) > 9 else 0

                        monsters.append({
                            'room': room,
                            'chance': chance,
                            'name': name,
                            'attack': attack,
                            'defense': defense,
                            'hp': hp,
                            'damage': damage,
                            'special': special,
                            'xp': xp,
                            'flag': 0
                        })
                    except (ValueError, IndexError) as e:
                        pass

    return monsters


def create_monster_record(attack, defense, hp, damage, special, xp, flag):
    """
    Create a 20-byte monster record for ADVENT.MON.

    Layout:
    - Bytes 0-1: Attack level (16-bit)
    - Bytes 2-3: Defense level (16-bit)
    - Bytes 4-5: Hit points (16-bit)
    - Bytes 6-7: Damage (16-bit)
    - Bytes 8-13: Special abilities string (6 bytes)
    - Bytes 14-15: Experience points (16-bit)
    - Bytes 16-17: Flags (16-bit)
    - Bytes 18-19: Padding (16-bit)
    """
    # Ensure special is exactly 6 bytes
    special_bytes = special.encode('ascii', errors='replace')[:6].ljust(6, b'\x00')

    record = (
        struct.pack('<h', attack) +
        struct.pack('<h', defense) +
        struct.pack('<h', hp) +
        struct.pack('<h', damage) +
        special_bytes +
        struct.pack('<h', xp) +
        struct.pack('<h', flag) +
        struct.pack('<h', 0)  # padding
    )

    return record


def generate_advent_mon(monsters, output_path):
    """Generate ADVENT.MON file with monster spawn data."""
    print(f"Generating ADVENT.MON...")

    record_count = 10000
    record_size = 20

    # Initialize all records as empty
    records = [b'\x00' * record_size] * record_count

    # Place monsters at their room indices
    monster_count = 0
    for mon in monsters:
        room = mon['room']
        if 0 <= room < record_count:
            records[room] = create_monster_record(
                mon['attack'],
                mon['defense'],
                mon['hp'],
                mon['damage'],
                mon['special'],
                mon['xp'],
                mon['flag']
            )
            monster_count += 1

    # Write file
    with open(output_path, 'wb') as f:
        for record in records:
            f.write(record)

    file_size = os.path.getsize(output_path)
    print(f"  Created ADVENT.MON: {file_size:,} bytes")
    print(f"  Placed {monster_count} monsters")


def generate_advent_chr(output_path):
    """Generate empty ADVENT.CHR file (character save data)."""
    print(f"Generating ADVENT.CHR...")

    # 100 records x 512 bytes
    record_count = 100
    record_size = 512

    with open(output_path, 'wb') as f:
        f.write(b'\x00' * (record_count * record_size))

    file_size = os.path.getsize(output_path)
    print(f"  Created ADVENT.CHR: {file_size:,} bytes")


def generate_board_ntc(output_path):
    """Copy original BOARD.NTC with 1986-87 noticeboard data.

    The original tape/BOARD.NTC contains real player-written messages
    including Monty Python quotes, schoolboy humor, and game tips.
    This is historical content worth preserving!
    """
    print(f"Copying original BOARD.NTC with 1986-87 data...")

    # Look for original BOARD.NTC in tape directory
    script_dir = Path(__file__).parent.parent
    original_path = script_dir / "tape" / "BOARD.NTC"

    if original_path.exists():
        import shutil
        shutil.copy(original_path, output_path)
        file_size = os.path.getsize(output_path)
        print(f"  Copied original BOARD.NTC: {file_size:,} bytes")
    else:
        # Fallback: generate empty file if original not found
        print(f"  WARNING: Original tape/BOARD.NTC not found, generating empty file")
        record_count = 512
        record_size = 512
        with open(output_path, 'wb') as f:
            f.write(b'\x00' * (record_count * record_size))
        file_size = os.path.getsize(output_path)
        print(f"  Created empty BOARD.NTC: {file_size:,} bytes")


def generate_messag_npc(output_path):
    """Generate empty MESSAG.NPC file (NPC shout messages)."""
    print(f"Generating MESSAG.NPC...")

    # 1000 records x 60 bytes
    record_count = 1000
    record_size = 60

    with open(output_path, 'wb') as f:
        f.write(b'\x00' * (record_count * record_size))

    file_size = os.path.getsize(output_path)
    print(f"  Created MESSAG.NPC: {file_size:,} bytes")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate Advent MUD data files')
    parser.add_argument('--data-dir', type=Path, default=DATA_DIR,
                        help='Directory containing salvaged data files')
    parser.add_argument('--output-dir', type=Path, default=OUTPUT_DIR,
                        help='Directory for output files')
    args = parser.parse_args()

    data_dir = args.data_dir
    output_dir = args.output_dir

    print("=" * 60)
    print("Advent MUD Data Migration")
    print("=" * 60)
    print(f"Data dir: {data_dir}")
    print(f"Output dir: {output_dir}")
    print()

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse room data
    roomfil_path = data_dir / "roomfil.fil"
    if roomfil_path.exists():
        print(f"Parsing {roomfil_path}...")
        rooms = parse_roomfil(roomfil_path)
        print(f"  Found {len(rooms)} rooms")
    else:
        print(f"Warning: {roomfil_path} not found!")
        rooms = {}

    # Parse monster data
    refrsh_path = data_dir / "REFRSH.CTL"
    if refrsh_path.exists():
        print(f"Parsing {refrsh_path}...")
        monsters = parse_refrsh_ctl(refrsh_path)
        print(f"  Found {len(monsters)} monsters")
    else:
        print(f"Warning: {refrsh_path} not found!")
        monsters = []

    print()

    # Generate all data files
    generate_advent_dta(rooms, output_dir / "ADVENT.DTA")
    generate_advent_mon(monsters, output_dir / "ADVENT.MON")
    generate_advent_chr(output_dir / "ADVENT.CHR")
    generate_board_ntc(output_dir / "BOARD.NTC")
    generate_messag_npc(output_dir / "MESSAG.NPC")

    print()
    print("=" * 60)
    print(f"Data files generated in: {output_dir}")
    print("=" * 60)

    # List generated files
    print("\nGenerated files:")
    for filename in sorted(output_dir.iterdir()):
        if filename.is_file():
            size = filename.stat().st_size
            print(f"  {filename.name}: {size:,} bytes")

    return 0


if __name__ == "__main__":
    sys.exit(main())
