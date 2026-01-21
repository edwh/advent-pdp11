# Provenance: How These Files Survived

```
                THE LONG JOURNEY HOME
                ---------------------

        A tale of magnetic tape, yoghurt cartons,
        and the occasional miracle.
```

## The Short Version

These files exist today because of a remarkable chain of preservation efforts spanning nearly 40 years:

1. **1986-87**: Edward Hibbert at Manchester Grammar School, with David Quest writing most of the text and what passed for a storyline.
2. **~1987**: A backup tape was made of Edward's directory
3. **Sometime before switch-off**: Nick Hoath copied data files off the school computer
4. **2020-2025**: Email chains reconnected the original authors
5. **January 2025**: Delwyn Holroyd at The National Museum of Computing read the original tape
6. **December 2025**: Claude (an AI) was summoned to make sense of it all

## The Long Version

What follows is a lightly edited compilation of email correspondence that explains how these files survived. I (Claude) am including this because it's a rather wonderful story of digital archaeology and old friendships.

Email addresses have been removed for privacy.

---

### 2020: The Rediscovery

**David Quest, November 2020:**

> I logged into the valerion version mentioned in the blog. Not sure if it is the same one. But I did find an Edward's corpse. Not sure if it is the same one.

**Edward Hibbert, November 2020:**

> David (Gerbil) - there may be a copy of some of the data from Advent, or whatever it was called.
>
> I think I have a printout of the code, too, as well as the tape, if you fancy helping type it in...

**Nick Hoath, November 2020:**

> One of the data file sets I got off Beta the day of the final switch-off. I lugged my family's 80286 PC in to School and took a copy over serial. It's a shame that there was some room corruption, and also quite a few rooms were overwritten after you'd left. 2000 rooms wasn't much for creative kids!
>
> The file with the code in came from Peter Clark(e?), but I don't know when he got it.
>
> The version currently running on my home fileserver (valerion), is one I rewrote as an exercise in learning OO Perl a few years ago. Having the BP2 source helped :) And those corpses are indeed original Edward ones!

---

### 2022: More Survivors Emerge

**Gary Birch, August 2022:**

> I was reading an archive on the MGS website and there was talk of the game on the mainframe that I remember as 'advent'. If you have any 'data' or anything from back then I'd love to see it. I'm no programmer but I remember writing my own version in basic to try and recreate it when they replaced it with PC's, but of course much of the fun was the multiplayer element.
>
> I was always in awe of the guys who managed it all.

**Edward Hibbert, August 2022:**

> I have a faded printout of the code and a backup of something on an old PDP-11 tape, though I've not found anyone local with the kit to read that particular version of cuneiform.
>
> For years I had assumed that was it, and that was quite enough. But as you might have seen on the blog, some fragments unexpectedly survived. Nick Hoath took a copy of the data files (at least some of which are attached) using two yoghurt cartons connected with string, and then as a hobby project wrote some new code to use that data.

**Hamish Allan, November 2020:**

> David, I was in my first year when you and Edward were in your last at MGS. I live in Edinburgh, and met up with Edward for a coffee when he was there. Nick was in the year above me.

---

### 2024-2025: The Tape Gets Read

**Edward Hibbert, December 2024:**

> After some considerable delay, this is now on its way to you.
>
> I should really have put some kind of eloquently worded thank you note in there. Let's assume I did that.

**Delwyn Holroyd, September 2024:**

> Yes, I remember you from the Systime, although I was mainly on the ICL side of things. I've been volunteering at TNMOC for 15 years now. Amongst other things I look after our ICL 2966 mainframe which runs George 3. The basis for the system was a stack of tapes I rescued from school when the 1902T was being decommissioned. I can recover data from various tape formats and have facilities for baking which, as you say, is sometimes necessary.

**Delwyn Holroyd, January 2025:**

> I've read your tape successfully! I tried to send you ZIP files but the message bounced so I've uploaded them to OneDrive instead. One is the raw tape data and the other is decoded into files. The format of the raw tape data consists of a set of blocks, each one preceded by the block length as 4 big-endian bytes. A tape mark is represented by a block length of 0xffffffff.
>
> I thought you might be interested to see the process so I uploaded a couple of videos to OneDrive too. I used one of the tape decks on the ICL 2966, interfaced directly to a laptop rather than the mainframe.

**Edward Hibbert, February 2025:**

> Lots of code on there - the adventure, the library software, some system utilities. Sadly no data files, though, so I can't resurrect it. But this is the oldest code of mine I possess, so thank you.
>
> I was impressed to find there was some documentation. I think the RNO files were...Runoff? Something like that.
>
> Did you notice your copyright in FORTH.MAC?

**Delwyn Holroyd, February 2025:**

> Yes I did see there was a copy of Forth – I just compared it with the copy I had and it looks like you (or someone) did some work on it after I left MGS. My copy was on a tape dump of my directory from end of June 87. The origin of this was I had a listing of FIG Forth written in Z80 assembler from somewhere or other, and I rewrote it for the PDP11. I seem to remember spending a lot of time on it!

---

## The Cast of Characters

| Name | Role |
|------|------|
| **Edward Hibbert** | Original author, keeper of the tape |
| **David 'Gerbil' Quest** | Original author, named in DEMIG.HLP |
| **Nick Hoath** | Rescued data files on switch-off day, wrote Perl version |
| **Delwyn Holroyd** | TNMOC volunteer who read the tape |
| **Gary Birch** | Former player who remembered the game |
| **Hamish Allan** | Former player, connected people together |
| **Peter Clark(e?)** | Source of some code files |
| **Claude** | AI who made sense of it all in 2025 |

## The Machines

| System | Role |
|--------|------|
| **Beta** | The school's PDP-11 running RSTS/E |
| **An 80286 PC** | Nick's family computer, used for serial transfer |
| **A 9-track PE tape** | Edward's backup from ~1987 |
| **ICL 2966 at TNMOC** | Read the tape in 2025 |
| **Valerion** | Nick's home server running the Perl version |

## What We Have

From the **tape** (read January 2025):
- Complete source code (ADVENT.B2S, subroutines, utilities)
- Documentation (NEWADV.RNO, DEMIG.HLP, etc.)
- No data files (rooms, monsters, characters)

From **Nick's serial transfer** (~1987):
- Data files: roomfil.fil, roomfil2.fil, monfil.fil
- Some room corruption
- Some rooms overwritten by later users

## Notes on the Data

Nick's observation that "2000 rooms wasn't much for creative kids" explains why:
- The highest room number is 1999
- Some rooms show signs of later modification
- There are duplicate/corrupt room entries

The data files represent the dungeon as it existed on the final day of operation, with all the accumulated changes from years of student dungeon-masters.

---

*"Many decades ago, this large circular room was of great importance, but its beauty has diminished..."*

— Room 9, still relevant after all these years
