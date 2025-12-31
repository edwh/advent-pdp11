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
- **Several .RNO files** - Documentation in RUNOFF format

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
| `roomfil.fil` | 1,587 rooms with all their glorious descriptions |
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

My solution involves several layers of emulation and virtualization:

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
│  │         RSTS/E V10.1 Operating System         │  │
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

## The Journey

### Getting It Running

The process involved:

1. **Finding RSTS/E** - Available from trailing-edge.com under a hobbyist license from Mentec Corporation
2. **Creating a Docker container** - Using Alpine Linux, SIMH, and ttyd for web access
3. **Getting RSTS/E booting** - Learning that dates must be `DD-MMM-YY` format with a 1970s year
4. **Upgrading to V10.1** - V7 only had BASIC-PLUS; V10.1 includes the BASIC-PLUS-2 compiler
5. **Transferring files** - A saga unto itself (see TECHNICAL.md)
6. **Converting data** - Writing Python scripts to parse salvage data and generate binary files

### The File Transfer Problem

Getting files *into* a running RSTS/E system is absurdly difficult:

- The `flx` tool only writes to properly dismounted disks
- Paper tape emulation exists in SIMH, but RSTS/E lacks the driver
- Kermit exists as source code but needs compiling
- DECnet requires a proper implementation on the host side

The 1980s solution would have been a proper tape drive or DECnet connection. The 2020s solution was to patch files directly into the disk image before booting.

### The Data Conversion

I wrote Python scripts to:
1. Parse the text salvage files (roomfil.fil, monfil.fil)
2. Generate binary data with the exact format the game expects
3. Patch these onto the disk image using `flx`

This took considerable reverse-engineering of the BASIC-PLUS-2 source code to understand the exact binary format expected.

## Historical Context

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

## What's Next

**UPDATE December 31, 2025**: A simplified single-user version (MINI3.TSK) is now fully working!
- Room descriptions display correctly
- Navigation between rooms works (NORTH/SOUTH/EAST/WEST)
- LOOK command shows current room
- QUIT exits cleanly

What remains for the full version:
- Fix KB% terminal routing in ADVOUT.SUB
- Add combat and inventory systems
- Eventually, multi-user mode

## Credits

- **Original Authors**: David 'Gerbil' Quest and Edward Hibbert (1987)
- **SIMH Project**: For preserving computer history through emulation
- **Trailing-edge.com**: For hosting vintage software distributions
- **Mentec Corporation**: For the hobbyist license
- **Nick Hoath**: For saving the data files in 1987
- **Delwyn Holroyd @ TNMOC**: For reading the tape in 2025
- **Edward Hibbert & Claude (AI)**: For piecing all this together

## Final Notes

If something doesn't work, which is likely, see TECHNICAL.md for the gory details.

If you're reading this and the game is actually running, then I've succeeded beyond my expectations. If not, well, I did warn you that life is never simple.

---

*"Many decades ago, this large circular room was of great importance, but its beauty has diminished..."*

— Room 9 description, Advent (1987)

---

This documentation was written by Claude, an AI assistant made by Anthropic, in December 2025. I found this project fascinating and hope you do too.
