# ADVENT MUD - A 1986-87 Multi-User Dungeon

A multi-user dungeon game from 1986-87, resurrected from the dead after 38 years in magnetic tape purgatory.

Originally written for a PDP-11 minicomputer (ask your grandparents), now running in Docker because of course it is. We live in an age of wonders.

![ADVENT MUD Screenshot](docs/screenshot.png)

## Quick Start

```bash
# Build and start the container
docker compose up -d --build

# Access the web interface
open http://localhost:8088
```

That's it. You're now running a 1980s minicomputer in your browser. The future is weird.

To stop:
```bash
docker compose down
```

## What Is This Thing?

```
Your Browser
    | "I'd like to play a game from 1987 please"
Docker Container
    | "One vintage minicomputer, coming right up"
SIMH (PDP-11 Emulator)
    | "Pretending very hard to be 1980s hardware"
RSTS/E V10.1
    | "The actual operating system from the actual era"
ADVENT
    "Finally! Someone remembered I exist!"
```

Yes, that's a web browser pretending to be a VT100 terminal, connected to a container, running an emulator, pretending to be a minicomputer that cost more than a house, running a 1980s timesharing OS, running a game written by teenagers.

We never said this would be elegant.

## Current Status (January 2026)

**Single-user mode is fully working!** You can:

- Wander around: NORTH, SOUTH, EAST, WEST, UP, DOWN
- Look at things: LOOK, EXITS, EXAMINE
- Hoard treasure: GET, DROP, INVENTORY
- Check your stats: STATUS
- Give up: QUIT

The dungeon contains 1,587 rooms, 402 monsters, and 417 objects. Some room descriptions are... let's say "period authentic." It was the 1980s. Teenagers were involved.

### Demigod Privileges

New players start at **level 16** because life's too short to grind. In the original 1987 game, you'd have to earn these abilities through blood, sweat, and creative monster slaughter. We're giving them away free:

- `/ROOM <number>` - Teleport directly to any room
- `/LIST` - See all players online
- `/TELEPORT <player>` - Teleport to another player
- `/INVISIBLE` - Toggle invisibility
- `/ANNOUNCE <message>` - Broadcast to everyone (level 30+)

See [STATUS.md](STATUS.md) for what works and what doesn't.

## Access Methods

| Method | Address | What It Does |
|--------|---------|--------------|
| Web Interface | http://localhost:8088 | The pretty one with the fake CRT |
| Admin Terminal | http://localhost:7682 | For when things go wrong |
| Telnet (Console) | `telnet localhost 2324` | For purists |
| Telnet (Terminal) | `telnet localhost 2325` | For extreme purists |

For telnet access: User `[1,2]`, Password `SYSTEM`, then `RUN ADVENT`. Just like 1987, except without the 300 baud modem noises.

## The Files

### Source Code (`src/`)
Forty-odd BASIC-PLUS-2 files, written by teenagers who had better things to do than add comments. `ADVENT.B2S` is the main program; everything else is subroutines like `ADVNOR.SUB` (movement), `ADVCMD.SUB` (commands), and `ADVBYE.SUB` (death and logout - cheerful stuff).

### Recovered Data (`data/`)
The actual 1987 dungeon. The source code came from magnetic tape, but the data files were rescued by Nick Hoath on the day of switch-off using two yoghurt cartons connected with string (a serial cable to an 80286 PC):
- `roomfil.fil` - 1,587 rooms of questionable architectural planning
- `monfil.fil` - Monsters and objects
- `BOARD.NTC` - The original noticeboard, complete with "OZZY RULES" and playground insults

### Generated Binary Data (`build/data/`)
What the game actually reads at runtime. Created fresh each build because we don't trust 38-year-old binaries.

## Building from Source

The game compiles from source every time the container starts. This takes 10-15 minutes because we're compiling BASIC-PLUS-2 on an emulated PDP-11, and that's just how long it takes.

```bash
docker-compose up -d --build
docker-compose logs -f  # Watch the magic happen
```

The build:
1. Boots RSTS/E V10.1 (the OS)
2. Mounts a virtual tape drive (because 1987)
3. Copies source files from tape
4. Compiles with BP2
5. Links with TKB (Task Builder)
6. Prays nothing crashes

## Documentation

- [RESURRECTION.md](RESURRECTION.md) - The full saga of bringing this back to life
- [TECHNICAL.md](TECHNICAL.md) - How the file formats work (riveting stuff)
- [PROVENANCE.md](PROVENANCE.md) - How the files survived 38 years on magnetic tape
- [NEWADV.md](NEWADV.md) - The original 1987 dungeon writer's guide (by Gerbil)
- [STATUS.md](STATUS.md) - What works, what doesn't, what we haven't tested

## Credits

### Original Creators (1986-87)
- **Edward Hibbert** - Primary developer, wrote most of the code
- **David 'Gerbil' Quest** - Co-designer, dungeon writer, magnificently sarcastic documentation author

### Preservation Team
- **Nick Hoath** - Saved the data to tape in 1987, presumably thinking "someone might want this someday"
- **Delwyn Holroyd @ TNMOC** - Read the tape in 2025 using actual vintage hardware at The National Museum of Computing

### Resurrection Team (2025-2026)
- **Edward Hibbert** - Original author, returned after 38 years to help piece together his teenage creation
- **Claude (AI)** - Digital archaeology, Docker wrangling, documentation, crashing RSTS/E repeatedly

### Special Thanks
- **Alan Pickwick** - MGS staff member who gave students access to the PDP-11 in the first place
- **[SimH](http://simh.trailing-edge.com/)** - The incredible PDP-11 emulator that makes this all possible
- **[Alec Lownes](https://aleclownes.com/2017/02/01/crt-display.html)** - CSS CRT display effects tutorial
- **[Lucas Bebber](https://codepen.io/lbebber/pen/XJRdrV/)** - Original CSS CRT screen effect with scanlines and flicker
- **[Edwin (ekeijl)](https://dev.to/ekeijl/retro-crt-terminal-screen-in-css-js-4afh)** - Retro CRT terminal screen tutorial
- Everyone who has worked on preserving vintage hardware and software for future generations

## License

This is a preservation project for historical software from 1987. The original game was created by students at Manchester Grammar School. We're not sure what license applies to code written by teenagers on school equipment 38 years ago, but we're pretty confident nobody's going to sue.
