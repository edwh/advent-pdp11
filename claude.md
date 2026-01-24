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
- **Demigod privileges** - New players start at level 11 for exploration (not how original worked)

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

---

## Session Log (Date-Stamped)

### January 15, 2026 - "Odd address trap" crashes after tmux changes

**Problem:** Game commands (LOOK, N, S, E, W) cause "Odd address trap at line XX in ADVNOR" crashes.

**Context:** Implemented persistent tmux session architecture so users don't need to log in each time they connect via web terminal. The game displays correctly but crashes when processing any command.

**Key insight from RESURRECTION.md:** This exact error was previously fixed by moving ADVOUT to the ROOT segment in the ODL file. The error occurs when ADVOUT is called from overlay segments, causing memory corruption during overlay swaps.

**Current ODL in build_advent.exp (lines 210-225):**
```
.ROOT SY:ADVENT-SY:ADVOUT-LIBR-*(OVLY)
LIBR:   .FCTR LB:BP2OTS/LB
OVLY:   .FCTR *(A,B,C,D,E)
A:      .FCTR SY:ADVINI,SY:ADVNOR
B:      .FCTR SY:ADVCMD,SY:ADVODD,SY:ADVMSG
C:      .FCTR SY:ADVBYE,SY:ADVSHT,SY:ADVNPC
D:      .FCTR SY:ADVPUZ,SY:ADVDSP,SY:ADVFND
E:      .FCTR SY:ADVTDY
        .END
```

**Investigation needed:**
1. Check if ODL file is being created correctly during build
2. Verify the actual ODL content after creation (TYPE SY:ADVENT.ODL)
3. Compare with known working ODL from before tmux changes
4. Check git history for any ODL changes

**Files changed in this session:**
- docker/start_game_session.exp (new - persistent game session)
- docker/attach_game.sh (new - user attachment)
- docker/entrypoint.sh (modified - tmux session startup)
- Dockerfile (modified - added tmux package)

**REMINDER:** Always use `docker-compose up -d --build` not raw docker commands!

### January 15, 2026 (continued) - ODL Investigation

**Root Cause Analysis:**
The "Odd address trap" occurs when subroutines in one overlay call subroutines in another overlay during the overlay swap. The original fix (ADVOUT in ROOT) only addressed one cross-overlay call pattern.

**Investigation revealed additional cross-overlay calls:**
- ADVNOR (overlay A) calls ADVDSP (overlay D) at line 20
- ADVNOR (overlay A) calls ADVSHT (overlay C) multiple times
- ADVNOR (overlay A) calls ADVFND (overlay D) multiple times

**Fix attempted:**
Modified ODL to put ADVOUT, ADVDSP, ADVSHT, and ADVFND all in ROOT:
```
.ROOT SY:ADVENT-SY:ADVOUT-SY:ADVDSP-SY:ADVSHT-SY:ADVFND-LIBR-*(OVLY)
LIBR:   .FCTR LB:BP2OTS/LB
OVLY:   .FCTR *(A,B,C,D)
A:      .FCTR SY:ADVINI,SY:ADVNOR
B:      .FCTR SY:ADVCMD,SY:ADVODD,SY:ADVMSG
C:      .FCTR SY:ADVBYE,SY:ADVNPC,SY:ADVPUZ
D:      .FCTR SY:ADVTDY
        .END
```

**Result:**
- When ADVOUT alone is in ROOT: "Odd address trap" at line 20 (CALL ADVDSP)
- When ADVOUT+ADVDSP+ADVSHT+ADVFND in ROOT: LOOK command works, but build may be unstable

**Created ralph skill:**
Added `.claude/skills/ralph/SKILL.md` - iterative development approach adapted for this codebase.

