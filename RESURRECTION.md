# Resurrecting Advent: A Tale of Digital Archaeology

```
First came.....   The Discovery
  Then..........   The Analysis
    And then.....   The Docker Container......


And now...
                RESURRECTION HELPTEXTS

                      present

             HOW I BROUGHT ADVENT BACK TO LIFE
             ---------------------------------

        Produced and directed by Claude (an AI), December 2025.
```

## In the Beginning

In the beginning, there was nothing.

Well, that's not quite true. There was a folder full of files dated July 4th, 1988, sitting on a modern computer, doing precisely nothing. The files had names like ADVENT.B2S and ADVMSG.SUB, and to the untrained eye they looked like gibberish.

Then the Human said 'Let there be understanding'. And I (Claude, an AI assistant) was summoned to make sense of it all.

And I looked upon the gibberish, and found it was not gibberish at all. It was a multi-user dungeon game. A proper one, from before the term "MUD" was even commonly used. Eight players could log in simultaneously, explore a dungeon of nearly 2000 rooms, fight monsters, cast spells, and presumably argue about who stole whose treasure.

And I said 'Ha! Let me figure out how to run this thing then!'

This, then, is the documentation of that process.

## What I Found

### The Source Code

I discovered approximately 226 files, comprising:

- **~40 .B2S files** - BASIC-PLUS-2 source code (the main game)
- **11 .SUB files** - Subroutines (combat, messaging, puzzles, and so on)
- **14 .MAC files** - MACRO-11 assembly (for when BASIC wasn't fast enough)
- **~30 .BAS files** - Various utilities
- **Several .RNO files** - Documentation in RUNOFF format (which is where I learned about the Gerbil and the painting of the Forth Bridge)

The game is called ADVENT, and it's wonderfully sophisticated for 1987:

| Feature | Description |
|---------|-------------|
| Multi-user | 8 simultaneous players sharing the same world |
| Combat | HP, XP, weapons with damage bonuses |
| Magic | Teleport, Fireball, Heal, Stun, Invisibility |
| Levels | 0-30+, with "demigods" at level 16+ |
| Puzzles | Special room commands and locked doors |
| Social | Tell, Shout, Announce, noticeboards |

It is, essentially, a MUD - written before most people had heard the term.

### The Data Files

The original binary data files were missing. This is a bit like finding a car with no fuel - technically complete, but not going anywhere.

However, I found text exports in a separate archive:

| File | What's in it |
|------|--------------|
| `roomfil.fil` | 1,601 rooms with all their glorious descriptions |
| `monfil.fil` | 402 monsters and 417 objects |

The rooms include locations such as Santa's Grotto, THOMAS COVENANT's retreate (sic), and various hobbit dwellings. One room description reads:

> "You are in a room which invites death."

I'm not making this up. Room 1999 actually says that.

A note on content: this game was created and maintained by teenage boys in the 1980s, and some of the room descriptions and monster names reflect that. The data files represent decades of accumulated student creativity, for better or worse.

## The Problem

The game was written for a **PDP-11 minicomputer** running **RSTS/E** (Resource Sharing Time Sharing / Extended). This was DEC's timesharing operating system, popular in educational institutions during the 1970s and 1980s.

I cannot simply run BASIC-PLUS-2 code on a modern computer. It uses features specific to RSTS/E - things like the SYS() function for low-level system calls, and RMS (Record Management Services) for binary file handling.

The data files I found are text exports, but the game expects binary files with 512-byte fixed-length records. Life, as they say, is never simple.

## The Solution

### The Architecture

My solution involves several layers of emulation and virtualization, which I shall now attempt to explain with an ASCII diagram:

```
┌─────────────────────────────────────────────────────┐
│                   Your Web Browser                   │
│              (http://localhost:7681)                │
└─────────────────────┬───────────────────────────────┘
                      │ "I'd like to play Advent please"
                      ▼
┌─────────────────────────────────────────────────────┐
│           Docker Container (Linux)                   │
│  ┌───────────────────────────────────────────────┐  │
│  │        ttyd (Web Terminal Emulator)           │  │
│  └─────────────────────┬─────────────────────────┘  │
│                        ▼                            │
│  ┌───────────────────────────────────────────────┐  │
│  │        SIMH (PDP-11 Emulator)                 │  │
│  │    "Pretends to be a 1970s minicomputer"      │  │
│  └─────────────────────┬─────────────────────────┘  │
│                        ▼                            │
│  ┌───────────────────────────────────────────────┐  │
│  │         RSTS/E V7 Operating System            │  │
│  │    "The actual OS from the actual era"        │  │
│  └─────────────────────┬─────────────────────────┘  │
│                        ▼                            │
│  ┌───────────────────────────────────────────────┐  │
│  │             ADVENT.B2S                         │  │
│  │    "The game itself, finally running"         │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

Yes, that's a web browser, pretending to be a terminal, connected to a container, running an emulator, pretending to be a minicomputer, running a 1970s operating system, running a 1987 game.

I never said this would be elegant.

### What I've Done So Far

1. **Analysed all the source files** - I now understand how the game works, which is more than can be said for some of the original documentation

2. **Obtained RSTS/E V7** - Available from trailing-edge.com under a hobbyist license from Mentec Corporation (the rights holders after DEC)

3. **Created a Docker container** - Using Alpine Linux, SIMH, and ttyd for web access

4. **Got RSTS/E booting** - After much trial and error, the system boots and runs. Key discoveries:
   - Date format must be `DD-MMM-YY` with a 1970s/80s year (e.g., `01-JUN-87`)
   - Time format is `HH:MM AM/PM`
   - Use Ctrl+J (linefeed) not Enter at prompts
   - Login with `HELLO 1,2` password `SYSTEM`

5. **Set up the GitHub repository** - https://github.com/edwh/advent-pdp11

6. **Written this documentation** - Which you are reading, assuming you haven't given up already

### What's Been Done

1. **Upgraded to RSTS/E V10.1** - V7 only had BASIC-PLUS; V10.1 includes BASIC-PLUS-2 V2.7-A compiler needed for the game source files.

2. **File transfer** - Game source files (127 files including .B2S, .SUB, and .MAC) transferred to RSTS/E disk image using `flx` tool from simtools. Files accessible at `DM1:[1,3]`.

3. **Docker with volume mounts** - Created docker-compose.yml with persistent disk volumes so changes survive container restarts.

4. **BP2 compiler working** - Fixed source code issues:
   - Changed `_DK1:` device references to `DM1:`
   - Changed `MSG:` logical to `NL:` (null device)
   - Compiler runs with `SET NOWARNING` to suppress deprecated syntax warnings

5. **All 14 modules compiled successfully**:
   - Main program: `ADVENT.B2S`
   - Subroutines: `ADVINI.SUB`, `ADVOUT.SUB`, `ADVNOR.SUB`, `ADVCMD.SUB`, `ADVODD.SUB`, `ADVMSG.SUB`, `ADVBYE.SUB`, `ADVSHT.SUB`, `ADVNPC.SUB`, `ADVPUZ.SUB`, `ADVDSP.SUB`, `ADVFND.SUB`, `ADVTDY.SUB`

6. **Linked with TKB overlay structure** - The game is 265KB+ which doesn't fit in 64KB PDP-11 memory, so it uses overlays. Successfully created `ADVENT.TSK` (189 blocks) using Task Builder with custom ODL file.

7. **Data file generation** - Created Python script to generate binary data files from recovered text exports:
   - `ADVENT.DTA` - 2000 rooms × 512 bytes (room descriptions, exits, monsters, objects)
   - `ADVENT.MON` - 10000 × 20 bytes (monster spawn data, populated from REFRSH.CTL with 402 monsters)
   - `ADVENT.CHR` - 100 × 512 bytes (character saves - empty placeholder)
   - `BOARD.NTC` - 512 × 512 bytes (noticeboard - empty placeholder)
   - `MESSAG.NPC` - 1000 × 60 bytes (NPC messages - empty placeholder)

8. **Python automation script** - Created `rsts_control.py` using pexpect for reliable terminal automation.

### The File Transfer Problem (A Tale of Woe)

Here's a problem I did not anticipate: getting files *into* a running RSTS/E system is absurdly difficult.

You might think, "It's an emulator! Just copy files to the disk image!" And you'd be half right. The `flx` tool from simtools can read and write RSTS/E disk images directly - but only if the disk was "properly dismounted." If RSTS/E is running, or crashed, or you looked at it funny, `flx` refuses to write:

```
?FLX -- Disk was not properly dismounted; use /RS switch to examine
```

The `/RS` switch lets you read, but not write. To write, you must shut down RSTS/E cleanly, which defeats the purpose of "real-time" file transfer.

**What about paper tape?** SIMH emulates a paper tape reader (ptr device). I configured it:

```ini
set ptr enable
attach ptr /opt/advent/disks/myfile.txt
```

Then in RSTS/E:
```
$ COPY PR: DM1:[1,2]MYFILE.TXT
?Not a valid device
```

The paper tape device driver isn't loaded in RSTS/E V10.1. The hardware exists in the emulator, but the OS doesn't know about it.

**What about Kermit?** There's a KERMIT.MAC file on the disk - source code only, not compiled. Even if I compiled it, Kermit requires a working serial connection and both ends running compatible software. Over a telnet connection to an emulator, this gets... complicated.

**What about FTP/SCP/NFS?** RSTS/E V10.1 has no TCP/IP stack. It uses DECnet for networking, which requires additional setup and a proper DECnet implementation on the host side. This is theoretically possible but practically insane.

**What about the CREATE command?** Ah, yes. I can type files in character by character:

```
$ CREATE MYFILE.TXT
This is line one
This is line two
^Z
```

This works! Until you try to transfer BASIC-PLUS-2 source code. BP2 uses a peculiar line continuation format: ampersand at end of line, backslash-tab at the start of the next:

```basic
10  COMMON A%, B%, C%, &
\	D%, E%, F%
```

The CREATE command mangles this. The backslash-tab becomes... something else. The compiler then complains:
```
?Illegal line format or missing continuation
```

**What about EDT (the editor)?** Same problem. EDT also corrupts the continuation format when saving.

**The solution I eventually found:** Edit files *in place* on RSTS/E using EDT's search-and-replace, avoiding any new line creation. This works for simple changes like `_DK1:` → `_DM1:`.

For transferring entirely new files? Boot RSTS/E, shut it down cleanly, use `flx` to write to the disk image, boot again. Each cycle takes about a minute. This is... suboptimal.

The 1980s solution would have been a proper tape drive or DECnet connection. The 2020s solution remains elusive.

### Current Challenge: File Creation and BP2 Library

**BP2 Resident Library Issue (SOLVED):**
After boot, must install BP2 resident library:
```
RUN $UTLMGR
INSTALL/LIBRARY SY:[0,1]BP2RES.LIB
^Z
```
This should be added to SY:[0,1]START.COM for automatic installation.

**File Device Assignment Issue (ONGOING):**
When creating virtual array files in BASIC, only the first file goes to the specified device (DM1:), subsequent files default to SY:. This is a BASIC-PLUS-2 quirk.

Workaround needed: Exit and re-enter BASIC for each file, or use DCL file operations.

**ADVENT.TSK Needs Rebuild:**
Game executable was accidentally deleted during testing. Can be rebuilt using TKB:
```
RUN $TKB
DM1:[1,2]ADVENT/FP=DM1:[1,3]ADVENT.ODL
/
```

**Data Files:**
Virtual array files need to be created inside RSTS/E with proper structure, then populated with room/monster data.

### Recent Progress (December 2025)

**Single-User Mode Working!**

After extensive debugging, we got the game to start in single-user mode:

1. **Fixed ADVINI.SUB** - Changed `_KB11:` (multi-keyboard device) to `_KB:` (single terminal). Removed message receiver SYS() calls that fail without the multi-user messaging system.

2. **Fixed starting room** - The original code tried to read room 449 (the cloud starting area), but the test data file only had 100 rooms. Changed to start at room 1.

3. **Game now starts!** - Shows welcome message, displays command prompt (`>`), accepts commands (LOOK, NORTH, QUIT).

**Successful test output:**
```
Welcome to ADVENT!
Type LOOK to see your surroundings.
Type HELP for commands.
Type QUIT to exit.

>
```

### Current Status (December 30, 2025)

**Major Progress:**
1. **Room descriptions display correctly** - Single-user ADVOUT.SUB created that prints to console
2. **Exit list displays** - Shows available directions (North, South, etc.)
3. **Full data file created** - 2000 rooms × 512 bytes with binary exit format

**Current Blocker: Navigation**

Navigation fails with "You cannot go in that direction" even when exits display. Root cause identified:

The game code uses `CVT$%` to read room numbers as 2-byte binary integers:
```basic
NEW.ROOM%=CVT$%(MID(EX$,PO%+1%,2%))
```

The data file I created (`data/ADVENT_BINARY.DTA`) has the correct binary format, but I was writing it to the wrong disk location (block 5922 vs RSTS file system at block 467).

**Solution:** Use `flx` tool to properly write files to RSTS file system:
1. Clean shutdown of RSTS/E
2. `./flx -id disk.dsk -pu "[1,2]ADVENT.DTA" < data/ADVENT_BINARY.DTA`
3. Boot again

See `CONTINUATION.md` for detailed instructions for continuing this work.

### What Still Needs Doing

1. **Write ADVENT.DTA correctly** - Use flx to put binary data file onto RSTS file system
2. **Persist ADVOUT.SUB** - Also use flx to persist single-user output module
3. **Test navigation** - Verify movement between rooms works
4. **Enable multi-user mode** - Re-enable message passing for multi-user play
5. **Web interface polish** - Create nicer web interface with framed terminal

## How to Use This

### Building the Container

```bash
# Clone the repository
git clone https://github.com/edwh/advent-pdp11.git
cd advent-pdp11

# Run with docker compose (recommended - persists disk changes)
docker compose up -d
```

Or manually:
```bash
docker build -t advent-mud -f docker/Dockerfile .
docker run -d -p 7681:7681 -p 7682:7682 -p 2322:2322 \
  -v ./simh/Disks:/opt/advent/disks \
  --name advent advent-mud
```

### Connecting

```bash
telnet localhost 2322
```

### Booting RSTS/E V10.1

1. At `Today's date?` → type **`1-JAN-92`** (D-MMM-YY format)
2. At `Current time?` → type **`12:00`** (24-hour format)
3. Press Enter at prompts to accept defaults
4. Wait for startup (ignore DECnet errors)
5. At `User:` → type **`[1,2]`**
6. At `Password:` → type **`Digital1977`**
7. At job prompt → press Enter for new job

### Compiling the Game

Start BP2 compiler:
```
RUN $BP2IC2
```

Then compile all modules and build:
```
OLD DM1:[1,3]ADVINI.SUB
SET NOWARNING
COMPILE
OLD DM1:[1,3]ADVOUT.SUB
COMPILE
OLD DM1:[1,3]ADVNOR.SUB
COMPILE
OLD DM1:[1,3]ADVCMD.SUB
COMPILE
OLD DM1:[1,3]ADVODD.SUB
COMPILE
OLD DM1:[1,3]ADVMSG.SUB
COMPILE
OLD DM1:[1,3]ADVBYE.SUB
COMPILE
OLD DM1:[1,3]ADVSHT.SUB
COMPILE
OLD DM1:[1,3]ADVNPC.SUB
COMPILE
OLD DM1:[1,3]ADVPUZ.SUB
COMPILE
OLD DM1:[1,3]ADVDSP.SUB
COMPILE
OLD DM1:[1,3]ADVENT.B2S
COMPILE
BUILD ADVENT=ADVENT,ADVINI,ADVOUT,ADVNOR,ADVCMD,ADVODD,ADVMSG,ADVBYE,ADVSHT,ADVNPC,ADVPUZ,ADVDSP
```

### Running the Game

After successful build:
```
BYE
RUN DM1:[1,3]ADVENT
```

## Understanding the Room Data

Since I spent considerable time decoding this, I might as well share my findings.

### Text Export Format

The room files look like this:
```
21,W20E601
*A cave lizard
A chest of jewels~50/Kamthra's Gerbil
You crawl into a tiny hole littered with droppings and blood. The stench of
 lizard is overpowering.
```

Where:
- `21` = Room number
- `W20E601` = Exits (West to room 20, East to room 601)
- `*A cave lizard` = Monster (* means aggressive)
- `~50` = Treasure worth 50 XP at a shrine
- The rest is the description

### Binary Format Expected

The game wants 512-byte records:
```
Bytes 0-0:     Room number verification (1 byte)
Bytes 1-16:   Exits as N####S####E####W#### (16 bytes)
Bytes 17-99:  People/monsters (83 bytes)
Bytes 100-199: Objects (100 bytes)
Bytes 200-511: Description and special cases (312 bytes)
```

### Monster Prefixes

| Prefix | Meaning |
|--------|---------|
| `*` | Aggressive - attacks on sight |
| `#` | Defensive - attacks when you draw weapon |
| `!` | Corpse or scenery (doesn't attack) |

### Object Suffixes

| Suffix | Meaning |
|--------|---------|
| `~XP` | Treasure worth XP points at shrine |
| `$damage` | Weapon with damage bonus |

## Historical Context

### The Era

It's worth pausing to consider what 1987 was like for computer users:

- The IBM PC was 6 years old
- The World Wide Web did not exist
- Multi-user games required expensive minicomputers
- Students connected via dumb terminals at 9600 baud
- "Online" meant connected to your institution's computer

### Why This Matters

This game represents genuinely sophisticated software engineering for its time. It handles:

- 8 concurrent users in a shared world
- Real-time combat and communication
- Persistent characters and world state
- A complex command parser with puzzles

It's not just a game - it's an artifact of a particular era in computing history.

## Credits and Acknowledgments

- **Original Authors**: David 'Gerbil' Quest and Edward Hibbert (1987)
- **SIMH Project**: For preserving computer history through emulation
- **Trailing-edge.com**: For hosting vintage software distributions
- **Mentec Corporation**: For the hobbyist license
- **Edward Hibbert & Claude (AI)**: For piecing all this together in December 2025

## Final Notes

If something doesn't work, which is likely, the following resources may help:

- The SIMH documentation: https://simh.trailing-edge.com/pdf/pdp11_doc.pdf
- RSTS/E software archive: https://simh.trailing-edge.com/software.html
- RSTS/E history and lore: https://gunkies.org/wiki/RSTS/E
- The original `NEWADV.RNO` documentation in this repository

If you're reading this and the game is actually running, then I've succeeded beyond my expectations. If not, well, I did warn you that life is never simple.

---

*"Many decades ago, this large circular room was of great importance, but its beauty has diminished..."*

— Room 9 description, Advent (1987)

---

This documentation was written by Claude, an AI assistant made by Anthropic, in December 2025. I found this project fascinating and hope you do too. If you have questions or improvements, the GitHub repository awaits.
