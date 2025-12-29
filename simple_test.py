#!/usr/bin/env python3
"""Create minimal test data and run Advent game."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Creating Minimal Test Data for Advent")
    print("=" * 60)

    child = pexpect.spawn('telnet localhost 2323', encoding='latin-1')
    child.logfile = sys.stdout

    # Wait for connection
    child.expect('Connected to the PDP-11', timeout=10)
    time.sleep(2)
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
        child.sendline('')
    child.expect(r'\$ ', timeout=15)

    # Delete old files
    print("\n=== Deleting old files ===")
    for f in ['ADVENT.DTA', 'ADVENT.MON', 'ADVENT.CHR', 'BOARD.NTC', 'MESSAG.NPC', 'T.TMP']:
        child.sendline(f'DELETE/NOCONFIRM DM1:[1,2]{f}')
        child.expect(r'\$ ', timeout=5)
        time.sleep(0.3)

    print("\n=== Starting BASIC ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    def basic_cmd(cmd, timeout=30):
        child.sendline(cmd)
        idx = child.expect(['BASIC2', r'\?', r'\$ '], timeout=timeout)
        time.sleep(0.2)
        return idx == 0

    # Create ADVENT.DTA with a few test rooms
    print("\n--- Creating ADVENT.DTA with test room ---")
    basic_cmd('OPEN "DM1:[1,2]ADVENT.DTA" AS FILE #3%, ACCESS SCRATCH, ALLOW NONE', 60)
    basic_cmd('DIM #3%, ROOM$(2000%)=512%', 60)

    # Write a simple room record - record structure:
    # Byte 0: room number verification (1 byte as CHR$)
    # Bytes 1-16: exits (16 chars) - N####S####E####W####
    # Bytes 17-99: people/monsters (83 chars)
    # Bytes 100-199: objects (100 chars)
    # Bytes 200-511: description (312 chars)

    # Room 1 - starting room
    room1 = 'CHR$(1%) + "N0000S0000E0002W0000" + SPACE$(67%) + SPACE$(100%) + "You are in a small cave. Light filters in from the east." + SPACE$(256%)'
    basic_cmd(f'ROOM$(1%) = {room1}')

    # Room 2
    room2 = 'CHR$(2%) + "N0000S0000E0000W0001" + SPACE$(67%) + SPACE$(100%) + "A larger chamber opens before you. The walls glitter with crystals." + SPACE$(245%)'
    basic_cmd(f'ROOM$(2%) = {room2}')

    basic_cmd('CLOSE #3%')
    print("    ADVENT.DTA created with test rooms")

    # Create empty ADVENT.MON
    print("\n--- Creating ADVENT.MON ---")
    basic_cmd('OPEN "DM1:[1,2]ADVENT.MON" AS FILE #5%, ACCESS SCRATCH, ALLOW NONE', 60)
    basic_cmd('DIM #5%, MONSTER$(10000%)=20%', 60)
    basic_cmd('CLOSE #5%')

    # Create empty ADVENT.CHR
    print("\n--- Creating ADVENT.CHR ---")
    basic_cmd('OPEN "DM1:[1,2]ADVENT.CHR" AS FILE #7%, ACCESS SCRATCH, ALLOW NONE', 60)
    basic_cmd('DIM #7%, CHARACTER$(100%)=512%', 60)
    basic_cmd('CLOSE #7%')

    # Create empty BOARD.NTC
    print("\n--- Creating BOARD.NTC ---")
    basic_cmd('OPEN "DM1:[1,2]BOARD.NTC" AS FILE #6%, ACCESS SCRATCH, ALLOW NONE', 60)
    basic_cmd('DIM #6%, INDEX%(511%), BOARD$(511%)=512%', 60)
    basic_cmd('INDEX%(0%)=0%')
    basic_cmd('CLOSE #6%')

    # Create empty MESSAG.NPC
    print("\n--- Creating MESSAG.NPC ---")
    basic_cmd('OPEN "DM1:[1,2]MESSAG.NPC" AS FILE #9%, ACCESS SCRATCH, ALLOW NONE', 60)
    basic_cmd('DIM #9%, NUM%(0%), SHOUT$(1000%)=60%', 60)
    basic_cmd('NUM%(0%)=0%')
    basic_cmd('CLOSE #9%')

    child.sendline('EXIT')
    child.expect(r'\$ ', timeout=10)

    # Verify files
    print("\n=== Verifying files ===")
    child.sendline('DIR/SIZE DM1:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC')
    child.expect(r'\$ ', timeout=15)

    # Run game
    print("\n" + "=" * 60)
    print("TESTING ADVENT GAME")
    print("=" * 60)
    child.sendline('RUN DM1:[1,2]ADVENT')

    # Wait longer for game
    idx = child.expect([
        'Welcome',
        '>',
        'INITIALIZING',
        'What is your',
        'name',
        'Stop at',
        r'\?',
        r'\$ ',
        pexpect.TIMEOUT
    ], timeout=90)

    print(f"\n*** Got response index {idx} ***")

    if idx in [0, 1, 2, 3, 4]:
        print("\n*** GAME IS STARTING! ***")
        # Send a name
        time.sleep(2)
        child.sendline('TEST')
        time.sleep(3)
    elif idx == 5:
        print("\n*** STOPPED WITH ERROR ***")
    else:
        print("\n*** TIMEOUT OR OTHER ***")

    # Wait and capture output
    time.sleep(5)
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)

if __name__ == '__main__':
    main()
