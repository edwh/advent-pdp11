#!/usr/bin/env python3
"""
ADVENT Video Production Script
Produces a demo video with terminal footage, thought bubbles, and audio.

Usage:
    python3 produce_video.py

Requirements:
    pip install moviepy pillow pyyaml

This creates a simplified first version for testing.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Check dependencies
try:
    from moviepy import (
        VideoClip, TextClip, CompositeVideoClip, AudioFileClip,
        ColorClip, concatenate_videoclips, ImageClip, CompositeAudioClip,
        vfx, afx
    )
    from PIL import Image, ImageDraw, ImageFont
    import yaml
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install moviepy pillow pyyaml")
    sys.exit(1)

try:
    from gtts import gTTS
    HAS_TTS = True
except ImportError:
    HAS_TTS = False
    print("Note: gTTS not available, no voiceover")

import tempfile
import numpy as np

# Configuration
VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720
FPS = 30
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
OUTPUT_DIR = Path(__file__).parent / "output"

# Colors (VT100 green theme)
BG_COLOR = (0, 0, 0)
TEXT_COLOR = (0, 255, 0)
THOUGHT_COLOR = (0, 200, 0)
TITLE_COLOR = (0, 255, 0)


def create_text_frame(text, font_size=24, color=TEXT_COLOR, bg=BG_COLOR):
    """Create a single frame with text."""
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), bg)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(FONT_PATH, font_size)
    except:
        font = ImageFont.load_default()

    # Center text
    bbox = draw.textbbox((0, 0), text, font=font)
    x = (VIDEO_WIDTH - bbox[2]) // 2
    y = (VIDEO_HEIGHT - bbox[3]) // 2
    draw.text((x, y), text, font=font, fill=color)

    return img


def create_terminal_frame(content, prompt=">? "):
    """Create a terminal-style frame."""
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(FONT_PATH, 20)
    except:
        font = ImageFont.load_default()

    # Draw terminal content
    y = 50
    for line in content.split('\n'):
        draw.text((50, y), line, font=font, fill=TEXT_COLOR)
        y += 24

    return img


def create_thought_bubble_frame(text, terminal_content=""):
    """Create a frame with terminal and thought bubble overlay."""
    img = create_terminal_frame(terminal_content)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(FONT_PATH, 18)
    except:
        font = ImageFont.load_default()

    # Draw thought bubble at bottom
    bubble_y = VIDEO_HEIGHT - 120
    bubble_padding = 20

    # Background for bubble
    draw.rectangle(
        [40, bubble_y - bubble_padding, VIDEO_WIDTH - 40, VIDEO_HEIGHT - 40],
        fill=(20, 40, 20),
        outline=THOUGHT_COLOR,
        width=2
    )

    # Thought bubble text
    bubble_text = f"💭 Claude: {text}"
    draw.text((60, bubble_y), bubble_text, font=font, fill=THOUGHT_COLOR)

    return img


def create_crawl_frame(text, offset, speed=30):
    """Create a Star Wars-style crawl frame."""
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(FONT_PATH, 20)
    except:
        font = ImageFont.load_default()

    # Calculate text position based on offset
    lines = text.strip().split('\n')
    y = VIDEO_HEIGHT - offset

    for line in lines:
        if 50 < y < VIDEO_HEIGHT - 50:  # Only draw visible lines
            # Center each line
            bbox = draw.textbbox((0, 0), line, font=font)
            x = (VIDEO_WIDTH - bbox[2]) // 2
            draw.text((x, y), line, font=font, fill=TITLE_COLOR)
        y += 28

    return img


def typing_effect_frames(text, duration_ms=3000, chars_per_frame=2):
    """Generate frames for typing effect."""
    frames = []
    total_frames = int((duration_ms / 1000) * FPS)

    for i in range(total_frames):
        char_index = min(len(text), int(i * len(text) / total_frames))
        partial_text = text[:char_index]
        if i % 10 < 5:  # Blinking cursor
            partial_text += "█"
        frames.append(partial_text)

    return frames


def generate_tts_audio(text, output_path):
    """Generate speech audio from text using gTTS."""
    if not HAS_TTS:
        return None
    try:
        # Clean text for speech (remove emojis, special chars)
        clean_text = text.replace("💭", "").replace("█", "").strip()
        # Add "Claude thinks:" prefix for context
        speech_text = f"Claude thinks: {clean_text}"

        tts = gTTS(text=speech_text, lang='en', slow=False)
        tts.save(str(output_path))
        return output_path
    except Exception as e:
        print(f"  ⚠ TTS error: {e}")
        return None


def create_thought_clip_with_audio(thought_text, terminal_content, duration, output_dir):
    """Create a thought bubble clip with optional TTS audio."""
    thought_img = create_thought_bubble_frame(thought_text, terminal_content)
    clip = ImageClip(np.array(thought_img)).with_duration(duration)

    if HAS_TTS:
        # Generate TTS audio
        audio_path = output_dir / f"thought_{hash(thought_text) & 0xffffffff}.mp3"
        if generate_tts_audio(thought_text, audio_path):
            try:
                voice_audio = AudioFileClip(str(audio_path))
                # Adjust clip duration to match audio if needed
                if voice_audio.duration > duration:
                    clip = clip.with_duration(voice_audio.duration + 0.5)
                clip = clip.with_audio(voice_audio)
                print(f"    ✓ Added TTS for: {thought_text[:40]}...")
            except Exception as e:
                print(f"    ⚠ Could not add TTS audio: {e}")

    return clip


def produce_simple_video():
    """Produce a simplified first version of the video."""
    print("=== ADVENT Video Production ===\n")

    OUTPUT_DIR.mkdir(exist_ok=True)

    scenes = []

    # Scene 1: Jasper's Quote (6 seconds)
    print("Creating Scene 1: Jasper's Quote...")
    quote = '''
"Wow! I have forgotten quite how dull
 early text based adventure games are 🙂"

                            — Jasper, 2026
'''
    quote_img = create_text_frame(quote, font_size=28, color=(200, 200, 200))
    quote_clip = ImageClip(np.array(quote_img)).with_duration(6)
    scenes.append(quote_clip)

    # Scene 2: Star Wars Crawl (30 seconds simplified)
    print("Creating Scene 2: Star Wars Crawl...")
    crawl_text = """
