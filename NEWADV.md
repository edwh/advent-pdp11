# Guidelines for Dungeon Writers

*Written by David 'Gerbil' Quest and Edward Hibbert, 1986-87*

---

## Chapter 1: Commands

NEWADV is the program you use to edit the dungeon. The origins of the name NEWADV are now lost in the mists of time. It used to be called ADV, I think, but that was several versions ago.

NEWADV is incredibly stupid. It's not designed to be user-friendly, so you have to pander to its little whims.

I've recently cleared some junk out of the program, so with any luck all the commands that are in NEWADV should actually do something moderately useful. In addition I've incorporated some of the noddy programs into it.

Because of these changes, Gerbil's incredibly witty help text is now out of date. What I've done is to quote his jokes verbatim and take the credit myself.

Right, enough waffle, on with the help text...

Congratulations on obtaining permission to write some of the dungeon. If you haven't got permission, you will be hearing from the Frogsquad shortly.

As mentioned above, NEWADV is about as userfriendly as a mousetrap (Gerbiltrap?). On the whole, it works reasonably well, and does what it is supposed to (of course, whether this is what you want it to...). There are lots of commands (as you can see by hitting return). I'll describe them here.

### Enter

This command is used for extending the number of rooms in the dungeon. It doesn't work when the Adventure is running, might work when it is in a coma and probably works when it is dead. You probably won't need this one. The format of the questions is vaguely similar to those in change.

### Change

This command allows you to edit rooms, and is basically the one to use. It steps through the entries one by one, allowing you to change them. Hitting return keeps the old entry, typing 'none' might (depending on whether it is in upper case, what day it is, what the weather is like etc.) set the entry blank.

There are lots of things to remember here:

- **Exits** should be entered as N1023S002E0001 etc, ie always padded to 4 digits. I don't think you have to put them in NSEW order, but it is probably a good idea. N0000,S0000 etc sends somebody out of an exit, which allows them to rise a level if they've got enough XP, restores heal ability etc.

- **Monsters/Corpses** must be separated by '/'s (but not at the end), and prefixed with '*' for monsters which attack you as soon as you enter, '_#' for monsters which wait until you draw, and '!' for corpses or scenery.

- **Descriptions** should be entered as one line (ie just type over the edge of the screen, do your own formatting) upto a max of about 255. Special cases are in fact stored on the end of the description (they can be edited at the next prompt) so if you want a lot of special cases then it is probably unwise to have a long description. This is, of course, exactly how you DON'T want it.

