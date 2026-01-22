#!/usr/bin/env python3
"""
Create a SIMH tape image with all ADVENT source and data files.

This tape can be used to bootstrap ADVENT from a clean RSTS/E installation.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from create_tape import write_file_to_tape, write_end_of_medium

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Source files needed for ADVENT build (order matters for build process)
# NOTE: ODL files removed - they're created in-place with RT11 format
# (Tape transfer creates RSX format which TKB rejects as "illegal format")
SOURCE_FILES = [
    # Command file (game launcher with auto-restart)
    ('src/ADVENT.COM', 'ADVENT', 'COM'),

    # Main program
    ('src/ADVENT.B2S', 'ADVENT', 'B2S'),

    # Subroutines
    ('src/ADVINI.SUB', 'ADVINI', 'SUB'),
    ('src/ADVOUT.SUB', 'ADVOUT', 'SUB'),
    ('src/ADVNOR.SUB', 'ADVNOR', 'SUB'),
    ('src/ADVCMD.SUB', 'ADVCMD', 'SUB'),
    ('src/ADVODD.SUB', 'ADVODD', 'SUB'),
    ('src/ADVMSG.SUB', 'ADVMSG', 'SUB'),
    ('src/ADVBYE.SUB', 'ADVBYE', 'SUB'),
    ('src/ADVSHT.SUB', 'ADVSHT', 'SUB'),
    ('src/ADVNPC.SUB', 'ADVNPC', 'SUB'),
    ('src/ADVPUZ.SUB', 'ADVPUZ', 'SUB'),
    ('src/ADVDSP.SUB', 'ADVDSP', 'SUB'),
    ('src/ADVFND.SUB', 'ADVFND', 'SUB'),
    ('src/ADVTDY.SUB', 'ADVTDY', 'SUB'),

    # ODL files removed - see TKB_BUILD_RESEARCH.md for details
    # ODL files must be created in-place using COPY from system FEDTKB.ODL
    # to get RT11 file format attribute that TKB requires
]

# Data files
DATA_FILES = [
    ('generated_data/ADVENT.DTA', 'ADVENT', 'DTA'),
    ('generated_data/ADVENT.MON', 'ADVENT', 'MON'),
    ('generated_data/ADVENT.CHR', 'ADVENT', 'CHR'),
    ('generated_data/BOARD.NTC', 'BOARD', 'NTC'),
]

def create_advent_tape(output_path, include_data=True):
    """Create a tape with all ADVENT source and optionally data files."""

    print(f"Creating ADVENT tape: {output_path}")
    print("=" * 60)

    files_to_include = SOURCE_FILES.copy()
    if include_data:
        files_to_include.extend(DATA_FILES)

    total_size = 0
    file_count = 0

    with open(output_path, 'wb') as tape:
        for rel_path, name, ext in files_to_include:
            full_path = os.path.join(BASE_DIR, rel_path)

            if not os.path.exists(full_path):
                print(f"  WARNING: {rel_path} not found, skipping")
                continue

            with open(full_path, 'rb') as f:
                data = f.read()

            # Convert line endings to RSTS format (CR/LF)
            # Only for text files (.B2S, .SUB, .ODL)
            if ext in ('B2S', 'SUB', 'ODL', 'COM'):
                # Convert to text, normalize line endings
                try:
                    text = data.decode('ascii', errors='replace')
                    # Normalize to CR/LF
                    text = text.replace('\r\n', '\n').replace('\r', '\n')
                    text = text.replace('\n', '\r\n')
                    data = text.encode('ascii', errors='replace')
                except:
                    pass  # Keep binary data as-is

            print(f"  Adding: {name}.{ext} ({len(data):,} bytes)")
            write_file_to_tape(tape, name, ext, data)
            total_size += len(data)
            file_count += 1

        write_end_of_medium(tape)

    tape_size = os.path.getsize(output_path)
    print("=" * 60)
    print(f"Created tape with {file_count} files")
    print(f"Total data: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    print(f"Tape file: {tape_size:,} bytes ({tape_size/1024:.1f} KB)")
    print(f"Estimated transfer time at 18 KB/sec: {total_size/18000:.0f} seconds")

    return output_path

def create_source_only_tape(output_path):
    """Create a tape with only source files (no data)."""

    print(f"Creating source-only tape: {output_path}")
    print("=" * 60)

    total_size = 0
    file_count = 0

    with open(output_path, 'wb') as tape:
        for rel_path, name, ext in SOURCE_FILES:
            full_path = os.path.join(BASE_DIR, rel_path)

            if not os.path.exists(full_path):
                print(f"  WARNING: {rel_path} not found, skipping")
                continue

            with open(full_path, 'rb') as f:
                data = f.read()

            # Convert line endings for text files
            try:
                text = data.decode('ascii', errors='replace')
                text = text.replace('\r\n', '\n').replace('\r', '\n')
                text = text.replace('\n', '\r\n')
                data = text.encode('ascii', errors='replace')
            except:
                pass

            print(f"  Adding: {name}.{ext} ({len(data):,} bytes)")
            write_file_to_tape(tape, name, ext, data)
            total_size += len(data)
            file_count += 1

        write_end_of_medium(tape)

    print("=" * 60)
    print(f"Created tape with {file_count} source files")
    print(f"Total: {total_size:,} bytes ({total_size/1024:.1f} KB)")

    return output_path

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Create ADVENT tape image')
    parser.add_argument('--output', '-o', default='build/tapes/advent_source.tap',
                        help='Output tape file path')
    parser.add_argument('--source-only', action='store_true',
                        help='Only include source files, not data')
    parser.add_argument('--full', action='store_true',
                        help='Include source and data files (default)')

    args = parser.parse_args()

    output_path = os.path.join(BASE_DIR, args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if args.source_only:
        create_source_only_tape(output_path)
    else:
        create_advent_tape(output_path, include_data=True)
