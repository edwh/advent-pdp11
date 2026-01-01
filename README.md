# Advent: A 1987 Multi-User Dungeon

A multi-user dungeon game from 1987, originally for PDP-11/RSTS-E, now running in Docker via SIMH emulation.

## Quick Start

```bash
# Build disk images with patched source and data
make build

# Start the Docker container
make run
```

Then connect via:
- **Web terminal (game)**: http://localhost:7681
- **Web terminal (admin)**: http://localhost:7682
- **Telnet**: `telnet localhost 2323`

For telnet access, login with:
- User: `[1,2]`
- Password: `Digital1977`

To run the game after login:
```
RUN ADVENT
```

## Status (January 2026)

**ADVENT SINGLE-USER MODE IS WORKING!** The full game runs in single-user mode:
- LOOK, NORTH/SOUTH/EAST/WEST navigation works
- GET/DROP object interaction works
- INVENTORY and STATUS commands work
- 1587 rooms with descriptions and exits
- Room data reads correctly from binary data files

Technical fixes applied:
- Terminal character translation (tilde → CHR$(126%))
- Exit data byte order parsing fixed
- Room record offset (+1 for header) applied
- Overlay structure fixed (ADVFND/ADVTDY in root segment)

Full status:
- RSTS/E V10.1 boots automatically in Docker
- Game source files patched into disk image via `flx` tool
- Data files generated from recovered 1987 salvage data
- 1587 rooms populated with descriptions and exits
- 402 monsters placed in their rooms

## Build Process

The build system:

1. **`scripts/migrate_data.py`** - Parses the salvage data files (roomfil.fil, monfil.fil) and generates proper RSTS/E binary format files
2. **`scripts/build_disk.py`** - Creates clean disk images and patches in source code and data files using the `flx` tool
3. **Docker builds** use the pre-built disk images

```bash
# Full build
make build        # Generate disk images
make docker       # Build Docker image
make run          # Start container

# Or use make rebuild for a complete clean rebuild
make rebuild
```

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

## Files

### Source Code (`src/`)
- `ADVENT.B2S` - Main program
- `ADV*.SUB` - Subroutines (ADVINI, ADVNOR, ADVCMD, etc.)
- `ADVENT.ODL` - Overlay descriptor for Task Builder

### Salvage Data (`data/`)
- `roomfil.fil` - 1587 rooms recovered from 1987
- `monfil.fil` - Monster and object definitions
- `REFRSH.CTL` - Monster spawn configuration

### Generated Data (`build/data/`)
- `ADVENT.DTA` - Room data (2000 × 512 bytes)
- `ADVENT.MON` - Monster spawns (10000 × 20 bytes)
- `ADVENT.CHR` - Character saves
- `BOARD.NTC` - Noticeboard
- `MESSAG.NPC` - NPC messages

## Documentation

- [RESURRECTION.md](RESURRECTION.md) - The story of bringing this back to life
- [TECHNICAL.md](TECHNICAL.md) - Technical details of the resurrection
- [CONTINUATION.md](CONTINUATION.md) - Guide for continuing this work
- [PROVENANCE.md](PROVENANCE.md) - How the files survived 37 years

## Credits

- **Original authors**: Edward Hibbert, David 'Gerbil' Quest (1987)
- **Data preservation**: Nick Hoath
- **Tape reading**: Delwyn Holroyd @ TNMOC
- **Resurrection**: Edward Hibbert & Claude (AI), December 2025 - January 2026
