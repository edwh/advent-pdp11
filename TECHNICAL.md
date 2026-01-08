# Technical Details: Resurrecting Advent

This document covers the technical aspects of bringing a 1987 BASIC-PLUS-2 game back to life on modern hardware.

## The Challenge

The game was written for:
- **Hardware**: PDP-11 minicomputer
- **OS**: RSTS/E (Resource Sharing Time Sharing / Extended)
- **Language**: BASIC-PLUS-2 with MACRO-11 assembly routines
- **Data**: Binary files with 512-byte fixed-length records

None of this runs on modern computers directly.

## Solution Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Docker Container                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │        SIMH PDP-11 Emulator                       │  │
│  │    "Pretends to be a 1970s minicomputer"          │  │
│  └─────────────────────┬─────────────────────────────┘  │
│                        ▼                                │
│  ┌───────────────────────────────────────────────────┐  │
│  │         RSTS/E V10.1 Operating System             │  │
│  │    "The actual OS from the actual era"            │  │
│  └─────────────────────┬─────────────────────────────┘  │
│                        ▼                                │
│  ┌───────────────────────────────────────────────────┐  │
│  │             ADVENT.TSK + Data Files               │  │
│  │    "The game itself, finally running"             │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Key Technical Challenges

### 1. File Transfer into RSTS/E

Getting files *into* a running RSTS/E system was one of the biggest challenges. After trying many approaches, we found that **TMSCP tape emulation** provides the fastest and most reliable method.

#### Approaches That FAILED

1. **FLX Tool** - Files injected at high block offsets vanish after RSTS/E restarts
2. **RT-11/RSX RTS Programs** - Crash with "Reserved instruction trap"
3. **BASIC-PLUS-2 Programs** - "Can't find resident library" errors
4. **Paper Tape** - Driver not installed on this RSTS/E image
5. **TECO Text Editor** - Works but painfully slow (~160 bytes/sec)

#### The Working Solution: TMSCP Tape Transfer

SIMH can emulate a **TMSCP tape drive** (TQ controller) which RSTS/E sees as device `MU0:`. This provides **18KB/sec** transfer speed - 140x faster than TECO.

##### How It Works

1. **Build Phase** (Docker image creation):
   - `scripts/create_advent_tape.py` creates a DOS-11 format tape image
   - Tape contains source files (.B2S, .SUB) and data files (.DTA, .MON, .CHR)
   - SIMH configuration attaches tape: `attach tq0 /opt/advent/tapes/advent_source.tap`

2. **Runtime Phase** (container startup):
   - RSTS/E boots from RA72 disk image
   - `build_advent.exp` script logs in and mounts tape: `MOUNT MU0: ADVENT`
   - Files copied from tape: `COPY MU0:filename SY:`
   - Source compiled with BP2, linked with TKB

##### Transfer Speed Comparison

| Method | Speed | 1MB File Time |
|--------|-------|---------------|
| TECO (nI command) | ~160 B/s | 1.7 hours |
| TMSCP Tape (MU0:) | ~18 KB/s | 55 seconds |

##### Tape Creation (`scripts/create_advent_tape.py`)

Creates DOS-11 format tape images compatible with RSTS/E:

```python
# Add file to tape in DOS-11 format
def add_file_to_tape(tape_data, filename, content):
    # DOS-11 header: 14-byte filename, then data blocks
    header = filename.ljust(14).encode('ascii')
    tape_data.extend(header)
    # ... block formatting
```

### 2. Binary Data Format

The game expects 512-byte records with this structure (from ADVNOR.SUB):

```basic
FIELD #3%, 1% AS ROOM$, 16% AS EX$, 83% AS PEOPLE$, 100% AS OBJECT$, 312% AS DESC$
```

**Record Layout (512 bytes):**
- Byte 0: Room number low byte (verification)
- Bytes 1-16: Exits (4 bytes per direction: N, S, E, W)
  - Byte 0: Direction letter or space
  - Bytes 1-2: Room number (16-bit little-endian)
  - Byte 3: Padding
- Bytes 17-99: Monsters (83 bytes)
- Bytes 100-199: Objects (100 bytes)
- Bytes 200-511: Description (312 bytes)

### 3. Exit Parsing

The code uses `CVT$%` to convert 2-byte strings to integers:

```basic
NEW.ROOM%=CVT$%(MID(EX$,PO%+1%,2%))
```

This means exits must be stored as binary integers, not ASCII.

### 4. Memory Constraints

The PDP-11 has 64KB address space. The game is 265KB+, requiring overlays:

```
Root segment: Core code + common variables
Overlays: Each subroutine loaded on demand
```

