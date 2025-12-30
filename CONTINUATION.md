# Continuation Guide for Claude

This document is for another Claude instance continuing the Advent MUD resurrection project.

## Project Overview

Resurrecting a 1987 multi-user dungeon game (ADVENT) that runs on PDP-11/RSTS/E, now emulated via SIMH in Docker.

## Current State (December 30, 2025)

### What Works
- Docker container boots RSTS/E V10.1 successfully
- Game compiles and links (all 14 BP2 modules)
- Game starts, shows welcome message, accepts commands
- Single-user ADVOUT.SUB created (prints to console instead of multi-user message passing)
- Room descriptions display correctly
- Exit list displays (shows available directions)
- **BINARY FILE TRANSFER VIA TECO** - Verified working! (see TECHNICAL.md for details)

### What Doesn't Work Yet
- **Navigation fails**: "You cannot go in that direction" even when exits display
- Root cause identified: **Binary exit format mismatch**
- Need to transfer correct data files using TECO method

### Current Task: Transfer Data Files

The data files need to be transferred to RSTS/E using the TECO binary transfer method:

| File | Size | Purpose |
|------|------|---------|
| ADVENT.DTA | 1000 KB | Room data (exits, monsters, objects, descriptions) |
| ADVENT.CHR | 51 KB | Character data |
| ADVENT.MON | 196 KB | Monster definitions |
| BOARD.NTC | 256 KB | Notice board |
| MESSAG.NPC | 59 KB | NPC messages |

**Transfer script**: `scripts/teco_transfer.py`

**Status**: Transfer in progress (started with ADVENT.CHR as test)

## The Core Problem

### Exit Data Format Issue

The game reads room exit data from `ADVENT.DTA`. The format expected by the code:

```
FIELD #3%, 1% AS ROOM$, 16% AS EX$, 83% AS PEOPLE$, 100% AS OBJECT$, 312% AS DESC$
```

Exit parsing in ADVNOR.SUB line 46:
```basic
NEW.ROOM%=CVT$%(MID(EX$,PO%+1%,2%))
```

`CVT$%` converts a **2-byte binary string** to a 16-bit integer. The format should be:
- Byte 1: Direction letter ('N'/'S'/'E'/'W') or space if no exit
- Bytes 2-3: Room number as 16-bit little-endian binary
- Byte 4: Padding
- Repeat 4 times = 16 bytes total

### The Mistake Made

I was writing to disk block 5922, but RSTS has `ADVENT.DTA` at block 467. Direct disk writes bypassed the RSTS file system entirely.

### The Correct Approach

1. **Shut down RSTS/E cleanly** (so disk is properly dismounted)
2. **Use `flx` tool** to write files to the disk image
3. **Boot RSTS/E again**

The `flx` tool from simtools only writes to properly dismounted disks:
```
./flx -id simh/Disks/rsts1.dsk -pu "[1,2]ADVENT.DTA" < data/ADVENT_BINARY.DTA
```

## Key Files

### Source Code (in `src/`)
- `ADVENT.B2S` - Main program
- `ADVINI.SUB` - Initialization, opens data files
- `ADVOUT.SUB` - Output to player (modified for single-user)
- `ADVDSP.SUB` - Display room descriptions
- `ADVNOR.SUB` - Normal commands (movement, inventory, etc.)
- `ADVCMD.SUB` - Command parser
- Other .SUB files for various subsystems

### Data Files
- `data/ADVENT.DTA` - 2000 rooms × 512 bytes (ASCII format - WRONG)
- `data/ADVENT_BINARY.DTA` - Same but with binary exit format (CORRECT)
- `data/REFRSH.CTL` - Monster spawn configuration

### Expect Scripts
- `create_advout.exp` - Creates single-user ADVOUT.SUB
- `create_proper_data.exp` - Creates support data files
- `clean_shutdown.exp` - Shuts down RSTS/E cleanly

### Docker
- `docker-compose.yml` - Main compose file
- `docker/Dockerfile` - Container build
- `docker/pdp11.ini` - SIMH configuration
- `simh/Disks/rsts1.dsk` - Main disk image (DM1:)

## Next Steps

### Immediate: Fix Navigation

1. Stop Docker container
2. Create correct binary ADVENT.DTA:
   ```python
   # Already done - see data/ADVENT_BINARY.DTA
   # Format: Direction letter only if room>0, else space
   # Room number as 2-byte little-endian
   ```

