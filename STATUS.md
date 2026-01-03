# ADVENT Function Status

*Last updated: January 3, 2026*

This table shows the current implementation status of all ADVENT features.

## Legend

| Symbol | Meaning |
|--------|---------|
| Y | Working |
| ~ | Partially working |
| N | Not yet working |
| ? | Untested |

---

## Player Movement Commands

| Command | Description | Status | Notes |
|---------|-------------|--------|-------|
| NORTH / N | Move north | Y | Working in single-user mode |
| SOUTH / S | Move south | Y | Working in single-user mode |
| EAST / E | Move east | Y | Working in single-user mode |
| WEST / W | Move west | Y | Working in single-user mode |
| UP / U | Move up | ? | Untested |
| DOWN / D | Move down | ? | Untested |
| LOOK / L | Examine room | Y | Shows room description |
| EXITS | Show available exits | ? | Untested |

## Inventory & Objects

| Command | Description | Status | Notes |
|---------|-------------|--------|-------|
| GET / TAKE | Pick up object | Y | Working |
| DROP | Drop object | ? | Untested |
| INVENTORY / I | List carried items | Y | Working |
| EXAMINE | Look at object | ? | Untested |
| USE | Use an object | ? | Untested |

## Combat System

| Command | Description | Status | Notes |
|---------|-------------|--------|-------|
| ATTACK / KILL | Attack monster | ? | Untested |
| DRAW | Ready weapon | ? | Untested |
| SHEATH | Put weapon away | ? | Untested |
| FLEE / RUN | Escape combat | ? | Untested |

## Magic System

| Spell | Description | Status | Notes |
|-------|-------------|--------|-------|
| TELEPORT | Transport to location | ? | Untested |
| FIREBALL | Damage spell | ? | Untested |
| HEAL | Restore HP | ? | Untested |
| STUN | Paralyze enemy | ? | Untested |
| INVISIBILITY | Hide from monsters | ? | Untested |

## Communication (Multi-user)

| Command | Description | Status | Notes |
|---------|-------------|--------|-------|
| TELL | Private message | N | Requires multi-user mode |
| SHOUT | Broadcast to area | N | Requires multi-user mode |
| ANNOUNCE | Global broadcast | N | Requires multi-user mode |
| WHO | List online players | N | Requires multi-user mode |

## Character Management

| Command | Description | Status | Notes |
|---------|-------------|--------|-------|
| STATUS | Show character stats | ? | Untested |
| SCORE | Show XP/level | ? | Untested |
| QUIT | Exit game | Y | Working |
| SAVE | Save character | ? | Untested |

## Special Room Commands

| Feature | Description | Status | Notes |
|---------|-------------|--------|-------|
| Puzzles | Room-specific commands | ? | Untested |
| Noticeboards | Read/write messages | ? | Untested |
| Shrines | Drop treasure for XP | ? | Untested |
| Shops | Buy/sell items | ? | Untested |

## Background Systems

| System | Description | Status | Notes |
|--------|-------------|--------|-------|
| Monster AI | Monsters follow/attack | N | Requires multi-user mode |
| NPC Workman | Restocks monsters/items | N | Requires WORKMAN job |
| Poison/Paralysis | Status effects | ? | Untested |
| Level progression | XP and leveling | ? | Untested |
| Character persistence | Save between sessions | ? | Untested |

## Core Infrastructure

| Component | Description | Status | Notes |
|-----------|-------------|--------|-------|
| Room data file | 1,587 rooms loaded | Y | Data files generated |
| Monster data file | 402 monsters loaded | Y | Data files generated |
| Object data file | 417 objects loaded | Y | Data files generated |
| Single-user mode | One player at a time | Y | ADVENT.TSK working |
| Multi-user mode | 8 concurrent players | N | File locking prevents concurrent access |
| Web interface | Browser-based access | Y | CRT terminal with status overlay |
| Auto-login | Automatic RSTS/E login | Y | Expect script handles login |

---

## Known Display Issues

- Exit display shows "^B" control character after "West"
- Tab alignment issues in exits display (first Tab stripped)
- Occasional "?" prompts from CR/LF handling (stty fix deployed)

## Summary

**Working:** 12+ features
**Partially working:** 0 features
**Not working:** 5 features (multi-user only)
**Untested:** 15+ features

The single-user exploration mode is functional with movement, inventory, and basic commands working. Multi-user features require resolving the file locking issue in ADVENT.MON.
