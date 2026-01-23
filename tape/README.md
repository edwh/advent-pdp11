# Original Tape Contents

These files are the **unmodified contents** of Edward Hibbert's backup tape from ~1987, as read by Delwyn Holroyd at The National Museum of Computing in January 2025.

## What's Here

This tape contains Edward's entire home directory from the school's PDP-11 running RSTS/E, including:

### ADVENT MUD Game (1986-7)
- `ADVENT.B2S` - Main game loop
- `ADV*.SUB` - Game subroutines (ADVNOR, ADVCMD, ADVODD, etc.)
- `ADVNPC.SUB` - NPC AI behavior
- `NEWADV.RNO` - Dungeon Master documentation
- `DEMIG.HLP` - Demigod help file
- `ADVENT.ODL` - Overlay definition (empty - the missing piece!)

### Library System
- `LIBR.B2S`, `LIBR.ODL` - School library management system
- Various `*INT.B2S`, `*LST.B2S` files - Library modules

### Utilities
- `KERMIT.BAS`, `KERMIT.MAC` - File transfer protocol
- `FORTH.MAC` - Forth interpreter (with Delwyn Holroyd's copyright!)
- `ZAPPER.MAC` - System utility
- Various `.CMD`, `.CTL` files - Command/control files

### Documentation
- `*.RNO` files - RUNOFF documentation format
- `*.HLP` files - Help files

## File Dates

All files are dated 4th July 1988 - this is when the tape was written, not when the files were created. The actual creation dates would have been 1986-1988.

## Relationship to Working Code

The `src/` directory contains the **modified versions** of the ADVENT files that have been updated to work in single-user mode in 2025-6. This `tape/` directory preserves the **original unmodified code** exactly as it was on the tape.

Key differences in `src/`:
- Single-user mode support added to ADVINI.SUB and ADVOUT.SUB
- ODL file reconstructed (the original was empty)
- Minor fixes for modern emulation

## See Also

- `PROVENANCE.md` - The story of how these files survived
- `RESURRECTION.md` - How the game was brought back to life
- `data/` - Data files from Nick Hoath's serial transfer (rooms, monsters)
