#!/bin/bash
# Reassemble the split disk image parts into the full disk image
# This script should be run before starting SIMH if the disk doesn't exist

DISK_DIR="$(dirname "$0")"
DISK_FILE="$DISK_DIR/rstse_10_ra72.dsk"

if [ -f "$DISK_FILE" ]; then
    echo "Disk image already exists: $DISK_FILE"
    exit 0
fi

echo "Assembling disk image from parts..."
cat "$DISK_DIR"/rstse_10_ra72.dsk.part_* > "$DISK_FILE"

if [ $? -eq 0 ]; then
    echo "Successfully assembled disk image: $DISK_FILE"
    ls -lh "$DISK_FILE"
else
    echo "ERROR: Failed to assemble disk image"
    exit 1
fi
