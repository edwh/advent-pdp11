#!/usr/bin/env python3
"""
Generate RSTS/E data files for Advent MUD game from recovered data.

File formats:
- ADVENT.MON: 10000 records x 20 bytes (virtual array of monster spawns by room)
- ADVENT.CHR: 100 records x 512 bytes (character save data)
- BOARD.NTC: 512 records x 512 bytes (noticeboard)
- MESSAG.NPC: 1000 records x 60 bytes (NPC messages/shouts)
- ADVENT.DTA: Already exists - 2000 records x 512 bytes (room data)

Monster record structure (20 bytes):
  ATT.LEVEL% (2 bytes) - Attack level
  DEF.LEVEL% (2 bytes) - Defense level
  MON.HP% (2 bytes) - Hit points
  MON.DAM% (2 bytes) - Damage
  SPEC$ (6 bytes) - Special abilities (e.g., "/PA20/")
  MON.XP% (2 bytes) - Experience points
  MON.FLAG% (2 bytes) - Flags
  unused (2 bytes) - Padding
"""

import struct
import os

# Output directory
OUTPUT_DIR = "/home/edward/advent/generated_data"
DATA_DIR = "/home/edward/advent/data"

def cvt_int16(value):
    """Convert integer to 2-byte little-endian string (PDP-11 format)."""
    return struct.pack('<h', value)

def parse_refrsh_ctl(filepath):
    """Parse REFRSH.CTL to extract monster spawn data."""
    monsters = []  # List of (room, monster_data)

    with open(filepath, 'r') as f:
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
                        # chance = int(parts[2])  # Not stored in MON file
                        # name = parts[3]  # Stored in room file, not MON
                        attack = int(parts[4])
                        defense = int(parts[5])
                        hp = int(parts[6])
                        damage = int(parts[7])
                        special = parts[8] if len(parts) > 8 else ""
                        xp = int(parts[9]) if len(parts) > 9 else 0

                        monsters.append({
                            'room': room,
                            'attack': attack,
                            'defense': defense,
                            'hp': hp,
                            'damage': damage,
                            'special': special,
                            'xp': xp,
                            'flag': 0
                        })
                    except (ValueError, IndexError) as e:
                        print(f"Warning: Could not parse line: {line} - {e}")

    return monsters

def create_monster_record(attack, defense, hp, damage, special, xp, flag):
    """Create a 20-byte monster record."""
    # Ensure special is exactly 6 bytes
    special_bytes = special.encode('ascii')[:6].ljust(6, b'\x00')

    record = (
        cvt_int16(attack) +
        cvt_int16(defense) +
        cvt_int16(hp) +
        cvt_int16(damage) +
        special_bytes +
        cvt_int16(xp) +
        cvt_int16(flag) +
        cvt_int16(0)  # unused padding
    )

    assert len(record) == 20, f"Monster record should be 20 bytes, got {len(record)}"
    return record

def generate_advent_mon(output_path):
    """Generate ADVENT.MON file from REFRSH.CTL data."""
    print("Generating ADVENT.MON...")

    # Parse monster data
    refrsh_path = os.path.join(DATA_DIR, "REFRSH.CTL")
    if os.path.exists(refrsh_path):
        monsters = parse_refrsh_ctl(refrsh_path)
        print(f"  Parsed {len(monsters)} monsters from REFRSH.CTL")
    else:
        print("  Warning: REFRSH.CTL not found, creating empty file")
        monsters = []

    # Create 10000 records x 20 bytes file
    # Index by room number - each room can have one monster spawn
    record_count = 10000
    record_size = 20

    # Initialize all records as empty
    records = [b'\x00' * record_size] * record_count

    # Place monsters at their room indices
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

    # Write file
    with open(output_path, 'wb') as f:
        for record in records:
            f.write(record)

    file_size = os.path.getsize(output_path)
    print(f"  Created ADVENT.MON: {file_size} bytes ({file_size // record_size} records)")

def generate_advent_chr(output_path):
    """Generate empty ADVENT.CHR file (character save data)."""
    print("Generating ADVENT.CHR...")

    # 100 records x 512 bytes
    record_count = 100
    record_size = 512

    with open(output_path, 'wb') as f:
        f.write(b'\x00' * (record_count * record_size))

    file_size = os.path.getsize(output_path)
    print(f"  Created ADVENT.CHR: {file_size} bytes ({file_size // record_size} records)")

def generate_board_ntc(output_path):
    """Generate empty BOARD.NTC file (noticeboard)."""
    print("Generating BOARD.NTC...")

    # 512 records x 512 bytes
    record_count = 512
    record_size = 512

    with open(output_path, 'wb') as f:
        f.write(b'\x00' * (record_count * record_size))

    file_size = os.path.getsize(output_path)
    print(f"  Created BOARD.NTC: {file_size} bytes ({file_size // record_size} records)")

def generate_messag_npc(output_path):
    """Generate empty MESSAG.NPC file (NPC shout messages)."""
    print("Generating MESSAG.NPC...")

    # 1000 records x 60 bytes (plus a 2-byte count at record 0)
    # The file uses MODE 4096% which is virtual array mode
    record_count = 1000
    record_size = 60

    with open(output_path, 'wb') as f:
        f.write(b'\x00' * (record_count * record_size))

    file_size = os.path.getsize(output_path)
    print(f"  Created MESSAG.NPC: {file_size} bytes ({file_size // record_size} records)")

def main():
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("Generating Advent MUD data files")
    print("=" * 60)

    # Generate each file
    generate_advent_mon(os.path.join(OUTPUT_DIR, "ADVENT.MON"))
    generate_advent_chr(os.path.join(OUTPUT_DIR, "ADVENT.CHR"))
    generate_board_ntc(os.path.join(OUTPUT_DIR, "BOARD.NTC"))
    generate_messag_npc(os.path.join(OUTPUT_DIR, "MESSAG.NPC"))

    # Copy existing ADVENT.DTA if it exists
    dta_source = os.path.join(DATA_DIR, "ADVENT.DTA")
    dta_dest = os.path.join(OUTPUT_DIR, "ADVENT.DTA")
    if os.path.exists(dta_source):
        import shutil
        shutil.copy2(dta_source, dta_dest)
        print(f"\nCopied existing ADVENT.DTA: {os.path.getsize(dta_dest)} bytes")
    else:
        print(f"\nWarning: {dta_source} not found!")

    print("\n" + "=" * 60)
    print("Data files generated in:", OUTPUT_DIR)
    print("=" * 60)

    # List generated files
    print("\nGenerated files:")
    for filename in sorted(os.listdir(OUTPUT_DIR)):
        filepath = os.path.join(OUTPUT_DIR, filename)
        size = os.path.getsize(filepath)
        print(f"  {filename}: {size:,} bytes")

if __name__ == "__main__":
    main()