- **Special cases** should be separated by a slash, with a trailing slash at the end (where else?). There are lots of different special cases. Special cases should take precedence over real commands - if they don't then remind me to edit it so they do. Here is a list of special commands:

  1. `/C` - this specifies which command they must type to do the special case. As with all the cases, if it fails this, then it drops out of the special cases. No IF statements here, I'm afraid. Eg /CJUMP/.... means they have to type 'JUMP'. /C is the only compulsory special case. You must put it in!

  2. `/A` - this refers to the argument they must have specified. Eg .../AUP/... means they must have type .... UP.

  3. `/T` - this is 'TELL' - send a message to the person doing it. It sends exactly what you say, so make it look nice. Eg. .../TYou jump up./...

  4. `/S` - this is 'SHOUT' - sends the name of the person doing it plus a space plus what you say here. Eg .../Sjumps up./...

  5. `/N` - this is 'NEED' - they need this object to continue, otherwise it says 'You can't do that yet.' Note the 'yet' - this gives them a clue that they are at least thinking of the right thing. Eg .../NROPE/... By the way, it does an instr, so don't put A rope. Probably this had better be in upper case.

  6. `/U` - this is like /N but it uses (ie zaps) the object as it passes.

  7. `/M` - this makes an object and dumps it on the floor. Eg .../MSome chalk/...

  8. `/R` - this is 'ROOM' - you use it to send somebody somewhere. It does a look when it has, so don't bother telling them anything if you're going to do a /R later. The room number doesn't have to be padded. Make sure the number is reasonable (like <2000?). It doesn't tell anybody else in the room anything, so /S is probably a good idea. Eg .../Sdisappears./R1/Sappears./...

  9. `/%` - this is the % chance of continuing with the special case. If it fails, it prints 'Nothing happens.'

  10. `/G` - this gives them an object, if they can carry it. If they can't, I think it might drop it on the floor, but don't hold me to that.

  11. `/H` - this gives them HP. It can be <0. This is a good point to mention that anybody who puts infinite HP special cases in will instantly have NEWADV removed. Infinite HP really wreck the game. Eg .../H1/...

  12. `/E` - this is 'EXTEND' - continue with the special cases in the room given by the argument. Eg .../E123/

  13. `/O` - Occurrence (the initials are getting more and more far fetched, but I'm running out of letters). This is something which just happens - best explained by an example:

  14. `/;` - totally run out of meaningful letters by now, sorry. /; means fail - eg .../;123/... means when one of the special case checks (eg /N) fails, processing will continue with the special cases in room 123.

  Example: `/O/TA voice booms 'Get out of my office/`

  NB All the "You can't" messages don't appear for /O/, so you can use a /% to get an occurrence which only happens some of the time!

  15. `/L` - Level. Continues if level>=whatever. Eg /L3/...

  16. `/<` - Level again. Continues if level <=whatever.

Use special cases carefully, otherwise you won't have the opportunity at all.

A final example: `/CCLIMB/AROPE/UROPE/Sclimbs up the rope./R123/TYou climb up the rope but it breaks as you get to the top./Sclimbs up using the rope./`

- **Objects** should be separated by a slash as with people.
- Objects can only be thirty characters long.
- `Some treasure~20` means it is worth 20 XP if you drop it in a shrine.
- `A weapon$4` means a weapon of damage bonus 4. Be cautious about giving high weapons out, and be imaginative with the names.
- You can edit rooms without putting the Adventure to sleep if no-one can get in them. Make very sure of this. If you're editing some other part of the dungeon (why? sounds corrupt), use the sleep command, edit, then send it wake.

### Monster

This is used for putting a one off monster into the monster file. The questions are self-explanatory, except for special attacks. There are, I think, three special attacks:

1. `/FO??/` - follow. ?? is % chance, 00 ==> doesn't move. Must be two characters long.
2. `/PA??/` - chance of paralysis on successful hit.
3. `/PO??/` - chance of poison on a successful hit. Be careful with this - you can really make yourself unpopular by putting too many poisonous monsters in, witness Roxby and the island.

It is probably a good idea to emphasize that this is a one off command. Usually, people use REFRSH to put a monster in the refresh file, so that it will get put in again after it has been killed.

Don't forget to put the monster in the people, using the change command.

This command sends a message to the Adventure, so the Adventure needs to be alive, awake and not in a coma.

### List

This lists the statistics for a monster. They may be out of date, if you have just done a monster command, as the Adventure, in its ceaseless search for efficiency, buffers the monster while they're being used.

### Send

This sends a message to the Adventure. You may or may not be able to do this. If the Adventure is in a coma, the message will only get processed when you do a WAKECOMA command.

The Adventure accepts the following commands:

1. `LOG X` - logs character with name X into the Adventure on your keyboard. You must logout after sending this.
2. `CREATE` - don't use this, use CRENEW.
3. `MON` - don't use this, use the MONSTER command.
4. `BROADCAST` - this sends an announcement to everybody in the Adventure.
5. `SLEEP` - puts the Adventure to sleep. Use the SLEEP command - it's quicker.
6. `WAKE` - brings the Adventure out of a sleep.
7. `WORKMAN X` - puts character X in as a workman. The usual workman is UNCLE.
8. `LIST` - sends you a list of who's playing.
9. `COMA` - puts the Adventure in a coma. Use the wake command to wake it up again.
10. `LT n` - logs character on keyboard n out.
11. `NPC X` - sends character X in as an NPC.
12. `TIDY` - produces ADVTDY.RPT. Takes a few minutes.
13. `TELL name message` - I'll leave you to work this one out yourself.
14. `STAT name` - Ditto.

### Morbid

This command looks for corpses. This is completely useless, as it starts from room 1, and as far as bodies go, the Adventure makes Southern Cemetery look pretty sick.

### Log

This allows you to look at the logfile. This contains such thrilling information as when the Adventure went up and down, and when level 10+ characters logged in and out.

### Corrupt

This looks for rooms which are either corrupt or unused. Now superceded by the TIDY command (you have to send that to the Adventure, and it produces a file called ADVTDY.RPT, which contains lots of information on the data file, and checks for corrupties), but I might as well leave it in.

### Sleep

This sends a sleep message to the Adventure. When the Adventure is asleep, all the people in it can do is exit. They can wait for it to wake up, though.

### WakeComa

Brings the Adventure out of a coma. Not like SEND WAKE.

### WakeSleep

Brings the Adventure out of a sleep. Equivalent to SEND WAKE.

### Message

This is for entering messages for NPCs to shout. They should be apt, witty and shorter than 60 characters.

### Exitfind

This command is useful if a room gets corrupted. It allows you to look through the dungeon for rooms which have exits into the room you tell it. If the room was in a maze, where the corridors are twisty, then tough, but probably nobody would notice if you just put in any exits. By the way, about repairing corrupt rooms - try to get the description right. It is possible that I can recover a copy of the data file with the room intact, in which case it's dead easy.

### Notice

This allows you to specify that a room has a noticeboard. Don't forget to put something in the description about it. I think this only works when the Adventure is down.

### Reccor

This command allows you to recover corrupt rooms. Don't mess about with it.

### Find

This allows you to look through the dungeon for an object.

### Advert

This allows you to put a message on all the noticeboards.

### Other Programs

There are some other programs, as well as NEWADV, though now fewer than at one time. Here they are:

1. **REFRSH.BAC** - this enters monsters and objects into REFRSH.CTL, so that when the workman makes his rounds, he will put them into the dungeon. Initially it was envisaged that the demigods would replace the monsters by hand! The program is self-explanatory. % chance is the chance that the workman will put the object in this time. Note that monsters don't get put in if there is another monster in the room, though if there is a copy of the same monster in the room, it gets healed a bit (though not above its maximum). It is tempting to use REFRSH for all your monsters, as it keeps the dungeon full and once it is in the file you can forget about it, but try and be sensible. If you have a powerful, interesting or unique monster, don't put it in the refresh file - we want to avoid the 'Oh no, it's the one and only high supreme lord of the entire dungeon again' syndrome. Instead put a lot of different monsters and objects for the same room with low probabilities - more work, but it leads to a better section. But do make sure that the dungeon is well stocked. Incidentally, REFRSH was written by a halfwit, so you have to type small o for object and anything else for monster. This can be infuriating, but I can't be bothered changing it.

2. **REFLST.BAS** - this produces a nice printout of the contents of the refresh file.

3. **SNDNEW.BAC** - sends a message to the Adventure.

4. **ADEDIT.BAC** - allows you to edit characters. You can search for characters to Edit, List, Kill, by a variety of things, like weapon bonus. For numeric things like level, it lists all those equal or above. Try it and see. If you want to edit, the Adventure must be in a coma.

5. **CRENEW.BAC** - Oh yes, CRENEW. I think you'll find out about that.

---

## Chapter 2: Guidelines

The previous chapter was mostly about the commands, though it did have some advice in it. This one is mainly advice. You must read it and take it seriously (apart from the jokes, which are mostly Gerbil's), otherwise you will do something stupid and you'll have NEWADV removed. If you can describe yourself as a maelstrom of literary brilliance, then you probably won't have many problems, but you might as well have the benefit of the vast experience of previous dungeon writers.

**Realism** is the most important thing. I know it's only a game, but if your Dungeon is not both believable (to some extent anyway) and interesting, then people will tire of it very quickly. Choose a theme, and write from 20 to 100 rooms on that theme. Keep to one style, and don't change rapidly from mountains to caves to cities to rivers etc. otherwise there will be no overall picture, and no-one will be able to perceive the (undoubted) brilliance of your masterpiece.

The odd incongruous section - a futuristic room in an underground cavern for instance - can be amusing or surreal, if you use this technique sensibly and sparingly. It gives an impression of size and extent to the Dungeon, if strange objects from far away parts are carried into the main sections by characters. However, if you overdo this, then the whole thing becomes silly, unconvincing and a waste of time, effort, runtime and disk space.

Try and make sure that there is a **gradual increase in difficulty**, don't let hideous hellbeasts loose in 0th level nurseries. Well not too often anyway. Warnings like 'YOU WILL DIE IF YOU GO IN HERE' are quite useful, but most people completely ignore them. Treasure and experience points should be appropriate for the monster guarding them. Remember that if a monster follows someone, he/she/it might leave behind treasure unguarded. It adds interest to the life of a 0th level character if he occasionally wanders into a room and gets his head torn off by a rabid, slavering megamonster; but this can become irritating if it happens too frequently. Characters also do not appreciate having spent an hour hacking a green dragon to pieces to get 4 XP and a copper coin.

Don't give your monsters or treasure **fantastic descriptions** if they don't merit it. If the 'Enormous glittering diamond' is only worth 70 XP, this tends to devalue the Dungeon monetary system. Similarly, if the 'Giant armour plated six headed fire breathing hamster' is only level 3 the convincability factor drops rapidly.

In many parts of the Dungeon, particularly the more surrealistic regions, strange monsters such as the light shade et al abound. This is fine, but again, don't overdo it. Sometimes a monster needs to be unkillable, e.g. a school of barracuda, or a falling rock. If you think this is necessary make sure it IS unkillable - and never give a monster a ridiculous number of XP because you think it is too powerful. It never is.

Put as many **civilians** (workmen, shopkeepers, cleaners, advertising executives etc.) as you like into the dungeon - they all add atmosphere. Make sure that their level is appropriate - just because a monster is in a level 5 area of the Dungeon doesn't mean it can't be level 0.

Similarly for **objects**, when in doubt put one in. It doesn't matter if an object is completely useless, it makes a room more convincing. There could well be a limit on the length of objects - probably about 30 characters. There is no limit on corpses or monsters I think.

For any monster you put in, consider **what it will look like when it's dead**. It is possible to put a corpse in as a monster, as in the notorious 'HERON's corpse', but when it died it became 'HERON's corpse's corpse', which is a little silly. Also check the hit and follow messages. 'A falling rock has followed you' must surely be the ultimate in avoidable stupidity (set /FO00/).

Make sure that the Dungeon you write is in a **logical, mappable form**. Unfortunately, there is no complete map of the Dungeon in its entirety, and in view of its staggering size, it is unlikely that anyone knows the way round all its myriad capillaries (good phrase eh?). If you've got a few months free, and have got a degree in Applied Geological Cartography you might like to try making a map of the whole thing - but at least map the new bits. Although it is realistic and sometimes interesting to have twisting corridors and mazes, don't have them too often. Encourage characters to make maps (check they can read and write first - some can't) and when you have finished your brand new section, still in its polystyrene box, don't just plug it in anywhere. Check with other authors to find a space. It should be very difficult and take a long time for a 0th level to get to a really nasty section, but it must be possible. One way doors are a useful, if unimaginative, way to stop high levels returning to 0th level kindergartens.

**TELEPORT GATES ARE A BAD IDEA!** They destroy the individuality of different sections by allowing people to move from far flung corners of the Dungeon much too quickly. Think very carefully before putting in a teleport gate.

Changing parts of the Dungeon **written by other people** is discourteous, destructive, arrogant, unnecessary and stupid. Deleting them is even worse. Unless the room or the author is corrupt, it is a very, very bad idea. If you innocently change an exit, you might cut off hundreds of rooms, or upset the finely balanced ecosphere someone has spent years setting up. Always check with the original author before altering anything. Even if the author was really corrupt (I could give you a list, but there's only about 30000 blocks free on DP1: so I won't bother) don't delete his rooms - just take out the illegal bits.

On the subject of **corruption**, a great deal of responsibility and trust has been invested in you as a Dungeon writer, and we expect you not to abuse it. Don't create yourself ludicrous weapons, fantastic treasure, stupid monsters and don't create them for your friends either. Don't let other people suggest bits for you to write and NEVER let anyone else use your NEWADV program. Here is what happens to corrupt people - in 4 easy stages:

1. You create something corrupt for an accomplice
2. You are caught
3. Your NEWADV program, character, and illegal objects are removed by a Demigod who has inconceivably more important things to do.
4. You are spread in a very, very thin layer over a very, very large area.

As far as **monster XP and hit points** go, level 0-2 should have 3-40 HP and be worth about 2-50 XP (including treasure) and do about 1-6 points of damage. These should increase gradually to about 350 HP/40 DAM/1500 XP for a level 10 monster - but these are rough guidelines only. Make sure any values you use are appropriate.

Use as many **special cases** as possible in anything you write - but don't make them too obscure (surprisingly people might not think of typing DETOXIFY STREAM) and don't tell anyone about them - put it in the room description. There are lots of good examples in Hell.

If you want to see examples of how good Dungeon should be written, there are plenty around - mostly written by Messrs. Allan, Hibbert, Short, Vout and Gerbil. Good examples of other people's mistakes, which you might like to learn from, can be found all over the place, notably in Mr. Roxby's sections.

To summarise, remember the 3 C's:

1. **Creativity**
2. **Coherence**
3. **Conscientiousness**

...and you won't go (too) far wrong.

---

Well, that's about all we've got time for this week. Next week we'll be looking at the Papua New Guinea economy, and building a thermonuclear bomb out of yoghourt cartons.
