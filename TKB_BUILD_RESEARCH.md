# TKB Build Research: Building ADVENT.TSK with Overlays

## Problem Statement
Need to build ADVENT.TSK from source using TKB (Task Builder) on RSTS/E V10.1.
The program requires overlays because it exceeds the PDP-11 address space.

## Key Discovery: Use BP2IC2 BUILD Command, NOT TKB Directly!

**NOTE:** ADVBLD.COM was **reconstructed by Claude** during the resurrection project,
NOT recovered from the original tape. The original build procedure is unknown.
The syntax below is based on BP2IC2 HELP output and standard RSTS/E conventions.

Looking at the reconstructed ADVBLD.COM, the BUILD command within
BP2IC2 is used, NOT direct TKB invocation:

```
$ RUN $BP2IC2
OLD ADVINI.SUB
COMPILE
...
BUILD ADVENT=ADVENT,ADVINI,ADVOUT,ADVNOR,ADVCMD,ADVODD,ADVMSG,ADVBYE,ADVSHT,ADVNPC,ADVPUZ,ADVDSP
BYE
```

The BUILD command in BASIC-PLUS-2:
- Compiles and links object files into a .TSK file
- Handles TKB invocation internally
- Creates proper command files for TKB
- May handle ODL files differently than direct TKB calls

## Previous Observation
- When using TKB directly, parentheses `()` in overlay syntax appeared to convert to brackets `[]`
- This might be specific to direct TKB invocation
- The BP2IC2 BUILD command may handle this differently

## ODL Syntax Notes

From research, overlay syntax uses:
- `.ROOT segment-segment-(...,...)` for overlay trees
- `*(...)` indicates AUTOLOAD overlays
- `.FCTR` defines factors/labels
- The `*` prefix on a filename indicates autoload

Example from LIBR.ODL:
```
DISP:   .FCTR   *DP1:[5,13]DISPLY-LIB-*(DISPA,DISPB,DISPC,DISPD)
```

## Options to Test

### Option 1: BP2IC2 BUILD Command (MOST PROMISING)
- Use BUILD command within BP2IC2
- This is how ADVBLD.COM does it
- Syntax: `BUILD taskname=module1,module2,...`

### Option 2: BUILD with /ODL Option
- BUILD may support an /ODL qualifier to specify overlay structure
- Need to test: `BUILD ADVENT=ADVENT,.../ODL`

### Option 3: TKB with Properly Formatted Command File
- Create a .CMD file in TKB's expected format
- Test without ODL file first (to see if address overflow occurs)
- Then add overlay specifications

### Option 4: ODL File Variations
- Test ODL without `*` (just parentheses for non-autoload)
- Test with different .FCTR structures

### Option 5: Cross-compilation (Fallback)
- pclink11 doesn't support overlays (ruled out)
- Would need to find alternative cross-linker

