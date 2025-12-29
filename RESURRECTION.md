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

4. **Set up the GitHub repository** - https://github.com/edwh/advent-pdp11

5. **Written this documentation** - Which you are reading, assuming you haven't given up already

### What Still Needs Doing

1. **Data file conversion** - The text room files need converting to binary RMS format. I'm working on a Python script for this.

2. **File transfer** - Getting the source code and data onto the RSTS/E disk image. The original authors helpfully included KERMIT.BAS for exactly this purpose.

3. **Testing** - Making sure the game actually runs, which is by no means guaranteed.

## How to Use This

### Building the Container

```bash
# Clone the repository (assuming you haven't already)
git clone https://github.com/edwh/advent-pdp11.git
cd advent-pdp11

# Build the Docker image
docker build -t advent-mud -f docker/Dockerfile .

# Run it
docker run -d -p 7681:7681 --name advent advent-mud
```

### Connecting

Point your web browser at http://localhost:7681

You should see a SIMH prompt, followed by the RSTS/E boot sequence.

### Booting RSTS/E

RSTS/E has, shall we say, a distinctive personality. Here's what to expect:

1. At `Option:` prompt, press **Enter** (or Ctrl-J, which sends a line feed)
2. Enter the date and time when prompted: `29-DEC-25 12:00`
3. At `Command File:` prompt, press **Enter**
4. Wait. Patience is a virtue, and RSTS/E will teach you this.
5. When you see activity stop, type: `HELLO 1,2`
6. Password: `SYSTEM`

If everything works, you'll see `Ready`, which is RSTS/E's way of saying "I'm listening".

### Playing the Game

Once logged in:
```
RUN ADVENT
```

This is the theory, anyway. In practice, the game won't run until I've finished the data conversion and file transfer. Check the repository for updates.

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
- **Me (Claude)**: For piecing all this together while trying to maintain my sanity

## Final Notes

If something doesn't work, which is likely, the following resources may help:

- The RSTS/E readme in `simh/Disks/rsts_readme.txt`
- The SIMH documentation at https://simh.trailing-edge.com/
- The original `NEWADV.RNO` documentation in this repository

If you're reading this and the game is actually running, then I've succeeded beyond my expectations. If not, well, I did warn you that life is never simple.

---

*"Many decades ago, this large circular room was of great importance, but its beauty has diminished..."*

— Room 9 description, Advent (1987)

---

This documentation was written by Claude, an AI assistant made by Anthropic, in December 2025. I found this project fascinating and hope you do too. If you have questions or improvements, the GitHub repository awaits.
