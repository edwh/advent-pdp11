# Development Notes

Internal development context for Claude Code sessions.

## Current State (January 3, 2026)

### Docker Build

- **Root Dockerfile** builds same image as fly.io
- **SIMH v4.0-Beta-1** boots RSTS/E successfully
- **Console connection** (port 2322) is more reliable than DZ terminals
- **Boot time** ~2 minutes, detected by verify_ready.exp

### Console vs DZ Terminals

We switched from DZ terminals (port 2323) to console (port 2322) because:
- DZ terminals are flaky - sometimes don't respond with User: prompt
- Console is special in RSTS/E - always available and reliable
- Single-user mode only needs one terminal anyway

Files changed:
- `docker/game_connect.exp` - connects to port 2322 instead of 2323
- `docker/verify_ready.exp` - checks console, handles multiple prompt types

### Known Issues

1. **^B character in exit display** - appears after "West"
2. **Tab alignment** - exits display has formatting issues
3. **Extra "?" prompts** - stty fix deployed, needs testing on fly.io

## Disk Images

| File | Purpose |
|------|---------|
| `rsts0.dsk` | Boot disk (working copy) |
| `rsts1.dsk` | Game disk (working copy) |
| `rsts0-base-os.dsk` | Clean RSTS/E image |
| `rsts1-base-os.dsk` | Clean game disk |

To reset to clean state:
```bash
cp build/disks/rsts0-base-os.dsk build/disks/rsts0.dsk
cp build/disks/rsts1-base-os.dsk build/disks/rsts1.dsk
```

## Build Commands

```bash
# Build Docker image (same as fly.io):
docker build -f Dockerfile -t advent-mud .

# Run locally:
docker run -d --name advent-mud -p 8080:8080 advent-mud

# Test via telnet:
telnet localhost 2322
```

## File Transfer Notes

**IMPORTANT:** The `flx` tool truncates large files. Use TECO transfer instead.

- `scripts/setup_advent.py` uses TECO to transfer files properly
- TECO transfer rate: ~120-130 bytes/sec
- ADVENT.DTA (1MB) takes ~2 hours via TECO

## Key Source Files

- `src/ADVOUT.SUB` - Output handling, SINGLE.USER% flag
- `src/ADVINI.SUB` - Initialization, sets SINGLE.USER%=-1%
- `scripts/migrate_data.py` - Converts salvage data to RSTS/E format
- `scripts/build_disk.py` - Creates disk images

## RSTS/E Notes

- Login: `[1,2]` / `Digital1977`
- Run game: `RUN ADVENT`
- Console is KB0 (port 2322)
- DZ terminals are KB1-KB8 (port 2323)

## Deployment

Fly.io auth token is in `/home/edward/.env`. To deploy:

```bash
source /home/edward/.env
/home/edward/.fly/bin/flyctl deploy --remote-only
```
