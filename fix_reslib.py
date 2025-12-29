#!/usr/bin/env python3
"""Fix RSTS/E resident library issue and create data files."""

import pexpect
import sys
import time

class RSTSControl:
    def __init__(self, host='localhost', port=2323, timeout=30):
        self.timeout = timeout
        self.child = pexpect.spawn(f'telnet {host} {port}', encoding='latin-1')
        self.child.logfile = sys.stdout

    def wait_for(self, pattern, timeout=None):
        """Wait for a pattern."""
        t = timeout or self.timeout
        try:
            self.child.expect(pattern, timeout=t)
            return True
        except pexpect.TIMEOUT:
            print(f"\n[TIMEOUT waiting for '{pattern}']")
            return False

    def send(self, cmd, wait=0.3):
        """Send command."""
        time.sleep(wait)
        self.child.sendline(cmd)

    def login(self, user='[1,2]', password='Digital1977'):
        """Login to RSTS/E."""
        print("\n=== Logging in ===")
        self.wait_for('Connected', timeout=10)
        time.sleep(1)
        self.send('')

        idx = self.child.expect(['User:', 'Password:', r'\$ ', 'Job number'], timeout=15)
        if idx == 2:
            print("\n[Already at $ prompt]")
            return True
        if idx == 3:
            # Already logged in, detach from previous job
            self.send('')
            self.wait_for(r'\$ ')
            return True

        # At User: prompt
        if idx == 0:
            self.send(user)
            self.wait_for('Password:', timeout=10)

        self.send(password)

        # Handle job number prompt or go straight to $
        idx = self.child.expect(['Job number', r'\$ '], timeout=15)
        if idx == 0:
            self.send('')  # Start new job
            self.wait_for(r'\$ ')
        return True

    def cmd(self, command, timeout=None):
        """Execute DCL command and wait for prompt."""
        t = timeout or self.timeout
        self.send(command)
        self.wait_for(r'\$ ', timeout=t)
        time.sleep(0.2)

    def check_reslib(self):
        """Check resident library status."""
        print("\n=== Checking Resident Libraries ===")
        self.cmd('SYSTAT/RESIDENT', timeout=10)
        self.cmd('DIRECTORY SY:[0,1]BP2*.LIB', timeout=10)
        self.cmd('DIRECTORY SY:[0,1]*.LIB', timeout=10)

    def install_reslib(self):
        """Try to install BP2 resident library."""
        print("\n=== Installing BP2 Resident Library ===")
        # Try running UTLMGR to install
        self.send('RUN $UTLMGR')
        idx = self.child.expect(['Utlmgr>', r'\$ ', 'error', pexpect.TIMEOUT], timeout=10)
        if idx == 0:
            self.send('INSTALL/RUNTIME BP2RES')
            self.child.expect(['Utlmgr>', r'\$ '], timeout=10)
            self.send('EXIT')
            self.wait_for(r'\$ ')
        else:
            print("\n[Could not start UTLMGR]")

    def test_basic_open(self):
        """Test if BASIC can open files."""
        print("\n=== Testing BASIC File I/O ===")
        self.send('RUN $BP2IC2')
        idx = self.child.expect(['BASIC2', r'\$ ', pexpect.TIMEOUT], timeout=15)
        if idx != 0:
            print("\n[Could not start BASIC]")
            return False

        # Try a simple file operation
        self.send('OPEN "DM1:[1,2]TEST.TMP" FOR OUTPUT AS FILE #1%')
        idx = self.child.expect(['BASIC2', 'Unable to attach', 'error', r'\$ '], timeout=10)
        if idx == 1:
            print("\n*** RESIDENT LIBRARY ERROR STILL PRESENT ***")
            self.wait_for(r'\$ ')
            return False
        elif idx == 0:
            print("\n*** FILE OPEN SUCCEEDED! ***")
            self.send('PRINT #1%, "TEST"')
            self.child.expect('BASIC2', timeout=5)
            self.send('CLOSE #1%')
            self.child.expect('BASIC2', timeout=5)
            self.send('EXIT')
            self.wait_for(r'\$ ')
            self.cmd('DELETE/NOCONFIRM DM1:[1,2]TEST.TMP')
            return True
        else:
            print("\n*** UNKNOWN ERROR ***")
            self.wait_for(r'\$ ', timeout=5)
            return False

    def create_data_files(self):
        """Create the game data files."""
        print("\n=== Creating Game Data Files ===")

        # Delete old files
        for f in ['ADVENT.DTA', 'ADVENT.MON', 'ADVENT.CHR', 'BOARD.NTC', 'MESSAG.NPC']:
            self.cmd(f'DELETE/NOCONFIRM DM1:[1,2]{f}', timeout=5)

        self.send('RUN $BP2IC2')
        if not self.wait_for('BASIC2', timeout=15):
            return False

        # ADVENT.DTA - 2000 records x 512 bytes
        print("\n--- Creating ADVENT.DTA ---")
        self.send('OPEN "DM1:[1,2]ADVENT.DTA" AS FILE #3%, ACCESS SCRATCH, ALLOW NONE')
        if not self.wait_for('BASIC2', timeout=30):
            return False
        self.send('DIM #3%, ROOM$(2000%)=512%')
        self.wait_for('BASIC2', timeout=30)
        self.send('ROOM$(0%)=STRING$(512%,0%)')
        self.wait_for('BASIC2', timeout=10)
        self.send('ROOM$(1999%)=STRING$(512%,0%)')
        self.wait_for('BASIC2', timeout=10)
        self.send('CLOSE #3%')
        self.wait_for('BASIC2', timeout=10)

        # ADVENT.MON - 10000 records x 20 bytes
        print("\n--- Creating ADVENT.MON ---")
        self.send('OPEN "DM1:[1,2]ADVENT.MON" AS FILE #5%, ACCESS SCRATCH, ALLOW NONE')
        self.wait_for('BASIC2', timeout=30)
        self.send('DIM #5%, MONSTER$(10000%)=20%')
        self.wait_for('BASIC2', timeout=30)
        self.send('MONSTER$(0%)=STRING$(20%,0%)')
        self.wait_for('BASIC2', timeout=10)
        self.send('MONSTER$(9999%)=STRING$(20%,0%)')
        self.wait_for('BASIC2', timeout=10)
        self.send('CLOSE #5%')
        self.wait_for('BASIC2', timeout=10)

        # ADVENT.CHR - 100 records x 512 bytes
        print("\n--- Creating ADVENT.CHR ---")
        self.send('OPEN "DM1:[1,2]ADVENT.CHR" AS FILE #7%, ACCESS SCRATCH, ALLOW NONE')
        self.wait_for('BASIC2', timeout=30)
        self.send('DIM #7%, CHARACTER$(100%)=512%')
        self.wait_for('BASIC2', timeout=30)
        self.send('CHARACTER$(0%)=STRING$(512%,0%)')
        self.wait_for('BASIC2', timeout=10)
        self.send('CHARACTER$(99%)=STRING$(512%,0%)')
        self.wait_for('BASIC2', timeout=10)
        self.send('CLOSE #7%')
        self.wait_for('BASIC2', timeout=10)

        # BOARD.NTC - 512 records x 512 bytes
        print("\n--- Creating BOARD.NTC ---")
        self.send('OPEN "DM1:[1,2]BOARD.NTC" AS FILE #6%, ACCESS SCRATCH, ALLOW NONE')
        self.wait_for('BASIC2', timeout=30)
        self.send('DIM #6%, INDEX%(511%), BOARD$(511%)=512%')
        self.wait_for('BASIC2', timeout=30)
        self.send('INDEX%(0%)=0%')
        self.wait_for('BASIC2', timeout=10)
        self.send('BOARD$(0%)=STRING$(512%,0%)')
        self.wait_for('BASIC2', timeout=10)
        self.send('CLOSE #6%')
        self.wait_for('BASIC2', timeout=10)

        # MESSAG.NPC - 1000 records x 60 bytes
        print("\n--- Creating MESSAG.NPC ---")
        self.send('OPEN "DM1:[1,2]MESSAG.NPC" AS FILE #9%, ACCESS SCRATCH, ALLOW NONE')
        self.wait_for('BASIC2', timeout=30)
        self.send('DIM #9%, NUM%(0%), SHOUT$(1000%)=60%')
        self.wait_for('BASIC2', timeout=30)
        self.send('NUM%(0%)=0%')
        self.wait_for('BASIC2', timeout=10)
        self.send('SHOUT$(0%)=STRING$(60%,0%)')
        self.wait_for('BASIC2', timeout=10)
        self.send('CLOSE #9%')
        self.wait_for('BASIC2', timeout=10)

        self.send('EXIT')
        self.wait_for(r'\$ ')
        print("\n=== All data files created ===")
        return True

    def verify_files(self):
        """List the data files."""
        print("\n=== Verifying files ===")
        self.cmd('DIR/FULL DM1:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC', timeout=15)

    def test_game(self):
        """Try to run the game."""
        print("\n=== Testing ADVENT ===")
        self.send('RUN DM1:[1,2]ADVENT')

        idx = self.child.expect([
            'Welcome',
            '>',
            'Stop at',
            'Error',
            r'\?',
            r'\$ ',
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
    print("=" * 60)
    print("RSTS/E Resident Library Fix and Data File Creation")
    print("=" * 60)

    r = RSTSControl()

    try:
        r.login()
        r.check_reslib()
        r.install_reslib()

        if r.test_basic_open():
            print("\n*** BASIC file I/O working! ***")
            r.create_data_files()
            r.verify_files()
            r.test_game()
        else:
            print("\n*** BASIC file I/O still broken ***")
            print("The resident library issue needs manual investigation.")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        r.close()


if __name__ == '__main__':
    main()
