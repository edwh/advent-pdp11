# Development Notes

Internal development context for Claude Code sessions.

## CRITICAL: How to Build and Run a Working Container

**Last verified: January 8, 2026**

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

### Step 2: Build and Run with Docker Compose

**ALWAYS use Docker Compose for local development.**

```bash
# Build and start
docker compose up -d --build

# Wait ~2 minutes for RSTS/E to boot, then check logs
docker compose logs -f
```

To stop:
```bash
docker compose down
```

### Step 3: Verify It Works

```bash
# Web interface (note: port 8088, not 8080)
open http://localhost:8088

# Or telnet to console (note: port 2324, not 2322)
telnet localhost 2324
# Login: [1,2] / Digital1977
# Command: RUN ADVENT
```

### Local Ports (chosen to avoid conflicts)

| Port | Maps To | Purpose |
|------|---------|---------|
| 8088 | 8080 | Web interface (nginx) |
| 7681 | 7681 | Game web terminal (ttyd) |
| 7682 | 7682 | Admin web terminal |
| 2324 | 2322 | SIMH console (telnet) |
| 2325 | 2323 | RSTS/E terminal (telnet) |

## WARNING: Common Mistakes That Break Things

### DO NOT modify disk images while RSTS/E is running
The container must be STOPPED before using `flx` on disks. Modifying disks while running causes corruption ("swap file is invalid" errors on next boot).

### DO NOT use raw `docker run` commands
Always use `docker compose up -d --build` for consistency. The docker-compose.yml file has the correct port mappings and volume mounts.

### DO NOT use docker/Dockerfile directly
There are multiple Dockerfiles. The ROOT `Dockerfile` is the main one, and docker-compose.yml is configured to use it.

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

## Current State (January 8, 2026)

### What Works
- Full ADVENT game running in single-user mode
- CRT web interface with auto-login
- Navigation, inventory, combat commands
- 1,587 rooms with descriptions
- 402 monsters, 417 objects
- Fly.io deployment: https://advent-pdp11.fly.dev

### Known Issues
1. **^B character in exit display** - appears after "West"
2. **Tab alignment** - exits display has formatting issues
3. **Multi-user mode** - file locking prevents concurrent access

## Console vs DZ Terminals

We use console (port 2322) instead of DZ terminals (port 2323) because:
- DZ terminals are flaky - sometimes don't respond with User: prompt
- Console is special in RSTS/E - always available and reliable
- Single-user mode only needs one terminal anyway

**Local port mappings** (via docker-compose.yml):
- Console: localhost:2324 -> container:2322
- DZ terminals: localhost:2325 -> container:2323

**Console Port Contention Fix (January 8, 2026):**
Both `verify_ready.exp` and `game_connect.exp` use port 2322 (console). SIMH console only allows ONE connection. During RSTS/E restarts, `entrypoint.sh` now:
1. Kills ttyd processes before running verify_ready.exp
2. Restarts ttyd after RSTS/E is verified ready

This prevents "All connections busy" errors on fly.io.

Files:
- `docker/game_connect.exp` - connects to port 2322 for game sessions
- `docker/verify_ready.exp` - checks console for system readiness
- `docker/entrypoint.sh` - manages ttyd lifecycle during restarts

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

**App name:** `advent-pdp11` (already created - DO NOT create a new app!)

**Live URL:** https://advent-pdp11.fly.dev

Fly.io auth token is in `/home/edward/.env`. To deploy:

```bash
# Load the token (single-quoted to handle special characters)
source /home/edward/.env

# Check current status first
/home/edward/.fly/bin/flyctl status

# Deploy (uses existing app, don't use 'fly launch')
/home/edward/.fly/bin/flyctl deploy --remote-only
```

**IMPORTANT:**
- Never run `fly launch` - that creates a NEW app. Always use `fly deploy`.
- The app `advent-pdp11` already exists in the `lhr` (London) region.
- Deploy takes ~5 minutes (build + RSTS/E boot time).
- Health check grace period is 5 minutes to allow RSTS/E to boot.

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Swap file is invalid" | Disk corrupted. Run `git checkout build/disks/*.dsk` |
| "Odd address trap" | Boot disk corrupted. Restore from git |
| Port conflict | Check `docker ps` for existing containers using ports. Run `docker compose down` first |
| SIMH port conflicts | Container restarted while old sockets still bound. Wait 30s or restart Docker |
| "Address already in use" | Run `docker compose down`, wait for port release, then `docker compose up -d` |
| "All connections busy" | Console port contention. Fixed in Jan 2026 - entrypoint.sh now manages ttyd lifecycle |

## Tape Drive File Transfer (January 2026) - WORKING!

### BREAKTHROUGH: Tape Transfer Works!

**Date: January 4, 2026**

After extensive investigation, tape-based file transfer is now **fully working**:

- **Transfer speed: ~18 KB/sec** (140x faster than TECO's 130 bytes/sec!)
- **90KB transferred in 5 seconds**
- **The 1MB ADVENT.DTA file would take ~55 seconds** instead of 2+ hours via TECO

### How It Works

1. Create a tape image with DOS-11 format headers using `scripts/create_tape.py`
2. Attach the tape in SIMH via `attach ts /opt/advent/tapes/transfer.tap`
3. In RSTS/E: `MOUNT MS:` then `COPY MS:filename.ext destination`

**Critical Discovery**: You must specify the exact filename when copying. Using `DIR MS:` first corrupts the tape position and causes "Fatal system I/O failure" on subsequent operations.

### Usage

```bash
# Create a tape from files
python3 scripts/create_tape.py create output.tap file1.dat file2.bas

# Include in Docker build and restart
cp output.tap build/tapes/transfer.tap
docker compose up -d --build

# In RSTS/E after boot:
$ MOUNT MS:
Density is 1600
Tape is in DOS format
$ COPY MS:FILE1.DAT FILE1.DAT
[File MS:[1,2]FILE1.DAT copied to [1,2]FILE1.DAT]
```

### Technical Details

DOS-11 Tape Header (14 bytes = 7 words):
```
Word 0-1: RAD50 filename chars 1-6
Word 2:   RAD50 extension
Word 3:   UIC as (group << 8) | user
Word 4:   Protection code (0o233 = 155)
Word 5:   Date ((year-1970)*1000 + day_of_year)
Word 6:   RAD50 filename chars 7-9 (optional)
```

SIMH tape format:
- 4-byte record length (little-endian)
- Data (padded to even bytes)
- 4-byte record length (same)
- Tape mark = 0x00000000
- End of medium = 0xFFFFFFFF

### Files Created
- `scripts/create_tape.py` - Creates SIMH tape images with DOS-11 format
- `build/tapes/transfer.tap` - Tape image included in container

Reference: https://github.com/andreax79/xferx (xferx/pdp11/dos11magtapefs.py)
