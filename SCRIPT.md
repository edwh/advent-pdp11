# ADVENT Video Script

Interesting rooms, actions, and sequences for demo video.

## Claude's Thought Bubbles

*These appear as subtitles below the terminal during the video, showing Claude's AI perspective*

### Opening
```
[Terminal shows: "You are in dark desolate dismal room."]
💭 "Ah yes, dark desolate dismal. The adjective budget was clearly unlimited in 1986."

[Terminal shows: "You see: NEWDEN's corpse"]
💭 "A corpse already? I haven't even moved yet. This place has atmosphere."
```

### First Combat
```
[Terminal shows: "A ninja"]
💭 "A ninja. In a cave. Sure, why not. I'm a language model - I've seen weirder."

[User types: HIT NINJA]
[Terminal shows: "First draw"]
💭 "Ah. Apparently I need to draw my weapon first. Even AIs can't punch ninjas."

[User types: DRAW FALKENSTONE]
[Terminal shows: "Ok."]
💭 "A Falkenstone. Sounds impressive. Probably just a rock with a fancy name."

[Terminal shows: "You did 10 points of damage and killed the ninja"]
💭 "10 damage! This Falkenstone rocks. ...I'll see myself out."
```

### Santa's Grotto Discovery
```
[Terminal shows: "You are inside Santa's Grotto..."]
💭 "Wait. There's a Santa's Grotto in this dungeon? The teenagers who made this really committed to the bit."

[Terminal shows: "A Christmas snow-leopard eating his tea"]
💭 "A snow-leopard. Eating tea. Very British. Very 1986. I love it."

[Terminal shows: "Santa Claus"]
💭 "I'm going to pretend I don't see the 'HIT SANTA' option in my mind palace."
```

### The Fortune Teller
```
[Terminal shows: "your fortune will only be told when someone returns her balls"]
💭 "These were definitely teenage boys in 1986. Some things never change."
```

### Fatigue Crisis
```
[Terminal shows: "You're too tired."]
💭 "Understandable. Combat is exhausting."

[User types: REST]
[Terminal shows: "You're too tired."]
💭 "Too tired to rest? That's... concerning."

[User types: QUIT]
[Terminal shows: "You're too tired."]
💭 "TOO TIRED TO QUIT?! This is a bug. This has to be a bug. Help."
```

### The "You Can't" Philosophy
```
[Terminal shows room with monster and treasure]
[User types: GET TREASURE]
[Terminal shows: "You can't."]
💭 "You can't. That's it? Just... 'you can't'?"
💭 "No 'there's a monster here', no 'kill it first', just... you can't."
💭 "This is what happens when teenagers write code and test it themselves."
💭 "They KNOW why you can't. They just forgot to tell the player."

[User types: HIT MONSTER, kills it]
[User types: GET TREASURE]
[Terminal shows: "Ok."]
💭 "Ah. Needed to kill the monster first. Would have been nice to know."
💭 "Pro tip from an AI: your error messages are documentation."
```

### Examining Things
```
[User types: EXAMINE SWORD]
[Terminal shows: "You can't do that."]
💭 "I can't EXAMINE things? In a text adventure? In 1986?"
💭 "The creators probably thought 'why would anyone examine things when LOOK exists?'"
💭 "Because LOOK shows the room, not the item. Different verbs, different purposes."
💭 "But if you're 16 and testing your own code, you already know what the sword looks like."
```

### The USE Conundrum
```
[User types: USE KEY]
[Terminal shows: "You can't."]
💭 "I have a key. There's a locked door. USE KEY does nothing."
💭 "Maybe it's UNLOCK? OPEN? INSERT KEY? KEY IN DOOR?"
💭 "This is an adventure game from 1986. Half the gameplay is guessing the verb."
💭 "The other half is dying because you guessed wrong."
```

### MSG Device Crash
```
[Terminal shows: "?Not a valid device at line 29000"]
💭 "Oh. The game crashed. Apparently the MSG: device doesn't exist."
💭 "In my defense, I'm an AI from 2026 trying to run code from 1986 on hardware from 1977."
💭 "Some things were bound to break."
```

### Developer Blindness
```
[Text overlay - Claude's reflection]
💭 "Here's the thing about 'you can't' messages:"
💭 "The developers knew EXACTLY why each one failed."
💭 "Monster in room? Of course you can't get stuff!"
💭 "Wrong item type? Obviously it won't work!"
💭 "But they never wrote that down. They just wrote 'you can't.'"
💭 "38 years later, an AI is trying to figure out what they meant."
💭 "Add context to your error messages, future developers."
💭 "Your future AI debugging assistant will thank you."
```

