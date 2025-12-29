# Advent: A 1987 Multi-User Dungeon

A multi-user dungeon game from 1987, originally for PDP-11/RSTS-E, now in Docker.

## Status

**RSTS/E V10.1 Running!** - Upgraded to V10.1 which includes BASIC-PLUS-2 compiler. Game source files accessible on DM1:[1,3].

## Quick Start

```bash
docker compose up -d
```

Or manually:
```bash
docker build -t advent-mud -f docker/Dockerfile .
docker run -d -p 7681:7681 -p 7682:7682 -p 2322:2322 \
  -v ./simh/Disks:/opt/advent/disks \
  --name advent advent-mud
```

**Connecting** (manual boot currently required):
```bash
telnet localhost 2322
```

**Boot sequence** (V10.1):
1. At `Today's date?` → type **`1-JAN-92`** (D-MMM-YY format)
2. At `Current time?` → type **`12:00`** (24-hour format)
3. Press Enter at prompts to accept defaults
4. Wait for startup (ignore DECnet errors)
5. At `User:` → type **`[1,2]`**
6. At `Password:` → type **`Digital1977`**
7. At job prompt → press Enter for new job

## What Works

- RSTS/E V10.1 boots in SIMH PDP-11 emulator (RK07 disks)
- BASIC-PLUS-2 V2.7-A compiler included
- System startup and login functional
- Docker container with ttyd web terminal and volume mount for persistent disks
- Game source files accessible on DM1:[1,3]

## Accessing Game Files

After login, the game files are on the second disk:
```
DIR DM1:[1,3]
```

## Compiling the Game

Start the BP2 compiler:
```
RUN $BP2IC2
```

Compile all modules (paste this block):
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

## What's Next

- Test compiled game
- Automate boot sequence
- Create web interface with framed terminal

## Documentation

- [RESURRECTION.md](RESURRECTION.md) - How this was brought back to life
- [PROVENANCE.md](PROVENANCE.md) - How the files survived 37 years
- [NEWADV.RNO](src/NEWADV.RNO) - Original dungeon writer's guide (1987)

## Credits

**Original authors**: Edward Hibbert, David 'Gerbil' Quest (1987)
**Data preservation**: Nick Hoath
**Tape reading**: Delwyn Holroyd @ TNMOC
**Resurrection**: Edward Hibbert & Claude (AI), December 2025
