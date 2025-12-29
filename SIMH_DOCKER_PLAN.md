# Advent MUD on SIMH/RSTS/E Docker Plan

## Project Overview

Resurrect a 1987 multi-user dungeon game ("Advent") originally written for PDP-11/RSTS/E, running in a Docker container with web-based terminal access.

---

## What We Have

### Source Code (in `/home/edward/advent/`)

| Type | Files | Description |
|------|-------|-------------|
| `.B2S` | ~40 | BASIC-PLUS-2 source (main game code) |
| `.SUB` | 11 | BASIC-PLUS-2 subroutines (ADVCMD, ADVMSG, ADVNOR, etc.) |
| `.MAC` | 14 | MACRO-11 assembly (FORTH, SYSTAT, SPEAK, etc.) |
| `.BAS` | ~30 | BASIC utilities |
| `.RNO` | Several | RUNOFF documentation |

**Key game files:**
- `ADVENT.B2S` - Main game loop, handles 8 simultaneous users
- `ADV*.SUB` - Command handlers, messaging, display, combat
- `NEWADV.RNO` - Dungeon writer's guide (documentation)

### Data Files (extracted to `/home/edward/advent/data/`)

| File | Contents |
|------|----------|
| `roomfil.fil` | 1,601 rooms in text export format |
| `roomfil2.fil` | 1,601 rooms (backup/variant) |
| `monfil.fil` | 402 monsters + 417 objects (refresh data) |
| `peter` | RSTS/E terminal session log |

### Data Format Analysis

**Room file format (text, line-based):**
```
ROOM_NUMBER,EXITS           (e.g., "1,N740W700")
PEOPLE/MONSTERS             (* = aggressive, # = attacks on draw, ! = corpse)
OBJECTS                     (~XP for treasure, $damage for weapons)
DESCRIPTION                 (may span multiple lines)
SPECIAL_CASES               (/CCOMMAND/TTELL/SSHOUT/RROOM/etc.)
```

**Binary format expected by ADVENT.B2S (512 bytes per room):**
```basic
FIELD #3%, 1% AS ROOM$, 16% AS EX$, 83% AS PEOPLE$, 100% AS OBJECT$, 312% AS DESC$
```

**Required data files (from ADVINI.SUB):**
- `ADVENT.DTA` - Room database (binary, 512-byte records)
- `ADVENT.MON` - Monster definitions
- `ADVENT.CHR` - Character save data
- `BOARD.NTC` - Noticeboards
- `MESSAG.NPC` - NPC dialogue

---

## Architecture Plan

```
+-------------------+
|   Web Browser     |
+--------+----------+
         | HTTP/WebSocket
         v
+-------------------+
|   ttyd / wetty    |  <- Web terminal emulator
+--------+----------+
         | PTY
         v
+-------------------+
|   SIMH PDP-11     |  <- Emulator
+--------+----------+
         | Virtual hardware
         v
+-------------------+
|   RSTS/E OS       |  <- Operating system
+--------+----------+
         |
         v
+-------------------+
|   ADVENT game     |  <- BASIC-PLUS-2 program
+-------------------+
```

---

## Implementation Steps

### Phase 1: Docker Base Setup

1. **Start with existing SIMH Docker image**
   - Option A: `rattydave/alpine-simh` (includes multiple machines)
   - Option B: Build from `jguillaumes/dockersimh`
   - Option C: Custom build from SIMH source

2. **Add web terminal**
   - `ttyd` - Lightweight terminal over HTTP/WebSocket
   - Or `wetty` - Web-based terminal emulator
   - Expose port 7681 (ttyd default)

### Phase 2: RSTS/E Installation

**Sources for RSTS/E:**
- Official: https://simh.trailing-edge.com/software.html
  - `kits/rstsv7gen.tar.Z` (V7 distribution)
  - `kits/rstsv7swre.tar.Z` (V7 prebuilt)
- FTP: `ftp://ftp.trailing-edge.com/pub/rsts_dists/`
- GitHub: https://github.com/TerryEbdon/RSTS (V9.5 sysgen scripts)
- GitHub: https://github.com/agn453/RSTS-E (V10.1)

**Licensing:** Mentec granted free hobbyist license for non-commercial use.

