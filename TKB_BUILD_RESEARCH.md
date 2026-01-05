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