**Final Result:**
- **ODL fix SUCCESSFUL** - "Odd address trap" eliminated
- **LOOK command works** - no more overlay crashes
- **New issue discovered:** Error 11 (file I/O error) when moving (W, N, etc.)
  - This is a data access issue, not an overlay issue
  - Line 60 in ADVNOR tries to read room data that may not exist
  - Likely caused by exit data pointing to invalid room numbers

**Current working ODL (build_advent.exp):**
```
.ROOT SY:ADVENT-SY:ADVOUT-SY:ADVDSP-SY:ADVSHT-SY:ADVFND-LIBR-*(OVLY)
LIBR:   .FCTR LB:BP2OTS/LB
OVLY:   .FCTR *(A,B,C,D)
A:      .FCTR SY:ADVINI,SY:ADVNOR
B:      .FCTR SY:ADVCMD,SY:ADVODD,SY:ADVMSG
C:      .FCTR SY:ADVBYE,SY:ADVNPC,SY:ADVPUZ
D:      .FCTR SY:ADVTDY
        .END
```

**Next steps:**
- Investigate Error 11 data access issue when moving
- Check if room exit data points to valid rooms
- Verify ADVENT.DTA file integrity and record access

### January 15, 2026 (continued) - Data File Byte Order Fix

**Root Cause Found - THREE issues in data file generation:**

1. **Byte order mismatch:** `CVT$%` in BASIC-PLUS-2 interprets bytes as big-endian, but `migrate_data.py` and `reconstruct_rooms.py` were storing exits in little-endian format.

2. **Record indexing mismatch:** BASIC-PLUS-2 uses 1-based record indexing (`GET #3%, RECORD N` reads file offset `(N-1)*512`), but `migrate_data.py` was using 0-based indexing.

3. **Validation byte mismatch:** `reconstruct_rooms.py` expected `(room_num - 1) % 256` but BASIC's `CHR$(room_num)` returns `room_num % 256`.

**Files fixed:**
- `scripts/migrate_data.py`:
  - Line 85-86: Changed exit bytes to big-endian (high byte first)
  - Lines 235-245: Changed loop from `range(record_count)` to `range(1, record_count + 1)` for 1-based indexing

- `scripts/reconstruct_rooms.py`:
  - Line 51: Changed exit parsing to big-endian: `(byte1 << 8) + byte2`
  - Lines 113-114: Changed exit writing to big-endian
  - Line 37: Changed validation to `number & 0xFF` (was `(number - 1) % 256`)

**Testing progress:**
- After byte order fix: "Error 11" changed to "corrupt room" message
- After record indexing fix: Pending test (WSL shutdown interrupted)

**To resume:**
1. Data files regenerated with `python3 scripts/migrate_data.py`
2. Need to rebuild container: `docker-compose down && docker-compose up -d --build`
3. Wait 10-15 minutes for ADVENT to build from source
4. Test navigation: `docker exec advent-mud tmux send-keys -t advent W Enter`
5. Verify with: `docker exec advent-mud tmux capture-pane -t advent -p`

**Expected behavior after fix:**
- Room numbers stored in big-endian format matching CVT$% interpretation
- Room N's data at file offset (N-1)*512 matching BASIC's 1-based RECORD indexing
- Validation byte `room_num & 0xFF` matching BASIC's `CHR$(room_num)`

**CRITICAL TODO for next session:**
- We have ~2000 rooms, so room numbers MUST be 16-bit (2 bytes)
- If you see single-byte room number handling anywhere, that's a bug!
- Room numbers range from 1 to ~2000, requiring full 16-bit storage
- The validation byte only uses low byte (`room_num & 0xFF`) but exit destinations need full 16 bits

### January 19, 2026 - SIMH Character Dropping Bug Fixed

**Problem:** Keyboard input via web terminal was unreliable - characters dropped intermittently.

