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

Getting files *into* a running RSTS/E system is extremely difficult. This section documents all approaches tried and the final working solution.

#### Approaches That FAILED

1. **FLX Tool (Partial Success)**
   - The `flx` tool from simtools can read/write RSTS/E disk images
   - **Problem**: Files injected at high block offsets (>~5000) disappear when RSTS/E restarts
   - Files at low block offsets survive, but we can't control allocation
   - The `clean` command fixes "disk not properly dismounted" errors
   - **Verdict**: Unreliable for persistent file transfer

2. **RT-11 RTS Programs with CALFIP (EMT 376)**
   - Attempted to write MACRO-11 assembly programs using CALFIP file I/O
   - Programs compile and link successfully with MACRO/RT11 + LINK/RT11
   - **Problem**: Crashes with "M-Ovly err at user PC" when EMT 376 executes
   - Root cause: RT-11 RTS doesn't support CALFIP EMT calls
   - **Verdict**: RT-11 RTS cannot do file I/O on RSTS/E

3. **RSX RTS Programs (.TSK files)**
   - Built with Task Builder (TKB)
   - **Problem**: Crashes with "Reserved instruction trap" at PC 000124
   - Crashes during RMS initialization before reaching user code
   - **Verdict**: RSX RTS file I/O also doesn't work for this purpose

4. **BASIC-PLUS-2 Programs**
   - **Problem**: "Unable to attach to resident library" and "Can't find file or account"
   - The BP2 resident library isn't properly configured on this system
   - **Verdict**: Can't run standalone BP2 programs

5. **Paper Tape (PTR:)**
   - SIMH can emulate paper tape reader
   - **Problem**: RSTS/E V10.1 doesn't have the paper tape driver installed
   - **Verdict**: Would require system reconfiguration

6. **Kermit**
   - KERMIT.MAC source exists in [1,3]
   - **Problem**: Would need compilation and serial port setup
   - **Verdict**: Too complex for this use case

#### The Working Solution: TECO Binary Transfer

**TECO (Text Editor and COrrector)** is available on the system and can insert characters by ASCII code using the `nI` command.

##### How It Works

1. Connect via telnet to port 2323
2. Login as `[1,2]` with password `Digital1977`
3. Start TECO: `TECO<CR>`
4. Use `EW` to open output file, `nI` to insert bytes, `EX` to save

##### TECO Command Reference

| Command | Description |
|---------|-------------|
| `EWFILE.EXT$$` | Open file for writing (Enter for Writing) |
| `nI$$` | Insert character with ASCII code n (0-255) |
| `ITEXT$$` | Insert literal text |
| `HT$$` | Type buffer contents |
| `Z=$$` | Show buffer size |
| `EX$$` | Exit and save file |
| `$$` | Two ESC characters (`\x1b\x1b`) terminate each command |

##### Critical Details

1. **Each command needs `$$`**: You cannot batch like `72I66I67I$$`. Each insert must be `72I$$66I$$67I$$`.

2. **Batching in single send()**: You CAN send multiple complete commands in one TCP send:
   ```python
   sock.send(b"72I\x1b\x1b66I\x1b\x1b67I\x1b\x1b")  # Works!
   ```

3. **All byte values work**: Tested 0x00 through 0xFF including:
   - Null bytes (0x00) - work correctly
   - Control characters (0x01-0x1F) - work correctly
   - High bytes (0x80-0xFF) - work correctly

4. **Files persist across restarts**: Unlike FLX-injected files, TECO-created files go through the proper RSTS/E file system and survive container restarts.

##### Transfer Script: `scripts/teco_transfer.py`

```python
#!/usr/bin/env python3
"""Transfer binary files to RSTS/E using TECO's nI command."""

import socket
import time

# Connection settings
HOST = 'localhost'
PORT = 2323
USER = '[1,2]'
PASSWORD = 'Digital1977'

# Each byte becomes "nI\x1b\x1b" where n is the decimal ASCII code
# Batch multiple commands per send() for speed
BATCH_SIZE = 100  # commands per batch

def transfer_file(local_path, remote_name):
    with open(local_path, 'rb') as f:
        data = f.read()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    # Login sequence...

    # Start TECO and open file
    sock.send(b"TECO\r")
    time.sleep(1)
    sock.send(f"EW{remote_name}\x1b\x1b".encode())

    # Transfer bytes in batches
    batch = []
    for byte_val in data:
        batch.append(f"{byte_val}I\x1b\x1b")
        if len(batch) >= BATCH_SIZE:
            sock.send(''.join(batch).encode())
            batch = []
            time.sleep(0.02)  # Prevent buffer overflow

    # Send remaining bytes
    if batch:
        sock.send(''.join(batch).encode())

    # Save and exit
    sock.send(b"EX\x1b\x1b")
```

##### Transfer Speed and Time Estimates

- **Effective rate**: ~100-200 bytes/second
- **Bottleneck**: TECO command processing, not network

| File | Size | Estimated Time |
|------|------|----------------|
| ADVENT.CHR | 51 KB | ~5-8 minutes |
| MESSAG.NPC | 59 KB | ~6-10 minutes |
| ADVENT.MON | 196 KB | ~20-30 minutes |
| BOARD.NTC | 256 KB | ~25-40 minutes |
| ADVENT.DTA | 1000 KB | ~1.5-2.5 hours |

##### Verification

After transfer, verify with FLX (requires stopping container first):

```bash
docker stop advent-mud
./flx << EOF
disk build/disks/rsts1.dsk
clean
get [1,2]FILENAME.EXT /tmp/extracted.bin
quit
EOF
diff /tmp/extracted.bin original_file.bin
docker start advent-mud
```

##### Tested and Confirmed Working

1. Created 1024-byte test file with pattern 0x00-0xFF repeated
2. Transferred via TECO
3. Extracted via FLX
4. Binary comparison: **IDENTICAL**
5. Container restart: **File persisted**

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

### Data Migration (`scripts/migrate_data.py`)

Converts text salvage files to binary format:

1. Parse `roomfil.fil` - Extract room number, exits, monsters, objects, description
2. Parse `REFRSH.CTL` - Extract monster spawn data
3. Generate binary files with proper record structure

### Disk Patching (`scripts/build_disk.py`)

Uses the `flx` tool from simtools:

1. Copy base disk image (rsts_backup.dsk)
2. Run `flx clean` to clear dirty flag
3. Patch source files to [1,3]
4. Patch data files to [1,2]

### Docker Build

The Dockerfile:
- Uses `rattydave/alpine-simh` as base
- Copies pre-built disk images
- Configures SIMH for auto-boot
- Sets up ttyd web terminals

## SIMH Configuration

Key settings in `pdp11.ini`:

```ini
; CPU setup
set cpu 11/44
set cpu 4M

; Disk drives
attach hk0 /opt/advent/disks/rsts0.dsk
attach hk1 /opt/advent/disks/rsts1.dsk

; Terminal multiplexer
attach dz 2323

; Auto-boot with expect scripts
expect "Today's date?" send "1-JAN-92\r"; continue
expect "Current time?" send "12:00\r"; continue
```

## RSTS/E Boot Sequence

1. Boot from HK0 (system disk)
2. Answer date/time prompts
3. Start timesharing
4. System runs [0,1]START.COM
5. User can login on DZ11 terminals

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

## Future Work

- Compile game from source within RSTS/E
- Enable multi-user mode (KB11: device)
- Test combat and inventory systems
- Verify all 1587 rooms are navigable
