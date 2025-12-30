# Advent: A 1987 Multi-User Dungeon

A multi-user dungeon game from 1987, originally for PDP-11/RSTS-E, now running in Docker via SIMH emulation.

## Status (December 30, 2025)

**Game Nearly Working!** - Room descriptions and exits display correctly. Navigation code runs but fails due to data format issue. Fix identified.

### What's Working
- RSTS/E V10.1 boots automatically in Docker
- BASIC-PLUS-2 compiler and Task Builder (TKB)
- Game compiles and links with overlay structure
- Single-user ADVOUT created (prints to console)
- Room descriptions display correctly
- Exit directions show (North, South, etc.)
- Web terminal access on ports 7681 (game) and 7682 (admin)
- Telnet access on port 2323

### Current Blocker
**Navigation fails** - "You cannot go in that direction" even when exits display.

**Root cause**: I was writing room data to wrong disk location (direct block writes bypassed RSTS file system).

**Solution**: Use `flx` tool to properly write `data/ADVENT_BINARY.DTA` to RSTS file system. See [CONTINUATION.md](CONTINUATION.md) for details.

## Quick Start

```bash
docker compose up -d
```

Then connect via:
- **Web terminal**: http://localhost:7681 (auto-login to game)
- **Admin terminal**: http://localhost:7682 (raw RSTS/E)
- **Telnet**: `telnet localhost 2323`

The system boots automatically. For telnet access, login with:
- User: `[1,2]`
- Password: `Digital1977`

## File Transfer Method

Getting files into RSTS/E is non-trivial. Here's how it works:

### The `flx` Tool
We use `flx` (from simtools) to read/write RSTS/E disk images directly:

```bash
# List files on disk
./flx
dir [1,2]

# Extract a file
get [1,2]ADVENT.DTA .

# Upload a file (disk must be cleanly dismounted)
put myfile.txt [1,2]MYFILE.TXT
```

**Limitation**: `flx` only writes to properly dismounted disks. If RSTS/E is running, you must shut down first.

### Current Workflow
1. Stop Docker container (or shutdown RSTS/E cleanly)
2. Use `flx` to modify disk images in `simh/Disks/`
3. Restart container - changes persist

### Expect Scripts
For runtime automation, we use expect scripts that telnet into RSTS/E and type commands:
- `boot_and_build.exp` - Boot, compile, and link game
- `final_single_user.exp` - Build single-user version

## Architecture

```
┌─────────────────────────────────────────┐
│  Web Browser → ttyd → SIMH → RSTS/E    │
│                                         │
│  SIMH emulates PDP-11/70               │
│  RSTS/E V10.1 timesharing OS           │
│  BASIC-PLUS-2 compiled game            │
│                                         │
│  Disk images: rsts0.dsk, rsts1.dsk     │
│  (RK07 format, ~27MB each)             │
└─────────────────────────────────────────┘
```

## Game Files

Game source and data on DM1:[1,2]:
- `ADVENT.B2S` - Main program
- `ADV*.SUB` - Subroutines (ADVINI, ADVNOR, ADVCMD, etc.)
- `ADVENT.TSK` - Linked executable (overlay structure)
- `ADVENT.DTA` - Room data (512 bytes × N rooms)
- `ADVENT.MON` - Monster spawn data
- `ADVENT.CHR` - Character saves

## What's Next

- [ ] **Write ADVENT.DTA correctly** - Use `flx` to put `data/ADVENT_BINARY.DTA` onto RSTS file system
- [ ] **Persist ADVOUT.SUB** - Also use `flx` to persist single-user output module
- [ ] **Test navigation** - Verify movement between rooms works
- [x] ~~Complete single-user mode output~~ (done - ADVOUT.SUB created)
- [x] ~~Room descriptions display~~ (done)
- [ ] Add mode switching (single/multi user)
- [ ] Full game testing

## Documentation

- [RESURRECTION.md](RESURRECTION.md) - How this was brought back to life
- [CONTINUATION.md](CONTINUATION.md) - Technical details for continuing this work
- [PROVENANCE.md](PROVENANCE.md) - How the files survived 37 years
- [NEWADV.RNO](src/NEWADV.RNO) - Original dungeon writer's guide (1987)

## Credits

**Original authors**: Edward Hibbert, David 'Gerbil' Quest (1987)
**Data preservation**: Nick Hoath
**Tape reading**: Delwyn Holroyd @ TNMOC
**Resurrection**: Edward Hibbert & Claude (AI), December 2025