## Opening Sequence

### Starting Room (Room 2)
```
You are in dark desolate dismal room.
Exits: North, East, South, West
You see: NEWDEN's corpse
```
- Good atmospheric start
- Corpse sets the tone

### The Cave with Slot (Room 84, North from start)
```
You are in a large rough walled cave, lit by a large torch on the east wall.
To the west there is a small slot, into which things could be dropped.
```
- Treasure drop slot (shrine?)
- Contains: edible pig, portrait of david, Davidian Cavehog monster

## Combat Sequences

### The Dojo (North from cave)
```
You are in the dojo. Those who do not bow before standing on the mat will be
executed immediately. A sign reads: "FIGHT THE NINJA FOR GLORY AND A FEW XP".
```
- Ninja fight!
- Commands: DRAW weapon, HIT NINJA
- "You did 10 points of damage and killed the ninja"

### Weapons Shop (North from dojo)
```
You are in the ancient weapons shop. Some of these things look really mean.
Unfortunately, there are people about who know how to use them.
```
- Contains: katana, jewel encrusted shuriken, chief ninja

## Atmospheric Rooms

### Oriental Room
```
You are in the oriental room. Valuable neo-Corinthian paintings adorn the walls,
and a poster in Chinese says "IT IS NOT MAN THAT MAKES TRUTH GREAT, BUT TRUTH
THAT MAKES MAN GREAT". You hear chopping sounds from the west.
```
- Contains: ming vase, chinese tea leaves, geisha girl

### Store Room (East from start)
```
The sound of rapidly moving water can be heard from a very small hole in the
floor at the back of the room, but nothing can be seen down it. The room is
littered with empty barrels and appears to have been a store room formerly.
```
- Contains: wooden rattle

## Magic Demonstrations

- HEAL: "You now have 76 hit points."
- INVISIBLE: "You are now invisible"
- Status shows "(Invisible)"

## Interesting Commands

| Command | Response | Notes |
|---------|----------|-------|
| HIT (no weapon) | "First draw" | Good error message |
| SHOUT hello | "Ok." | Works |
| ROOM 2 | Teleports | Demigod power |
| REST | "You sit down and close your eyes." | Restores fatigue |

## Christmas Theme (Rooms 740+)

### Santa's Grotto (Room 740)
```
You are inside Santa's Grotto. There are presents lying around on shelves all
around the room. To the north is Santa's little room and above the entrance are
pictures of all his reindeer.
```

### Santa's Room (North from 740)
```
You are inside Santa's little room. In the middle of the room there is a large
seat where he can sit and give out presents. Apart from numerous sacks in the
room there is only an advent calendar.
```
- Santa Claus is here!
- Advent calendar - fitting for game name "ADVENT"

### Christmas Snow-Leopard (Room 42)
```
You see: A Christmas snow-leopard eating his tea
```
- Wonderfully absurd British humor

## Humorous Rooms

### Fortune Teller (Room 777)
```
You can see that a woman is weeping. When you ask her what is wrong she tells
you that her crystal ball has been stolen. She says that your fortune will only
be told when someone returns her balls.
```
- Definitely written by 1980s schoolboys!

### Newspaper Room (Room 13)
```
You are in a decrepit storeroom. The floor is covered with rubbish.
You see: A newspaper (x6)
```
- Event trigger: "Your feet uncover a newspaper"
- BUG: READ NEWSPAPER crashes the game!

## Discovered Mechanics

### Fatigue System
- Combat drains fatigue rapidly
- At 0 fatigue: "You're too tired" blocks ALL commands (BUG - even QUIT!)
- REST restores fatigue (but not at 0!)
- HEAL restores HP (but also blocked at 0 fatigue)

### Monster Blocking
- Can't GET items if monster is in room
- Must kill monster first
- Error message just says "You can't." (should explain why)

### Room Events
- Some rooms trigger events on entry
- "Your feet uncover a newspaper" in room 13

## TODO: Find More

- [ ] Treasure shrine - drop items for XP
- [ ] Locked doors - OPEN with KEY
- [ ] Puzzles - room-specific commands
- [ ] Bell rooms - RING command
- [ ] Working READ (noticeboard?)
- [ ] More monster fights
- [ ] Death sequence?