**Root Cause:** SIMH v4.0-Beta-1 (November 2014) has a known bug ([GitHub issue #246](https://github.com/simh/simh/issues/246)) where console input characters get dropped. The bug is caused by XON/XOFF flow control being precisely emulated over telnet - data arrives faster than the emulated FIFO can handle.

**Fix Applied:**
- Updated Dockerfile to use latest SIMH master branch instead of v4.0-Beta-1
- Changed from `git clone --branch v4.0-Beta-1` to `git clone --depth 1`
- Also fixed terminal CSS width collapse in mobile media query

**Files Modified:**
- `Dockerfile` (lines 25-30) - Use latest SIMH master
- `docker/web/style.css` (lines 623-639) - Fixed CSS terminal width

**Testing Results (via Chrome MCP):**
- ✅ LOOK command - received and processed correctly
- ✅ NORTH command - movement worked, arrived at new room
- ✅ INVENTORY command - showed "You are carrying: Nothing"
- ✅ STATUS command - showed player stats (Level 16, HP 20, Fatigue 47)
- ✅ SOUTH command - returned to starting room
- ✅ 60-second stability test - no degradation

**Commits:**
- `a0adcd6` - Document the SIMH character dropping bug discovery
- `47234ef` - Fix terminal CSS width in mobile media query
- `1c23b0b` - Update SIMH to latest master to fix character dropping bug

**Status:** Keyboard input now works reliably. Ready for fly.io deployment.

**Next:** Deploy updated container to fly.io

<<<<<<< Updated upstream
### January 20, 2026 - Backspace, Terminal Scaling, Disk Image Split

**Tasks:**
1. ✅ Fix backspace not working (was echoing `\` instead of deleting)
2. ✅ Fix terminal scaling (terminal not filling window)
3. ✅ Split large disk image for git push (954MB -> 20 x 50MB parts)
4. ✅ Remove large file from git history (filter-branch)

**Root Causes Found:**

1. **Backspace issue:** RSTS/E was in rubout-echo mode, where pressing DEL echoes back the deleted character. For video terminals like VT100, you need "scope" mode.
   - Fix: Added `SET TERMINAL /SCOPE` command after login in start_game_session.sh

2. **Terminal scaling:** JavaScript transform scaling was using wrong character dimensions
   - Fix: Configure ttyd with fontSize=20 to make terminal text larger

3. **Large disk image blocking git push:** 954MB file exceeds GitHub's 100MB limit
   - Fix: Split into 20 x 50MB parts, assemble during Docker build
   - Also: Used git filter-branch to remove large file from history

**Files Modified:**
- `docker/start_game_session.sh` - Add SET TERMINAL /SCOPE
- `docker/entrypoint.sh` - Add ttyd fontSize=20 option
- `docker/web/terminal.js` - Simplify scaling function
- `docker/screenrc` - Screen configuration (new file)
- `Dockerfile` - Assemble disk parts during build
- `.gitignore` - Exclude assembled disk image
- `simh/Disks/ra72/` - Split disk parts and assembly script

**Commits:**
- `81f9a1b` - Fix backspace, terminal scaling, and split large disk image

**Testing:**
- ✅ Backspace works (verified by sending DEL characters to screen session)
- ✅ Disk assembly works (verified 954MB file size in container)
- ✅ Git push succeeded after history rewrite

**Status:** All fixes complete and pushed to GitHub

### January 23, 2026 - ADVENT Feature Testing Phase 1

**Goal:** Test core single-player loop - explore, collect items, fight

## Task Status

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1.1 | Test LOOK command | 🔄 In Progress | Room description display |
| 1.2 | Test movement (N/S/E/W) | ⬜ Pending | Navigation between rooms |
| 1.3 | Test GET/DROP | ⬜ Pending | Pick up/drop items |
| 1.4 | Test INVENTORY | ⬜ Pending | List carried items |
| 1.5 | Test STATUS | ⬜ Pending | Display HP, level, fatigue |
| 1.6 | Test DRAW/SHEATH | ⬜ Pending | Equip/unequip weapon |
| 1.7 | Test HIT (combat) | ⬜ Pending | Attack a monster |

**Testing via:** Chrome DevTools MCP on http://localhost:7681

**Results:**

**Phase 1: Core Loop ✅**
- LOOK: Works (crashes in some puzzle rooms)
- Movement N/S/E/W: All working
- GET/DROP: Working (monster blocking as expected)
- INVENTORY: Working
- STATUS: Working (shows level 16 demigod)
- DRAW/SHEATH: Working
- HIT combat: Working! ("You did X damage and killed the [monster]")

**Bonus Features Found:**
- HEAL: Works ("You now have X hit points")
- INVISIBLE: Works ("You are now invisible")
- ROOM [n]: Teleport works (demigod)
- RING: Works ("[Player] rings the bell")
- VALUE: Works ("worth about X XP")
- REST: Works ("sit down and close your eyes")
- SHOUT: Works
- EAT: Works

**Bugs Found:**
1. **CRITICAL**: MSG: device crash at line 29000 (READ, LOOK in puzzle rooms)
2. **CRITICAL**: Fatigue=0 blocks ALL commands including QUIT
3. "You can't" messages need reasons
4. HELP refers to "Beta" system

**Files Created:**
- STATUS.md - Full feature status with test results
- SCRIPT.md - Video script with Claude thought bubbles
- ENHANCEMENTS.md - Code improvements needed

**Interesting Rooms Found:**
- Santa's Grotto (740) with Santa Claus
- Fortune teller (777) - schoolboy humor
- Dojo with ninja (north from start)
- Weapons shop (north from dojo)
- Bell rooms (56, 83, 249, 351, 527)

**Next:**
- Fix MSG: device issue (create MSG: or disable logging)
- Test shrine treasure drops for XP
- Continue Phase 2 testing

### January 24, 2026 - ^Z Flooding Bug Root Cause Found and Fixed

**Problem:** Game was continuously receiving ^Z/EOF at INPUT prompt, causing rapid restarts with `> ? ^Z` appearing repeatedly.

**Root Cause Identified:** Commit `b4adbac` introduced a problematic combination:

1. **ADVENT.COM command file** - Auto-restart loop:
   ```
   $ SET NOON
   $ LOOP:
   $ RUN ADVENT
   $ GOTO LOOP
   ```

2. **Changed start_game_session.sh** from `RUN ADVENT` to `@ADVENT`

3. **Added ^Z error handler** at line 25003:
   ```basic
   RESUME 32766 IF ERR=11% AND ERL=36% AND SINGLE.USER%
   ```
   Which jumps to `END` (line 32766)

**The infinite loop:** When any ^Z exists in the input buffer:
1. Game receives ^Z at INPUT (line 36)
2. Error handler catches EOF (error 11), jumps to END
3. Game exits
4. ADVENT.COM loop immediately restarts the game
5. Still has ^Z in buffer → repeat

**Fix:** Reverted to using `RUN ADVENT` directly instead of `@ADVENT` command file.

**Testing (via Chrome MCP on old version before b4adbac):**
- ✅ Game starts normally, waits at `>?` prompt
- ✅ LOOK command - displays room description
- ✅ NORTH command - movement works, arrived at new room (rough walled cave)
- ✅ Room shows objects: "ediblefood pig", "portrait of david", "Davidian Cavehog"
- ✅ No ^Z flooding

**Fix Applied:**
- Modified `docker/start_game_session.sh` line 112: Use `RUN ADVENT` instead of `@ADVENT`
- Removed ADVENT.COM from build (not needed without auto-restart)
- Removed ^Z error handler from ADVENT.B2S (line 25003)

**Verified Working:**
- ✅ Game starts with `RUN ADVENT` (not `@ADVENT`)
- ✅ No ^Z flooding at prompt
- ✅ LOOK command works
- ✅ NORTH movement works
- ✅ Room descriptions and objects display correctly

**Commits:**
- `3e13464` - Fix ^Z flooding bug by reverting to RUN ADVENT
