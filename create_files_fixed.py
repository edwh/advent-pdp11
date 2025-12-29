#!/usr/bin/env python3
"""Create data files on DM1: with explicit paths."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Creating Data Files (Fixed Device Paths)")
    print("=" * 60)

    child = pexpect.spawn('telnet localhost 2323', encoding='latin-1')
    child.logfile = sys.stdout

    child.expect('Connected to the PDP-11', timeout=10)
    time.sleep(2)
    child.sendline('')
    time.sleep(1)
    child.sendline('')
    time.sleep(1)

    idx = child.expect(['User:', r'\$ ', 'Job number'], timeout=20)
    if idx == 0:
        child.sendline('[1,2]')
        child.expect('Password:', timeout=10)
        child.sendline('Digital1977')
        idx2 = child.expect(['Job number', r'\$ '], timeout=15)
        if idx2 == 0:
            child.sendline('')  # Start new job
    elif idx == 2:
        child.sendline('')  # Start new job
    child.expect(r'\$ ', timeout=30)

    def dcl_cmd(cmd, timeout=10):
        child.sendline(cmd)
        child.expect(r'\$ ', timeout=timeout)
        time.sleep(0.3)

    # Delete ALL old files from both devices
    print("\n=== Deleting old files from DM1: and SY: ===")
    for dev in ['DM1:', 'SY:']:
        for f in ['ADVENT.DTA', 'ADVENT.MON', 'ADVENT.CHR', 'BOARD.NTC', 'MESSAG.NPC']:
            dcl_cmd(f'DELETE/NOCONFIRM {dev}[1,2]{f}')

    # Use ASSIGN to make sure we're on DM1:
    dcl_cmd('ASSIGN DM1: SY:')  # Temporarily make SY: point to DM1:

    print("\n=== Starting BASIC ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    def basic_cmd(cmd, timeout=30):
        child.sendline(cmd)
        idx = child.expect(['BASIC2', r'\?.*BASIC2', r'\$ '], timeout=timeout)
        time.sleep(0.2)
        return idx == 0

    # Create each file individually, opening and closing each one
    print("\n--- Creating ADVENT.DTA ---")
    basic_cmd('OPEN "DM1:[1,2]ADVENT.DTA" AS FILE #1%, ACCESS SCRATCH, ALLOW NONE', 60)
    basic_cmd('DIM #1%, R$(2000%)=512%', 60)
    basic_cmd('CLOSE #1%')

    print("\n--- Creating ADVENT.MON ---")
    basic_cmd('OPEN "DM1:[1,2]ADVENT.MON" AS FILE #2%, ACCESS SCRATCH, ALLOW NONE', 60)
    basic_cmd('DIM #2%, M$(10000%)=20%', 60)
    basic_cmd('CLOSE #2%')

    print("\n--- Creating ADVENT.CHR ---")
    basic_cmd('OPEN "DM1:[1,2]ADVENT.CHR" AS FILE #3%, ACCESS SCRATCH, ALLOW NONE', 60)
    basic_cmd('DIM #3%, C$(100%)=512%', 60)
    basic_cmd('CLOSE #3%')

    print("\n--- Creating BOARD.NTC ---")
    basic_cmd('OPEN "DM1:[1,2]BOARD.NTC" AS FILE #4%, ACCESS SCRATCH, ALLOW NONE', 60)
    basic_cmd('DIM #4%, I%(511%), B$(511%)=512%', 60)
    basic_cmd('I%(0%)=0%')
    basic_cmd('CLOSE #4%')

    print("\n--- Creating MESSAG.NPC ---")
    basic_cmd('OPEN "DM1:[1,2]MESSAG.NPC" AS FILE #5%, ACCESS SCRATCH, ALLOW NONE', 60)
    basic_cmd('DIM #5%, N%(0%), S$(1000%)=60%', 60)
    basic_cmd('N%(0%)=0%')
    basic_cmd('CLOSE #5%')

    child.sendline('EXIT')
    child.expect(r'\$ ', timeout=10)

    # Remove the SY: assignment
    dcl_cmd('DEASSIGN SY:')

    # Verify files
    print("\n=== Verifying files on DM1:[1,2] ===")
    dcl_cmd('DIR DM1:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC', 15)

    # Test if NL: device exists
    print("\n=== Checking NL: device ===")
    dcl_cmd('DIR NL:', 5)

    # Run game
    print("\n" + "=" * 60)
    print("TESTING ADVENT")
    print("=" * 60)
    child.sendline('RUN DM1:[1,2]ADVENT')

    idx = child.expect([
        'Welcome',
        'What is your',
        'name',
        '>',
        'INITIALIZING',
        'Stop at',
        r'\?Not a valid',
        r'\?',
        r'\$ ',
        pexpect.TIMEOUT
    ], timeout=60)

    print(f"\n*** Response index: {idx} ***")
    time.sleep(5)
    child.close()

if __name__ == '__main__':
    main()