3. Use flx to write to disk:
   ```bash
   # First, clean shutdown RSTS (or just stop container)
   docker stop advent

   # Delete old file and add new one
   ./flx -id simh/Disks/rsts1.dsk -dl "[1,2]ADVENT.DTA"
   ./flx -id simh/Disks/rsts1.dsk -pu "[1,2]ADVENT.DTA" < data/ADVENT_BINARY.DTA

   # Restart
   docker start advent
   ```

4. Test navigation works

### Then: Persist All Changes

The single-user ADVOUT.SUB also needs to be persisted to the disk image using the same flx approach.

## Binary File Transfer via TECO (WORKING METHOD)

**This is the reliable method for getting binary files onto RSTS/E.**

The problem: FLX tool only works reliably for files at low block offsets. Files placed at high offsets disappear when RSTS/E restarts.

The solution: Use DCL to create hex-encoded text, then TECO to convert to binary.

### How It Works

1. Connect via telnet to port 2323
2. Login as [1,2] with password Digital1977
3. Use TECO's `nI` command to insert characters by ASCII code
4. TECO commands terminate with double-escape (`\x1b\x1b`)

### TECO Binary File Creation

```python
import socket
import time

# Connect and login (code omitted for brevity)

# Start TECO
sock.send(b"TECO\r")
time.sleep(1)
# Wait for * prompt

# Open output file
sock.send(b"EWFILENAME.BIN\x1b\x1b")
time.sleep(0.5)

# Insert binary bytes using nI command (n = ASCII code)
# Example: "Hello" = 72, 101, 108, 108, 111
for byte_value in [72, 101, 108, 108, 111]:
    sock.send(f"{byte_value}I\x1b\x1b".encode())
    time.sleep(0.1)

# Exit and save
sock.send(b"EX\x1b\x1b")
```

### Key TECO Commands

- `EWFILE.EXT$$` - Open file for writing (EW = Enter for Writing)
- `nI$$` - Insert character with ASCII code n (e.g., `72I$$` inserts 'H')
- `ITEXT$$` - Insert literal text
- `EX$$` - Exit and save file
- `$$ = \x1b\x1b` (two escape characters)

### Files Created This Way SURVIVE RESTARTS

Tested and confirmed: Files created via TECO persist across Docker container restarts because they go through the proper RSTS/E file system.

### Transfer Script Location

See `scripts/teco_transfer.py` for the complete binary transfer implementation.

## Useful Commands

### flx Tool (USE WITH CAUTION)
```bash
# List directory
./flx -di simh/Disks/rsts1.dsk

# Extract file
./flx -id simh/Disks/rsts1.dsk -ge "[1,2]ADVENT.DTA" > extracted.dat

# Put file (disk must be dismounted) - MAY NOT PERSIST!
./flx -id simh/Disks/rsts1.dsk -pu "[1,2]FILENAME.EXT" < local_file
```

**WARNING**: FLX-injected files at high block offsets disappear on restart. Use TECO method instead.

### RSTS/E
```bash
# Login
User: [1,2]
Password: Digital1977

# Run game
RUN DM1:[1,2]ADVENT

# Compile BP2
RUN $BP2IC2
OLD DM1:[1,2]filename.SUB
COMPILE

# Clean shutdown
RUN $SHUTUP
```

## Binary Exit Format Details

```python
def create_correct_binary_exits(exits_dict):
    """Create 16-byte binary exit string"""
    result = bytearray(16)
    directions = ['N', 'S', 'E', 'W']

    for idx, d in enumerate(directions):
        pos = idx * 4
        room = exits_dict.get(d, 0)

        if room > 0:
            # Valid exit - put direction letter and room number
            result[pos] = ord(d)
            result[pos+1] = room & 0xFF        # Low byte
            result[pos+2] = (room >> 8) & 0xFF # High byte
            result[pos+3] = 0                  # Padding
        else:
            # No exit - put space (NOT direction letter!)
            result[pos] = ord(' ')
            result[pos+1] = 0
            result[pos+2] = 0
            result[pos+3] = 0

    return bytes(result)
```

Important: ADVDSP shows an exit if it finds a direction letter in the slot. If you put 'N' even with room=0, it will display "North" as an available exit. Only put the direction letter if the room number is non-zero.

## Room Structure

Players start in room 449. Room connectivity:
- Room 449: N->300
- Room 740: N->741, S->1 (connects to room 1)
- Room 1: N->740

The game has 1582 rooms with data out of 2000 slots.

## Contact

This resurrection project is at: https://github.com/edwh/advent-pdp11

---

Good luck, future Claude. The game is very close to working. The main blocker is just getting the correctly-formatted ADVENT.DTA onto the RSTS file system.