Task Builder (TKB) creates the overlay structure from ADVENT.ODL.

## Build System

The build system compiles ADVENT from source on every container start. This ensures source code changes are always reflected in the running game.

### Data Migration (`scripts/migrate_data.py`)

Converts text salvage files to binary format:

1. Parse `roomfil.fil` - Extract room number, exits, monsters, objects, description
2. Parse `REFRSH.CTL` - Extract monster spawn data
3. Generate binary files with proper record structure

### Room Reconstruction (`scripts/reconstruct_rooms.py`)

The original dungeon map was incomplete (only 4,201 of ~6,000+ exits). This script:

1. Analyzes existing exit patterns
2. Discovers room clusters (Labyrinth, Arena, Shop etc.)
3. Connects isolated rooms using heuristics
4. Generates `dungeon_map.json` for the web map viewer

### Tape Creation (`scripts/create_advent_tape.py`)

Creates a DOS-11 format tape image containing all source and data files:

```
ADVENT.B2S      Main program
ADVINI.SUB      Initialization
ADVOUT.SUB      Output routines (in ROOT segment)
ADVNOR.SUB      Room handling
ADVCMD.SUB      Command parsing
...etc...
ADVENT.DTA      Room data (813KB)
ADVENT.MON      Monster data
ADVENT.CHR      Character data
```

### Docker Build

The Dockerfile:
- Builds SIMH PDP-11 emulator from source
- Uses base RA72 disk image with RSTS/E V10.1 (no ADVENT)
- Copies source files and creates tape image at build time
- Runs room reconstruction to reconnect dungeon exits
- On container start: boots RSTS/E, copies from tape, compiles, links

### Build-from-Source Workflow

Every container start:

1. Restore pristine disk image (prevents corruption from unclean shutdown)
2. Boot RSTS/E from RA72 disk
3. Mount TMSCP tape: `MOUNT MU0: ADVENT`
4. Copy source files: `COPY MU0:*.B2S SY:` etc.
5. Copy data files: `COPY MU0:*.DTA SY:` etc.
6. Compile with BP2: `OLD SY:filename` then `COMPILE`
7. Link with TKB using ADVENT.ODL overlay definition
8. Test game startup

Build time: ~10-15 minutes on first start.

## SIMH Configuration

Key settings in `pdp11_ra72.ini`:

```ini
; CPU setup
set cpu 11/44
set cpu 4M

; Throttle to realistic speed (~1.5 MIPS)
set throttle 1500K

; RA72 disk (1GB) with MSCP controller
set rq0 ra72
attach rq0 /opt/advent/disks/rstse_10_ra72.dsk

; TMSCP tape for file transfer
set tq enable
attach tq0 /opt/advent/tapes/advent_source.tap

; Terminal multiplexer
set dz enable
set dz lines=8
attach dz 2323

; Console on TCP (buffered for auto-boot)
set console telnet=2322
set console telnet=buffered

; Auto-boot with expect scripts
expect "Today's date?" send "1-JAN-92\r"; continue
expect "Current time?" send "12:00\r"; continue
expect "Start timesharing?" send "Y\r"; continue

boot rq0
```

## RSTS/E Boot Sequence

1. Boot from RQ0 (RA72 system disk via MSCP controller)
2. SIMH expect scripts answer date/time prompts automatically
3. Start timesharing (answered automatically)
4. System runs [0,1]START.COM
5. `build_advent.exp` logs in and compiles ADVENT from tape
6. Users can login via web interface or DZ11 terminals

## Data Recovery

The salvage data came from Nick Hoath's serial transfer in ~1987:

**roomfil.fil format:**
```
21,W20E601
*A cave lizard
A chest of jewels~50/Kamthra's Gerbil
You crawl into a tiny hole littered with droppings...
```

Where:
- `21` = Room number
- `W20E601` = Exits (West to 20, East to 601)
- `*A cave lizard` = Aggressive monster
- `~50` = Treasure worth 50 XP
- Rest = Room description

## Testing

The test script (`scripts/test_setup.py`) verifies:

1. Disk images exist and are correct size
2. Data files have expected sizes
3. Ports are responding
4. Login works (with pexpect)
5. Game starts

## Accomplished

- **Build from source**: Game compiles on every container start via TMSCP tape transfer
- **Room reconstruction**: 4,201 exits connected, enabling navigation of most rooms
- **Web interface**: CRT-style terminal with status overlay and session takeover

## Future Work

- Enable multi-user mode (KB11: device for multiple concurrent players)
- Test combat and inventory systems
- Verify all 1590 rooms are navigable
- Add character persistence between sessions