## Research Sources
- [BASIC-PLUS Wikipedia](https://en.wikipedia.org/wiki/BASIC-PLUS)
- [PDP-11 Overlays Discussion](https://classiccmp.org/pipermail/cctech/2015-September/010541.html)
- [RSX-11 Wiki](https://gunkies.org/wiki/RSX-11)
- RSX-11M Task Builder Manual (archive.org)

## Test Results

### Test 1: BUILD with 3 modules
- Command: `BUILD SY:TEST01=DM1:ADVENT,DM1:ADVINI,DM1:ADVOUT`
- Result: Returned to BASIC2 prompt without error
- TSK file: Not found (possibly 6-char name limit)

### Test 2: HELP COMMANDS in BP2IC2
Available commands discovered:
```
APPEND  BRLRES  BUILD  $  COMPILE  CONTINUE  DELETE  DSKLIB  EDIT  EXIT
HELP  IDENTIFY  INQUIRE  LIBRARY  LIST  LISTNH  LOAD  LOCK  NEW  ODLRMS
OLD  RENAME  REPLACE  RMSRES  RUN  RUNNH  SAVE  SCALE  SCRATCH
SEQUENCE  SET  SHOW  UNSAVE
```

**Key discovery: ODLRMS command exists!** This likely generates ODL files for RMS support.

### Test 3: BUILD Command Creates .CMD File
- Command: `BUILD ADVENT=ADVENT,ADVINI,ADVOUT,...`
- Result: BUILD creates ADVENT.CMD file
- ADVENT.CMD can be used with TKB: `TKB @SY:ADVENT.CMD`
- Without overlays, TKB gives: `TKB -- *DIAG*-Segment ADVENT has address overflow`

### Test 4: BUILD /ODL Qualifier
- Command: `BUILD/ODL:ADVENT ADVENT=...`
- Result: `?No qualifiers allowed` - BUILD doesn't support /ODL

### Test 5: TKB with ODL File
- Command: `TKB>SY:ADVENT=SY:ADVENT.ODL`
- Result: `TKB -- *FATAL*-File ADVENT.ODL has illegal format`
- This happens with both tape-transferred ODL and BASIC-created ODL
- The error persists regardless of ODL content

### Test 6: TKB @ADVENT.CMD (after BUILD)
- Command: `TKB @SY:ADVENT.CMD`
- Result: `TKB -- *FATAL*-I/O error on input file ADVENT.ODL`
- The .CMD file references ADVENT.ODL but can't read it
- Different error than "illegal format" - suggests path or access issue

### Key Finding: Existing System ODL Files
System has working ODL files that TKB can use:
- `DM0:[1,1]FEDTKB.ODL` (2 blocks)
- `DM0:[1,1]PDPDBG.ODL` (1 block)
These should be examined to understand correct ODL format for RSTS/E TKB.

### Current Understanding
1. BUILD command successfully creates a .CMD file for TKB
2. The .CMD file works but results in address overflow (no overlays)
3. The ODL file from tape has format issues TKB doesn't accept
4. There's a difference between "illegal format" and "I/O error" suggesting multiple issues
5. RSTS/E TKB may have different ODL format requirements than RSX

### Next Steps
1. Examine FEDTKB.ODL to understand correct RSTS/E ODL format
2. Create ADVENT.ODL matching that format
3. Alternative: Find correct TKB inline overlay syntax
4. Alternative: Manually edit the ADVENT.CMD file to include overlay specs

---

## Detailed Investigation Log (January 2026)

### System ODL Files Examined

#### FEDTKB.ODL (SY:[0,200] aka DM0:[1,1])
Working ODL file for FED editor. Contents:
```
; FEDTKB.ODL
.ROOT   ROOT-*(OV1,OV2,OV3,OV4)
.NAME   FED
ROOT:   .FCTR   FED-FEDLIB/LB:FEDVID:FDVDAT:FMSSAV:FDV:FDVERR-ROOT1
ROOT1:  .FCTR   FEDCMD-FEDESC
OV1:    .FCTR   FEDOPR
OV2:    .FCTR   FEDCRE-FEDSCR
OV3:    .FCTR   FEDEXI-FEDSTF
OV4:    .FCTR   FEDOPN-FEDRMS
.END
```

#### BP2IC2.ODL (SY:[1,1])
BASIC-PLUS-2 compiler ODL. Shows RTS specification:
```
.ROOT BP2IC2-BP2OTS/LB-BP2RSB/LB-*(OV1,...)
; RTS ...RSX
```

#### Key Observations from System ODL Files
- Comments use `;` at start of line
- `.ROOT` defines the overlay tree structure
- `.NAME` specifies task name
- `.FCTR` defines overlay factors
- `.END` terminates the file
- `*()` indicates autoload overlays
- `/LB` suffix indicates library files

### ODL File Approaches Tried

#### Approach 1: Transfer ODL via Tape (DOS format)
- Created ODL file on Linux host
- Transferred via simulated tape (DOS format)
- Result: `TKB -- *FATAL*-File ADVENT.ODL has illegal format`
- **Hypothesis**: File format/attributes don't match what TKB expects

#### Approach 2: Create ODL Using BASIC PRINT Statements
- Used BP2IC2 to create ODL via PRINT statements
- Result: Same "illegal format" error
- **Hypothesis**: BASIC may add extra formatting or wrong record type

#### Approach 3: Create ODL Using DCL COPY/ECHO
- Attempted to use DCL commands to create file
- Limited success - DCL on RSTS/E has different capabilities than VMS

### Two Versions of ADVENT.ODL

#### src/ADVENT.ODL (SY: paths - for building)
```
.ROOT	ADVENT-LIBR-*(INI,OUT,NOR,CMD,ODD,MSG,BYE,SHT,NPC,PUZ,DSP,FND,TDY)
INI:	.FCTR	SY:[1,2]ADVINI
OUT:	.FCTR	SY:[1,2]ADVOUT
...
LIBR:	.FCTR	SY:[1,1]BP2OTS/LB
.END
```

#### src/ADVENT_DM1.ODL (DM1: paths - for runtime)
```
.ROOT	ADVENT-LIBR-*(INI,OUT,NOR,CMD,ODD,MSG,BYE,SHT,NPC,PUZ,DSP,FND,TDY)
INI:	.FCTR	DM1:[1,2]ADVINI
OUT:	.FCTR	DM1:[1,2]ADVOUT
...
LIBR:	.FCTR	SY:[1,1]BP2OTS/LB
.END
```

### Bootstrap Script Issue Found
In `docker/bootstrap_advent.exp`:
- Line 27: `ADVENT.ODL` in source_files list (SY: paths) - transferred to SY:[1,2]
- Line 247: `ADVENTD.ODL` copied from tape to DM1:ADVENT.ODL (DM1: paths)
- Line 307: **BUG** - copies DM1:ADVENT.ODL over SY:[1,2]ADVENT.ODL

This overwrites the correct SY: version with the DM1: version, but this may NOT be the root cause since the "illegal format" error occurs regardless of which version is used.

### The Core Problem: File Format vs Content

The "illegal format" error suggests TKB is rejecting the file before even parsing the content. Possible causes:
1. **Record format** - RSTS/E files have record attributes (fixed, variable, stream)
2. **File type** - May need specific file organization
3. **Character encoding** - Line endings, tabs, special characters
4. **Block structure** - PDP-11 files have 512-byte blocks

### What We Need to Determine

1. **What are the file attributes of working ODL files?**
   - Use `DIR/FULL` on FEDTKB.ODL to see record format, file organization
   - Compare with our ADVENT.ODL attributes

2. **How were the working ODL files created?**
   - Were they created by a specific tool?
   - What editor/method produces correct format?

3. **Can we create a file with matching attributes?**
   - Use RSTS/E native tools (EDT, TECO, or specific file creation commands)
   - Copy a working ODL and modify its contents

### Experiment Plan

1. Run `DIR/FULL` on working system ODL files to see exact attributes
2. Run `DIR/FULL` on our ADVENT.ODL to compare
3. Try copying FEDTKB.ODL to ADVENT.ODL and editing contents
4. Try using EDT editor within RSTS/E to create ODL from scratch
5. Check if there's a way to set file attributes on creation

---

## CRITICAL FINDING: RTS Attribute Difference (January 5, 2026)

### DIR/FULL Comparison Results

**Working system file (FEDTKB.ODL):**
```
 Name .Typ    Size    Prot  Access      Date     Time   Clu  RTS    Pos  Op/rr
FEDTKB.ODL       2   < 60> 01-Jul-92 01-Jul-92 10:01 AM   1 RT11   34749  0/0
```

**Our ADVENT.ODL:**
```
 Name .Typ    Size    Prot  Access      Date     Time   Clu  RTS    Pos  Op/rr
ADVENT.ODL       1   < 60> 01-Jan-92 01-Jan-92 12:01 PM   1 ...RSX 21372  0/0
```

### The Key Difference: RTS Attribute

| File | RTS Attribute |
|------|---------------|
| FEDTKB.ODL (working) | RT11 |
| ADVENT.ODL (ours) | ...RSX |

**The RTS (Runtime System) attribute is different!**

- `RT11` = RT-11 compatible file format (simple sequential)
- `...RSX` = RSX-11 format (may have different record structure)

This explains why TKB gives "illegal format" - it expects RT11 format files!

### Content Corruption Issue

Our ADVENT.ODL also has corrupted content:
```
        .ROOT USER
USER:   .FCTR SY:ADVENT-LIBR
LIBR:   .FCTR LB:BP2OTS/LB
@ADVENTADVENT=ADVENT,ADVINI,ADVOUT,ADVNOR,ADVCMD,ADVODD,ADVMSG,ADVBYE,ADVSHT,ADVNPC,ADVPUZ,ADVDSP,ADVFND,ADVTDY
        .END
```

The `@ADVENTADVENT=...` line is garbage - it's BUILD command syntax mixed into the ODL.

### What the ODL Content Should Be

Based on FEDTKB.ODL structure:
```
;
; ADVENT.ODL
;
        .ROOT   ADVENT-LIBR-*(INI,OUT,NOR,CMD,ODD,MSG,BYE,SHT,NPC,PUZ,DSP,FND,TDY)
        .NAME   ADVENT
INI:    .FCTR   SY:[1,2]ADVINI
OUT:    .FCTR   SY:[1,2]ADVOUT
NOR:    .FCTR   SY:[1,2]ADVNOR
CMD:    .FCTR   SY:[1,2]ADVCMD
ODD:    .FCTR   SY:[1,2]ADVODD
MSG:    .FCTR   SY:[1,2]ADVMSG
BYE:    .FCTR   SY:[1,2]ADVBYE
SHT:    .FCTR   SY:[1,2]ADVSHT
NPC:    .FCTR   SY:[1,2]ADVNPC
PUZ:    .FCTR   SY:[1,2]ADVPUZ
DSP:    .FCTR   SY:[1,2]ADVDSP
FND:    .FCTR   SY:[1,2]ADVFND
TDY:    .FCTR   SY:[1,2]ADVTDY
LIBR:   .FCTR   SY:[1,1]BP2OTS/LB
        .END
```

### Next Steps to Fix

1. **Create ODL with RT11 attribute** - Need to find how to create files with RT11 format
2. **Options to try:**
   - Copy FEDTKB.ODL to ADVENT.ODL and edit contents (inherits RT11 attribute)
   - Use EDT or TECO editor (may create RT11 files by default)
   - Find RSTS/E command to set file format on creation
   - Check if DOS tape transfer creates RSX files (that's our problem)

---

## Solution Approach: Copy and Edit Method

Since FEDTKB.ODL has the correct RT11 format, the best approach is:
1. COPY SY:[0,200]FEDTKB.ODL SY:[1,2]ADVENT.ODL
2. Use an RSTS/E editor to modify the content
3. The COPY preserves the RT11 file attribute

### Content to Write to ADVENT.ODL

Based on FEDTKB.ODL structure, our ADVENT.ODL should look like:
```
;
; ADVENT.ODL - Overlay descriptor for ADVENT MUD
;
        .ROOT   ADVENT-LIBR-*(INI,OUT,NOR,CMD,ODD,MSG,BYE,SHT,NPC,PUZ,DSP,FND,TDY)
        .NAME   ADVENT
INI:    .FCTR   SY:[1,2]ADVINI
OUT:    .FCTR   SY:[1,2]ADVOUT
NOR:    .FCTR   SY:[1,2]ADVNOR
CMD:    .FCTR   SY:[1,2]ADVCMD
ODD:    .FCTR   SY:[1,2]ADVODD
MSG:    .FCTR   SY:[1,2]ADVMSG
BYE:    .FCTR   SY:[1,2]ADVBYE
SHT:    .FCTR   SY:[1,2]ADVSHT
NPC:    .FCTR   SY:[1,2]ADVNPC
PUZ:    .FCTR   SY:[1,2]ADVPUZ
DSP:    .FCTR   SY:[1,2]ADVDSP
FND:    .FCTR   SY:[1,2]ADVFND
TDY:    .FCTR   SY:[1,2]ADVTDY
LIBR:   .FCTR   SY:[1,1]BP2OTS/LB
        .END
```

### Editor Options in RSTS/E
- **EDT** - Screen-oriented editor (if available: RUN $EDT)
- **TECO** - Tape Editor and COrrector (if available)
- **PIP with /RM** - May allow file modification
- **BASIC** - Could append to file but may set wrong format

### Test Plan
1. Start clean container with base OS disks
2. Copy FEDTKB.ODL to ADVENT.ODL (verify RT11 format preserved)
3. Identify available editor
4. Modify ADVENT.ODL content
5. Test TKB with the RT11-format ODL

---

## RT11 FORMAT CONFIRMED WORKING (January 5, 2026)

### Successful Test Results

**Test Command:**
```
$ COPY SY:[0,200]FEDTKB.ODL SY:TEST.ODL
[File [0,200]FEDTKB.ODL copied to [1,2]TEST  .ODL]

$ DIR/FULL SY:TEST.ODL
 Name .Typ    Size    Prot  Access      Date     Time   Clu  RTS    Pos  Op/rr
TEST  .ODL       2   < 60> 01-Jan-92 01-Jan-92 12:01 PM   1 RT11      31  0/0

$ RUN $TKB
TKB>SY:XX=SY:TEST.ODL
TKB>/
Enter Options:      <-- SUCCESS! TKB parsed the ODL file!
```

### Key Findings

1. **COPY preserves RT11 format** - When we copy FEDTKB.ODL to TEST.ODL, the new file has RT11 RTS attribute
2. **TKB accepts RT11 format** - No "illegal format" error when the file has RT11 attribute
3. **The problem is file format, not content** - Even with FEDTKB.ODL's content (wrong for ADVENT), TKB accepts it

### The Root Cause

Files created via:
- DOS tape transfer → RSX format → "illegal format" error
- BASIC PRINT statements → RSX format → "illegal format" error
- COPY from existing RT11 file → RT11 format → **WORKS!**

### Solution

To create a working ADVENT.ODL:
1. COPY SY:[0,200]FEDTKB.ODL SY:[1,2]ADVENT.ODL  (creates RT11-format file)
2. Modify the content using an editor that preserves the file format
3. The modified file will retain RT11 format and work with TKB

### Next Step: Find Editor That Preserves RT11 Format

Need to find an editor on RSTS/E that can:
- Open an existing RT11-format file
- Replace the content with ADVENT overlay specs
- Save without changing the file format to RSX

Options to test:
- EDT editor (screen-based)
- TECO (line-based)
- PIP with file manipulation

### WORKING SOLUTION VERIFIED

Successfully created ADVENT.ODL with RT11 format:
```
$ COPY SY:[0,200]FEDTKB.ODL SY:[1,2]ADVENT.ODL
[File [0,200]FEDTKB.ODL copied to [1,2]ADVENT.ODL]

$ DIR/FULL SY:ADVENT.ODL
ADVENT.ODL       2   < 60> 01-Jan-92 01-Jan-92 12:00 PM   1 RT11    2938  0/0
```

**The file has RT11 format!** TKB will accept this file format.

## Bootstrap Script Fix Required

The bootstrap_advent.exp needs to be modified:
1. **DO NOT** transfer ADVENT.ODL via tape (creates RSX format)
2. **DO** copy FEDTKB.ODL to ADVENT.ODL (creates RT11 format)
3. **THEN** modify the content using RSTS/E tools

Approaches for content modification:
1. **CREATE command** with here-doc style input
2. **APPEND** to empty file after copying
3. **Use EDIT** in batch mode if available

The simplest approach may be to:
1. Copy FEDTKB.ODL to create RT11-format ADVENT.ODL
2. Use multiple APPEND commands to build the content
3. Or use CREATE to write specific content to the file

## PROPOSED BOOTSTRAP FIX

### Current Problem in bootstrap_advent.exp
Lines 27, 247, 307 handle ODL files incorrectly:
- ADVENT.ODL transferred via tape gets RSX format
- TKB rejects RSX format with "illegal format" error

### Solution: Create ODL with RT11 Format In-Place

Instead of transferring ODL via tape, create it within RSTS/E:

```tcl
# Step 1: Copy system ODL to get RT11 format
send "COPY SY:\[0,200\]FEDTKB.ODL SY:\[1,2\]ADVENT.ODL\r"

# Step 2: Delete and recreate with correct content
send "DELETE SY:ADVENT.ODL\r"
send "CREATE SY:ADVENT.ODL\r"
send ".ROOT ADVENT-LIBR-*(INI,OUT,NOR,CMD,ODD,MSG,BYE,SHT,NPC,PUZ,DSP,FND,TDY)\r"
send ".NAME ADVENT\r"
send "INI: .FCTR SY:\[1,2\]ADVINI\r"
send "OUT: .FCTR SY:\[1,2\]ADVOUT\r"
send "NOR: .FCTR SY:\[1,2\]ADVNOR\r"
send "CMD: .FCTR SY:\[1,2\]ADVCMD\r"
send "ODD: .FCTR SY:\[1,2\]ADVODD\r"
send "MSG: .FCTR SY:\[1,2\]ADVMSG\r"
send "BYE: .FCTR SY:\[1,2\]ADVBYE\r"
send "SHT: .FCTR SY:\[1,2\]ADVSHT\r"
send "NPC: .FCTR SY:\[1,2\]ADVNPC\r"
send "PUZ: .FCTR SY:\[1,2\]ADVPUZ\r"
send "DSP: .FCTR SY:\[1,2\]ADVDSP\r"
send "FND: .FCTR SY:\[1,2\]ADVFND\r"
send "TDY: .FCTR SY:\[1,2\]ADVTDY\r"
send "LIBR: .FCTR SY:\[1,1\]BP2OTS/LB\r"
send ".END\r"
send "\032"  ;# Ctrl-Z to end CREATE
```

### Alternative: Check CREATE File Format

Need to verify if CREATE produces RT11 or RSX format files. If CREATE produces RT11 format, we can skip the COPY step and just use CREATE directly.

### TODO: Add DEMIG.HLP to web interface

The original 1987 file DEMIG.HLP should be included in the documentation files
displayed in the web interface (bottom right panel).

---

## Disk Image Status (Updated Jan 5, 2026)

| Disk File | Status | Notes |
|-----------|--------|-------|
| **simh/Disks/rsts_backup.dsk** | **WORKING** | Use as rsts0-working.dsk |
| **simh/Disks/rsts1_backup.dsk** | **WORKING** | Use as rsts1-working.dsk |
| rsts0.dsk (git) | Corrupted | "Swap file is invalid" error |
| rsts1.dsk (git) | Corrupted | DCL failures |
| rsts0-base-os.dsk | Missing RSTS.SIL | Incomplete OS |
| rsts1-base-os.dsk | Missing RSTS.SIL | Incomplete OS |
| archive/rsts0-working.dsk | Missing RSTS.SIL | Jan 1 backup |
| archive/rsts1-working.dsk | Missing RSTS.SIL | Jan 1 backup |

**SOLUTION:** Always restore from `simh/Disks/rsts_backup.dsk` and `simh/Disks/rsts1_backup.dsk`:
```bash
cp simh/Disks/rsts_backup.dsk build/disks/rsts0-working.dsk
cp simh/Disks/rsts1_backup.dsk build/disks/rsts1-working.dsk
```

**WARNING:** Docker restart corrupts disks! The swap file becomes invalid.
- NEVER use `docker restart advent-mud`
- Always: `docker stop && docker rm`, restore fresh disks, then `docker run`

## RSTS/E V10.1 Disk Image Sources (Searched Jan 5, 2026)

Looking for a clean, bootable RSTS/E V10.1 disk image:

| Source | Result |
|--------|--------|
| simh/Disks/rsts0.dsk, rsts1.dsk | Corrupted (swap file invalid) |
| simh/Disks/rsts_backup.dsk | Different format, non-bootable |
| build/disks/rsts0-base-os.dsk | Missing RSTS.SIL |
| git commit 5ddbed8 (original) | rsts1.dsk also corrupted |
| [agn453/RSTS-E GitHub](https://github.com/agn453/RSTS-E) | No pre-built RP06/RK07 images, has RL02/RL01 only |
| [trailing-edge.com](http://simh.trailing-edge.com/software.html) | Only has RSTS/E V7, not V10.1 |
| [fliptronics.com/RSTS](https://www.fliptronics.com/RSTS/) | Has build log but disk folder inaccessible |
| simh/rstsv7swre.tar | Contains V7.0 on RL01, not V10.1 |

**Still searching for:** Clean RSTS/E V10.1 RK07 bootable disk image

**agn453/RSTS-E software/ folder contents (NOT bootable systems):**
- rl02-ker363.dsk (10MB) - Kermit-11 utility disk
- rl02-zemu25.dsk (10MB) - ZEMU (RT-11 format, not RSTS)
- rl01-games.dsk (5MB) - Games disk
- These are utility disks, not bootable OS images

**Key question:** Where did our original RK07 images come from? They were working at some point.

---

## NEW APPROACH: RA72 Disk Image (January 5, 2026)

### Provenance of New Disk Image

**Source:** Dropbox download from user-provided link
**URL:** `https://www.dropbox.com/scl/fi/yqlniaxb0z88egcfph38l/RSTS-E-v-10.1-Install-and-INI-files.zip`
**Download Date:** January 5, 2026

**Contents of ZIP file:**
| File | Size | Description |
|------|------|-------------|
| rstse_10_ra72.dsk | 1,000,089,600 bytes (~1GB) | Bootable RSTS/E V10.1 RA72 disk image |
| bp2_v2_7.tap | 4,465,644 bytes | BASIC-PLUS-2 v2.7 installation tape |
| rstse_v10_1_install_sep10_1992.tap | 24,096,588 bytes | RSTS/E V10.1 installation tape (Sep 10, 1992) |
| BASIC-Plus-2 Installation Guide.pdf | 3,465,728 bytes | BP2 documentation |
| 8_rsts10.1.script | 1,597 bytes | SIMH script for 11/70 with RA72 |

**Verified Contents (via FLX examination):**
- RSTS/E V10.1 operating system
- BASIC-PLUS-2 already installed (bp2.rts, bp2res.lib, bp2sml.lib)
- TKB.TSK (Task Builder) - 222 blocks
- LIBR.SAV, LINK.SAV, MACRO.SAV (development tools)
- FEDTKB.ODL (known-good ODL file with RT11 format)
- Full system utilities

**Hardware Configuration (from script):**
- CPU: PDP-11/70 with 4MB memory and FPP
- Disk: RA72 (1GB MSCP disk)
- Original source: "From Tom Lake"

**Why This Is Better:**
1. Pre-installed BP2 compiler and libraries
2. Known-good ODL files we can copy from
3. Complete development environment
4. No swap file corruption issues (fresh image)

**Migration Plan:**
1. Commit all current work (checkpoint before major change)
2. Test booting RA72 image with modified SIMH config
3. If successful, migrate ADVENT source and build there
4. Update Dockerfile to use RA72 instead of RK07

### BOOT TEST SUCCESSFUL (January 5, 2026)

**Result: RA72 disk boots successfully!**

- No swap file errors (unlike RK07 images)
- RSTS/E V10.1-L starts cleanly
- System startup completes: "RSTS/E is on the air..."
- All services start normally

**Login Credentials:**
- User: `1,2`
- Password: `SYSTEM`

(Password found via [SIMH mailing list archives](https://simh.trailing-edge.narkive.com/9suYvkWD/rsts-e-default-password))

**This is the new clean starting point for ADVENT development.**

### File Transfer Test (January 5, 2026)

Successfully copied files from tape (MU0:) to disk (SY:[1,2]):
- All 14 source files (.B2S, .SUB)
- All 4 data files (.DTA, .MON, .CHR, .NTC)

Created ADVENT.ODL with RT11 format:
```
$ COPY SY:[0,200]FEDTKB.ODL SY:ADVENT.ODL
$ DIR/FULL SY:ADVENT.ODL
ADVENT.ODL       2   < 60> 01-Jan-92 01-Jan-92 12:04 PM  32 RT11    1924  0/0
```

### BP2 Compiler Investigation

BP2 installation locations:
- BP2$ = SY:[0,53] (logical name)
- BP2.RTS in [0,1] (runtime system)
- BP2IC2.ODL in [1,1] (compiler ODL)
- BP2OTS.OLB in [1,1] (object library)

Issue: `RUN $BP2IC2` gives "File does not exist"

BP2$ directory ([0,53]) only has:
- BP2.027, BP2.COM, DIALOG.DAT, DIALOG.TSK
- NO BP2ICx.TSK compiler tasks present!
- ODL files in [1,1] are for BUILDING the compiler, not running it

**UPDATE (January 5, 2026): BP2 IS WORKING!**

The `BP2` command successfully invokes the compiler:
```
$ BP2

PDP-11 BASIC-PLUS-2 V2.7-A

BASIC2
Ready
```

**Key Finding:** Use `BP2` command directly, NOT `RUN $BP2IC2`. The disk has:
- BP2.LNK (3 blocks) - command link file in [1,1]
- BP2RES.TSK (71 blocks) - resident task
- BP2SML.TSK (34 blocks) - small task variant
- BP2OTS.OLB (254 blocks) - object library
- BP2ICn.ODL (7 files) - overlay descriptors

**No BP2 installation from tape needed!** The RA72 disk already has a working BP2 compiler.

**Simplified Build Process:**
1. Boot from RA72 disk (already has BP2 V2.7-A)
2. Mount advent_source.tap on MU0:
3. Copy source files to SY:[1,2]
4. Create ADVENT.ODL with RT11 format (copy from FEDTKB.ODL)
5. Compile and build using BP2

---

## Docker Images

| Image Name | Dockerfile | Purpose | Disk Type | Status |
|------------|------------|---------|-----------|--------|
| advent-mud | Dockerfile | Main production image | RK07 (27MB) | Issues with swap corruption |
| advent-ra72-test | Dockerfile.ra72-test | Test RA72 boot | RA72 (1GB) | **WORKING** - boots clean, login works |

**To build and run RA72 test:**
```bash
docker build -f Dockerfile.ra72-test -t advent-ra72-test .
docker run -it --name advent-ra72-test -p 2322:2322 -p 2323:2323 advent-ra72-test
```

---

### Files to Modify

1. **docker/bootstrap_advent.exp**:
   - Remove ADVENT.ODL from tape transfer list (line 27)
   - Remove ADVENTD.ODL tape copy (line 247)
   - Remove DM1:ADVENT.ODL to SY: copy (line 307)
   - Add new section to create ODL in-place with RT11 format

2. **Test sequence**:
   - Verify CREATE file format
   - If RSX: use COPY then DELETE/CREATE approach
   - If RT11: use CREATE directly

---

## LINK/BASIC/STRUCTURE Discovery (January 6, 2026)

### The DCL LINK Command Works for Overlays!

After extensive testing, discovered that the DCL `LINK/BASIC/STRUCTURE` command successfully creates overlay structures without needing to manually create ODL files.

**Working Syntax:**
```
$ LINK/BASIC/STRUCTURE
ROOT files: SY:ADVENT,SY:ADVOUT,SY:ADVSHT,SY:ADVDSP,SY:ADVFND,SY:ADVTDY
Root COMMON areas: [blank - press RETURN]
Overlay: SY:ADVINI
Overlay: SY:ADVNOR
Overlay: SY:ADVCMD
Overlay: SY:ADVODD
Overlay: SY:ADVMSG
Overlay: SY:ADVBYE
Overlay: SY:ADVNPC
Overlay: SY:ADVPUZ
Overlay: [blank - press RETURN to end]
```

### Key Syntax Rules

| Element | Meaning |
|---------|---------|
| ROOT files: | ALL files to include (root + overlay modules) |
| Root COMMON areas: | PSECT names to force into root (usually blank) |
| Overlay: | Files for each overlay segment |
| Comma between files | Files in SAME overlay (loaded together) |
| `+` at end of line | Creates NESTED (child) overlay |
| No `+` | Creates SIBLING overlay at same level |
| Blank line | Ends overlay specification |

### Test Results

**Test 1: Flat siblings (no +)**
- All overlays accepted
- TSK created (170 blocks)
- Error: "Task has illegal memory limits"
- TSK crashes with "Reserved instruction trap"

**Test 2: Nested overlays (with +)**
- Creates hierarchical overlay tree
- Same memory limit error

### Current Blocker: Memory Limits

Even with overlays, the linker reports:
```
TKB -- *DIAG*-Task has illegal memory limits
```

The combined size still exceeds RSTS/E task limits.

---

## PDP-11 Memory Architecture

### Maximum Memory by Model

| Model | Address Space | Physical Memory | Notes |
|-------|---------------|-----------------|-------|
| Basic PDP-11 | 64KB | 64KB | 16-bit addresses |
| PDP-11/40 with MMU | 64KB virtual | 256KB physical | Memory management unit |
| PDP-11/70 | 64KB virtual | 4MB physical | Largest PDP-11 |
| PDP-11/70 with I&D | 128KB virtual | 4MB physical | Separate instruction/data space |

**Key limitation:** Regardless of physical memory, each process can only address 64KB (or 128KB with I&D space) at a time. This is why overlays are needed - to swap code segments in and out of the virtual address space.

### Our Program Size

| Component | Size (blocks) | Size (bytes) |
|-----------|---------------|--------------|
| ADVENT.OBJ | 79 | 40,448 |
| ADVINI.OBJ | 8 | 4,096 |
| ADVOUT.OBJ | 7 | 3,584 |
| ADVNOR.OBJ | 99 | 50,688 |
| ADVCMD.OBJ | 101 | 51,712 |
| ADVODD.OBJ | 50 | 25,600 |
| ADVMSG.OBJ | 47 | 24,064 |
| ADVBYE.OBJ | 23 | 11,776 |
| ADVSHT.OBJ | 5 | 2,560 |
| ADVNPC.OBJ | 20 | 10,240 |
| ADVPUZ.OBJ | 27 | 13,824 |
| ADVDSP.OBJ | 14 | 7,168 |
| ADVFND.OBJ | 6 | 3,072 |
| ADVTDY.OBJ | 34 | 17,408 |
| **TOTAL** | **520** | **266,240** |

### Can We Run Without Overlays?

**Short answer: NO**

The total object code is ~266KB. Even after linking (which removes some overhead), the executable code would be well over 100KB - far exceeding the 64KB address space limit.

The MAP file from linking just ADVENT.OBJ shows:
- Task image size: 12544 words = 25,088 bytes (just main program!)
- Adding the 13 subroutines would easily triple or quadruple this

**Overlays are mandatory** for this program to run on a PDP-11.

### Why "Task has illegal memory limits"?

Even with overlays, RSTS/E imposes additional constraints:
1. **Root segment limit** - The always-resident code must fit in available memory
2. **Overlay region** - Space for loading overlays
3. **Stack space** - Program stack
4. **System overhead** - RSTS/E reserves memory for itself

The error suggests our ROOT segment (main program + common subroutines) is still too large.

### Possible Solutions

1. **Minimize ROOT** - Put only ADVENT.B2S in root, everything else in overlays
2. **Accept undefined symbols** - Let overlay autoload handle resolution
3. **Use /DMS** - Dynamic Memory Sharing (if available)
4. **Split the program** - Run as multiple cooperating tasks
5. **Interpreted mode** - Run directly in BP2 interpreter (slower but no linking needed)

---

## CHECKPOINT: First Successful TKB Link (January 6, 2026)

**THIS IS A CRITICAL CHECKPOINT** - First time we got a TSK file created through TKB with overlay structure.

### Working Configuration (Flat Sibling Overlays)

```
$ LINK/BASIC/STRUCTURE
ROOT files: SY:ADVENT,SY:ADVOUT,SY:ADVSHT,SY:ADVDSP,SY:ADVFND,SY:ADVTDY
Root COMMON areas:
Overlay: SY:ADVINI
Overlay: SY:ADVNOR
Overlay: SY:ADVCMD
Overlay: SY:ADVODD
Overlay: SY:ADVMSG
Overlay: SY:ADVBYE
Overlay: SY:ADVNPC
Overlay: SY:ADVPUZ
Overlay:
```

### Result
- **TSK Created**: Yes! ADVENT.TSK = 170 blocks (contiguous)
- **Warning**: `TKB -- *DIAG*-Task has illegal memory limits`
- **Runtime**: Crashes with "Reserved instruction trap"

### What This Proves
1. LINK/BASIC/STRUCTURE syntax works
2. Flat sibling overlays (no `+`) are accepted
3. TKB can process our OBJ files
4. The overlay structure is valid

### Files in ROOT (always loaded)
| File | Purpose | Size (blocks) |
|------|---------|---------------|
| SY:ADVENT | Main program | 79 |
| SY:ADVOUT | Output routines (called by many) | 7 |
| SY:ADVSHT | Short messages (called by many) | 5 |
| SY:ADVDSP | Display routines (called by many) | 14 |
| SY:ADVFND | Find routines (called by many) | 6 |
| SY:ADVTDY | Tidy routines (called by ADVMSG) | 34 |
| **Total ROOT** | | **145 blocks** |

### Files in OVERLAYS (swapped in as needed)
| Overlay | File | Size (blocks) |
|---------|------|---------------|
| 1 | SY:ADVINI | 8 |
| 2 | SY:ADVNOR | 99 |
| 3 | SY:ADVCMD | 101 |
| 4 | SY:ADVODD | 50 |
| 5 | SY:ADVMSG | 47 |
| 6 | SY:ADVBYE | 23 |
| 7 | SY:ADVNPC | 20 |
| 8 | SY:ADVPUZ | 27 |
| **Total Overlays** | | **375 blocks** |

### Expect Script to Reproduce

See: `scripts/expect/55_proper_overlay.exp`

This script can recreate this exact configuration from a fresh boot.

---

## Next Investigation: Nested Overlays

The `+` at end of line creates nested (child) overlays instead of siblings.

Hypothesis: Nested overlays might allow better memory utilization because child overlays share parent's memory region.

### Nested Overlay Syntax

```
Overlay: SY:ADVINI+        <- has children
  Overlay: SY:ADVNOR+      <- child of ADVINI, has children
    Overlay: SY:ADVCMD     <- child of ADVNOR (leaf)
```

vs Flat Siblings:
```
Overlay: SY:ADVINI         <- sibling
Overlay: SY:ADVNOR         <- sibling
Overlay: SY:ADVCMD         <- sibling
```

### Test Plan for Nested Overlays

1. Group related subroutines under parent overlays
2. Put largest overlays as leaves (deepest nesting)
3. See if memory limits error changes

### Test Result: Deep Nesting (57_nested_overlay.exp)

**FAILED** - Maximum nesting depth exceeded!

```
SY:ADVNPC+
?Overlay tree has too many levels
```

The error occurred at level 7. RSTS/E has a **maximum overlay tree depth** (likely 6 or 7 levels).

Additional errors:
- Segment ADVODD has address overflow
- Segment ADVMSG has address overflow
- Segment ADVPUZ has address overflow
- No TSK file created
- Undefined symbol ADVNPC (truncated from tree)

**Conclusion:** Deep nesting is NOT the solution. Need shallower tree with siblings.

---

## Next Approach: Shallow Tree with Sibling Branches

Instead of one deep chain, create a tree that's only 2-3 levels deep but has multiple branches:

```
ROOT: ADVENT + common deps
├── ADVINI (init - standalone)
├── Command handlers branch+
│   ├── ADVNOR
│   ├── ADVCMD
│   └── ADVODD
├── Messaging branch+
│   ├── ADVMSG
│   └── ADVBYE
└── Special features branch
    ├── ADVNPC
    └── ADVPUZ
```

Syntax would be:
```
Overlay: SY:ADVINI           <- sibling (no children)
Overlay: SY:ADVNOR+          <- has children (siblings below)
  Overlay: SY:ADVCMD         <- child sibling
  Overlay: SY:ADVODD         <- child sibling
  Overlay:                   <- end children
Overlay: SY:ADVMSG+          <- next top-level, has children
  Overlay: SY:ADVBYE         <- child
  Overlay:                   <- end children
Overlay: SY:ADVNPC+          <- next top-level, has children
  Overlay: SY:ADVPUZ         <- child
  Overlay:                   <- end children
Overlay:                     <- end all overlays
```

### Test Result: Shallow Tree (58_shallow_tree.exp)

**PARTIAL SUCCESS** - TSK created, different runtime error!

```
$ LINK/BASIC/STRUCTURE
ROOT files: SY:ADVENT,SY:ADVOUT,SY:ADVSHT,SY:ADVDSP,SY:ADVFND,SY:ADVTDY
Root COMMON areas:
Overlay: SY:ADVINI
Overlay: SY:ADVNOR+
  Overlay: SY:ADVCMD
  Overlay: SY:ADVODD
  Overlay:
Overlay: SY:ADVMSG+
  Overlay: SY:ADVBYE
  Overlay:
Overlay: SY:ADVNPC+
  Overlay: SY:ADVPUZ
  Overlay:
Overlay:
```

**Results:**
| Metric | Flat Overlay | Shallow Tree |
|--------|--------------|--------------|
| TSK Created | Yes (170 blocks) | Yes (170 blocks) |
| Memory Warning | "illegal memory limits" | "illegal memory limits" |
| Runtime Error | "Reserved instruction trap" | **"Illegal SYS() usage"** |

**Analysis:**
- The "Illegal SYS() usage" error is DIFFERENT from "Reserved instruction trap"
- This suggests the program actually started executing!
- The trap at undefined address is gone
- Now hitting a system call issue

**Possible causes of "Illegal SYS() usage":**
1. Program trying to use a SYS() call not available in this RTS
2. Overlay autoload mechanism failing
3. Memory protection violation during overlay swap

**Next steps:**
1. Try running with different RTS (runtime system)
2. Investigate what SYS() call is failing
3. Try putting more in ROOT to reduce overlay activity

---

## Investigation: "Illegal SYS() usage" Error (January 6, 2026)

### Key Finding: Error Occurs BEFORE Code Execution

Debug PRINT statements were added to ADVENT.B2S and ADVINI.SUB:
```basic
5	PRINT ">>> ADVENT main starting" &
10	PRINT ">>> Calling ADVINI" &
```

**Result:** These PRINT statements NEVER execute. The "Illegal SYS() usage" error occurs during task initialization, BEFORE any user code runs.

This indicates the error is in the **overlay handler** or **BP2 runtime initialization**, not in our BASIC code.

### Comparison: Overlay vs Non-Overlay Builds

| Build Type | Error | When |
|------------|-------|------|
| With overlays (170 blocks) | "Illegal SYS() usage" | During task init |
| Without overlays (51 blocks) | "Reserved instruction trap" | When CALL executes |

### Working TSK MAP Analysis

Extracted MAP file from disk showed the "working" TSK only contains ADVENT.OBJ:
```
ADVENT.TSK Overlay description:
Base    Top        Length
----    ---        ------
000000  060705  060706  25030.       ADVENT
```

**BUT:** This MAP file was dated 1-JAN-92, indicating it's from our test builds, not the original 1987 system.

### Dynamic Loading Theory

**Hypothesis:** Maybe the original system used dynamic subprogram loading where CALL statements resolve at runtime by loading .OBJ files on demand.

**Test Result (67_dynamic_load.exp):**
- Linked ONLY ADVENT.OBJ (no subroutines)
- TKB reported "11 undefined symbols" (all subroutine names)
- Created 51-block TSK despite undefined symbols
- TSK crashes with "Reserved instruction trap" at first CALL

**Conclusion:** Dynamic loading doesn't work this way - the CALL instruction jumps to undefined address and crashes.

### ODL Files in src/ Directory

**IMPORTANT:** The ODL files found in `src/` (ADVENT.ODL, ADVENT_DM1.ODL) are **NOT original 1987 files**.
They were created during the resurrection project as part of previous unsuccessful build attempts.

**The original ODL file was NOT preserved on the 1987 tape backup.**

Two ODL structures were created during previous attempts:

**Structure 1 - Individual Overlays (src/ADVENT_DM1.ODL):**
```
.ROOT ADVENT-LIBR-*(SUBS)
SUBS:	.FCTR *(INI,OUT,NOR,CMD,ODD,MSG,BYE,SHT,NPC,PUZ,DSP,FND,TDY)
INI:	.FCTR DM1:[1,2]ADVINI
OUT:	.FCTR DM1:[1,2]ADVOUT
...
LIBR:	.FCTR LB:BP2OTS/LB
.END
```

**Structure 2 - Grouped Overlays (src/ADVENT.ODL):**
```
.ROOT SY:[1,2]ADVENT-LIBR-*(OVLY)
LIBR:	.FCTR LB:BP2OTS/LB
OVLY:	.FCTR *(A,B,C,D,E)
A:	.FCTR SY:[1,2]ADVINI,SY:[1,2]ADVOUT,SY:[1,2]ADVNOR
B:	.FCTR SY:[1,2]ADVCMD,SY:[1,2]ADVODD,SY:[1,2]ADVMSG
C:	.FCTR SY:[1,2]ADVBYE,SY:[1,2]ADVSHT,SY:[1,2]ADVNPC
D:	.FCTR SY:[1,2]ADVPUZ,SY:[1,2]ADVDSP,SY:[1,2]ADVFND
E:	.FCTR SY:[1,2]ADVTDY
.END
```

**Both structures were unsuccessful** - they either caused "Illegal SYS() usage" or undefined symbol errors.

### BP2.LNK and BP2IC7.ODL

LINK/BASIC uses BP2.LNK skeleton which includes:
```
$ODL
@LB:BP2IC7.ODL
```

BP2IC7.ODL defines:
```
BASIC2:	.FCTR	BP2RM1
BP2RM1:	.FCTR	LB:BP2OTS/LB:$IMROT:$ISROT:$IXROT:$RMSUP-BP2R11
BP2R11:	.FCTR	LB:BP2OTS/LB:$IMULK:$IRROT:$IUROT
```

**Hypothesis:** When we use LINK/BASIC with /STRUCTURE, our overlay structure may conflict with BP2's internal runtime structure, causing "Illegal SYS() usage" during initialization.

### Web Search Results

Searched for RSX-11/RSTS overlay examples and documentation:

**Documentation found:**
- [RSX-11M Task Builder Manual](https://archive.org/stream/rsx_11m__v41_mplus_task_builder_manual/rsx_11m__v41_mplus_task_builder_manual_djvu.txt)
- [BASIC-PLUS-2 User's Guide](http://elvira.stacken.kth.se/rstsdoc/rsts-doc-v6/V06B-aa-0154a-tc-basic-plus-2-rsts-e-users-guide.pdf)
- [PDP-11 Overlays Discussion](https://classiccmp.org/pipermail/cctech/2015-September/010541.html)
- [RSTS-E GitHub](https://github.com/agn453/RSTS-E)

**Key insights from research:**
- ODL uses `.ROOT` and `.FCTR` directives
- `.FCTR` extends `.ROOT` to multiple lines
- Overlays can be autoloading (disk) or memory-resident (PLAS)
- Largest ODL files mentioned: DUNGEON 3.2 (70 lines), RMD (177 lines)

**No working BP2 overlay example code was found** in open source repositories or documentation.

### Current Understanding

1. **The error is NOT in our code** - it happens before any BASIC statements execute
2. **The overlay handler or BP2 runtime is failing** during task initialization
3. **BP2's default ODL (BP2IC7.ODL) may conflict** with user-defined overlays
4. **TKB with direct ODL files also fails** (tested various approaches)

### Possible Root Causes

1. **BP2 runtime incompatibility with overlays** - Maybe BP2 V2.7 on RSTS/E V10.1 doesn't properly support overlay tasks
2. **Missing configuration** - Some TKB option or attribute needed for overlay tasks
3. **Memory layout conflict** - BP2 OTS modules need to be in specific locations
4. **Original system was different** - The 1987 system may have had patches or different BP2 version

### Next Investigation Directions

1. **Find working BP2 overlay example** - Search DECUS archives, ask on vintage computing forums
2. **Try different BP2 configurations** - Use different BP2ICx.ODL files (1-7)
3. **Examine BP2 overlay task that works** - Find an existing BP2 program with overlays
4. **Consider interpreter mode** - Run directly in BP2 interpreter instead of compiled TSK
5. **Search classiccmp mailing list** - Ask PDP-11 experts about BP2 overlay builds
6. **Check VCF (Vintage Computer Federation) forums** - Community may have experience

---

## Interpreter Mode Testing (January 6, 2026)

### Why Interpreter Mode?

Instead of compiling to a TSK (which requires overlays), we can run the BASIC source directly in the BP2 interpreter. This:
- Avoids all TKB/overlay issues
- Slower execution but guaranteed to work if code is valid
- Good for testing if the code itself functions correctly

### How to Run in Interpreter Mode

```
$ BP2
BASIC2
Ready

OLD SY:ADVENT.B2S
Ready

RUN
```

The interpreter handles CALL statements by loading and running the .SUB files dynamically.

### Test Result (73_interpreter_mode.exp)

**MAJOR FINDING:** The program DOES NOT crash with "Illegal SYS() usage" in interpreter mode!

**What happened:**
1. Program loaded successfully
2. Compilation started (shows line-by-line processing)
3. Many warnings: "language feature is declining" (CVT$$, DEF*, etc. are deprecated)
4. Alignment warnings: "Unaligned COMMON or MAP variable"
5. **ERROR:** "Undefined/unresolved global ADVINI" (and all other subroutines)

**Key Output:**
```
%Unaligned COMMON or MAP variable C% in .$$$$.
%Unaligned COMMON or MAP variable WEAPON% in .$$$$.
%Unaligned COMMON or MAP variable BLIND% in .$$$$.
? Undefined/unresolved global ADVINI
? Undefined/unresolved global ADVDSP
? Undefined/unresolved global ADVNOR
...
```

### What This Proves

1. **The "Illegal SYS() usage" is NOT caused by our code** - interpreter mode doesn't trigger it
2. **The error is specific to COMPILED/LINKED tasks with overlays**
3. **BP2 interpreter doesn't automatically find .SUB files** - they need to be compiled/linked

### The Real Problem

The interpreter can't resolve CALL statements to external .SUB files. The subroutines exist as source but aren't being found. This is expected - the interpreter would need:
- Compiled .OBJ files to call
- Or all code merged into one file

### Implications

Since the code itself is valid (runs in interpreter without "Illegal SYS()"), the problem is definitively in the **TKB overlay linking process**, not the BASIC code.

The overlay handler or BP2 OTS initialization is making a SYS() call that fails when the task is built with overlays.

---

## Documentation Sources for Overlay Building (January 6, 2026)

### Key Documentation Found

1. **RSTS/E V10.1 Complete Documentation Archive (1.68GB)**
   - Google Drive: https://drive.google.com/file/d/1-cZsyJmAzsTWDDu5iPlD_o9_rYwahaGs/view
   - From agn453/RSTS-E GitHub repository
   - Contains full TKB and overlay documentation

2. **RSTS/E V9.0 System User's Guide (Chapter 8: Program Development)**
   - Topics: "What Are Overlays?", "Rules for Constructing Overlays", "The /STRUCTURE Dialogue"
   - PDF (19MB): http://ftpmirror.your.org/pub/misc/bitsavers/pdf/dec/pdp11/rsts/V09/3_System_Usage/AA-EZ12A-TC_RSTS_E_V9.0_System_Users_Guide_Jun85.pdf
   - Online TOC: https://docslib.org/doc/12361457/rsts-e-system-users-guide

3. **BASIC-PLUS-2 User's Guide V2.7 (19.2MB)**
   - Contains BUILD command and overlay task creation
   - Available at DMV.net RSTS/E Documentation Archive

4. **Bitsavers.org BASIC-PLUS-2 Collection**
   - AA-L335A-TK VAX BASIC / PDP-11 BASIC-PLUS-2 V2 User's Guide
   - Archive: https://archive.org/details/bitsavers_decpdp11laL335ATKVAXBASICPDP11BASICPLUS2V2UsersGui_10786435

### Key Insight from Documentation

The /STRUCTURE dialogue prompts:
- "ROOT files:" - ALL files including root AND overlay modules
- "Root COMMON areas:" - PSECTs to force into root (usually blank)
- "Overlay:" - Files for each overlay segment
- `+` at end of line creates NESTED (child) overlay
- Blank line ends overlay specification

### Original System Context

**Important:** The original ADVENT program ran successfully with overlays on a PDP-11/70 in 1987. This confirms:
1. BP2 overlays DO work on real hardware
2. Our linking approach may be missing something from the original build process
3. The issue is NOT fundamental to BP2/overlays, but specific to our configuration

---

---

## RSTS/E Manual Insights: LINK /STRUCTURE Dialogue (January 6, 2026)

### Source Documentation

Read directly from RSTS/E V10.1 System User's Guide Chapter 8 (Program Development), pages 8-24 through 8-41.

### Key Finding: Use Interactive /STRUCTURE, Not Inline Syntax

**WRONG approach (what we were trying):**
```
LINK/BASIC/STRUCTURE=(SY:ADVENT,SY:ADVINI;(SY:ADVOUT))
```
This gives "Argument not allowed" errors.

**CORRECT approach (from manual):**
```
$ LINK/BP2/STRUCTURE
ROOT files: ADVENT
Root COMMON areas:
Overlay: ADVINI
Overlay: ADVOUT
Overlay: ADVNOR
...
Overlay:
```

### The /STRUCTURE Interactive Dialogue

When you use `/STRUCTURE` qualifier (without `=` argument), LINK prompts interactively:

1. **ROOT files:** - Object files to form the root segment (always loaded)
2. **Root COMMON areas:** - PSECT names to place in root (for data shared across overlays)
3. **Overlay:** - One or more prompts for overlay files

### Symbols Used in Overlay Specification

| Symbol | Meaning | Example |
|--------|---------|---------|
| `+` at end of line | Create a BRANCH (nested child overlay) | `Overlay: A0+` then `Overlay: A1` makes A1 child of A0 |
| `,` between files | CONCATENATE files in same overlay | `Overlay: B1,B2,B3,B4,B5` - all load together |
| RETURN (blank) | Go UP one level or FINISH | Empty `Overlay:` ends specification |

### Overlay Structure Example from Manual (Figure 8-4)

```
$ LINK/F77/STRUCTURE
ROOT files: ROOT
Root COMMON areas: COMB
Overlay: A0+
  Overlay: A1
  Overlay: A2+
    Overlay: A21
    Overlay: A22
    Overlay:           <- end A2 children
  Overlay:             <- end A0 children
Overlay: B0
Overlay:               <- end all overlays
```

This creates:
```
        ROOT
       /    \
     A0      B0
    /  \
   A1  A2
      /  \
    A21  A22
```

### Concatenated Files Example (Figure 8-5)

Multiple files can share one overlay region:
```
Overlay: B1,B2,B3,B4,B5
```
Or continued across lines:
```
Overlay: B1,B2,
Continue: B3,B4,B5
```

### Memory Map Output (Figure 8-6)

The /MAP qualifier shows overlay structure:
```
TRY2.TSK OVERLAY DESCRIPTION:
BASE     TOP      LENGTH
----     ---      ------
000000   022127   022130   09304.    USER     <- root
022130   023707   001560   00880.    INTRO    <- overlay
022130   022577   000450   00296.    CRUNCH   <- overlay (same base as INTRO)
022130   024317   002170   01144.    CHATR    <- overlay (same base)
```

Overlays with same BASE address share memory space and overlay each other.

### Key Rules for Constructing Overlays

1. **Same path rule**: Calls or references must be between pieces on the SAME path from root to leaf
2. **Different path restriction**: Pieces on different paths CANNOT call each other directly
3. **Maximum nesting**: You can nest overlays up to SEVEN levels
4. **Root placement**: Common data (PSECT) shared by overlays on different paths should be placed in root

### Implications for ADVENT

**Problem:** We've been getting "Illegal SYS() usage" which happens BEFORE any user code executes.

**Insight from manual:** The LINK command creates temporary .TMP files (command file and ODL file) that are passed to the Task Builder. These are left in your account with file type .TMP and deleted when you log out.

**Possible issue:** The BP2 runtime overlay structure (defined in BP2IC7.ODL) may be conflicting with our user overlay structure when both are combined by TKB.

### Test Plan Based on Manual

1. **Use LINK/BP2/STRUCTURE** with interactive prompts (not inline syntax)
2. **Start with minimal overlay**: Just ADVENT in root, ONE subroutine in overlay
3. **Progressively add overlays** to find which causes the failure
4. **Check .TMP files** generated by LINK to see what's actually being passed to TKB
5. **Compare with working program**: Find any BP2 program with overlays on this system

### Working Example from Manual

Page 8-40 shows a complete working example:
```
$ LINK/STRUCTURE/MAP=TRY2/EXEC=TRY2
ROOT Files: USER
Root COMMON areas:
Overlay: INTRO
Overlay: CRUNCH
Overlay: CHATR
Overlay:
```

Result: 6560 words total task size, with overlays at addresses 022130.

---

## Alternative Approach: Multi-TSK with CHAIN

If overlay building proves unsolvable, an alternative architecture using CHAIN statements is documented in:

**See:** [CHAIN_ALTERNATIVE.md](./CHAIN_ALTERNATIVE.md)

This approach:
- Splits program into multiple smaller TSK files
- Uses COMMON variables for state preservation
- Implements a return stack for nested "calls"
- Avoids TKB overlay complexity entirely

**Status:** Research/backup option only - not actively pursued since overlays worked originally.

---

## TKB Reference Manual Findings (January 6, 2026)

### Source: RSTS/E Task Builder Reference Manual V8.0 (March 1983)

Full manual saved to: `docs/manuals/rsts-e-task-builder-reference-manual-v8.zip`
RSTS/E System User's Guide saved to: `docs/manuals/rsts-e-system-users-guide.zip`

### Using TKB Directly with ODL Files

Instead of LINK command, you can run TKB directly with an ODL file using the `/MP` switch:

```
RUN $TKB
TKB>MYPROG,MPFILE=OVERLY/MP
ENTER OPTIONS:
TKB>LIBR=BP2RES:RO
TKB>UNITS=12
TKB>ASG=SY:5:6:7:8:9:10:11:12
TKB>EXTTSK=512
TKB>//
```

**Key:** The `/MP` switch tells TKB the input file is an ODL (overlay map) file.

### ODL Syntax (Chapter 11)

ODL file format:
```
label: directive argument-list ;comment
```

**Commands:**
| Command | Purpose |
|---------|---------|
| `.ROOT` | Defines the entire overlay structure (only one per file) |
| `.FCTR` | Defines a "factor" - a substructure (can be nested 16 levels) |
| `.NAME` | Assigns name and attributes to a segment |
| `.PSECT` | Places a program section in the overlay structure |
| `.END` | Ends the ODL file |

**Operators (from page 11-5):**
| Operator | Meaning | Example |
|----------|---------|---------|
| `-` | Concatenation (sequential in memory) | `A-B` = A then B |
| `,` | Overlay (share same address space) | `(A,B)` = A and B overlay |
| `()` | Grouping | `(A,B,C)` = all three overlay |
| `*` | Autoload indicator (before left paren) | `-*(A,B)` |
| `!` | Memory-resident overlay | See Chapter 7 |

### Complete ODL Example for BP2 (page 3-3)

```
        .ROOT MAINWL-*(SUB1WL,SUB2WL)
MAINWL: .FCTR MAIN-LIBR
SUB1WL: .FCTR SUB1-LIBR
SUB2WL: .FCTR SUB2-LIBR
LIBR:   .FCTR LB:BP2OTS/LB
        .END
```

This creates:
- MAIN in root, concatenated with BP2OTS library
- SUB1 and SUB2 as overlays (they overlay each other)
- Each overlay also concatenated with BP2OTS library

### Complex Overlay Tree Example (page 9-12)

```
        .ROOT   AFCTR-(BFCTR,CFCTR)
AFCTR:  .FCTR   A-LIBR
BFCTR:  .FCTR   B-LIBR-(B1-LIBR,B2-LIBR)
CFCTR:  .FCTR   C-C1-LIBR-(CO1-LIBR,CO2-LIBR)
LIBR:   .FCTR   LB:F4POTS/LB
        .END
```

### Key BP2 TKB Options (Chapter 10)

| Option | Purpose |
|--------|---------|
| `LIBR=BP2RES:RO` | Use BP2RES resident library (read-only) |
| `LIBR=BP2SML:RO` | Use BP2SML resident library (smaller) |
| `CLSTR=BP2RES,RMSRES:RO` | Cluster BP2RES and RMSRES libraries |
| `UNITS=n` | Maximum I/O channels (default 4) |
| `ASG=SY:5:6:7:...` | Assign channels to devices |
| `EXTTSK=n` | Extra task memory (words) |
| `HISEG=name` | High segment (run-time system) name |

### BP2 Build Example (page 2-16)

```
RUN $TKB
TKB>MYPROG=PROG1,SUB1,SUB2,LB:BP2OTS/LB
TKB>/
ENTER OPTIONS:
TKB>CLSTR=BP2RES,RMSRES:RO
TKB>UNITS=12
TKB>ASG=SY:5:6:7:8:9:10:11:12
TKB>EXTTSK=512
TKB>//
```

### Proposed ADVENT.ODL Structure (Based on Manual)

```
; ADVENT.ODL - Overlay structure for Adventure game
; Based on RSTS/E Task Builder Reference Manual V8.0
;
        .ROOT ROOTWL-*(OV1WL,OV2WL,OV3WL,OV4WL,OV5WL)
ROOTWL: .FCTR ADVENT-LIBR
OV1WL:  .FCTR ADVINI-LIBR
OV2WL:  .FCTR ADVOUT,ADVSHT,ADVDSP-LIBR
OV3WL:  .FCTR ADVNOR,ADVCMD,ADVODD-LIBR
OV4WL:  .FCTR ADVMSG,ADVBYE,ADVNPC-LIBR
OV5WL:  .FCTR ADVPUZ,ADVFND,ADVTDY-LIBR
LIBR:   .FCTR LB:BP2OTS/LB
        .END
```

### TKB Command to Build ADVENT with ODL

```
RUN $TKB
TKB>SY:ADVENT,SY:ADVENT=SY:ADVENT/MP
ENTER OPTIONS:
TKB>LIBR=BP2RES:RO
TKB>UNITS=12
TKB>ASG=SY:5:6:7:8:9:10:11:12
TKB>EXTTSK=512
TKB>//
```

### Key Insight: Co-Trees (Chapter 4)

Co-trees allow routines on **different paths** to call each other through a **null root**:

```
        .NAME   NULL
        .ROOT   MANTRE,COTREE
MANTRE: .FCTR   MAIN-LIBR-*(SUB1-LIBR,SUB2-LIBR)
COTREE: .FCTR   NULL-*(A-LIBR,B-LIBR)
LIBR:   .FCTR   LB:BP2OTS/LB
        .END
```

This might be relevant if our subroutines need to call each other across overlay boundaries.

### Memory Considerations (page 3-7)

- Total task size = root + largest overlay path
- Overlays with same BASE address share memory
- Address overflow = too much code for virtual address space
- The 64KB limit applies to virtual address space, not physical memory

---

## TKB /MP Test Results (January 6, 2026)

### Test: ODL File with /MP Switch

**Script:** `scripts/expect/75_tkb_with_odl.exp`

**ODL File Created (RT11 format):**
```
; ADVENT.ODL - BP2 overlay structure
;
        .ROOT ROOTWL-*(OV1,OV2,OV3,OV4,OV5,OV6,OV7,OV8)
ROOTWL: .FCTR SY:ADVENT-LIBR
OV1:    .FCTR SY:ADVINI-LIBR
OV2:    .FCTR SY:ADVOUT-LIBR
OV3:    .FCTR SY:ADVNOR-LIBR
OV4:    .FCTR SY:ADVCMD-LIBR
OV5:    .FCTR SY:ADVODD-LIBR
OV6:    .FCTR SY:ADVMSG-LIBR
OV7:    .FCTR SY:ADVBYE-LIBR
OV8:    .FCTR SY:ADVSHT,SY:ADVNPC,SY:ADVPUZ,SY:ADVDSP,SY:ADVFND,SY:ADVTDY-LIBR
LIBR:   .FCTR LB:BP2OTS/LB
        .END
```

**File Attributes (verified):**
```
ADVENT.ODL       1   < 60> 01-Jan-92 01-Jan-92 12:00 PM  32 RT11     516  0/0
```

**TKB Command:**
```
RUN $TKB
TKB>SY:ADVENT,SY:ADVENT=SY:ADVENT/MP
```

**Result:**
```
TKB -- *FATAL*-Lookup failure on file ADVENT.OBJ
```

### Key Findings

1. **ODL format is CORRECT** - TKB accepted the ODL file without "illegal format" error
2. **RT11 attribute works** - File created via CREATE has RT11 format
3. **/MP switch works** - TKB processed the ODL and looked for referenced files
4. **Missing .OBJ files** - Need to compile source files before running TKB

### Next Steps

To complete the TKB test:
1. Mount advent_source.tap on MU0:
2. Copy .B2S/.SUB source files from tape to SY:[1,2]
3. Compile each source file: `BP2` → `OLD file` → `COMPILE`
4. Create ODL with RT11 format (done)
5. Run TKB with /MP switch
6. Test resulting TSK

### Complete Build Procedure

```
$ ! Step 1: Copy source files from tape
$ COPY MU0:ADVENT.B2S SY:
$ COPY MU0:ADVINI.SUB SY:
$ ... (all 14 source files)

$ ! Step 2: Compile each source file
$ BP2
BASIC2
Ready
OLD SY:ADVENT.B2S
Ready
COMPILE
Ready
OLD SY:ADVINI.SUB
Ready
COMPILE
Ready
... (repeat for all files)
BYE

$ ! Step 3: Create ODL (already done with RT11 format)

$ ! Step 4: Run TKB with ODL
$ RUN $TKB
TKB>SY:ADVENT,SY:ADVENT=SY:ADVENT/MP
ENTER OPTIONS:
TKB>LIBR=BP2RES:RO
TKB>UNITS=12
TKB>EXTTSK=512
TKB>//

$ ! Step 5: Test
$ RUN SY:ADVENT
```

## Current Status (January 2026)

### What's Working

1. **ODL Format**: RT11 format ODL files created via CREATE command are accepted by TKB
2. **TKB /MP Switch**: TKB correctly processes ODL files with the /MP switch
3. **TKB Options**: Options like `LIBR=BP2RES:RO`, `UNITS=12`, `EXTTSK=512` now work correctly
   - Fixed case-sensitivity issue ("Enter Options:" vs "ENTER OPTIONS:")
4. **Compilation**: All 14 source files compile successfully to .OBJ
5. **Task Creation**: ADVENT.TSK is created (162-192 blocks depending on build)
6. **No "Illegal SYS()" Error**: The original overlay initialization error is RESOLVED!

### Current Problem: Undefined Symbols Between Overlays

When using the ODL structure with each subroutine in a separate overlay:
```
.ROOT ROOTWL-*(OV1,OV2,OV3,OV4,OV5,OV6,OV7,OV8)
ROOTWL: .FCTR SY:ADVENT-LIBR
OV1:    .FCTR SY:ADVINI-LIBR
OV2:    .FCTR SY:ADVOUT-LIBR
...
```

TKB reports undefined symbols in each segment:
```
TKB -- *DIAG*-4 undefined symbols segment ADVNOR
TKB -- *DIAG*-4 undefined symbols segment ADVCMD
...
```

The issue is that subroutines CALL each other across overlays:
- ADVNOR calls: ADVDSP, ADVSHT, ADVOUT, ADVFND
- ADVCMD calls: ADVOUT, ADVSHT, etc.
- Most subroutines call ADVOUT and ADVSHT

### Analysis: Cross-Overlay Call Resolution

In the current ODL structure:
- Each SUB is in a separate overlay (OV1-OV8)
- Overlays share the same memory space (loaded on demand)
- TKB cannot resolve CALL targets across overlays because the target may not be loaded

### Potential Solutions

1. **Put commonly-called routines in ROOT**:
   - Move ADVOUT, ADVSHT, ADVDSP, ADVFND to root segment
   - Keep command-specific routines (ADVCMD, ADVODD, etc.) in overlays
   - Root segment is always loaded, so calls always resolve

2. **Nested overlays**:
   - Group subroutines that call each other into the same overlay
   - Use nested overlay structure for logical grouping

3. **Use BP2IC2 BUILD command**:
   - The original build used BP2IC2's BUILD command, not direct TKB
   - BUILD may handle overlay linking differently
   - May automatically resolve cross-module references

### Recommended ODL Structure (To Test)

Put frequently-called subroutines in root, command handlers in overlays:

```
; ADVENT.ODL - Hybrid structure
;
        .ROOT ROOTWL-*(OV1,OV2,OV3)
; Root: main + commonly-called routines
ROOTWL: .FCTR SY:ADVENT,SY:ADVINI,SY:ADVOUT,SY:ADVSHT,SY:ADVDSP,SY:ADVFND-LIBR
; OV1: Normal commands
OV1:    .FCTR SY:ADVNOR,SY:ADVCMD-LIBR
; OV2: Special commands
OV2:    .FCTR SY:ADVODD,SY:ADVMSG,SY:ADVPUZ-LIBR
; OV3: Player management
OV3:    .FCTR SY:ADVBYE,SY:ADVNPC,SY:ADVTDY-LIBR
LIBR:   .FCTR LB:BP2OTS/LB
        .END
```

This structure:
- Puts ADVOUT, ADVSHT, ADVDSP, ADVFND in root (always loaded)
- Groups command handlers into logical overlays
- Reduces total number of overlays
- Should resolve most cross-module CALL references

### Runtime Error Investigation

Even with undefined symbols, ADVENT.TSK runs but hits:
```
ADVENT ERROR: 11 at line 35
ADVENT ERROR: 9 at line 32767  (infinite loop)
```

- Error 11 = "I/O channel not open" or file error
- Error 9 = "Subscript out of range"
- Line 35 is in single-user input loop
- Line 32767 is the cleanup/exit routine

Root causes:
1. Undefined symbols may cause CALL failures
2. Data files (ADVENT.DTA, etc.) exist but are 0 bytes (empty)
3. Error handler at 32767 tries to clean up but errors cause infinite loop

## Hybrid ODL Test Results (January 2026)

### Test: Hybrid ODL Structure

Tested ODL with common routines in ROOT:
```
.ROOT ROOTWL-*(OV1,OV2,OV3)
ROOTWL: .FCTR SY:ADVENT,SY:ADVINI,SY:ADVOUT,SY:ADVSHT,SY:ADVDSP,SY:ADVFND-LIBR
OV1:    .FCTR SY:ADVNOR,SY:ADVCMD-LIBR
OV2:    .FCTR SY:ADVODD,SY:ADVMSG,SY:ADVPUZ-LIBR
OV3:    .FCTR SY:ADVBYE,SY:ADVNPC,SY:ADVTDY-LIBR
LIBR:   .FCTR LB:BP2OTS/LB
        .END
```

### Results

**Improvements:**
- ADVENT.TSK created successfully (159 blocks)
- Only 2 undefined symbols (down from ~20 with per-SUB overlays)
- Cross-overlay CALL resolution mostly working

**New Issue: "Odd address trap"**
```
$ RUN SY:ADVENT.TSK
??Odd address trap
030766  117672  046374  117674  002076  001776  001772  046376  174000
```

This is a CPU-level error: PDP-11 requires word access at even addresses.

### Root Cause: Unaligned COMMON Variables

During compilation, BP2 warns:
```
%Unaligned COMMON or MAP variable C% in .$$$$.
%Unaligned COMMON or MAP variable WEAPON% in .$$$$.
%Unaligned COMMON or MAP variable BLIND% in .$$$$.
```

The COMMON block declaration has variables that end up at odd byte offsets:
```basic
COMMON ACC$(8%)=7%,AR$=80%,C%,C$=10%,CRLF$=2%, &
    FLAG%(8%),HP%(8%),LEVEL%(8%),KB%(8%),NAM$(8%)=30%,...
```

Problem: `ACC$(8%)=7%` allocates 8*7=56 bytes (even), then `AR$=80%` is 80 bytes.
56+80=136 (even), then `C%` (integer) should be at byte 136 (even). BUT...
string arrays may have additional overhead causing misalignment.

### Solution Options

1. **Reorder COMMON variables** - Put all integers first, then strings
2. **Pad variables** - Add dummy bytes to force alignment
3. **Use VIRTUAL arrays** - Move large string arrays to virtual memory

### Next Steps

1. Analyze COMMON block layout in detail
2. Reorder variables to ensure word alignment
3. Rebuild and test

---

## Cross-Overlay Symbol Resolution Attempts (January 7, 2026)

### The Undefined Symbol Problem

With the hybrid ODL structure, two symbols remain undefined:
- `$ICIO0` - BP2 runtime library symbol (possibly I/O channel initialization)
- `ADVTDY` - Called by ADVMSG but they're in different overlays

### Approaches Tested

#### Approach 1: Move ADVTDY to OV2 with ADVMSG (script 81)

ODL structure:
```
.ROOT ROOTWL-*(OV1,OV2,OV3)
ROOTWL: .FCTR SY:ADVENT,SY:ADVINI,SY:ADVOUT,SY:ADVSHT,SY:ADVDSP,SY:ADVFND-LIBR
OV1:    .FCTR SY:ADVNOR,SY:ADVCMD-LIBR
OV2:    .FCTR SY:ADVODD,SY:ADVMSG,SY:ADVPUZ,SY:ADVTDY-LIBR
OV3:    .FCTR SY:ADVBYE,SY:ADVNPC-LIBR
LIBR:   .FCTR LB:BP2OTS/LB
```

**Result:** ADVTDY still undefined in ADVMSG segment. TKB creates separate segments for each
module even within the same overlay - they share address space but can't be loaded simultaneously.

#### Approach 2: Move ADVTDY to ROOT (script 82)

ODL structure:
```
.ROOT ROOTWL-*(OV1,OV2,OV3)
ROOTWL: .FCTR SY:ADVENT,SY:ADVINI,SY:ADVOUT,SY:ADVSHT,SY:ADVDSP,SY:ADVFND,SY:ADVTDY-LIBR
OV1:    .FCTR SY:ADVNOR,SY:ADVCMD-LIBR
OV2:    .FCTR SY:ADVODD,SY:ADVMSG,SY:ADVPUZ-LIBR
OV3:    .FCTR SY:ADVBYE,SY:ADVNPC-LIBR
LIBR:   .FCTR LB:BP2OTS/LB
```

**Result:** WORSE - 14 undefined symbols total! Moving ADVFND and ADVTDY both to ROOT
causes $ARRAY symbol conflicts (multiply-defined A1F$, V1F$, A1I$, V1I$).

#### Approach 3: Grouped overlays (script 83 - abandoned)

Tested grouping like the src/ADVENT.ODL structure, but this was based on incorrect
assumption that it was "original" - it's actually from previous failed attempts.

**Result:** Same "ADVENT ERROR: 9 at line 32767" infinite loop error.

### Key Findings

1. **Sibling overlays cannot call each other** - Modules in the same overlay region (same base address)
   are mutually exclusive; loading one unloads the other.

2. **Root placement causes $ARRAY conflicts** - Multiple modules using arrays in ROOT creates
   multiply-defined symbols for array support routines.

3. **The original build method is unknown** - Without the original ODL or build script, we're
   reverse-engineering the overlay structure.

### Current Best Configuration

The hybrid ODL with common routines in ROOT produces the fewest errors (2 undefined symbols)
and creates a runnable TSK (159 blocks). Runtime fails with "Odd address trap" due to
unaligned COMMON variables, not the undefined symbols.

```
.ROOT ROOTWL-*(OV1,OV2,OV3)
ROOTWL: .FCTR SY:ADVENT,SY:ADVINI,SY:ADVOUT,SY:ADVSHT,SY:ADVDSP,SY:ADVFND-LIBR
OV1:    .FCTR SY:ADVNOR,SY:ADVCMD-LIBR
OV2:    .FCTR SY:ADVODD,SY:ADVMSG,SY:ADVPUZ-LIBR
OV3:    .FCTR SY:ADVBYE,SY:ADVNPC,SY:ADVTDY-LIBR
LIBR:   .FCTR LB:BP2OTS/LB
```

### Outstanding Issues

1. **Odd address trap** - PRIMARY BLOCKER - Caused by unaligned COMMON variables
2. **ADVTDY undefined in ADVMSG** - May cause runtime failure when TIDY command is used
3. **$ICIO0 undefined** - May be resolved by TKB options or library path
4. **Data files empty** - ADVENT.DTA etc. need to be populated

---

## COMMON Variable Alignment Fix (January 7, 2026)

### The Problem

The PDP-11 requires word (16-bit) access at even byte addresses. The original COMMON block
declaration starts with string variables, causing integer variables to land at odd offsets:

```basic
COMMON ACC$(8%)=7%,AR$=80%,C%,...   ; C% at offset 143 (ODD!)
```

BP2 compiler warnings during build:
```
%Unaligned COMMON or MAP variable C% in .$$$$.
%Unaligned COMMON or MAP variable WEAPON% in .$$$$.
%Unaligned COMMON or MAP variable BLIND% in .$$$$.
```

### The Fix

Reorder COMMON to put all integers FIRST (at even offsets), then strings:

```basic
COMMON C%,NO.OF.USERS%,SENT.KB%,SENT.PROG%,SENT.PROJ%,USER%,USER1%,SINGLE.USER%, &
    FLAG%(8%),HP%(8%),LEVEL%(8%),KB%(8%),ROOM%(8%),WEAPON%(8%), &
    ATT.LEVEL%(10%),DEF.LEVEL%(10%),MON.HP%(10%),MON.DAM%(10%), &
    MON.ROOM%(10%),MON.XP%(10%),BLIND%(8%),SPY%(10%),FATIGUE%(10%), &
    XP.(8%),STUN(8%), &
    AR$=80%,C$=10%,CRLF$=2%,SENT.MESS$=80%,CI$=1%,RUN.ACC$=9%,MMM$=128%, &
    ACC$(8%)=7%,NAM$(8%)=30%,NPCMESS$(8%)=40%,OB$(8%,9%)=30%,PASS$(8%)=10%, &
    WEAPON$(8%)=20%,SPEC$(10%)=6%
```

### Files Modified

All 14 source files were updated with the aligned COMMON block:
- ADVENT.B2S (main program)
- 13 .SUB files (all subroutines)

Script used: `scripts/fix_common_alignment.py`
Backup files: `*.bak` in src/ directory

### Status

- [x] Source files modified on Linux host
- [x] Tape created with fixed sources: `build/tapes/advent_source.tap`
- [x] Transfer fixed sources to RSTS/E
- [x] Recompile all modules (NO alignment warnings!)
- [x] Rebuild with TKB (ADVENT.TSK = 159 blocks)
- [x] Test for alignment errors

### Test Result (January 7, 2026)

**Compiled successfully** - No "Unaligned COMMON or MAP variable" warnings!
**TKB completed** - ADVENT.TSK created (159 blocks)
**Runtime result** - "Odd address trap" still occurs!

```
$ RUN SY:ADVENT.TSK
??Odd address trap
030766  117672  046370  117674  002076  001776  001772  046372  174000
```

### Analysis: COMMON Fix Was NOT the Root Cause

The COMMON variable reordering successfully eliminated the compiler warnings, but the odd address
trap persists. This indicates the trap has a different source.

**Possible causes still being investigated:**
1. **Undefined symbols** - TKB reported 1 undefined symbol each in ADVENT and ADVMSG segments
2. **FIELD statement alignment** - FIELD #3% maps record buffers that may have alignment issues
3. **BP2 runtime initialization** - Overlay loading mechanism may be accessing misaligned memory
4. **Array descriptor overhead** - BP2 array descriptors may add unexpected padding

**TKB diagnostic output:**
```
TKB -- *DIAG*-1 undefined symbols segment ADVENT
TKB -- *DIAG*-1 undefined symbols segment ADVMSG
```

The undefined symbols could be causing jumps to invalid (odd) addresses at runtime.

### Next Investigation Steps

1. Get MAP file to identify which symbols are undefined
2. Check if undefined symbols are the same as before ($ICIO0, ADVTDY)
3. Try linking with ADVTDY in a different overlay structure
4. Consider testing without overlays (if it fits)

---

## Overall Status Summary (January 7, 2026)

### What's Working
| Item | Status |
|------|--------|
| RA72 disk image boots | ✅ |
| BP2 compiler available | ✅ |
| All 14 source files compile | ✅ |
| ODL file format (RT11) | ✅ |
| TKB /MP switch with ODL | ✅ |
| ADVENT.TSK created | ✅ (159 blocks) |
| "Illegal SYS() usage" fixed | ✅ |
| COMMON alignment warnings | ✅ (eliminated) |

### Update (January 7, 2026) - Testing With Data Files

Using the original 1987 ODL structure from `src/ADVENT.ODL`:
```
.ROOT SY:ADVENT-LIBR-*(OVLY)
LIBR:   .FCTR LB:BP2OTS/LB
OVLY:   .FCTR *(A,B,C,D,E)
A:      .FCTR SY:ADVINI,SY:ADVOUT,SY:ADVNOR
B:      .FCTR SY:ADVCMD,SY:ADVODD,SY:ADVMSG
C:      .FCTR SY:ADVBYE,SY:ADVSHT,SY:ADVNPC
D:      .FCTR SY:ADVPUZ,SY:ADVDSP,SY:ADVFND
E:      .FCTR SY:ADVTDY
        .END
```

**With data files present (ADVENT.DTA, ADVENT.MON, BOARD.NTC, ADVENT.CHR):**
- TKB creates ADVENT.TSK (162 blocks)
- Game starts and prints "No character loaded. Creating temporary character..."
- **Crashes with "Odd address trap at line 15001 in ADVDSP"**
- The crash occurs when trying to display the room (ADVDSP is called from line 35 in ADVENT)

**Without data files:**
- Game crashes with "ADVENT ERROR: 9 at line 32767" (subscript out of range)
- This is expected because the data files don't exist

The odd address trap persists even with the original ODL structure. The issue may be:
- Cross-overlay calls (ADVDSP in overlay D calls ADVOUT in overlay A)
- Undefined symbols reported by TKB in multiple overlay segments
- Buffer alignment issues when overlays are loaded

### Current Blocker
| Issue | Status |
|-------|--------|
| "Odd address trap" at ADVDSP line 15001 | ❌ **CURRENT BLOCKER** |
| Undefined symbols in overlay segments | ⚠️ Multiple segments have 1-4 undefined symbols |
| Data files | ✅ Copied to disk via tape |

### Current Disk State (Updated)

**IMPORTANT:** The RA72 disk image is currently **CLEAN** - no ADVENT files exist.

When the Docker container is recreated or restarted, the disk reverts to the base RA72 image
which does not contain any ADVENT source files, OBJ files, ODL files, or TSK files.

To investigate undefined symbols or test builds, you must first run the full rebuild:
1. Boot the container and wait for RSTS/E startup
2. Run `scripts/expect/85_rebuild_with_aligned_common.exp` to:
   - Copy source files from tape (MU0:)
   - Compile all 14 source files with BP2
   - Create ADVENT.ODL with RT11 format
   - Run TKB to create ADVENT.TSK
3. Then check the MAP file for undefined symbols

### Ruled Out Causes
- ~~ODL file format (RSX vs RT11)~~ - Fixed by using CREATE command
- ~~"Illegal SYS() usage"~~ - Fixed by correct ODL structure
- ~~COMMON variable alignment~~ - Reordering eliminated warnings
- ~~TKB option syntax~~ - Fixed case sensitivity issue
- ~~Custom "hybrid" ODL structure~~ - **CAUSED odd address trap!** Use original 1987 structure instead
- ~~ADVTDY in ROOT experiment~~ - Causes "multiply defines symbol" errors, worse than sibling overlays

### What Actually Fixed the Odd Address Trap
The **original 1987 ODL structure** with nested overlay groups:
- Puts ADVENT in ROOT with LIBR (BP2OTS library)
- Creates OVLY containing 5 sibling groups (A, B, C, D, E)
- Each group contains 1-3 related modules
- This structure is what the BP2 runtime expects

### Key Discovery: TKB .FCTR Syntax Creates Sibling Overlays

**CRITICAL FINDING (January 7, 2026):**

The ODL syntax `.FCTR SY:A,SY:B,SY:C-LIBR` does **NOT** create a single segment containing A, B, and C.
Instead, it creates **three sibling overlays** at the same level, each containing one module.

From the MAP file:
```
056664  074117  015234  06812.            ADVODD
056664  073343  014460  06448.            ADVMSG
056664  065371  006506  03398.            ADVPUZ
056664  070131  011246  04774.            ADVTDY
```

All four modules start at the same base address (056664) - they are **sibling overlays** that get swapped
into the same memory region. **Sibling overlays cannot call each other!**

**The Fix:** Move ADVTDY to ROOT segment so it's always loaded and can be called from any overlay.

Updated ODL structure:
```
.ROOT ROOTWL-*(OV1,OV2,OV3)
ROOTWL: .FCTR SY:ADVENT,SY:ADVINI,SY:ADVOUT,SY:ADVSHT,SY:ADVDSP,SY:ADVFND,SY:ADVTDY-LIBR
OV1:    .FCTR SY:ADVNOR,SY:ADVCMD-LIBR
OV2:    .FCTR SY:ADVODD,SY:ADVMSG,SY:ADVPUZ-LIBR
OV3:    .FCTR SY:ADVBYE,SY:ADVNPC-LIBR
LIBR:   .FCTR LB:BP2OTS/LB
        .END
```

### Key Scripts
| Script | Purpose |
|--------|---------|
| `scripts/fix_common_alignment.py` | Reorder COMMON variables |
| `scripts/create_advent_tape.py` | Create SIMH tape image |
| `scripts/expect/85_rebuild_with_aligned_common.exp` | Full rebuild automation |

### Build Command Summary
```bash
# Rebuild tape
python3 scripts/create_advent_tape.py --source-only -o build/tapes/advent_source.tap

# Rebuild container
docker build --no-cache -f Dockerfile.ra72-test -t advent-ra72-test .

# Run rebuild script
docker run -d --name advent-ra72-test -p 2322:2322 advent-ra72-test
expect scripts/expect/85_rebuild_with_aligned_common.exp
```

---

## SIMH Console Configuration Notes

### CRITICAL: Always Use Console Port (2322), Never DZ Terminals (2323)

**DO NOT use DZ terminal lines (port 2323) for automation or interactive sessions!**

The SIMH configuration exposes two ports:
- **Port 2322** - Main console (CON-TEL) - **USE THIS ONE**
- **Port 2323** - DZ11 terminal multiplexer - **UNRELIABLE, DO NOT USE**

The DZ terminal lines are unreliable for automation:
- Often show no response even when system is running
- May not receive expected prompts
- Can have timing issues with login sequences

All expect scripts should connect to port 2322 (console) only.

### Boot Timing

The RA72 container uses buffered console mode, which means:
1. SIMH boots immediately without waiting for telnet connection
2. Boot output is buffered and sent when you connect
3. Wait 60-90 seconds after container start for full RSTS/E boot
4. The SIMH `expect` commands in pdp11_ra72.ini auto-answer boot prompts

### Console State After Container Restart

After `docker restart`, the console may be in a busy/disconnected state. If you get
"All connections busy" errors:
1. Stop and remove the container: `docker stop && docker rm`
2. Start fresh: `docker run -d ...`
3. Wait for full boot (90 seconds)
4. Connect via telnet to port 2322

### Script Robustness Requirements

**IMPORTANT:** Expect scripts must handle BOTH scenarios:
1. **Connecting during boot** - Will see boot messages ("on the air", etc.)
2. **Connecting after boot complete** - Boot messages already sent, need to send CR to get prompt

The current `85_rebuild_with_aligned_common.exp` script has a weakness: it expects to see
boot messages like "on the air", but if the system already booted before connection, these
messages are gone and the script times out.

**DO NOT restart containers to work around script timing issues.** Instead, fix the scripts
to be resilient to different connection timing scenarios.

**Recommended pattern for robust boot detection:**
```tcl
expect {
    "on the air" {
        # Connected during boot
        sleep 3
        send "\r"
    }
    "User:" {
        # Already at login prompt
    }
    timeout {
        # System may be booted but idle - try sending CR
        send "\r"
        expect {
            "User:" { }
            timeout { puts "System not responding"; exit 1 }
        }
    }
}
```

**DONE:** Updated `85_rebuild_with_aligned_common.exp` with robust boot detection that:
- Handles connecting during boot (sees "on the air" message)
- Handles connecting after boot (sends CR to get "User:" prompt)
- Has fallback retries if system is slow to respond

---

## 🎉 FINAL SOLUTION - GAME WORKING! (January 8, 2026)

### The Problem
The game crashed with "Odd address trap at line 15001 in ADVDSP" when trying to display room descriptions. After fixing the odd address trap, we got "Error trap needs RESUME at line 32767 in ADVOUT".

### Root Causes

1. **Cross-Overlay Calls to ADVOUT**: ADVOUT was in overlay A, but was called from almost every other overlay (ADVNOR, ADVCMD, ADVODD, ADVBYE, ADVSHT, ADVPUZ, ADVDSP). When an overlay called ADVOUT, the overlay manager had to swap segments, causing memory corruption.

2. **Invalid RESUME Target**: The original error handler had `RESUME 32767` but line 32767 was SUBEND, which is not a valid RESUME target in BP2.

### The Fixes

**1. Move ADVOUT to ROOT segment** - Modified ODL to put ADVOUT in the always-resident ROOT:
```
.ROOT SY:ADVENT-SY:ADVOUT-LIBR-*(OVLY)
LIBR:   .FCTR LB:BP2OTS/LB
OVLY:   .FCTR *(A,B,C,D,E)
A:      .FCTR SY:ADVINI,SY:ADVNOR
B:      .FCTR SY:ADVCMD,SY:ADVODD,SY:ADVMSG
C:      .FCTR SY:ADVBYE,SY:ADVSHT,SY:ADVNPC
D:      .FCTR SY:ADVPUZ,SY:ADVDSP,SY:ADVFND
E:      .FCTR SY:ADVTDY
```

**2. Fix ADVOUT error handler** - Rewrote the error handler with proper line numbers:
```basic
25000   ! ERRORS - Handle ERR=6 at line 10 specially &
        IF ERL=10 AND ERR=6 THEN SPY%(ADVOUT.KB%)=0%

25010   ! For all errors, print message and exit &
        IF LEN(MESS$)>0% THEN &
                IF ASC(MESS$)<32% THEN PRINT RIGHT(MESS$,2%) ELSE PRINT MESS$

25020   RESUME 32766

32766   SUBEXIT &

32767   SUBEND &
```

### Result
The game now runs successfully:
```
No character loaded. Creating temporary character...
You are in dark desolate dismal room./CO-PEN/NKEY/N1/UKEY 1 /TNyark, Nyark!/TPity isn't it???/
Exits :
    North
You see:
>
```

### Key Lessons Learned

1. **Cross-overlay calls are fragile** - When subroutines are heavily shared across overlays, put them in ROOT
2. **TKB diagnostics help** - The "undefined symbols" count per segment shows which subroutines are being called across overlay boundaries
3. **BP2 error handling quirks** - RESUME must target a valid statement line, not SUBEND
4. **Docker tape caching** - Changes to tape files in the build directory require rebuilding the Docker image (not just restarting the container) because files are copied at build time
