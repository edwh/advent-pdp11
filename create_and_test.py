#!/usr/bin/env python3
"""Create all data files and test the Advent game."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Creating Data Files and Testing Advent")
    print("=" * 60)

    child = pexpect.spawn('telnet localhost 2323', encoding='latin-1')
    child.logfile = sys.stdout

    # Wait for connection
    child.expect('Connected to the PDP-11', timeout=10)
    time.sleep(2)

    # Send carriage returns to wake up terminal
    child.sendline('')
    time.sleep(1)
    child.sendline('')
    time.sleep(1)

    # Login
    idx = child.expect(['User:', r'\$ ', 'Job number'], timeout=20)
    if idx == 0:
        child.sendline('[1,2]')
        child.expect('Password:', timeout=10)
        child.sendline('Digital1977')
    if idx == 2 or child.expect(['Job number', r'\$ '], timeout=15) == 0:
        child.sendline('')  # New job
    child.expect(r'\$ ', timeout=15)

    print("\n=== Deleting old data files ===")
    for f in ['ADVENT.DTA', 'ADVENT.MON', 'ADVENT.CHR', 'BOARD.NTC', 'MESSAG.NPC']:
        child.sendline(f'DELETE/NOCONFIRM DM1:[1,2]{f}')
        child.expect(r'\$ ', timeout=10)
        time.sleep(0.5)

    print("\n=== Starting BASIC to create files ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    def basic_cmd(cmd, timeout=30):
        child.sendline(cmd)
        child.expect('BASIC2', timeout=timeout)
        time.sleep(0.3)

    # ADVENT.DTA - 2000 records x 512 bytes
    print("\n--- Creating ADVENT.DTA (2000 x 512 bytes) ---")
    basic_cmd('OPEN "DM1:[1,2]ADVENT.DTA" AS FILE #3%, ACCESS SCRATCH, ALLOW NONE', 60)
    basic_cmd('DIM #3%, ROOM$(2000%)=512%', 60)
    basic_cmd('ROOM$(0%)=STRING$(512%,0%)')
    basic_cmd('ROOM$(1999%)=STRING$(512%,0%)')
    basic_cmd('CLOSE #3%')
    print("    ADVENT.DTA created")

    # ADVENT.MON - 10000 records x 20 bytes
    print("\n--- Creating ADVENT.MON (10000 x 20 bytes) ---")
    basic_cmd('OPEN "DM1:[1,2]ADVENT.MON" AS FILE #5%, ACCESS SCRATCH, ALLOW NONE', 60)
    basic_cmd('DIM #5%, MONSTER$(10000%)=20%', 60)
    basic_cmd('MONSTER$(0%)=STRING$(20%,0%)')
    basic_cmd('MONSTER$(9999%)=STRING$(20%,0%)')
    basic_cmd('CLOSE #5%')
    print("    ADVENT.MON created")

    # ADVENT.CHR - 100 records x 512 bytes
    print("\n--- Creating ADVENT.CHR (100 x 512 bytes) ---")
    basic_cmd('OPEN "DM1:[1,2]ADVENT.CHR" AS FILE #7%, ACCESS SCRATCH, ALLOW NONE', 60)
    basic_cmd('DIM #7%, CHARACTER$(100%)=512%', 60)
    basic_cmd('CHARACTER$(0%)=STRING$(512%,0%)')
    basic_cmd('CHARACTER$(99%)=STRING$(512%,0%)')
    basic_cmd('CLOSE #7%')
    print("    ADVENT.CHR created")

    # BOARD.NTC - 512 records x 512 bytes
    print("\n--- Creating BOARD.NTC (512 x 512 bytes) ---")
    basic_cmd('OPEN "DM1:[1,2]BOARD.NTC" AS FILE #6%, ACCESS SCRATCH, ALLOW NONE', 60)
    basic_cmd('DIM #6%, INDEX%(511%), BOARD$(511%)=512%', 60)
    basic_cmd('INDEX%(0%)=0%')
    basic_cmd('BOARD$(0%)=STRING$(512%,0%)')
    basic_cmd('CLOSE #6%')
    print("    BOARD.NTC created")

    # MESSAG.NPC - 1000 records x 60 bytes
    print("\n--- Creating MESSAG.NPC (1000 x 60 bytes) ---")
    basic_cmd('OPEN "DM1:[1,2]MESSAG.NPC" AS FILE #9%, ACCESS SCRATCH, ALLOW NONE', 60)
    basic_cmd('DIM #9%, NUM%(0%), SHOUT$(1000%)=60%', 60)
    basic_cmd('NUM%(0%)=0%')
    basic_cmd('SHOUT$(0%)=STRING$(60%,0%)')
    basic_cmd('CLOSE #9%')
    print("    MESSAG.NPC created")

    child.sendline('EXIT')
    child.expect(r'\$ ', timeout=10)

    print("\n=== Verifying files ===")
    child.sendline('DIR DM1:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC')
    child.expect(r'\$ ', timeout=15)

    print("\n" + "=" * 60)
    print("TESTING ADVENT GAME")
    print("=" * 60)
    child.sendline('RUN DM1:[1,2]ADVENT')

    # Wait for game response
    idx = child.expect([
        'Welcome',
        '>',
        'INITIALIZING',
        'Stop at',
        r'\?',
        r'\$ ',
        pexpect.TIMEOUT
    ], timeout=60)

    if idx == 0:
        print("\n*** GOT WELCOME MESSAGE! ***")
    elif idx == 1:
        print("\n*** GOT GAME PROMPT! ***")
    elif idx == 2:
        print("\n*** GAME IS INITIALIZING! ***")
        # Wait for more
        idx2 = child.expect(['Welcome', '>', pexpect.TIMEOUT], timeout=30)
        if idx2 in [0, 1]:
            print("\n*** GAME STARTED SUCCESSFULLY! ***")
    elif idx == 3:
        print("\n*** GAME STOPPED - Error ***")
    elif idx == 4:
        print("\n*** GAME ERROR ***")
    elif idx == 5:
        print("\n*** RETURNED TO PROMPT ***")
    else:
        print("\n*** TIMEOUT ***")

    # Give it a moment
    time.sleep(2)

    # Try a command
    child.sendline('LOOK')
    time.sleep(3)
    print("\n=== Final output ===")

    child.close()
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)

if __name__ == '__main__':
    main()
