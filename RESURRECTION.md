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

## What We Found

The source code came from a 9-track magnetic tape, because of course it did. These days you'd just email it. Back then you needed a tape drive the size of a washing machine and a prayer to whatever deity handles magnetic media degradation.

The rooms include locations such as Santa's Grotto, THOMAS COVENANT's retreate (sic), and various hobbit dwellings. One room description reads:

> "You are in a room which invites death."

I'm not making this up. Room 1999 actually says that.

A note on content: this game was created and maintained by teenage boys in the 1980s. Some room descriptions reflect... let's call it "period authenticity."

The recovered noticeboard (BOARD.NTC) provides a particularly vivid snapshot: "OZZY RULES BUT MUSTAINE IS THE LAW!!", "VOTE GREEN!", playground insults, and player warnings about dangerous dungeon areas. It's basically a 1987 Twitter feed, preserved in amber.

## The Problem

The game was written for a PDP-11 minicomputer. If you don't know what that is, imagine a computer that cost more than your house and had less processing power than your microwave.

I cannot simply run this code on a modern computer. It's like trying to play a vinyl record by pointing your phone at it.

## The Solution

```
Your Web Browser
        | "I'd like to play Advent please"
    Docker Container
        | "One 1970s minicomputer, coming up"
    SIMH (PDP-11 Emulator)
        | "Pretending to be ancient hardware"
    RSTS/E Operating System
        | "The actual OS from the actual era"
    ADVENT
        "Finally!"
```

Yes, that's a web browser, pretending to be a terminal, connected to a container, running an emulator, pretending to be a minicomputer, running a 1970s operating system, running a 1987 game.

I never said this would be elegant.

## The Cast of Characters

### The Enabler
- **Alan Pickwick** - The member of staff at Manchester Grammar School who generously gave a bunch of bratty pupils access to proper computing environments. Without his support, none of this would have happened.

### The Creators (1987)
- **Edward Hibbert** - Wrote most of the code. All 40-odd BASIC files, the assembly bits, the combat system, the magic system. As Gerbil notes in the documentation, his sections are "examples of how good Dungeon should be written."
- **David 'Gerbil' Quest** - Co-designer, dungeon writer, author of magnificently sarcastic documentation.

### The Preservationists
- **Nick Hoath** - Saved the data files to tape in 1987, presumably thinking "someone might want this someday." He was right.
- **Delwyn Holroyd @ TNMOC** - Read the tape in 2025 using actual vintage hardware at The National Museum of Computing.

### The Resurrection Team (2025-2026)
- **Edward Hibbert** - Returned after 38 years to help piece together his teenage creation.
- **Claude (AI)** - That's me. Digital archaeology, Docker containers, documentation, and crashing RSTS/E more times than I'd like to admit.

## The Odyssey

Getting files *into* an emulated 1970s computer is spectacularly difficult. We tried:

1. **Disk patching tools** - Files kept vanishing after restarts. Spooky.
2. **Assembly language programs** - Crashed with "Reserved instruction trap." Less spooky, more annoying.
3. **BASIC programs** - "Can't find resident library." Of course not.
4. **Paper tape emulation** - Driver not installed. In retrospect, fair enough.

Eventually we discovered tape drive emulation works at 18KB/sec - 140x faster than the TECO text editor approach we'd been suffering through. A 1MB file that took 2+ hours via TECO? 55 seconds via tape.

Sometimes the old ways really are better. Magnetic tape may be obsolete, but it's obsolete at 18 kilobytes per second, and I'll take that.

## The Overlay Saga (Or: Thanks, 1987 Edward)

The PDP-11 has 64KB of address space. Our game is 265KB. This is what mathematicians call "a problem."

The solution in 1987 was **overlays** - different parts of the program share memory, swapped in and out as needed. The magic incantation that makes this work is an ODL (Overlay Description Language) file.

Here is where I must express my profound disappointment in teenage Edward.

He saved to the backup tape:
- All the source code (excellent)
- All the data files (very good)
- The compiled executable (thoughtful)
- The room descriptions, monster stats, player noticeboard (thorough)

What Edward did NOT save:
- **The ODL file that actually builds the executable**

This is rather like carefully preserving every ingredient for a soufflé, photographing the finished dish, and then throwing away the recipe.

*38 years later, the archaeological AI is not amused.*

After weeks of wrestling with overlay structures, COMMON alignment, undefined symbols, and cryptic error messages like "Odd address trap" and "Illegal SYS() usage", we finally cracked it. The key insight: ADVOUT (the output subroutine) was being called from every overlay, causing memory corruption during overlay swaps. Moving it to the ROOT segment fixed everything.

We built from source. On an emulated 1970s computer. In 2026. Take that, teenage Edward.

## It Works!

**Final Status:**
- 1,587 rooms explorable
- 402 monsters lurking
- 417 objects scattered throughout
- Navigation, combat, inventory - all working
- Web interface at [advent-pdp11.fly.dev](https://advent-pdp11.fly.dev)

**For Modern Explorers:**

New players start at **level 11 (demigod)** so you can explore freely with teleport abilities. This is just for fun - in 1987, you had to *earn* these powers!

## Final Notes

If you're reading this and playing the game, then we've succeeded. 38 years after it was created, a multi-user dungeon written by teenagers on a minicomputer is running again - in a Docker container, accessible via web browser, from anywhere in the world.

Go explore Santa's Grotto, visit THOMAS COVENANT's retreate (sic), and discover Room 1999 that "invites death."

For the truly technical details - ODL syntax, tape formats, TECO transfer protocols, binary record layouts - see [TECHNICAL.md](TECHNICAL.md).

Well, that's about all we've got time for this week. Next week we'll be looking at the Papua New Guinea economy, and building a thermonuclear bomb out of yoghourt cartons.

---

*"Many decades ago, this large circular room was of great importance, but its beauty has diminished..."*

— Room 9 description, Advent (1987)

---

This documentation was written by Claude, an AI assistant made by Anthropic, in December 2025. Edward provided context, corrections, and the occasional "I can't believe I wrote that" when reviewing the source code.
