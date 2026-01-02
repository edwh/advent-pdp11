# Claude Context Continuation Notes

## Disk Image Inventory

**Location:** `build/disks/`

| Filename | Purpose | Contents |
|----------|---------|----------|
| `rsts0.dsk` | Boot disk (working copy) | RSTS/E OS + system files |
| `rsts1.dsk` | Game disk (working copy) | ADVENT code + data files |
| `rsts0-base-os.dsk` | Clean base image | RSTS/E OS only, no ADVENT |
| `rsts1-base-os.dsk` | Clean base image | Empty game disk |
| `kermit.dsk` | File transfer | Kermit utility disk |
| `archive/` | Old snapshots | Various intermediate states |

**Build Stages:**
1. **Base OS** → Base RSTS/E, no ADVENT code
2. **Data Transferred** → ADVENT.DTA, ADVENT.CHR, ADVENT.MON, etc.
3. **Source Compiled** → .OBJ files created
4. **Linked (MINI3)** → MINI3.TSK working (single-user version)
5. **Full ADVENT** → ADVENT.TSK (blocked by TKB linker crash)

**Current State:**
- `rsts{0,1}.dsk` contain ADVENT.TSK (working single-user mode)
- Run `RUN ADVENT` for gameplay
- Multi-user mode has file locking issues (ADVENT.MON opened with exclusive lock)

**To Reset to Clean State:**
```bash
cp build/disks/rsts0-base-os.dsk build/disks/rsts0.dsk
cp build/disks/rsts1-base-os.dsk build/disks/rsts1.dsk
```

## Dockerfiles

| File | Base Image | Purpose |
|------|------------|---------|
| `docker/Dockerfile` | alpine:3.18 | Full build (SIMH not in Alpine repos - broken) |
| `docker/Dockerfile.with-simh-base` | rattydave/alpine-simh | Alternate base (has symbol issues) |
| `docker/Dockerfile.update` | advent-mud:latest | **USE THIS** - Incremental updates |

Build with: `docker build -f docker/Dockerfile.update -t advent-mud .`

---

## CRITICAL: How File Transfer Works

**The `flx` tool TRUNCATES large files.** Do NOT rely on flx for data files.

The correct setup uses Docker with automatic TECO transfer:

1. `docker/Dockerfile` (copied from Dockerfile.new) uses `entrypoint.sh`
2. `docker/entrypoint.sh` runs `scripts/setup_advent.py` after RSTS/E boots
3. `scripts/setup_advent.py` uses TECO to transfer ALL files properly

To rebuild and run:
```bash
docker stop advent-mud; docker rm advent-mud
python3 scripts/migrate_data.py
python3 scripts/build_disk.py
docker build -t advent-mud .
docker run -d --name advent-mud -p 7681:7681 -p 2322:2322 -p 2323:2323 -v ./build/disks:/opt/advent/disks advent-mud
```

The first startup takes ~2-3 hours for TECO transfer of all data files.
Set `SKIP_SETUP=1` to skip setup on subsequent runs.

## IMPORTANT: Save Disk Image After Successful Setup

After the server successfully starts up with all data files transferred:

1. **Stop RSTS/E gracefully** to ensure disk writes complete
2. **Save a copy of the working disk** for faster future startups:
   ```bash
   docker stop advent-mud
   cp build/disks/rsts1.dsk build/disks/rsts1-with-data.dsk
   ```
3. **Use the saved disk** on subsequent runs to skip slow TECO transfer:
   - Copy `rsts1-with-data.dsk` back to `rsts1.dsk`
   - Run with `SKIP_SETUP=1` or `SKIP_DATA=1`
   - Only transfer code fixes (much faster)

This speeds up startup from ~2-3 hours to ~minutes.

## Current Status (Dec 31, 2025)

### Transfer Status (Jan 1, 2025)
**ALL DATA FILES TRANSFERRED SUCCESSFULLY!**
- ADVENT.DTA (1MB), ADVENT.MON (200KB), ADVENT.CHR (51KB), BOARD.NTC (262KB), MESSAG.NPC (60KB)
- All source files compiled with BP2
- Disk image saved: `build/disks/rsts1-with-data.dsk`

### Current Issue: TKB Linking
- Simple link (no overlays) causes "address overflow" and memory trap when run
- ODL-based overlay linking needed but TKB can't find ODL file
- Game is 265KB+ requiring overlays for 64KB address space
- Library path: `LB:BP2OTS/LB` (not SY:BP2OTS)

### What We're Doing
1. Verifying fixes to ADVOUT.SUB (SINGLE.USER% flag for direct PRINT)
2. Verifying fix to migrate_data.py ($ terminator instead of \n)
3. The "puff of smoke" garbage in room descriptions was caused by wrong terminator

### Key Issue: Data File Truncation
- `build_disk.py` uses `flx` tool to patch ADVENT.DTA onto disk
- FLX truncates large files (1MB file → ~51KB on disk)
- RSTS/E sees only 100 blocks, but room 449 needs ~450 blocks
- Result: "End of file on device at line 30" when accessing room 449

### Working Solution: TECO Transfer (via setup_advent.py)
- `scripts/setup_advent.py` is the main setup script
- Uses TECO `nI$$` command to insert bytes by ASCII code
- Files created via TECO persist across restarts
- Speed: ~120-130 bytes/sec (measured; ADVENT.DTA takes ~2 hours)
- Called automatically by `docker/entrypoint.sh`

### Reliable Transfer Requirements
1. **Long timeout required:** Use `timeout 10800` (3 hours) for full transfer
2. **Detached job handling:** Login must send "0\r" when prompted "Job number to attach to?"
3. **TECO buffer limits:** Use small CHUNK_SIZE (100 bytes) to avoid buffer overflow
   - Previous 500-byte chunks caused crash at 86% (~880KB)
   - Reduced to 100-byte chunks with more frequent P (flush) commands
   - **FIX CONFIRMED:** ADVENT.DTA (1MB) completed successfully with smaller chunks
4. **Monitor with:** `tail -f /tmp/setup.log`
5. **Rate:** ~110-130 bytes/sec for binary files via TECO

### Key Files Modified This Session
- `src/ADVOUT.SUB` - Added SINGLE.USER% check
- `src/ADVINI.SUB` - Set SINGLE.USER%=-1%
- `scripts/migrate_data.py` - Fixed $ terminator
- All ADV*.SUB files - Added SINGLE.USER% to COMMON block
- `scripts/setup_advent.py` - Fixed login to handle detached jobs (send "0\r" for new job)

### Docker Info
- Container: advent-mud
- Mounts: build/disks -> /opt/advent/disks
- Telnet: localhost:2323
- Login: [1,2] / Digital1977

### Documentation
- CONTINUATION.md - How to continue project
- TECHNICAL.md - File transfer methods, binary format
- MINI3 source in CONTINUATION.md line 261-297
