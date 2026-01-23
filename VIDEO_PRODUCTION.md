# ADVENT Video Production Plan

## Overview

Create a demo video of Claude exploring ADVENT, with:
- Terminal gameplay footage
- Claude's thought bubbles with typing effect
- Sound effects matching game events
- Ambient background music

## Technical Approach

### Recording Method (REVISED)

**Recommended: Chrome DevTools MCP Screen Recording**
- Record the actual Chrome browser window showing the game
- Captures real terminal scrolling, not reconstructed frames
- Uses Chrome DevTools Protocol for reliable capture

```bash
# Use Playwright to:
# 1. Open the game in Chrome
# 2. Start screen recording
# 3. Automate gameplay via terminal input
# 4. Stop recording when done
```

**Key Requirements:**
- Must capture ACTUAL screen content, not reconstruct from text
- Terminal text must scroll naturally up the screen
- Thought bubbles appear with typing effect (character by character)

### Star Wars Opening Crawl

The crawl needs **3D perspective transform** to look authentic:

```css
/* Container with perspective */
.crawl-container {
  perspective: 300px;
  perspective-origin: 50% 100%;
}

/* Text tilted into distance */
.crawl-text {
  transform-origin: 50% 100%;
  transform: rotateX(25deg);
  animation: crawl 60s linear forwards;
}

@keyframes crawl {
  from { transform: rotateX(25deg) translateY(100%); }
  to { transform: rotateX(25deg) translateY(-300%); }
}
```

