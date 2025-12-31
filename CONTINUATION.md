# Continuation Guide for Claude

This document is for another Claude instance continuing the Advent MUD resurrection project.

## Project Overview

Resurrecting a 1987 multi-user dungeon game (ADVENT) that runs on PDP-11/RSTS/E, now emulated via SIMH in Docker.

## Current State (December 31, 2025)

### MINI-ADVENT IS WORKING!

A simplified single-user version (`MINI3.TSK`) is now fully functional:
- **LOOK** command shows room descriptions and exits
- **NORTH/SOUTH/EAST/WEST** navigation works correctly
- **QUIT** command exits cleanly
- Room data read correctly from `ADVENT.DTA`

### What Works
- Docker container boots RSTS/E V10.1 successfully
- **MINI3.TSK** - Simplified single-user game, fully working
- Room descriptions display correctly (1587 rooms)
- Navigation between rooms works
- Exit display works
- BASIC-PLUS-2 compilation via BP2IC2 works
- TKB linking works

### The Original Multi-User Version
The full ADVENT.TSK compiles and links but has output routing issues:
- Uses `PRINT #1%, RECORD 32767+KB%` for multi-terminal output
- Single-user version sets KB%(1%)=0, sending output to KB0 instead of our terminal (KB5)
- Solution: Created MINI3 with direct PRINT statements

### How to Play

1. Start Docker: `docker-compose up -d`
2. Wait 60 seconds for RSTS/E to boot
3. Connect: `telnet localhost 2323`
4. Login: `[1,2]` / `Digital1977`
5. Run: `RUN SY:[1,2]MINI3`

## Technical Issues Solved

### Issue 1: CVT$% Byte Order

**Problem**: Room numbers stored little-endian (PDP-11 native), but `CVT$%` interprets big-endian.

Example: Bytes `44, 1` should be room 300 (44 + 1×256), but `CVT$%` returns 11265 (44×256 + 1).

**Solution**: Manual byte calculation:
```basic
NW%=ASC(MID(E$,I%+1%,1%))+256%*ASC(MID(E$,I%+2%,1%))
```

### Issue 2: Variable Name Conflict

**Problem**: `D$` used both as FIELD variable (description) and for direction storage.

**Solution**: Use `DIR$` for direction, keep `D$` for description field.

### Issue 3: Multi-User Output Routing

**Problem**: Original ADVOUT.SUB uses `PRINT #1%, RECORD 32767+KB%` to route output to specific terminals. Single-user version sets KB%(1%)=0, sending output to KB0 (console) instead of KB5 (our telnet).

**Solution**: Created MINI3.BAS with direct `PRINT` statements instead of ADVOUT calls.

### Exit Data Format

The game reads room exit data from `ADVENT.DTA`:

```
FIELD #3%, 1% AS ROOM$, 16% AS EX$, 83% AS PEOPLE$, 100% AS OBJECT$, 312% AS DESC$
```

Exit format (16 bytes = 4 exits × 4 bytes each):
- Byte 1: Direction letter ('N'/'S'/'E'/'W') or space if no exit
- Bytes 2-3: Room number as 16-bit little-endian binary
- Byte 4: Padding/condition

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

### MINI3 Source Code (Working Version)

The working MINI3.BAS is created on RSTS/E via Python script. Key features:
- Opens `ADVENT.DTA` with `MODE 256%` (no locking)
- Uses `EDIT$(COM$,32%)` for uppercase conversion
- Manual room number calculation with ASC() instead of CVT$%
- Direct PRINT for output

### Future Improvements

1. **Add more commands**: INVENTORY, GET, DROP, ATTACK, etc.
2. **Add monster encounters**: Read from ADVENT.MON
3. **Add objects**: Parse O$ field from room data
4. **Fix the full ADVENT.TSK**: Patch KB% routing in compiled binary
5. **Multi-user support**: Fix the ADVOUT terminal routing

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

## MINI3.BAS Source

For reference, the working minimal ADVENT (compiled to MINI3.TSK):

```basic
5       ROOM%=449%
10      OPEN 'ADVENT.DTA' AS FILE #3%, MODE 256%
20      FIELD #3%, 1% AS R$, 16% AS E$, 83% AS P$, 100% AS O$, 312% AS D$
25      PRINT 'Welcome to Mini-ADVENT!'
26      PRINT 'Commands: LOOK, NORTH, SOUTH, EAST, WEST, QUIT'
30      GET #3%, RECORD ROOM%
50      DES$=D$
55      I%=INSTR(1%,DES$,'$')
60      IF I%>0% THEN DES$=LEFT(DES$,I%-1%)
70      PRINT DES$
90      PRINT 'Exits:'
100     I%=1%
105     X$=MID(E$,I%,1%)
110     IF X$='N' THEN PRINT '  North'
115     IF X$='E' THEN PRINT '  East'
120     IF X$='S' THEN PRINT '  South'
125     IF X$='W' THEN PRINT '  West'
130     I%=I%+4%
135     GOTO 105 IF I%<=13%
145     PRINT '> ';
150     LINPUT COM$
155     COM$=EDIT$(COM$,32%)
160     GOTO 800 IF COM$='Q' OR COM$='QUIT'
165     GOTO 30 IF COM$='L' OR COM$='LOOK'
170     DIR$='N'
175     GOTO 300 IF COM$='N' OR COM$='NORTH'
...     (similar for E, S, W)
300     GET #3%, RECORD ROOM%
310     IF MID(E$,I%,1%)=DIR$ THEN GOTO 350
...     (find matching exit)
350     NW%=ASC(MID(E$,I%+1%,1%))+256%*ASC(MID(E$,I%+2%,1%))
370     ROOM%=NW%
380     GOTO 30
800     PRINT 'Thanks for playing!'
810     CLOSE #3%
820     END
```

## Contact

This resurrection project is at: https://github.com/edwh/advent-pdp11

---

**STATUS: MINI-ADVENT IS WORKING!** (December 31, 2025)

The simplified version reads room data, displays descriptions, and allows navigation. The full multi-user version needs the KB% routing fixed but that's a separate task.
