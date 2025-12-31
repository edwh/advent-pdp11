#!/bin/bash
# Advent MUD - Disk Image Builder
#
# This script:
# 1. Creates a clean disk image from the backup
# 2. Runs the data migration to generate binary files
# 3. Patches source files and data files into the disk image using flx
#
# Usage: ./scripts/build_disk.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_DIR/build"
DISK_DIR="$BUILD_DIR/disks"
DATA_DIR="$BUILD_DIR/data"

# Source disk to use as base
BASE_DISK="$PROJECT_DIR/simh/Disks/rsts_backup.dsk"

# Target disk
TARGET_DISK="$DISK_DIR/rsts1.dsk"

# FLX tool
FLX="$PROJECT_DIR/flx"

echo "=============================================="
echo "  Advent MUD - Disk Image Builder"
echo "=============================================="
echo

# Create build directories
echo "Creating build directories..."
mkdir -p "$DISK_DIR"
mkdir -p "$DATA_DIR"

# Check for base disk
if [ ! -f "$BASE_DISK" ]; then
    echo "ERROR: Base disk not found: $BASE_DISK"
    exit 1
fi

# Check for flx tool
if [ ! -x "$FLX" ]; then
    echo "ERROR: FLX tool not found or not executable: $FLX"
    exit 1
fi

# Step 1: Copy base disk
echo "Copying base disk image..."
cp "$BASE_DISK" "$TARGET_DISK"
echo "  Created: $TARGET_DISK"

# Step 2: Clean the disk (remove dirty flag)
echo
echo "Cleaning disk image (removing dirty flag)..."
cd "$PROJECT_DIR"
echo "clean" | "$FLX" -id "$TARGET_DISK" > /dev/null 2>&1
echo "  Disk cleaned"

# Step 3: Run data migration
echo
echo "Running data migration..."
python3 "$SCRIPT_DIR/migrate_data.py"

# Step 4: Copy source files to build directory
echo
echo "Copying source files..."
SOURCE_BUILD="$BUILD_DIR/source"
mkdir -p "$SOURCE_BUILD"

# Copy the main game files
for f in ADVENT.B2S ADVINI.SUB ADVOUT.SUB ADVNOR.SUB ADVCMD.SUB ADVODD.SUB \
         ADVMSG.SUB ADVBYE.SUB ADVSHT.SUB ADVNPC.SUB ADVPUZ.SUB ADVDSP.SUB \
         ADVFND.SUB ADVTDY.SUB ADVENT.ODL; do
    if [ -f "$PROJECT_DIR/src/$f" ]; then
        cp "$PROJECT_DIR/src/$f" "$SOURCE_BUILD/"
    fi
done
echo "  Copied $(ls -1 "$SOURCE_BUILD" | wc -l) source files"

# Step 5: Patch source files into disk [1,3]
echo
echo "Patching source files to [1,3]..."
cd "$PROJECT_DIR"

for f in "$SOURCE_BUILD"/*; do
    filename=$(basename "$f")
    echo "put $f [1,3]$filename" | "$FLX" -id "$TARGET_DISK" -W > /dev/null 2>&1
    echo "  Added: [1,3]$filename"
done

# Step 6: Patch data files into disk [1,2]
echo
echo "Patching data files to [1,2]..."

for f in "$DATA_DIR"/*; do
    if [ -f "$f" ]; then
        filename=$(basename "$f")
        echo "put $f [1,2]$filename" | "$FLX" -id "$TARGET_DISK" -W > /dev/null 2>&1
        echo "  Added: [1,2]$filename"
    fi
done

# Also copy rsts0.dsk for boot
echo
echo "Copying boot disk..."
cp "$PROJECT_DIR/simh/Disks/rsts0.dsk" "$DISK_DIR/"

echo
echo "=============================================="
echo "  Disk image built successfully!"
echo "=============================================="
echo
echo "Output files:"
echo "  $DISK_DIR/rsts0.dsk (boot disk)"
echo "  $DISK_DIR/rsts1.dsk (game disk with source & data)"
echo
echo "To verify, run:"
echo "  echo 'id $TARGET_DISK' | $FLX"
echo "  echo 'dir [1,2]' | $FLX"
echo "  echo 'dir [1,3]' | $FLX"