**Version considerations:**
- V7: Available prebuilt, oldest
- V9.5/9.6: More features, sysgen scripts available
- V10.1: Final release (1998), Y2K support, matches original game era

### Phase 3: Data Conversion

Need to write a converter to transform text room files to binary format:

```python
# Pseudocode for converter
def convert_room(text_data):
    room_record = bytearray(512)
    room_record[0:1] = room_number        # 1 byte
    room_record[1:17] = exits             # 16 bytes (N####S####E####W####)
    room_record[17:100] = people          # 83 bytes
    room_record[100:200] = objects        # 100 bytes
    room_record[200:512] = description    # 312 bytes
    return room_record
```

### Phase 4: File Transfer

Options to get files into SIMH disk image:
1. **KERMIT** - Protocol supported (we have KERMIT.BAS and KERMIT.MAC!)
2. **rstsflx** - Paul Koning's utility to read/write RSTS disk images
3. **Build disk image** - Include files during disk creation

### Phase 5: Game Setup

1. Create RSTS/E accounts for players
2. Set up the ADVENT job to run as a detached process
3. Configure multi-user access (up to 8 simultaneous players)
4. Test character creation, room navigation, combat

---

## Docker Resources

### Existing Docker Images

| Image | Description |
|-------|-------------|
| [rattydave/alpine-simh](https://github.com/RattyDAVE/alpine-simh) | Alpine-based, multiple machines |
| [jguillaumes/dockersimh](https://github.com/jguillaumes/dockersimh) | Base SIMH image |
| [retroprom/docker](https://github.com/retroprom/docker) | Retrocomputing collection |
| [blarsen/docker-simh](https://github.com/blarsen/docker-simh) | Minimal SIMH |

### Sample Dockerfile Structure

```dockerfile
FROM alpine:latest

# Install dependencies
RUN apk add --no-cache build-base git ttyd

# Build SIMH
RUN git clone https://github.com/simh/simh.git && \
    cd simh && make pdp11

# Copy RSTS/E disk image
COPY rsts.dsk /opt/simh/

# Copy SIMH configuration
COPY pdp11.ini /opt/simh/

# Copy game files and data
COPY advent/ /opt/simh/advent/

# Expose web terminal port
EXPOSE 7681

# Start ttyd with SIMH
CMD ["ttyd", "-p", "7681", "/opt/simh/BIN/pdp11", "/opt/simh/pdp11.ini"]
```

---

## Game Features (from code analysis)

- **8 simultaneous players**
- **Commands:** LOOK, N/S/E/W, GET, DROP, HIT, TELEPORT, FIREBALL, HEAL, STUN, etc.
- **Character levels:** 0-30+ (demigods at 16+, gods at 30+)
- **Combat:** HP, XP, weapons with damage bonuses
- **Monsters:** Aggressive (*), defensive (#), corpses (!)
- **Special attacks:** Paralysis (/PA), Poison (/PO), Follow (/FO)
- **Objects:** Treasure (~XP), Weapons ($damage), Keys, Food
- **Special cases:** Room puzzles with /C, /T, /S, /R commands
- **Multi-user:** Tell, Shout, Announce, PvP combat

---

## Next Steps

1. [ ] Choose RSTS/E version (recommend V9.5 or V10.1)
2. [ ] Download RSTS/E disk images
3. [ ] Test basic SIMH + RSTS/E boot in Docker
4. [ ] Write Python converter for room data files
5. [ ] Transfer source code and data to RSTS/E disk
6. [ ] Compile/test ADVENT.B2S
7. [ ] Add ttyd web terminal layer
8. [ ] Create final Docker image
9. [ ] Document player instructions

---

## References

- SIMH Documentation: https://simh.trailing-edge.com/pdf/pdp11_doc.pdf
- RSTS/E Software: https://simh.trailing-edge.com/software.html
- RSTS/E History: https://gunkies.org/wiki/RSTS/E
- TerryEbdon RSTS Scripts: https://github.com/TerryEbdon/RSTS
- RattyDAVE Alpine SIMH: https://github.com/RattyDAVE/alpine-simh

---

*Document created: 2025-12-29*
*Project: Advent MUD Revival*
