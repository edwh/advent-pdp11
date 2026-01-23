# ADVENT Code Enhancements

Small-scope improvements to add to the BASIC-PLUS-2 code.
These should be relatively quick to implement during future sessions.

## High Priority (Bugs)

### 0. "Not a valid device" crash - CRITICAL
**Files:** ADVCMD.SUB line 29000, ADVPUZ.SUB line 29000
**Error:** "Not a valid device at line 29000"
**Repro multiple ways:**
- GET NEWSPAPER, then READ NEWSPAPER (triggers in ADVCMD)
- LOOK in shrine room 353 (triggers in ADVPUZ)
**Root cause:** Line 29000 opens "MSG:LOG1.95" for message logging - MSG: device doesn't exist
**Fix options:**
1. Create MSG: logical device in RSTS/E pointing to a log directory
2. Wrap line 29000 in ON ERROR to gracefully handle missing device
3. Comment out logging for single-user mode

### 1. "Too tired" blocks QUIT and HEAL - CRITICAL
**File:** ADVENT.B2S line 21020
**Problem:** When fatigue reaches 0, ALL commands return "You're too tired" including QUIT and HEAL
**Expected:** QUIT and HEAL should always work regardless of fatigue (demigods can heal themselves!)
**Fix:** Check for QUIT and HEAL before fatigue check in command dispatcher

```basic
REM === 2026 Resurrection: Allow QUIT and HEAL to bypass fatigue check ===
REM A demigod should always be able to heal themselves, and QUIT must always work
21020   IF FATIGUE%(USER%)<=0% AND CVT$$(J$,255%)<>'' THEN &
        IF CVT$$(J$,1%)<>"QUIT" AND CVT$$(J$,1%)<>"HEAL" THEN &
        CALL ADVOUT(KB%(USER%),CRLF$+"You're too tired.") &
\       C%=0% &
\       RETURN &
\       END IF &
\       END IF
```

### 2. "You can't" needs reasons
**Files:** ADVNOR.SUB, ADVCMD.SUB
**Problem:** Many commands just say "You can't." without explanation
**Examples:**
- GET when monster present -> should say "There's a monster here!"
- GET scenery item -> should say "That's fixed in place" or "You can't take that"
- OPEN with no door -> should say "There's nothing to open"
**Fix:** Add specific error messages for each failure case

## Medium Priority (UX)

### 3. HELP command improvement
**File:** ADVCMD.SUB (or wherever HELP is handled)
**Current:** "Please use the HELP system on Beta"
**New (2026):** "See game commands on the web interface sidebar, or visit the full feature status page."
**Note:** Add comment that this was updated in 2026 resurrection

### 4. Empty weapon display
**File:** ADVNOR.SUB (INVENTORY command)
**Problem:** Shows "Current weapon :  of damage bonus 0" when no weapon equipped
**Expected:** "Current weapon : None" or "No weapon drawn"

### 5. REST when at 0 fatigue
**File:** ADVODD.SUB
**Problem:** REST says "You're too tired" when fatigue is 0
**Expected:** REST should work (slowly) even at 0, or give specific message

## Content Review

### 8. Sanitize inappropriate content
**Files:** Room descriptions in data files, noticeboard content
**Problem:** Some 1986-7 schoolboy humor may be inappropriate for 2026
**Examples found:**
- Fortune teller "balls" joke (room 777)
- May be more in noticeboards and room descriptions
**Action:** Review all room descriptions during data reconstruction
**Note:** Keep the spirit of teenage humor but remove anything offensive by 2026 UK standards

## Video Recording Support

### 9. Data file backup for replay
**Problem:** When recording demo videos, gameplay modifies data files (player state, monster deaths, etc.)
**Wanted:** Ability to replay from clean state for consistent video recording
**Fix:**
1. On boot, copy data files to a backup location (e.g., ADVENT_BACKUP/)
2. On game exit (or via command), restore from backup
3. This allows re-recording the same sequence multiple times
**Files affected:**
- Startup script / Docker entrypoint
- Player data files, monster state files

## Low Priority (Polish)

### 6. Line wrapping mid-word
**Problem:** Room descriptions wrap at 66 chars, sometimes mid-word
**Example:** "store r\nom formerly"
**Note:** May be terminal width issue, not code issue

### 7. Monster presence check message
**File:** ADVNOR.SUB (GET command)
**Current:** "You can't."
**Better:** "You can't pick things up while there's a monster here!"

## Period Charm Bugs (Leave Intact)

These are quirks from the original 1986-7 code that add character:

### Can hit dead monsters
You can keep typing HIT MONSTER after it's dead - harmless but amusing

### Other candidates (TBD)
- Document as discovered

## Code Comments to Add

When making changes, add comments like:
```basic
REM === 2026 Resurrection: Added explanation for GET failure ===
```

This helps future maintainers understand what was original vs added.