ADVENT
A Tale of Digital Archaeology

In the beginning, there was nothing.

Well, that's not quite true. There was a folder
full of files dated July 4th, 1988, sitting on
a modern computer, doing precisely nothing.

It was a multi-user dungeon game from 1986-7,
written by teenagers at Manchester Grammar School.

The source code came from a 9-track magnetic tape.

38 years later, an AI was summoned to make sense of it all...
"""

    def make_crawl_frame(t):
        offset = t * 50  # Pixels scrolled
        return create_crawl_frame(crawl_text, offset)

    crawl_clip = VideoClip(lambda t: np.array(make_crawl_frame(t)), duration=30).with_fps(FPS)
    scenes.append(crawl_clip)

    # Scene 3: Title Card (5 seconds)
    print("Creating Scene 3: Title Card...")
    title = """
ADVENT
A Multi-User Dungeon from 1986-7
Manchester Grammar School

Resurrected in 2025-6
Explored by Claude (AI)
"""
    title_img = create_text_frame(title, font_size=32)
    title_clip = ImageClip(np.array(title_img)).with_duration(5)
    scenes.append(title_clip)

    # Scene 4: Terminal Demo (20 seconds)
    print("Creating Scene 4: Terminal Demo...")
    terminal_content = """
No character loaded. Creating temporary character...
You are in dark desolate dismal room.

Exits :

    North
    East
    South
    West

You see:
    NEWDEN's corpse
>?
"""

    # Terminal without thought bubble
    term_img = create_terminal_frame(terminal_content)
    term_clip = ImageClip(np.array(term_img)).with_duration(3)
    scenes.append(term_clip)

    # Terminal with thought bubble + TTS - era-specific witty observations
    # Keep thoughts SHORT to avoid overlapping the bubble
    thought1 = "Dark desolate dismal. Someone's read too much Tolkien."
    thought_clip = create_thought_clip_with_audio(thought1, terminal_content, 4, OUTPUT_DIR)
    scenes.append(thought_clip)

    thought2 = "A corpse already? The web hadn't been invented. This was entertainment."
    thought_clip2 = create_thought_clip_with_audio(thought2, terminal_content, 5, OUTPUT_DIR)
    scenes.append(thought_clip2)

    # Scene 5: Combat Demo
    print("Creating Scene 5: Combat Demo...")
    combat_content = """
You are in the dojo. Those who do not bow before standing
on the mat will be executed immediately. A sign reads:
"FIGHT THE NINJA FOR GLORY AND A FEW XP".

