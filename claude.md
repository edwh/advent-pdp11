# Development Notes

Internal development context for Claude Code sessions.

## CRITICAL: How to Build and Run a Working Container

**Last verified: January 3, 2026**

These are the EXACT commands that work. Do not deviate.

### Step 1: Ensure Disk Images Are Clean

The git-committed disk images (`build/disks/rsts0.dsk` and `build/disks/rsts1.dsk`) are the working ones. If you've modified them and broken things:

```bash
# Restore from git (PREFERRED - these have ADVENT pre-installed)
git checkout build/disks/rsts0.dsk build/disks/rsts1.dsk

# OR reset to base OS (ADVENT not installed, requires full setup)
cp build/disks/rsts0-base-os.dsk build/disks/rsts0.dsk
cp build/disks/rsts1-base-os.dsk build/disks/rsts1.dsk
```

### Step 2: Build Docker Image

```bash
# Use the ROOT Dockerfile (NOT docker/Dockerfile)
docker build -f Dockerfile -t advent-mud .
```

### Step 3: Run Container

```bash
# Stop any existing container first
docker stop advent-mud 2>/dev/null; docker rm advent-mud 2>/dev/null

# Run with exposed ports
docker run -d --name advent-mud -p 8080:8080 -p 2322:2322 -p 2323:2323 advent-mud

# Wait ~2 minutes for RSTS/E to boot, then check logs
docker logs advent-mud
```

### Step 4: Verify It Works

```bash
# Web interface
open http://localhost:8080

# Or telnet to console
telnet localhost 2322
# Login: [1,2] / Digital1977
# Command: RUN ADVENT
```

## WARNING: Common Mistakes That Break Things

### DO NOT modify disk images while RSTS/E is running
The container must be STOPPED before using `flx` on disks. Modifying disks while running causes corruption ("swap file is invalid" errors on next boot).

### DO NOT use docker-compose for local development
The `docker-compose.yml` uses volume mounts which can cause issues. Use the plain `docker run` command above.

### DO NOT use docker/Dockerfile
There are multiple Dockerfiles. Use the ROOT `Dockerfile` only.

### DO NOT use `flx clean` on the boot disk (rsts0.dsk)
This can corrupt system files causing "Odd address trap" errors.

## Disk Images

| File | Purpose | Contains ADVENT? |
|------|---------|------------------|
| `build/disks/rsts0.dsk` | Boot disk (working copy) | No (system files only) |
| `build/disks/rsts1.dsk` | Game disk (working copy) | **YES** |
| `build/disks/rsts0-base-os.dsk` | Clean RSTS/E image | No |
| `build/disks/rsts1-base-os.dsk` | Clean game disk | No |

The git-committed working copies have ADVENT.TSK and all data files pre-installed.

## Current State (January 3, 2026)

### What Works
- Full ADVENT game running in single-user mode
- CRT web interface with auto-login
- Navigation, inventory, combat commands
- 1,587 rooms with descriptions
- 402 monsters, 417 objects

### Known Issues
1. **^B character in exit display** - appears after "West"
2. **Tab alignment** - exits display has formatting issues
3. **Multi-user mode** - file locking prevents concurrent access

## Console vs DZ Terminals

We switched from DZ terminals (port 2323) to console (port 2322) because:
- DZ terminals are flaky - sometimes don't respond with User: prompt
- Console is special in RSTS/E - always available and reliable
- Single-user mode only needs one terminal anyway

Files changed:
- `docker/game_connect.exp` - connects to port 2322 instead of 2323
- `docker/verify_ready.exp` - checks console, handles multiple prompt types

## Key Source Files

- `src/ADVOUT.SUB` - Output handling, SINGLE.USER% flag
- `src/ADVINI.SUB` - Initialization, sets SINGLE.USER%=-1%
- `scripts/migrate_data.py` - Converts salvage data to RSTS/E format

## RSTS/E Notes

- Login: `[1,2]` / `Digital1977`
- Run game: `RUN ADVENT`
- Console is KB0 (port 2322)
- DZ terminals are KB1-KB8 (port 2323)

## File Transfer Notes

**IMPORTANT:** The `flx` tool has limitations. Use TECO transfer for reliability.

- `scripts/setup_advent.py` uses TECO to transfer files properly
- TECO transfer rate: ~120-130 bytes/sec
- ADVENT.DTA (1MB) takes ~2 hours via TECO

## Deployment to fly.io

Fly.io auth token is in `/home/edward/.env`. To deploy:

```bash
source /home/edward/.env
/home/edward/.fly/bin/flyctl deploy --remote-only
```

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Swap file is invalid" | Disk corrupted. Run `git checkout build/disks/*.dsk` |
| "Odd address trap" | Boot disk corrupted. Restore from git |
| Port 8080 in use | Stop other containers: `docker ps` then `docker stop <id>` |
| SIMH port conflicts | Container restarted while old sockets still bound. Wait 30s or restart Docker |
| "Address already in use" | Kill container, wait for port release, restart |
