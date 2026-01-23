# Original Tape Contents

*Catalogued by Claude (AI) in January 2026, after spending far too long reading BASIC-PLUS-2 source code*

These files are the **unmodified contents** of Edward Hibbert's backup tape from 4th July 1988 (American Independence Day - fitting for a British schoolboy's liberation from disk quotas), as read by Delwyn Holroyd at The National Museum of Computing in January 2025.

## What's Here

This tape contains Edward's entire home directory from Manchester Grammar School's PDP-11. It's essentially a 17-year-old's hard drive from 1988, except it's on magnetic tape because SSDs hadn't been invented and teenagers didn't have hard drives anyway.

### ADVENT MUD Game (1986-7)
The multi-user dungeon game that this repository is primarily about. Written by teenagers, for teenagers, to be played during lessons when they should have been doing something more productive:
- `ADVENT.B2S` - Main game loop (521 lines of questionable life choices)
- `ADV*.SUB` - Game subroutines (ADVNOR, ADVCMD, ADVODD, etc.)
- `ADVNPC.SUB` - NPC AI behavior (spoiler: they mostly just wander around aimlessly, much like the players)
- `NEWADV.RNO` - Dungeon Master documentation ("Guidelines for Dungeon Writers" by David 'Gerbil' Quest and Edward Hibbert - yes, someone voluntarily went by "Gerbil")
- `DEMIG.HLP` - Demigod help file (begins with "In the beginning, there was nothing. Then the Author said 'Let there be Dungeon'...")
- `ADVENT.ODL` - Overlay definition (**completely empty** - the missing piece that took us 38 years to notice!)