Exits :

    North
    East
    South
    West

You see:
    A bo staff
    A ninja
>? HIT NINJA

First draw
>?
"""
    combat_thought = "A ninja in a dungeon. Tolkien meets Bruce Lee."
    combat_clip = create_thought_clip_with_audio(combat_thought, combat_content, 4, OUTPUT_DIR)
    scenes.append(combat_clip)

    combat_content2 = combat_content + """
>? DRAW PIG

Ok.
>? HIT NINJA

You did 10 points of damage and killed the ninja
>?
"""
    victory_thought = "Like communism, this game feels like it will last forever."
    victory_clip = create_thought_clip_with_audio(victory_thought, combat_content2, 5, OUTPUT_DIR)
    scenes.append(victory_clip)

    # Scene 6: The Bug
    print("Creating Scene 6: The Fatigue Bug...")
    bug_content = """
>? LOOK

You're too tired.
>? REST

You're too tired.
>? QUIT

You're too tired.
>?
"""
    bug_thought = "You can't do anything. Very Thatcher's Britain."
    bug_clip = create_thought_clip_with_audio(bug_thought, bug_content, 4, OUTPUT_DIR)
    scenes.append(bug_clip)

    # Scene 7: Credits (15 seconds)
    print("Creating Scene 7: Credits...")
    credits = """
═══════════════════════════════════════

ADVENT
A Multi-User Dungeon from 1986-7
Manchester Grammar School

═══════════════════════════════════════

ORIGINAL AUTHORS
Edward Hibbert (Code)
David 'Gerbil' Quest (Design & Text)

PRESERVATIONISTS
Nick Hoath • Delwyn Holroyd (TNMOC)

RESURRECTION TEAM (2025-6)
Edward Hibbert • Claude (AI)

═══════════════════════════════════════

"Wow! I have forgotten quite how dull
 early text based adventure games are 🙂"
                            — Jasper, 2026

═══════════════════════════════════════

SOURCE CODE
github.com/edwardhib/advent-pdp11

Made with 💾 in 2026

═══════════════════════════════════════
"""
    credits_img = create_text_frame(credits, font_size=20)
    credits_clip = ImageClip(np.array(credits_img)).with_duration(15)
    scenes.append(credits_clip)

    # Concatenate all scenes
    print("\nCompositing video...")
    final = concatenate_videoclips(scenes, method="compose")

    # Add audio
    print("Adding audio...")
    script_dir = Path(__file__).parent

    try:
        # Load background music
        ambient_path = script_dir / "music" / "dungeon_ambient.mp3"
        if ambient_path.exists():
            ambient = AudioFileClip(str(ambient_path))
            # Loop if needed and trim to video length
            if ambient.duration < final.duration:
                # Loop the ambient track
                loops_needed = int(final.duration / ambient.duration) + 1
                ambient = ambient.with_effects([afx.AudioLoop(nloops=loops_needed)])
            ambient = ambient.subclipped(0, final.duration)
            # Reduce volume
            ambient = ambient.with_volume_scaled(0.3)

            # Add fade in/out
            ambient = ambient.with_effects([
                afx.AudioFadeIn(2),
                afx.AudioFadeOut(3)
            ])

            final = final.with_audio(ambient)
            print("  ✓ Added background music")
        else:
            print("  ⚠ No background music found")

    except Exception as e:
        print(f"  ⚠ Audio error: {e}")
        print("  Continuing without audio...")

    # Write output (temp file first)
    temp_path = OUTPUT_DIR / "advent_demo_temp.mp4"
    output_path = OUTPUT_DIR / "advent_demo_v1.mp4"
    print(f"Writing to {temp_path}...")
    final.write_videofile(
        str(temp_path),
        fps=FPS,
        codec='libx264',
        audio_codec='aac',
        preset='medium',
        threads=4
    )

    # Re-encode with Windows-compatible audio using ffmpeg
    print(f"Re-encoding for Windows compatibility...")
    import subprocess
    subprocess.run([
        'ffmpeg', '-y', '-i', str(temp_path),
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
        '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-ac', '2',
        '-movflags', '+faststart',  # Move moov atom for streaming
        str(output_path)
    ], check=True, capture_output=True)

    # Clean up temp file
    temp_path.unlink()

    print(f"\n✅ Video created: {output_path}")
    print(f"   Duration: {final.duration:.1f} seconds")

    return output_path


if __name__ == '__main__':
    produce_simple_video()
