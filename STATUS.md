# ADVENT Function Status

*Last updated: January 1, 2026*

This table shows the current implementation status of all ADVENT features.

## Legend

| Symbol | Meaning |
|--------|---------|
| :white_check_mark: | Working |
| :construction: | Partially working |
| :x: | Not yet working |
| :grey_question: | Untested |

---

## Player Movement Commands

| Command | Description | Status | Notes |
|---------|-------------|--------|-------|
| NORTH / N | Move north | :white_check_mark: | Working in single-user mode |
| SOUTH / S | Move south | :white_check_mark: | Working in single-user mode |
| EAST / E | Move east | :white_check_mark: | Working in single-user mode |
| WEST / W | Move west | :white_check_mark: | Working in single-user mode |
| UP / U | Move up | :grey_question: | Untested |
| DOWN / D | Move down | :grey_question: | Untested |
| LOOK / L | Examine room | :white_check_mark: | Shows room description |
| EXITS | Show available exits | :grey_question: | Untested |

## Inventory & Objects

| Command | Description | Status | Notes |
|---------|-------------|--------|-------|
| GET / TAKE | Pick up object | :x: | Not yet implemented |
| DROP | Drop object | :x: | Not yet implemented |
| INVENTORY / I | List carried items | :x: | Not yet implemented |
| EXAMINE | Look at object | :x: | Not yet implemented |
| USE | Use an object | :x: | Not yet implemented |

## Combat System

| Command | Description | Status | Notes |
|---------|-------------|--------|-------|
| ATTACK / KILL | Attack monster | :x: | Not yet implemented |
| DRAW | Ready weapon | :x: | Not yet implemented |
| SHEATH | Put weapon away | :x: | Not yet implemented |
| FLEE / RUN | Escape combat | :x: | Not yet implemented |

## Magic System

| Spell | Description | Status | Notes |
|-------|-------------|--------|-------|
| TELEPORT | Transport to location | :x: | Not yet implemented |
| FIREBALL | Damage spell | :x: | Not yet implemented |
| HEAL | Restore HP | :x: | Not yet implemented |
| STUN | Paralyze enemy | :x: | Not yet implemented |
| INVISIBILITY | Hide from monsters | :x: | Not yet implemented |

## Communication (Multi-user)

| Command | Description | Status | Notes |
|---------|-------------|--------|-------|
| TELL | Private message | :x: | Requires multi-user mode |
| SHOUT | Broadcast to area | :x: | Requires multi-user mode |
| ANNOUNCE | Global broadcast | :x: | Requires multi-user mode |
| WHO | List online players | :x: | Requires multi-user mode |

## Character Management

| Command | Description | Status | Notes |
|---------|-------------|--------|-------|
| STATUS | Show character stats | :grey_question: | Untested |
| SCORE | Show XP/level | :grey_question: | Untested |
| QUIT | Exit game | :white_check_mark: | Working |
| SAVE | Save character | :x: | Requires full implementation |

## Special Room Commands

| Feature | Description | Status | Notes |
|---------|-------------|--------|-------|
| Puzzles | Room-specific commands | :x: | Not yet tested |
| Noticeboards | Read/write messages | :x: | Not yet implemented |
| Shrines | Drop treasure for XP | :x: | Not yet implemented |
| Shops | Buy/sell items | :x: | Not yet implemented |

## Background Systems

| System | Description | Status | Notes |
|--------|-------------|--------|-------|
| Monster AI | Monsters follow/attack | :x: | Requires multi-user mode |
| NPC Workman | Restocks monsters/items | :x: | Requires WORKMAN job |
| Poison/Paralysis | Status effects | :x: | Combat not implemented |
| Level progression | XP and leveling | :x: | Requires combat/shrines |
| Character persistence | Save between sessions | :x: | Not yet tested |

## Core Infrastructure

| Component | Description | Status | Notes |
|-----------|-------------|--------|-------|
| Room data file | 1,587 rooms loaded | :white_check_mark: | Data files generated |
| Monster data file | 402 monsters loaded | :white_check_mark: | Data files generated |
| Object data file | 417 objects loaded | :white_check_mark: | Data files generated |
| Single-user mode | One player at a time | :white_check_mark: | MINI3.TSK working |
| Multi-user mode | 8 concurrent players | :x: | KB% terminal routing issue |
| Web interface | Browser-based access | :construction: | Login automation unreliable |
| Auto-login | Automatic RSTS/E login | :x: | Timing issues with expect |

---

## Summary

**Working:** 7 features
**Partially working:** 1 feature
**Not working:** 30+ features
**Untested:** 4 features

The single-user exploration mode is functional. Combat, inventory, magic, and multi-user features require additional implementation work.
