#!/usr/bin/env python3
"""
Advent MUD Connection Script

A reliable pexpect-based script to connect to RSTS/E and run the game.
Works from inside the Docker container or externally.

Usage:
    ./connect.py              # Connect interactively
    ./connect.py --test       # Run test sequence
    ./connect.py --compile    # Compile and build game
"""

import pexpect
import sys
import time
import argparse


class RSTSConnection:
    """Manage connection to RSTS/E via telnet."""

    def __init__(self, host='localhost', port=2323, timeout=30, verbose=True):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.verbose = verbose
        self.child = None

    def log(self, msg):
        if self.verbose:
            print(f"[*] {msg}")

    def connect(self):
        """Establish telnet connection to RSTS/E terminal."""
        self.log(f"Connecting to {self.host}:{self.port}...")
        self.child = pexpect.spawn(
            f'nc {self.host} {self.port}',
            encoding='latin-1',
            timeout=self.timeout
        )
        if self.verbose:
            self.child.logfile = sys.stdout
        time.sleep(1)
        return True

    def send(self, text, delay=0.5):
        """Send text with optional delay."""
        time.sleep(delay)
        self.child.sendline(text)

    def expect(self, pattern, timeout=None):
        """Wait for pattern."""
        t = timeout or self.timeout
        try:
            return self.child.expect(pattern, timeout=t)
        except pexpect.TIMEOUT:
            self.log(f"TIMEOUT waiting for: {pattern}")
            return -1
        except pexpect.EOF:
            self.log("Connection closed")
            return -1

    def login(self, user='[1,2]', password='Digital1977'):
        """Login to RSTS/E."""
        self.log("Logging in...")

        # Send a CR to wake up the terminal
        self.send('')
        time.sleep(1)

        # Check current state
        idx = self.expect(['User:', 'Password:', r'\$ ', 'Ready', 'Job'], timeout=10)

        if idx == 2 or idx == 3:
            # Already logged in
            self.log("Already logged in")
            return True

        if idx == 0:
            # At User: prompt
            self.send(user)
        elif idx == 4:
            # At Job number prompt, press enter
            self.send('')
            self.expect(r'\$ ')
            return True
        else:
            # Try HELLO
            self.send(f'HELLO {user}')
            self.expect('Password:', timeout=10)

        # Enter password
        self.send(password)

        # Handle job number or command prompt
        idx = self.expect(['Job', r'\$ ', 'Ready'], timeout=15)
        if idx == 0:
            self.send('')  # Accept default job
            self.expect(r'\$ ')

        self.log("Logged in successfully")
        return True

    def run_command(self, cmd, wait_prompt=True, timeout=None):
        """Execute a DCL command."""
        self.send(cmd)
        if wait_prompt:
            self.expect(r'\$ ', timeout=timeout or self.timeout)

    def run_game(self):
        """Start the Advent game."""
        self.log("Starting Advent game...")
        self.send('RUN DM1:[1,2]ADVENT')

        # Wait for game to start
        idx = self.expect(['Welcome', '>', 'Error', r'\?', 'Stop'], timeout=30)

        if idx in [0, 1]:
            self.log("Game started successfully!")
            return True
        else:
            self.log("Game failed to start")
            return False

    def test_game(self):
        """Run a test sequence on the game."""
        self.log("Testing game...")

        # Send LOOK command
        self.send('LOOK')
        time.sleep(2)

        # Send NORTH command
        self.send('NORTH')
        time.sleep(2)

        # Send QUIT
        self.send('QUIT')
        time.sleep(2)

        self.log("Test sequence complete")
        return True

    def compile_game(self):
        """Compile and build the game."""
        self.log("Compiling game (this takes a while)...")

        # Enter BASIC-PLUS-2 compiler
        self.send('RUN $BP2IC2')
        self.expect('BASIC2', timeout=60)

        modules = [
            'ADVINI.SUB', 'ADVOUT.SUB', 'ADVNOR.SUB', 'ADVCMD.SUB',
            'ADVODD.SUB', 'ADVMSG.SUB', 'ADVBYE.SUB', 'ADVSHT.SUB',
            'ADVNPC.SUB', 'ADVPUZ.SUB', 'ADVDSP.SUB', 'ADVFND.SUB',
            'ADVTDY.SUB', 'ADVENT.B2S'
        ]

        for module in modules:
            self.log(f"Compiling {module}...")
            self.send(f'OLD DM1:[1,3]{module}')
            self.expect('BASIC2', timeout=30)
            self.send('SET NOWARNING')
            self.expect('BASIC2', timeout=10)
            self.send('COMPILE')
            idx = self.expect(['BASIC2', 'Error'], timeout=120)
            if idx != 0:
                self.log(f"Compilation failed for {module}")
                return False

        # Build executable
        self.log("Building executable...")
        self.send('BUILD ADVENT=ADVENT,ADVINI,ADVOUT,ADVNOR,ADVCMD,ADVODD,'
                  'ADVMSG,ADVBYE,ADVSHT,ADVNPC,ADVPUZ,ADVDSP,ADVFND,ADVTDY')
        self.expect('BASIC2', timeout=300)

        # Exit BASIC
        self.send('EXIT')
        self.expect(r'\$ ', timeout=30)

        self.log("Compilation complete!")
        return True

    def interactive(self):
        """Hand over to interactive mode."""
        self.log("Entering interactive mode (Ctrl+] to exit)")
        self.child.interact()

    def close(self):
        """Close connection."""
        if self.child:
            self.child.close()


def main():
    parser = argparse.ArgumentParser(description='Advent MUD Connection Script')
    parser.add_argument('--host', default='localhost', help='RSTS/E host')
    parser.add_argument('--port', type=int, default=2323, help='Terminal port')
    parser.add_argument('--test', action='store_true', help='Run test sequence')
    parser.add_argument('--compile', action='store_true', help='Compile game')
    parser.add_argument('--quiet', action='store_true', help='Less verbose')
    args = parser.parse_args()

    conn = RSTSConnection(
        host=args.host,
        port=args.port,
        verbose=not args.quiet
    )

    try:
        conn.connect()
        conn.login()

        if args.compile:
            success = conn.compile_game()
            return 0 if success else 1

        if args.test:
            conn.run_game()
            conn.test_game()
            return 0

        # Default: run game and go interactive
        conn.run_game()
        conn.interactive()

    except KeyboardInterrupt:
        print("\nInterrupted")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        conn.close()

    return 0


if __name__ == '__main__':
    sys.exit(main())
