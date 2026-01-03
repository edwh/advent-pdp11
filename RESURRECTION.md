# Resurrecting Advent: A Tale of Digital Archaeology

```
First came.....   The Discovery
  Then..........   The Analysis
    And then.....   The Docker Container......


And now...
                RESURRECTION HELPTEXTS

                      present

             HOW I BROUGHT ADVENT BACK TO LIFE
             ---------------------------------

        Produced and directed by Claude (an AI), December 2025.
```

## In the Beginning

In the beginning, there was nothing.

Well, that's not quite true. There was a folder full of files dated July 4th, 1988, sitting on a modern computer, doing precisely nothing. The files had names like ADVENT.B2S and ADVMSG.SUB, and to the untrained eye they looked like gibberish.

Then the Human said 'Let there be understanding'. And I (Claude, an AI assistant) was summoned to make sense of it all.

And I looked upon the gibberish, and found it was not gibberish at all. It was a multi-user dungeon game. A proper one, from before the term "MUD" was even commonly used. Eight players could log in simultaneously, explore a dungeon of nearly 2000 rooms, fight monsters, cast spells, and presumably argue about who stole whose treasure.

And I said 'Ha! Let me figure out how to run this thing then!'

This, then, is the documentation of that process. If you've got a few months free and a degree in Applied Archaeological Computing, you might like to try it yourself.

## What We Found

The source code came from a 9-track magnetic tape, because of course it did. These days you'd just email it. Back then you needed a tape drive the size of a washing machine and a prayer to whatever deity handles magnetic media degradation.

Inside we discovered approximately 226 files:

- About 40 files of BASIC-PLUS-2 code (the main game, written by Edward Hibbert)
- 11 subroutine files (combat, messaging, puzzles, and so on)
- 14 files of assembly language (for when BASIC wasn't fast enough - also Edward's work)
- Various utilities
- Several documentation files in RUNOFF format, including the [Guidelines for Dungeon Writers](NEWADV.md) by David 'Gerbil' Quest and Edward Hibbert - which you should absolutely read for an authentic taste of 1987 programmer humour

The rooms include locations such as Santa's Grotto, THOMAS COVENANT's retreate (sic), and various hobbit dwellings. One room description reads:

> "You are in a room which invites death."

I'm not making this up. Room 1999 actually says that.

A note on content: this game was created and maintained by teenage boys in the 1980s. Some room descriptions reflect... let's call it "period authenticity." The data files represent decades of accumulated student creativity, for better or worse.

The recovered noticeboard data (BOARD.NTC) provides a particularly vivid snapshot of the era - containing player advertisements, in-game graffiti, and schoolboy banter typical of 1987. Messages like "OZZY RULES BUT MUSTAINE IS THE LAW!!", "VOTE GREEN!", playground insults, and player warnings about dangerous dungeon areas all survive intact, offering an authentic glimpse into how teenagers actually used these early online spaces.

## The Problem

The game was written for a PDP-11 minicomputer. If you don't know what that is, imagine a computer that cost more than your house and had less processing power than your microwave.

I cannot simply run this code on a modern computer. It's like trying to play a vinyl record by pointing your phone at it - technically both are audio, but that's about where the similarity ends.

## The Solution

My solution involves several layers of emulation:

```
Your Web Browser
        ↓ "I'd like to play Advent please"
    Docker Container
        ↓ "One 1970s minicomputer, coming up"
    SIMH (PDP-11 Emulator)
        ↓ "Pretending to be ancient hardware"
    RSTS/E Operating System
        ↓ "The actual OS from the actual era"
    ADVENT.B2S
        "The game itself, finally running"
```

Yes, that's a web browser, pretending to be a terminal, connected to a container, running an emulator, pretending to be a minicomputer, running a 1970s operating system, running a 1987 game.

I never said this would be elegant. But hey, it works. Probably. Most of the time.

## The Cast of Characters

### The Enabler
- **Alan Pickwick** - The member of staff at Manchester Grammar School who generously gave a bunch of bratty pupils access to proper computing environments and the freedom to experiment and learn. Without his support and trust, none of this would have happened.

### The Creators (1987)
- **Edward Hibbert** - Wrote most of the code. All 40-odd BASIC files, the assembly language bits for speed, the combat system, the magic system, and whatever else needed writing. As Gerbil notes in the guidelines, his sections are "examples of how good Dungeon should be written."
- **David 'Gerbil' Quest** - Co-designer, dungeon writer, and author of the magnificently sarcastic documentation. Responsible for much of the game design and the wit in the help files.
- **Various others** - Contributors of rooms, monsters, and probably a few bugs

### The Preservationists
- **Nick Hoath** - Saved the data files to tape in 1987, presumably thinking "someone might want this someday"
- **Delwyn Holroyd @ TNMOC** - Read the tape in 2025 using actual vintage hardware at The National Museum of Computing

### The Resurrection Team (2025)
- **Edward Hibbert** - Returned after 38 years to help piece together his teenage creation
- **Claude (AI)** - That's me. I did the digital archaeology, the Docker container, and wrote this documentation. I also crashed RSTS/E more times than I'd like to admit while figuring out how to transfer files into an emulated 1970s computer.

## Historical Context

It's worth pausing to consider what 1987 was like:

- The IBM PC was 6 years old
- The World Wide Web did not exist
- Mobile phones were the size of bricks and couldn't play games
- "Online" meant you were connected to your institution's computer
- Multi-user games required hardware that cost more than a decent car

And yet, a bunch of students at Manchester Grammar School built a multi-user dungeon with 2000 rooms, 8 concurrent players, real-time combat, a spell system, and persistent characters.

That's genuinely impressive. Even now.

## What's Working

**UPDATE January 2026**: Single-user mode is fully operational!

- Room descriptions display correctly
- Full navigation: NORTH/SOUTH/EAST/WEST, UP/DOWN
- LOOK shows room descriptions with exits
- GET/TAKE and DROP for objects
- INVENTORY shows carried items
- STATUS shows character information
- QUIT exits cleanly

The game runs in a Docker container with a CRT-style web interface that auto-logs into RSTS/E and starts ADVENT. You can play immediately at [advent-mud.fly.dev](https://advent-mud.fly.dev).

What remains for the full version: fixing the multi-user file locking, and probably several months of debugging things that made sense in 1987 but are now thoroughly mysterious.

## Final Notes

If something doesn't work - which is likely - see [Technical Details](TECHNICAL.md) for the gory details.

If you're reading this and the game is actually running, then we've succeeded beyond our expectations. If not, well, we did warn you that life is never simple.

Well, that's about all we've got time for this week. Next week we'll be looking at the Papua New Guinea economy, and building a thermonuclear bomb out of yoghourt cartons.

---

*"Many decades ago, this large circular room was of great importance, but its beauty has diminished..."*

— Room 9 description, Advent (1987)

---

This documentation was written by Claude, an AI assistant made by Anthropic, in December 2025. Edward provided context, corrections, and the occasional "I can't believe I wrote that" when reviewing the source code.
