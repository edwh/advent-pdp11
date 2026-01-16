---
name: ralph
description: "MUST use for any non-trivial development task in advent-pdp11 - implements iterative development with status tracking, session logging, validation, and one-task-at-a-time approach. Use when implementing features, fixing bugs, refactoring, or any task requiring more than a single simple change."
---

# Ralph Iterative Development Approach for Advent PDP-11

You are now using the Ralph approach for this task. This is MANDATORY for the advent-pdp11 codebase.

## 0. Session Logging (CRITICAL for Continuity)

**Before starting any work, check for and update the session log.**

Session logs preserve context across conversation restarts and context compaction. This is essential for long-running tasks.

### Session Log Location
```
claude.md -> "Session Log" section (at end of file)
```

### On Session Start
1. Read `claude.md` to check for existing session log
2. If resuming work, review the last session's state
3. Add a new dated entry showing you're continuing

### During Work
After completing each subtask or making significant progress:
```markdown
### YYYY-MM-DD HH:MM - [Brief description]
- **Status**: [Current task status table snapshot]
- **Completed**: [What was just finished]
- **Next**: [What's planned next]
- **Blockers**: [Any issues encountered]
- **Key Decisions**: [Important choices made and why]
```

### On Session End / Before Context Compaction
Update the session log with:
- Current state of all tasks
- Any uncommitted changes
- Commands that were running (e.g., docker build in progress)
- Exact next steps for continuation

### Example Session Log Entry
```markdown
### 2026-01-16 14:30 - Fixed byte order in migration scripts
- **Status**: Tasks 1-3 ✅, Task 4 🔄 (Docker rebuilding), Tasks 5-6 ⬜
- **Completed**: migrate_data.py and reconstruct_rooms.py now use big-endian
- **Next**: Wait for Docker build, then test LOOK/N/S/E/W commands
- **Blockers**: None
- **Key Decisions**: Used big-endian for CVT$% compatibility per BASIC-PLUS-2 docs
```

## Project Context

**This is a PDP-11 emulator running RSTS/E with the ADVENT MUD game from 1987.**

### Critical Development Rules from claude.md

1. **ALWAYS use Docker Compose for local development:**
   ```bash
   docker-compose up -d --build   # Build and start
   docker-compose down            # Stop
   docker-compose logs -f         # View logs
   ```

2. **NEVER use raw `docker run` commands** - use docker-compose for consistency

3. **NEVER modify disk images while RSTS/E is running** - container must be STOPPED first

4. **Local Ports (host -> container):**
   - 8088 -> 8080: Web interface
   - 7681 -> 7681: Game web terminal
   - 7682 -> 7682: Admin web terminal
   - 2324 -> 2322: SIMH console (telnet)
   - 2325 -> 2323: RSTS/E terminal (telnet)

5. **Login credentials:** [1,2] / SYSTEM (for scripts) or Digital1977 (documented)

6. **Build takes 10-15 minutes** - monitor via:
   ```bash
   docker exec advent-mud cat /tmp/boot_status.json
   ```

## 1. Break Down the Task

First, analyse the request and break it into discrete subtasks. Create a status table:

```markdown
## Task Status

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1 | [First subtask] | 🔄 In Progress | |
| 2 | [Second subtask] | ⬜ Pending | |
| 3 | [Third subtask] | ⬜ Pending | |
```

Status icons:
- ⬜ Pending - not started
- 🔄 In Progress - currently working on
- ✅ Complete - finished and validated
- ❌ Blocked - needs user input

## 2. Work Iteratively

For each subtask:
1. Mark it as 🔄 In Progress
2. Complete the work
3. **Validate before marking complete**:
   - Docker changes: Rebuild with `docker-compose up -d --build`
   - Wait for status to become "ready" (check `/tmp/boot_status.json`)
   - Test game functionality via tmux session or web terminal
   - Check logs: `docker-compose logs 2>&1 | grep -i error`
4. Mark as ✅ Complete or ❌ Blocked
5. Update the status table
6. Move to next task

## 3. Critical Rules

- **ONE task at a time** - do not try to do multiple things at once
- **NEVER mark complete without validation/testing**
- **NEVER modify disks while SIMH is running** - causes corruption
- **ALWAYS use docker-compose** - never raw docker commands
- **Update claude.md** with date-stamped notes for context preservation
- Update the status table after completing each task

## 4. Testing Game Changes

After any change to game code or ODL:
1. Rebuild: `docker-compose down && docker-compose up -d --build`
2. Wait for "ready" status (10-15 minutes)
3. Check build logs for errors: `docker-compose logs 2>&1 | grep -E "TKB|SUCCESS|Error"`
4. Test in game session:
   ```bash
   docker exec advent-mud tmux capture-pane -t advent -p
   docker exec advent-mud tmux send-keys -t advent "LOOK" Enter
   ```

## 5. Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| "Odd address trap" | Check ODL file - subroutines may need to be in ROOT |
| "Swap file is invalid" | Disk corrupted - run `git checkout build/disks/*.dsk` |
| Port conflict | Run `docker-compose down`, wait 30s, then restart |
| "All connections busy" | Console port contention - restart SIMH |
| Build timeout | Check `docker-compose logs` for errors |

## 6. Completion Criteria

Only declare the overall task complete when:
- All subtasks are ✅ Complete
- Container builds successfully
- Status reaches "ready"
- Game commands work without errors (LOOK, N, S, E, W)
- Changes documented in claude.md with date stamp

## 7. If Blocked

If you need user input or are blocked:
- Mark the task as ❌ Blocked
- Clearly explain what you need
- Wait for user response before continuing

Now analyse the user's request and create your status table to begin work.