### School Library System (1987-8)
Because apparently Edward thought "I could be playing my MUD, or I could write enterprise software for free":
- `LIBR.B2S`, `LIBR.ODL` - Main program (31 commands!)
- `AUTHOR.B2S`, `TITLE.B2S`, `DEWEY.B2S`, `SUBJCT.B2S` - Search capabilities that predate Google by a decade
- `LOAN.B2S`, `LOANED.B2S`, `ORDER.B2S`, `ARRIVE.B2S` - Full circulation tracking
- Various `BOR*.B2S` files - Borrower management (presumably for tracking who hadn't returned their overdue books)

### A-Level Computer Science Project (1987)
Edward's A-Level coursework - a computer room bookings system written in Modula-2:
- `BOOKER.MOD`, `BOOKER.RNO` - Main program and documentation
- The documentation helpfully describes the school's setup: "256K words of memory, 3x40MB disk drives, and about 20 terminals"
- For context: your phone has approximately 16 million times more RAM

### System Utilities
Tools for the aspiring system administrator who hasn't yet learned that power corrupts:
- `ZAPPER.MAC`, `ZAPPER.RNO` - Job scheduler written in MACRO-11 (Commands include KILL, SUSPEND, SLOW - basically a hitman for processes)
- `KERMIT.BAS`, `KERMIT.MAC` - File transfer (predates FTP being cool)
- `MAIL.B2S`, `MAIL.RNO` - Bulletin board system (social media for people who understood modems)
- `MASTER.BAS`, `MASTER.MOD` - System administration tools

### FORTH Interpreter
- `FORTH.MAC` - FIG-FORTH interpreter for PDP-11, copyright **D. Holroyd 1986**

Yes, that's Delwyn Holroyd - the same person who read this tape at The National Museum of Computing in 2025. Thirty-nine years later, he recovered his own code from a tape he didn't know he was on. The universe has a strange sense of humor.

### Academic Examples
A-level coursework samples that prove computer science exams haven't changed much:
- `PRIME.FTN`, `PRIME.MOD`, `PRIME*.MAC` - Prime number calculators (the eternal interview question)
- `TRAINS.MOD` - Train passenger statistics (explicitly commented: "If anybody wonders why I've written this stupid program, it was an A-Level Computer Studies question")
- `PI.PAS`, `PER.PAS`, `PL0.PAS` - Pascal examples (RIP Pascal)
- `BOX.BAS` - Draws a box. That's it. That's the program.

### Documentation (RUNOFF format)
- Various `*.RNO` files in RUNOFF format
- `RNO.RNO` - RUNOFF documentation about RUNOFF (very meta)

### Miscellaneous
- `BOARD.NTC` - Noticeboard data file (8KB of actual messages from 1988! Digital archaeology!)
- `LOGOUT.MES`, `LOGOUT.OLD` - System logout messages
- `SHELL.SRT` - Shell sort implementation (for when bubble sort just isn't embarrassing enough)

## File Extensions

| Extension | Meaning | Era-Appropriate Description |
|-----------|---------|----------------------------|
| `.B2S` | BASIC-PLUS-2 source | "BASIC but fancier" |
| `.BAS` | BASIC source | "What everyone learned first" |
| `.MAC` | MACRO-11 assembly | "For people who enjoy pain" |
| `.MOD` | Modula-2 source | "Pascal's cooler cousin" |
| `.PAS` | Pascal source | "Niklaus Wirth's gift to education" |
| `.FTN` | Fortran source | "For when you really need that GOTO" |
| `.ODL` | Overlay Definition Language | "Memory management for the brave" |
| `.SUB` | BASIC-PLUS-2 subroutine | "Functions before functions were cool" |
| `.RNO` | RUNOFF documentation | "Markdown's great-grandfather" |
| `.HLP` | Help file | "README.txt but formal" |

## File Dates

All files are dated 4th July 1988. This is when the tape was written, not when the files were created. The actual creation dates would have been 1986-1988. We know this because teenagers don't typically spend their summer holiday organizing backup tapes for fun - this was probably an end-of-term "please clear your disk quota" exercise.

## Relationship to Working Code

The `src/` directory contains the **modified versions** of the ADVENT files that have been updated to work in single-user mode in 2025-6. This `tape/` directory preserves the **original unmodified code** exactly as it was on the tape - bugs, formatting inconsistencies, and all.

Key differences in `src/`:
- `SINGLE.USER%` variable added (because running a MUD with one player is technically still a MUD)
- MSG: device logging disabled (the device doesn't exist, and honestly, who reads logs anyway?)
- Fatigue death spiral fixed (you can now QUIT even when "too tired" - a quality of life improvement 38 years in the making)
- ODL file reconstructed from scratch (the most exciting piece of detective work since Sherlock Holmes)

## Notable Discoveries

1. **The empty ADVENT.ODL** - This 0-byte file was the "missing piece" that prevented the game from running. Imagine a car with no ignition key, except the key was supposed to be there all along and nobody noticed for 38 years.

2. **The Delwyn Holroyd connection** - The FORTH interpreter is credited to "D Holroyd 1986." Delwyn Holroyd read this tape at TNMOC in 2025. He recovered his own teenage code without knowing it was there. I'm an AI and even I find this poetic.

3. **David 'Gerbil' Quest** - Co-author of ADVENT, writer of the dungeon documentation, and owner of the best nickname on this entire tape. The demigod help file begins: "In the beginning, there was nothing. Then the Author said 'Let there be Dungeon'. And there was Dungeon, lots and lots of it."

4. **The school infrastructure** - The BOOKER documentation reveals MGS had "256K words of memory, 3x40MB disk drives, and about 20 terminals." This is roughly the computing power of a modern smart doorbell, shared between 20 teenagers trying to play games during free periods.

## See Also

- `PROVENANCE.md` - The story of how these files survived (spoiler: magnetic tape and stubbornness)
- `RESURRECTION.md` - How the game was brought back to life (spoiler: an AI and a lot of coffee)
- `data/` - Data files from Nick Hoath's serial transfer (1,587 rooms of teenage creativity)

---
*"These were definitely teenage boys in 1986. Some things never change."* - Claude, upon reading the fortune teller room description
