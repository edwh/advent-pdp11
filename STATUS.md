# ADVENT Function Status

*Last updated: January 23, 2026*
*Tested by: Claude (with guidance from the ghost of Edward Future)*

This table shows the current implementation status of all ADVENT features, verified through actual gameplay testing.

## Legend

| Symbol | Meaning |
|--------|---------|
| Y | Working |
| ~ | Partially working |
| N | Not working |
| X | Crashes game |
| ? | Untested |

---

## Player Movement Commands

| Command | Description | Status | Notes |
|---------|-------------|--------|-------|
| NORTH / N | Move north | Y | Tested - works perfectly |
| SOUTH / S | Move south | Y | Tested - works perfectly |
| EAST / E | Move east | Y | Tested - works perfectly |
| WEST / W | Move west | Y | Tested - works perfectly |
| UP / U | Move up | ? | Untested |
| DOWN / D | Move down | ? | Untested |
| LOOK / L | Examine room | ~ | Works, but crashes in some puzzle rooms (MSG: device missing) |
| EXITS | Show available exits | ? | Untested |

## Inventory & Objects

| Command | Description | Status | Notes |
|---------|-------------|--------|-------|
| GET / TAKE | Pick up object | Y | Works - but blocked if monster present ("You can't.") |
| DROP | Drop object | Y | Works - "Ok." response |
| INVENTORY / I | List carried items | Y | Shows weapon and carried items |
| EXAMINE | Look at object | N | "You can't do that." |
| USE | Use an object | N | "You can't." |
| VALUE | Appraise treasure | Y | "You reckon that it's worth about X XP." |
| EAT | Consume food | Y | Works - "Ok." |
| DRINK | Drink something | N | "You can't do that." |
| READ | Read item | X | Crashes game - MSG: device missing |

## Combat System

| Command | Description | Status | Notes |
|---------|-------------|--------|-------|
| HIT | Attack monster | Y | Works! "You did X points of damage and killed the [monster]" |
| DRAW | Ready weapon | Y | Works - "Ok." - must draw before hitting |
| SHEATH | Put weapon away | Y | Works - "Ok." |
| ATTACK / KILL | Attack monster | N | "You can't do that." - use HIT instead |
| FLEE / RUN | Escape combat | ? | Untested |

## Magic System (Level 16+ demigod)

| Spell | Description | Status | Notes |
|-------|-------------|--------|-------|
| HEAL | Restore HP | Y | Works! "You now have X hit points." |
| INVISIBLE | Hide from view | Y | Works! "You are now invisible" - STATUS shows "(Invisible)" |
| ROOM [n] | Teleport to room | Y | Demigod power - instant travel |
| TELEPORT | Transport to location | N | "You can't." |
| FIREBALL | Damage spell | N | "You can't." - may need target |
| STUN | Paralyze enemy | N | "I can't see him." |

## Communication

| Command | Description | Status | Notes |
|---------|-------------|--------|-------|
| SHOUT [msg] | Broadcast message | Y | Works - "Ok." |
| TELL [player] | Private message | ~ | "I can't see him." if target not found |
| BELLOW | Loud broadcast | ? | Untested |
| WHO | List online players | N | "You can't do that." |

## Character Management

| Command | Description | Status | Notes |
|---------|-------------|--------|-------|
| STATUS | Show character stats | Y | Shows name, level, XP, HP, fatigue, room, (Invisible) |
| REST | Recover fatigue | Y | "You sit down and close your eyes." |
| SCORE | Show XP/level | N | "You can't do that." |
| QUIT | Exit game | ~ | Works normally, but blocked when fatigue=0 (BUG) |
| HELP | Show help | ~ | "Please use the HELP system on Beta" (outdated) |

## Special Room Commands

| Feature | Description | Status | Notes |
|---------|-------------|--------|-------|
| RING | Ring bell | Y | Works - "[Player] rings the bell in room X" |
| Puzzles | Room-specific | X | Some rooms crash due to MSG: device |
| Shrines | Drop treasure for XP | ? | DROP works but XP gain untested |
| Room events | Automatic triggers | Y | "Your feet uncover a newspaper" etc. |

## Background Systems

| System | Description | Status | Notes |
|--------|-------------|--------|-------|
| Fatigue system | Limits actions | Y | Depletes with combat/actions |
| Monster blocking | Can't GET with monster | Y | Must kill monster first |
| Combat XP | Gain XP from kills | ~ | Killed troll, showed 0 XP - needs investigation |
| NPC Workman | Restocks world | N | Requires WORKMAN batch job |

## Core Infrastructure

| Component | Description | Status | Notes |
|-----------|-------------|--------|-------|
| Room data | 1,587 rooms | Y | Working |
| Monster data | 402 monsters | Y | Working |
| Object data | 417 objects | Y | Working |
| Single-user mode | One player | Y | ADVENT.TSK working |
| Multi-user mode | 8 players | N | File locking issue |
| Web interface | Browser terminal | Y | CRT terminal with auto-login |

---

## Known Bugs

### Critical
1. **MSG: device crash** - READ and LOOK in puzzle rooms crash with "Not a valid device at line 29000"
2. **Fatigue death spiral** - When fatigue=0, ALL commands fail including QUIT

### Minor
1. "You can't." messages don't explain why
2. Empty weapon shows "of damage bonus 0" instead of "None"
3. HELP refers to outdated "Beta" system

### Period Charm (intentionally preserved)
1. Can keep hitting dead monsters
2. Schoolboy humor in room descriptions

---

## Summary

**Fully Working:** 20+ features
**Partially Working:** 5 features
**Not Working:** 8 features
**Crashes:** 2 features (MSG: device issue)
**Untested:** 10+ features

The core gameplay loop is functional: explore rooms, pick up items, fight monsters, use magic. The main issues are the MSG: device crashes in puzzle rooms and the fatigue death spiral bug.
