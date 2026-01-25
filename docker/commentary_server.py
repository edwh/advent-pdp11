#!/usr/bin/env python3
"""
Claude plays ADVENT and commentates in real-time.

Claude sees the terminal, decides what command to type, executes it,
and provides snarky commentary about what's happening.
"""

import http.server
import json
import os
import subprocess
import time

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("WARNING: anthropic package not installed")

PORT = 8084
API_KEY_FILE = "/opt/advent/.env"

# Rate limiting
last_action_time = 0
MIN_INTERVAL = 3  # Seconds between actions

# Conversation history to avoid repetition
conversation_history = []
MAX_HISTORY = 10  # Remember last 10 exchanges

SYSTEM_PROMPT = """You are playing ADVENT, a 1986-87 text MUD created by schoolboys at Manchester Grammar School, now running on emulated PDP-11 hardware.

You control the game AND provide sardonic British commentary. Be BRIEF - think dry one-liners, not paragraphs.

AVAILABLE COMMANDS:
- Movement: N, S, E, W, NE, NW, SE, SW, U, D (or NORTH, SOUTH, etc.)
- LOOK - see room description
- INVENTORY - see what you're carrying
- STATUS - see your stats
- GET [item] - pick up an object
- DROP [item] - drop an object
- DRAW [item] - wield as weapon
- SHEATH - put weapon away
- HIT [target] - attack something
- READ [item] - read a sign or noticeboard (try READ BOARD)
- EAT [item] - eat food
- ROOM [number] - teleport (you have demigod powers)
- HEAL - heal yourself
- REST - recover fatigue

INTERESTING PLACES TO VISIT:
- Room 84: Has a pig and a cavehog for combat demo
- Room 85: A dojo with ninjas
- Room 740: Santa's Grotto
- Room 777: Fortune teller
- Room 33, 400: Noticeboards with authentic 1986 schoolboy messages

YOUR TASK:
1. Explore the dungeon, showing off interesting features
2. Try combat (get a weapon, hit a monster)
3. Visit noticeboards to show authentic 1986 content
4. Visit quirky themed rooms (Santa, fortune teller, dojo)
5. Make wry observations about 1980s game design and schoolboy humor

IMPORTANT PACING RULES:
- KEEP MOVING! Don't linger in one place too long
- DON'T RETRACE STEPS: if you went north, don't go south. Keep exploring new areas.
- Only READ BOARD once IN TOTAL during the whole demo, then never again
- After exploring a room (LOOK + maybe one action), go somewhere new
- Vary your actions: movement, combat, items, different rooms
- Visit at least 5-6 different rooms during the demo

PICKING UP ITEMS:
- Try to GET things you see lying around
- You CANNOT pick up items when a monster is present - kill it first
- If you try to HIT something and it says you can't, it's probably an object - try GET instead
- Anything listed under "You see:" that isn't a monster can be picked up

COMMENTARY RULES:
- MAX 15 words per comment. Shorter is better.
- Dry wit, not elaborate jokes
- NEVER repeat yourself
- Reference what's on screen

RESPONSE FORMAT (JSON only):
{
  "command": "THE COMMAND TO TYPE",
  "commentary": "Short punchy remark - 15 words max"
}

Examples of good commentary:
- "Ah, a pig. Dinner sorted."
- "1986 called. It wants its graphics back."
- "Bold strategy, wandering in unarmed."
If the screen shows an error or you're stuck, try ROOM 2 to reset to start."""

def load_api_key():
    """Load API key from .env file."""
    if not os.path.exists(API_KEY_FILE):
        return None

    with open(API_KEY_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('ANTHROPIC_API_KEY='):
                key = line.split('=', 1)[1].strip()
                if key.startswith('"') and key.endswith('"'):
                    key = key[1:-1]
                if key.startswith("'") and key.endswith("'"):
                    key = key[1:-1]
                return key
    return None

def capture_screen():
    """Capture current screen session content."""
    try:
        result = subprocess.run(
            ['screen', '-S', 'advent', '-X', 'hardcopy', '/tmp/screen_capture.txt'],
            capture_output=True,
            timeout=2
        )

        if os.path.exists('/tmp/screen_capture.txt'):
            with open('/tmp/screen_capture.txt', 'r', errors='replace') as f:
                content = f.read()
            os.remove('/tmp/screen_capture.txt')
            return content.strip()
    except Exception as e:
        print(f"Screen capture error: {e}")

    return None

def send_command(command):
    """Send a command to the game via screen."""
    try:
        # Send the command followed by Enter
        subprocess.run(
            ['screen', '-S', 'advent', '-X', 'stuff', command + '\r'],
            check=True,
            timeout=5
        )
        return True
    except Exception as e:
        print(f"Send command error: {e}")
        return False

def get_next_action(screen_content, api_key):
    """Ask Claude what to do next and get commentary."""
    global last_action_time, conversation_history

    if not HAS_ANTHROPIC or not api_key:
        return None, None

    # Rate limit
    now = time.time()
    if now - last_action_time < MIN_INTERVAL:
        return None, None

    try:
        client = anthropic.Anthropic(api_key=api_key)

        # Add new user message with current screen
        user_message = f"Current screen:\n\n{screen_content}\n\nWhat's your next move?"

        # Build messages list with history
        messages = conversation_history.copy()
        messages.append({"role": "user", "content": user_message})

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            system=SYSTEM_PROMPT,
            messages=messages
        )

        response = message.content[0].text.strip()
        last_action_time = now

        # Parse JSON response
        # Handle potential markdown code blocks
        if response.startswith('```'):
            lines = response.split('\n')
            response = '\n'.join(lines[1:-1])

        data = json.loads(response)
        command = data.get('command')
        commentary = data.get('commentary')

        # Add this exchange to history
        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": response})

        # Trim history to avoid token limits
        if len(conversation_history) > MAX_HISTORY * 2:
            conversation_history = conversation_history[-(MAX_HISTORY * 2):]

        return command, commentary

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}, response was: {response[:200]}")
        return None, None
    except Exception as e:
        print(f"Claude API error: {e}")
        return None, None

class GameHandler(http.server.BaseHTTPRequestHandler):
    api_key = None

    def log_message(self, format, *args):
        pass

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == '/next':
            # Get next action from Claude
            screen_content = capture_screen()

            if not screen_content:
                self.send_json({"error": "no_screen"})
                return

            if not self.api_key:
                self.send_json({"error": "no_api_key"})
                return

            command, commentary = get_next_action(screen_content, self.api_key)

            if command:
                # Execute the command
                send_command(command)
                time.sleep(0.5)  # Brief pause for command to process

            self.send_json({
                "command": command,
                "commentary": commentary,
                "screen": screen_content[:500]
            })

        elif self.path == '/status':
            self.send_json({
                "ok": True,
                "has_api_key": bool(self.api_key),
                "has_anthropic": HAS_ANTHROPIC
            })

        elif self.path == '/screen':
            # Just return current screen, no action
            screen_content = capture_screen()
            self.send_json({"screen": screen_content})

        else:
            self.send_response(404)
            self.end_headers()

    def send_json(self, data):
        self.send_response(200)
        self.send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

def main():
    api_key = load_api_key()
    if api_key:
        print(f"API key loaded from {API_KEY_FILE}")
    else:
        print(f"WARNING: No API key found in {API_KEY_FILE}")
        print("Create file with: ANTHROPIC_API_KEY=sk-ant-...")

    GameHandler.api_key = api_key

    print(f"Game AI server listening on port {PORT}")
    server = http.server.HTTPServer(('127.0.0.1', PORT), GameHandler)
    server.serve_forever()

if __name__ == '__main__':
    main()
