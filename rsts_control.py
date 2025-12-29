#!/usr/bin/env python3
"""Control RSTS/E via pexpect for reliable automation."""

import pexpect
import sys
import time

class RSTSControl:
    def __init__(self, host='localhost', port=2323, timeout=30):
        self.timeout = timeout
        self.child = pexpect.spawn(f'telnet {host} {port}', encoding='latin-1')
        self.child.logfile = sys.stdout

    def wait_prompt(self, prompt='$ ', timeout=None):
        """Wait for DCL prompt."""
        t = timeout or self.timeout
        try:
            self.child.expect(prompt, timeout=t)
            return True
        except pexpect.TIMEOUT:
            print(f"\n[TIMEOUT waiting for '{prompt}']")
            return False

    def send(self, cmd, wait=0.5):
        """Send command."""
        time.sleep(wait)
        self.child.sendline(cmd)

    def login(self, user='[1,2]', password='Digital1977'):
        """Login to RSTS/E."""
        print("\n=== Logging in ===")
        self.child.expect('Connected', timeout=10)
        time.sleep(1)
        self.send('')

        if self.child.expect(['User:', 'Password:', r'\$ '], timeout=15) == 2:
            print("\n[Already logged in]")
            return True

        self.send(user)
        self.child.expect('Password:', timeout=10)
        self.send(password)

        # Handle job number prompt or go straight to $
        idx = self.child.expect(['Job number', r'\$ '], timeout=15)
        if idx == 0:
            self.send('')
            self.wait_prompt()
        return True

    def cmd(self, command, expect_prompt=True, timeout=None):
        """Execute DCL command."""
        t = timeout or self.timeout
        self.send(command)
        if expect_prompt:
            self.wait_prompt(timeout=t)
        time.sleep(0.3)

    def basic_cmd(self, command, timeout=None):
        """Execute BASIC command, wait for BASIC2 prompt."""
        t = timeout or self.timeout
        self.send(command)
        try:
            self.child.expect('BASIC2', timeout=t)
        except pexpect.TIMEOUT:
            print(f"\n[TIMEOUT in BASIC]")
            return False
        return True

    def enter_basic(self):
        """Enter BASIC interpreter."""
        print("\n=== Entering BASIC ===")
        self.send('RUN $BP2IC2')
        self.child.expect('BASIC2', timeout=30)
        return True

    def exit_basic(self):
        """Exit BASIC interpreter."""
        self.send('EXIT')
        self.wait_prompt()

    def create_advent_dta(self):
        """Create ADVENT.DTA virtual array file with 2000 x 512 byte records."""
        print("\n=== Creating ADVENT.DTA ===")

        # Delete old file if exists
        self.cmd('DELETE/NOCONFIRM DM1:[1,2]ADVENT.DTA', timeout=10)

        self.enter_basic()

        # Create virtual array file
        self.basic_cmd('OPEN "DM1:[1,2]ADVENT.DTA" AS FILE #3%, ACCESS SCRATCH, ALLOW NONE')
        self.basic_cmd('DIM #3%, ROOM$(2000%)=512%')
        self.basic_cmd('ROOM$(0%)=STRING$(512%,0%)')
        self.basic_cmd('ROOM$(1999%)=STRING$(512%,0%)')
        self.basic_cmd('CLOSE #3%')

        self.exit_basic()
        print("\n=== ADVENT.DTA created ===")

    def create_data_files(self):
        """Create all required data files."""
        print("\n=== Creating all data files ===")

        # Delete old files
        for f in ['ADVENT.MON', 'ADVENT.CHR', 'BOARD.NTC', 'MESSAG.NPC']:
            self.cmd(f'DELETE/NOCONFIRM DM1:[1,2]{f}', timeout=5)

        self.enter_basic()

        # ADVENT.MON - 10000 records x 20 bytes
        print("\n--- Creating ADVENT.MON ---")
        self.basic_cmd('OPEN "DM1:[1,2]ADVENT.MON" AS FILE #5%, ACCESS SCRATCH, ALLOW NONE')
        self.basic_cmd('DIM #5%, MONSTER$(10000%)=20%')
        self.basic_cmd('MONSTER$(0%)=STRING$(20%,0%)')
        self.basic_cmd('MONSTER$(9999%)=STRING$(20%,0%)')
        self.basic_cmd('CLOSE #5%')

        # ADVENT.CHR - 100 records x 512 bytes
        print("\n--- Creating ADVENT.CHR ---")
        self.basic_cmd('OPEN "DM1:[1,2]ADVENT.CHR" AS FILE #7%, ACCESS SCRATCH, ALLOW NONE')
        self.basic_cmd('DIM #7%, CHARACTER$(100%)=512%')
        self.basic_cmd('CHARACTER$(0%)=STRING$(512%,0%)')
        self.basic_cmd('CHARACTER$(99%)=STRING$(512%,0%)')
        self.basic_cmd('CLOSE #7%')

        # BOARD.NTC - 512 records x 512 bytes
        print("\n--- Creating BOARD.NTC ---")
        self.basic_cmd('OPEN "DM1:[1,2]BOARD.NTC" AS FILE #6%, ACCESS SCRATCH, ALLOW NONE')
        self.basic_cmd('DIM #6%, INDEX%(511%), BOARD$(511%)=512%')
        self.basic_cmd('INDEX%(0%)=0%')
        self.basic_cmd('BOARD$(0%)=STRING$(512%,0%)')
        self.basic_cmd('CLOSE #6%')

        # MESSAG.NPC - 1000 records x 60 bytes
        print("\n--- Creating MESSAG.NPC ---")
        self.basic_cmd('OPEN "DM1:[1,2]MESSAG.NPC" AS FILE #9%, ACCESS SCRATCH, ALLOW NONE')
        self.basic_cmd('DIM #9%, NUM%(0%), SHOUT$(1000%)=60%')
        self.basic_cmd('NUM%(0%)=0%')
        self.basic_cmd('SHOUT$(0%)=STRING$(60%,0%)')
        self.basic_cmd('CLOSE #9%')

        self.exit_basic()
        print("\n=== All data files created ===")

    def verify_files(self):
        """List the data files."""
        print("\n=== Verifying files ===")
        self.cmd('DIR DM1:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC', timeout=10)

    def test_game(self):
        """Try to run the game."""
        print("\n=== Testing ADVENT ===")
        self.send('RUN DM1:[1,2]ADVENT')

        # Wait for game response or error
        idx = self.child.expect([
            'Welcome',
            '>',
            'Stop at',
            'Error',
            r'\?',
            pexpect.TIMEOUT
        ], timeout=30)

        if idx in [0, 1]:
            print("\n*** GAME STARTED! ***")
            return True
        else:
            print(f"\n*** Game failed (index {idx}) ***")
            return False

    def close(self):
        """Close connection."""
        self.child.close()


def main():
    print("=" * 50)
    print("RSTS/E Control Script")
    print("=" * 50)

    r = RSTSControl()

    try:
        r.login()

        # Create all data files
        r.create_advent_dta()
        r.create_data_files()
        r.verify_files()

        # Test the game
        r.test_game()

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        r.close()


if __name__ == '__main__':
    main()