The key insight from [CSS-Tricks](https://css-tricks.com/snippets/css/star-wars-crawl-text/) and [SitePoint](https://www.sitepoint.com/css3-starwars-scrolling-text/):
- `perspective: 300px` creates depth
- `rotateX(25deg)` tilts text away from viewer
- Text shrinks as it moves "into" the screen

### Thought Bubble Typing Effect

Thoughts must appear with typing animation, not instant:

```javascript
// Type out text character by character
async function typeText(element, text, speed = 30) {
  for (let char of text) {
    element.textContent += char;
    await sleep(speed);
  }
}
```

**NOT**: Show all text at once and switch between scenes
**YES**: Character-by-character reveal with cursor blink

## Browser-Based Recording Architecture (PROPER APPROACH)

The current Python approach reconstructs frames from text. For **authentic video** we need:

### Architecture
```
┌─────────────────────────────────────────────────┐
│              Playwright/Puppeteer               │
│  (Controls headless Chrome, records viewport)   │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│              HTML Video Page                    │
│  ┌─────────────────────────────────────────┐   │
│  │  Star Wars Crawl (CSS 3D perspective)   │   │
│  │  - perspective: 300px                   │   │
│  │  - rotateX(25deg)                       │   │
│  │  - Text shrinks into distance           │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  Game Terminal (iframe to ttyd)         │   │
│  │  - Real scrolling text                  │   │
│  │  - Actual VT100 rendering               │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  Thought Bubble Overlay                 │   │
│  │  - Typing animation (char by char)      │   │
│  │  - Cursor blink                         │   │
│  │  - TTS audio sync                       │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│              Expect-style Input                 │
│  - Send characters one at a time               │
│  - 50-100ms delay between keystrokes           │
│  - Sync with recording timeline                │
└─────────────────────────────────────────────────┘
```

### Implementation Steps

1. **Create HTML video page** (`video/recorder.html`)
   - Star Wars crawl with CSS 3D perspective
   - Iframe for game terminal
   - Thought bubble div with typing animation
   - JavaScript to control scene transitions

2. **Playwright recording script** (`video/record.js`)
   ```javascript
   const { chromium } = require('playwright');

   async function record() {
     const browser = await chromium.launch();
     const context = await browser.newContext({
       recordVideo: { dir: 'output/', size: { width: 1280, height: 720 } }
     });
     const page = await context.newPage();

     // Load video page
     await page.goto('file:///path/to/recorder.html');

     // Scene 1: Star Wars crawl
     await page.evaluate(() => startCrawl());
     await page.waitForTimeout(30000);

     // Scene 2: Game terminal
     await page.evaluate(() => showTerminal());

     // Type commands character by character
     for (const char of 'LOOK') {
       await page.keyboard.type(char);
       await page.waitForTimeout(100);
     }
     await page.keyboard.press('Enter');

     // Show thought bubble with typing
     await page.evaluate(() => typeThought('Someone read too much Tolkien.'));

     // ... more scenes ...

     await context.close();
   }
   ```

3. **Thought bubble typing animation**
   ```javascript
   async function typeThought(text) {
     const bubble = document.getElementById('thought-bubble');
     bubble.style.display = 'block';
     bubble.textContent = '💭 Claude: ';

     for (const char of text) {
       bubble.textContent += char;
       await sleep(30); // 30ms per character
     }
   }
   ```

### Recommended Stack

```
Docker Container:
├── asciinema (terminal recording)
├── ffmpeg (video/audio processing)
├── Python + moviepy (composition)
├── Playwright (browser automation)
└── Audio files (downloaded)
```

## Sound Design

### Sound Effect Categories

| Category | Trigger | Example Sounds |
|----------|---------|----------------|
| **Ambient** | Room entry | dripping water, wind, torch crackle |
| **Movement** | N/S/E/W | footsteps (stone, sand, wood) |
| **Combat** | HIT, damage | sword clash, monster roar, death cry |
| **Magic** | HEAL, INVISIBLE | sparkle, whoosh, mystical hum |
| **UI** | Command entry | keyboard click, terminal beep |
| **Discovery** | New room type | door creak, revelation chime |
| **Error** | "You can't" | sad trombone, buzzer |
| **Crash** | Game crash | record scratch, system error |

### Public Domain Sound Sources

**Freesound.org (CC0 recommended):**
- Search: "dungeon ambience", "sword hit", "footsteps stone"
- Filter by: License = Creative Commons 0

**OpenGameArt.org:**
- RPG sound packs
- 8-bit/retro effects

**Archive.org:**
- Old radio drama effects
- 1980s computer sounds

### Background Music

**Style:** Low ambient synth, vaguely 1980s, mysterious

**Sources:**
- Kevin MacLeod (incompetech.com) - "Crypto", "Dark Fog", "Ossuary"
- Free Music Archive - search "dungeon ambient"
- Archive.org - public domain synthesizer albums

## Script Format

### Timed Script Structure (YAML)

```yaml
scenes:
  - id: opening
    duration: 15s
    music:
      track: ambient_dungeon.mp3
      volume: 0.3
      fade_in: 2s

    events:
      - time: 0s
        type: terminal
        action: show_prompt

      - time: 1s
        type: terminal
        action: type_command
        text: "LOOK"
        typing_speed: 100ms

      - time: 2s
        type: terminal
        action: show_output
        text: "You are in dark desolate dismal room..."

      - time: 3s
        type: sound
        file: dripping_water.wav
        volume: 0.5

      - time: 4s
        type: thought_bubble
        text: "Ah yes, dark desolate dismal. The adjective budget was clearly unlimited in 1986."
        typing_speed: 30ms
        duration: 4s

      - time: 8s
        type: terminal
        action: show_output
        text: "You see: NEWDEN's corpse"

      - time: 8.5s
        type: sound
        file: ominous_drone.wav
        volume: 0.4

      - time: 9s
        type: thought_bubble
        text: "A corpse already? I haven't even moved yet. This place has atmosphere."
        typing_speed: 30ms
```

### Thought Bubble Styling

```css
.thought-bubble {
  background: rgba(0, 0, 0, 0.8);
  border: 2px solid #00ff00;
  border-radius: 10px;
  padding: 15px;
  font-family: 'VT323', monospace;
  color: #00ff00;
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  max-width: 80%;
}

.thought-bubble::before {
  content: "💭 Claude: ";
  color: #ffff00;
}

/* Typing effect via JS */
.typing-cursor {
  animation: blink 0.7s infinite;
}
```

## Video Composition Pipeline

```
1. PREPARE
   ├── Download sound effects
   ├── Download background music
   ├── Create timed script YAML
   └── Set up Docker with tools

2. RECORD
   ├── Start asciinema recording
   ├── Execute gameplay commands (automated)
   ├── Stop recording
   └── Export as .cast file

3. RENDER
   ├── Convert .cast to video frames
   ├── Generate thought bubble overlays
   ├── Mix audio tracks
   └── Composite final video

4. POST-PROCESS
   ├── Add fade in/out
   ├── Color grade (CRT effect?)
   ├── Add intro/outro titles
   └── Export final MP4
```

## Dockerfile Addition

```dockerfile
# Video production tools
RUN apt-get update && apt-get install -y \
    asciinema \
    ffmpeg \
    python3-pip \
    fonts-liberation \
    && pip3 install moviepy pyyaml pillow

# Sound effects directory
COPY video/sounds/ /opt/advent/sounds/
COPY video/music/ /opt/advent/music/
COPY video/script.yaml /opt/advent/video_script.yaml
```

## Sound Effect Mapping

Based on our script, here are specific sounds needed:

### Opening Sequence
| Moment | Sound | Duration | Source Search |
|--------|-------|----------|---------------|
| Room description appears | stone_echo.wav | 2s | "cave echo ambience" |
| "corpse" mentioned | ominous_drone.wav | 3s | "horror drone" |
| Thought bubble appears | soft_chime.wav | 0.5s | "notification chime soft" |

### Combat Sequence
| Moment | Sound | Duration | Source Search |
|--------|-------|----------|---------------|
| Enter dojo | wooden_door.wav | 1s | "door creak wood" |
| See ninja | tension_sting.wav | 2s | "suspense hit" |
| "First draw" error | error_buzz.wav | 0.5s | "wrong answer buzzer" |
| DRAW weapon | sword_unsheath.wav | 1s | "sword draw" |
| HIT command | sword_slash.wav | 0.5s | "sword swing" |
| "killed the ninja" | death_cry.wav | 1s | "monster death" |
| Victory moment | success_chime.wav | 1s | "victory fanfare short" |

### Exploration
| Moment | Sound | Duration | Source Search |
|--------|-------|----------|---------------|
| Movement (N/S/E/W) | footsteps_stone.wav | 1s | "footsteps cave" |
| Santa's Grotto | sleigh_bells.wav | 2s | "christmas bells" |
| Fortune teller | mystical_hum.wav | 2s | "crystal ball" |
| "You can't" | sad_trombone.wav | 1s | "fail sound" |
| Game crash | record_scratch.wav | 1s | "record scratch" |

### Background Loops
| Scene | Track | Mood |
|-------|-------|------|
| General exploration | dungeon_ambient.mp3 | Mysterious, low |
| Combat | tension_loop.mp3 | Urgent, pulsing |
| Santa's Grotto | music_box.mp3 | Whimsical, eerie |
| Crashes/bugs | silence or glitch | Broken, confused |

## Recording Script (Python)

```python
#!/usr/bin/env python3
"""
ADVENT video recording script
Automates gameplay and records with timing
"""

import yaml
import time
import subprocess
from pathlib import Path

def load_script(path):
    with open(path) as f:
        return yaml.safe_load(f)

def send_command(cmd, delay=0.1):
    """Send command to screen session"""
    subprocess.run([
        'docker', 'exec', 'advent-mud',
        'screen', '-S', 'advent', '-X', 'stuff', f'{cmd}\r'
    ])
    time.sleep(delay)

def record_scene(scene):
    """Record a single scene"""
    for event in scene['events']:
        wait_until(event['time'])

        if event['type'] == 'terminal':
            if event['action'] == 'type_command':
                send_command(event['text'])

        elif event['type'] == 'sound':
            # Sound will be added in post
            log_sound_cue(event)

        elif event['type'] == 'thought_bubble':
            # Thought bubbles added in post
            log_thought_cue(event)

def main():
    script = load_script('/opt/advent/video_script.yaml')

    # Start asciinema
    start_recording()

    for scene in script['scenes']:
        record_scene(scene)

    # Stop asciinema
    stop_recording()

    # Generate timing file for post-processing
    export_timing_cues()

if __name__ == '__main__':
    main()
```

## Next Steps

1. **Download sounds** - Create script to fetch from Freesound
2. **Create script.yaml** - Convert SCRIPT.md to timed YAML
3. **Build video container** - Add tools to Dockerfile
4. **Test recording** - Dry run with asciinema
5. **Post-process** - Build composition pipeline
6. **Iterate** - Adjust timing based on actual footage

## File Structure

```
video/
├── sounds/
│   ├── ambience/
│   │   ├── dripping_water.wav
│   │   ├── torch_crackle.wav
│   │   └── wind_howl.wav
│   ├── combat/
│   │   ├── sword_draw.wav
│   │   ├── sword_hit.wav
│   │   └── monster_death.wav
│   ├── ui/
│   │   ├── typing.wav
│   │   ├── error_buzz.wav
│   │   └── success_chime.wav
│   └── misc/
│       ├── footsteps_stone.wav
│       ├── door_creak.wav
│       └── record_scratch.wav
├── music/
│   ├── dungeon_ambient.mp3
│   ├── tension_loop.mp3
│   └── credits.mp3
├── script.yaml
├── record.py
├── compose.py
└── README.md
```
