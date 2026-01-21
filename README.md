# ADVENT MUD - A 1987 Multi-User Dungeon

A multi-user dungeon game from 1987, originally written for PDP-11/RSTS-E, now running in Docker via SIMH emulation.

**Live Demo:** [https://advent-pdp11.fly.dev](https://advent-pdp11.fly.dev)

![ADVENT MUD Screenshot](docs/screenshot.png)

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Build and start the container
docker compose up -d --build

# Access the web interface
open http://localhost:8088
```

To stop:
```bash
docker compose down
```

### Access Methods

Once running, you can connect via:

| Method | Address | Description |
|--------|---------|-------------|
| Web Interface | http://localhost:8088 | CRT terminal with auto-login |
| Admin Terminal | http://localhost:7682 | Web-based admin access |
| Telnet (Console) | `telnet localhost 2324` | Operator console |
| Telnet (Terminal) | `telnet localhost 2325` | User terminal (DZ11) |

For telnet access:
- User: `[1,2]`
- Password: `SYSTEM`
- Command: `RUN ADVENT`

## Current Status (January 2026)

**Single-user mode is fully working!**

- Navigation: NORTH/SOUTH/EAST/WEST, UP/DOWN
- Exploration: LOOK, EXITS
- Objects: GET/TAKE, DROP, INVENTORY
- Character: STATUS, QUIT
- 1,587 rooms with descriptions and exits
- 402 monsters placed in their rooms
- 417 objects available

### Demigod Privileges (For Exploration)

New players start at **level 11 (demigod)** so you can explore the dungeon freely. This is just for fun - in the original 1987 game, you had to earn these abilities!

- `/TELEPORT <player>` - Teleport to another player
- `/LIST` - See all players online and their locations
- `/ROOM <number>` - Teleport directly to a room number (level 16+)
- `/INVISIBLE` - Toggle invisibility (level 16+)
- `/ANNOUNCE <message>` - Broadcast to all players (level 30+)

See [STATUS.md](STATUS.md) for detailed feature status.

## Architecture

```
Browser ---> nginx ---> ttyd ---> expect ---> SIMH ---> RSTS/E ---> ADVENT
   |                      |                     |
   |   CRT Terminal UI    |   Auto-login      PDP-11/70 emulator
   |   with status overlay|   script           running 1980s OS
```

- **Docker container** hosts all components
- **nginx** serves web UI and proxies terminal connections
- **ttyd** provides web-based terminal access
- **expect scripts** handle automatic login and game startup
- **SIMH** emulates a PDP-11/70 minicomputer
- **RSTS/E V10.1** is the authentic 1980s timesharing OS
- **ADVENT** is the BASIC-PLUS-2 compiled game

## Files

### Source Code (`src/`)
- `ADVENT.B2S` - Main program
- `ADV*.SUB` - Subroutines (ADVINI, ADVNOR, ADVCMD, etc.)
- `ADVENT.ODL` - Overlay descriptor for Task Builder

### Recovered Data (`data/`)
- `roomfil.fil` - 1,587 rooms from 1987
- `monfil.fil` - Monster and object definitions
- `BOARD.NTC` - Noticeboard with authentic 1987 player messages

### Generated Binary Data (`build/data/`)
- `ADVENT.DTA` - Room data (2000 x 512 bytes)
- `ADVENT.MON` - Monster spawns (10000 x 20 bytes)
- `ADVENT.CHR` - Character saves
- `MESSAG.NPC` - NPC messages
- `dungeon_map.json` - Room connectivity for web map viewer

### Disk Images (`simh/Disks/ra72/`)
- `rstse_10_ra72.dsk` - Base RSTS/E V10.1 RA72 image (1GB, no ADVENT)

## Building from Source

The game compiles from source on every container start (~10-15 minutes):

```bash
# Build and run with Docker Compose
docker-compose up -d --build

# Watch the build progress
docker-compose logs -f
```

The build process:
1. Restores pristine RA72 disk image
2. Boots RSTS/E V10.1
3. Copies source files from TMSCP tape
4. Compiles with BP2 (BASIC-PLUS-2)
5. Links with TKB (Task Builder)

## Documentation

- [RESURRECTION.md](RESURRECTION.md) - The story of bringing this back to life
- [TECHNICAL.md](TECHNICAL.md) - Technical details of the file formats and transfer
- [CONTINUATION.md](CONTINUATION.md) - Guide for continuing development
- [PROVENANCE.md](PROVENANCE.md) - How the files survived 37 years
- [NEWADV.md](NEWADV.md) - Original 1987 dungeon writer's guide
- [STATUS.md](STATUS.md) - Feature implementation status

## Known Issues

1. **Extra "?" prompts** - CR/LF handling causes occasional extra prompts
2. **Exit display alignment** - Tab characters not rendering correctly
3. **Multi-user mode** - File locking prevents concurrent access

## Credits

### Original Creators (1987)
- **Edward Hibbert** - Primary developer, wrote most of the code
- **David 'Gerbil' Quest** - Co-designer, dungeon writer, documentation author

### Preservation Team
- **Nick Hoath** - Saved the data files to tape in 1987
- **Delwyn Holroyd @ TNMOC** - Read the tape in 2025

### Resurrection Team (2025-2026)
- **Edward Hibbert** - Original author, returned to help resurrect the game
- **Claude (AI)** - Digital archaeology, Docker containerization, documentation

### Special Thanks
- **Alan Pickwick** - MGS staff member who gave students access to the PDP-11

## License

This is a preservation project for historical software from 1987. The original game was created by students at Manchester Grammar School.
