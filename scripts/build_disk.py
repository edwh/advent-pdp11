#!/usr/bin/env python3
"""
Advent MUD - Disk Image Builder

This script:
1. Creates a clean disk image from the backup
2. Runs the data migration to generate binary files
3. Patches source files and data files into the disk image using flx
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
BUILD_DIR = PROJECT_DIR / "build"
DISK_DIR = BUILD_DIR / "disks"
DATA_DIR = BUILD_DIR / "data"
SOURCE_DIR = PROJECT_DIR / "src"

# Base disk to use
BASE_DISK = PROJECT_DIR / "simh" / "Disks" / "rsts_backup.dsk"
BOOT_DISK = PROJECT_DIR / "simh" / "Disks" / "rsts0.dsk"

# FLX tool
FLX = PROJECT_DIR / "flx"

# Source files needed for the game
GAME_SOURCE_FILES = [
    "ADVENT.B2S",
    "ADVINI.SUB",
    "ADVOUT.SUB",
    "ADVNOR.SUB",
    "ADVCMD.SUB",
    "ADVODD.SUB",
    "ADVMSG.SUB",
    "ADVBYE.SUB",
    "ADVSHT.SUB",
    "ADVNPC.SUB",
    "ADVPUZ.SUB",
    "ADVDSP.SUB",
    "ADVFND.SUB",
    "ADVTDY.SUB",
    "ADVENT.ODL",
]

# Data files to install
DATA_FILES = [
    "ADVENT.DTA",
    "ADVENT.MON",
    "ADVENT.CHR",
    "BOARD.NTC",
    "MESSAG.NPC",
]


def run_flx(commands, disk_path):
    """Run flx commands against a disk image."""
    # Prepare commands with id first
    cmd_input = f"id {disk_path}\n" + "\n".join(commands) + "\nquit\n"

    result = subprocess.run(
        [str(FLX)],
        input=cmd_input,
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR
    )

    return result


def main():
    print("=" * 60)
    print("  Advent MUD - Disk Image Builder")
    print("=" * 60)
    print()

    # Create build directories
    print("Creating build directories...")
    DISK_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Check prerequisites
    if not BASE_DISK.exists():
        print(f"ERROR: Base disk not found: {BASE_DISK}")
        return 1

    if not FLX.exists():
        print(f"ERROR: FLX tool not found: {FLX}")
        return 1

    # Step 1: Copy base disk
    print()
    print("Step 1: Copying base disk image...")
    target_disk = DISK_DIR / "rsts1.dsk"
    shutil.copy2(BASE_DISK, target_disk)
    print(f"  Created: {target_disk}")

    # Step 2: Clean the disk
    print()
    print("Step 2: Cleaning disk image (removing dirty flag)...")
    result = run_flx(["clean"], target_disk)
    if "error" in result.stderr.lower():
        print(f"  WARNING: {result.stderr}")
    else:
        print("  Disk cleaned")

    # Step 3: Run data migration
    print()
    print("Step 3: Running data migration...")
    migrate_script = SCRIPT_DIR / "migrate_data.py"
    subprocess.run([sys.executable, str(migrate_script)], check=True)

    # Step 4: Verify disk is writeable
    print()
    print("Step 4: Verifying disk is writeable...")
    result = run_flx(["id"], target_disk)
    if "Dirty" in result.stdout:
        print("  WARNING: Disk still marked as dirty, running clean again...")
        run_flx(["clean"], target_disk)
    print("  Disk ready for writing")

    # Step 5: Copy source files to [1,3]
    print()
    print("Step 5: Patching source files to [1,3]...")
    source_build = BUILD_DIR / "source"
    source_build.mkdir(exist_ok=True)

    for filename in GAME_SOURCE_FILES:
        src_path = SOURCE_DIR / filename
        if src_path.exists():
            dst_path = source_build / filename
            shutil.copy2(src_path, dst_path)
            # Put file to disk
            result = run_flx([f"put {dst_path} [1,3]{filename}"], target_disk)
            if "error" in result.stderr.lower() or "not properly" in result.stdout.lower():
                print(f"  WARNING: Issue adding {filename}")
            else:
                print(f"  Added: [1,3]{filename}")
        else:
            print(f"  Missing: {filename}")

    # Step 6: Copy data files to [1,2]
    print()
    print("Step 6: Patching data files to [1,2]...")
    for filename in DATA_FILES:
        src_path = DATA_DIR / filename
        if src_path.exists():
            result = run_flx([f"put {src_path} [1,2]{filename}"], target_disk)
            if "error" in result.stderr.lower():
                print(f"  WARNING: Issue adding {filename}: {result.stderr}")
            else:
                print(f"  Added: [1,2]{filename}")
        else:
            print(f"  Missing: {filename}")

    # Step 7: Copy boot disk
    print()
    print("Step 7: Copying boot disk...")
    if BOOT_DISK.exists():
        shutil.copy2(BOOT_DISK, DISK_DIR / "rsts0.dsk")
        print(f"  Created: {DISK_DIR / 'rsts0.dsk'}")
    else:
        print(f"  WARNING: Boot disk not found: {BOOT_DISK}")

    # Step 8: Verify installation
    print()
    print("Step 8: Verifying installation...")
    result = run_flx(["dir [1,2]ADVENT.*", "dir [1,3]ADV*.SUB"], target_disk)
    print("  Data files on [1,2]:")
    for line in result.stdout.split('\n'):
        if 'advent' in line.lower():
            print(f"    {line.strip()}")
    print("  Source files on [1,3]:")
    for line in result.stdout.split('\n'):
        if '.sub' in line.lower():
            print(f"    {line.strip()}")

    print()
    print("=" * 60)
    print("  Disk image built successfully!")
    print("=" * 60)
    print()
    print("Output files:")
    print(f"  {DISK_DIR / 'rsts0.dsk'} (boot disk)")
    print(f"  {DISK_DIR / 'rsts1.dsk'} (game disk)")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
