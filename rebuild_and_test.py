#!/usr/bin/env python3
"""Rebuild ADVENT.TSK and create data files."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Rebuilding ADVENT.TSK and Creating Data Files")
    print("=" * 60)

    child = pexpect.spawn('telnet localhost 2323', encoding='latin-1')
    child.logfile = sys.stdout

    # Wait for connection
    try:
        child.expect('Connected to the PDP-11', timeout=10)
    except pexpect.TIMEOUT:
        print("\n*** Cannot connect - is the container running? ***")
        return False

    time.sleep(2)
    child.sendline('')
    time.sleep(1)
    child.sendline('')
    time.sleep(1)

    # Login
    idx = child.expect(['User:', r'\$ ', 'Job number'], timeout=30)
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
    print("\n*** Logged in successfully ***")

    def dcl_cmd(cmd, timeout=15):
        """Execute a DCL command and wait for prompt."""
        child.sendline(cmd)
        child.expect(r'\$ ', timeout=timeout)
        time.sleep(0.3)

    # Step 1: Install BP2RES library
    print("\n" + "=" * 60)
    print("Step 1: Installing BP2 Runtime Library")
    print("=" * 60)

    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)

    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)

    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)
    print("\n*** BP2RES library step complete ***")

    # Step 2: Check if ADVENT.TSK exists, rebuild if needed
    print("\n" + "=" * 60)
    print("Step 2: Checking/Rebuilding ADVENT.TSK")
    print("=" * 60)

    child.sendline('DIR DM1:[1,2]ADVENT.TSK')
    idx = child.expect([r'Total of \d+ block', r'\?Can\'t find'], timeout=10)
    child.expect(r'\$ ', timeout=5)

    if idx == 1:
        print("\n*** ADVENT.TSK not found - rebuilding with TKB ***")

        # Run TKB
        child.sendline('RUN $TKB')
        child.expect('TKB>', timeout=15)

        # Build command
        child.sendline('DM1:[1,2]ADVENT/FP=DM1:[1,3]ADVENT.ODL')

        # TKB will prompt with TKB> then "Enter Options:" then TKB> again
        # We need to handle multiple prompts
        while True:
            idx = child.expect(['TKB>', 'Enter Options:', r'\$ ', pexpect.TIMEOUT], timeout=60)
            if idx == 0:
                # At TKB> prompt - send / or empty line to continue
                child.sendline('/')
            elif idx == 1:
                # At Options prompt - send empty line
                child.sendline('')
            elif idx == 2:
                # Back at DCL prompt - done
                break
            elif idx == 3:
                print("\n*** TKB timeout ***")
                break

        print("\n*** TKB complete ***")

        # Verify build
        child.sendline('DIR/SIZE DM1:[1,2]ADVENT.TSK')
        child.expect(r'\$ ', timeout=10)
    else:
        print("\n*** ADVENT.TSK already exists ***")

    # Step 3: Clean up old files from BOTH devices
    print("\n" + "=" * 60)
    print("Step 3: Cleaning Up Old Data Files")
    print("=" * 60)

    for dev in ['DM1:', 'SY:']:
        for f in ['ADVENT.DTA', 'ADVENT.MON', 'ADVENT.CHR', 'BOARD.NTC', 'MESSAG.NPC']:
            dcl_cmd(f'DELETE/NOCONFIRM {dev}[1,2]{f}')

    # Step 4: Create data files using ASSIGN to force device
    print("\n" + "=" * 60)
    print("Step 4: Creating Data Files (with ASSIGN workaround)")
    print("=" * 60)

    # Use ASSIGN to make DM1: the system device for this job
    dcl_cmd('ASSIGN DM1: SY:')

    files_to_create = [
        ('ADVENT.DTA', 'R$(2000%)=512%', None),
        ('ADVENT.MON', 'M$(10000%)=20%', None),
        ('ADVENT.CHR', 'C$(100%)=512%', None),
        ('BOARD.NTC', 'I%(511%), B$(511%)=512%', 'I%(0%)=0%'),
        ('MESSAG.NPC', 'N%(0%), S$(1000%)=60%', 'N%(0%)=0%'),
    ]

    for filename, dim_spec, init_cmd in files_to_create:
        print(f"\n--- Creating [1,2]{filename} (via ASSIGN) ---")

        # Start fresh BASIC session
        child.sendline('RUN $BP2IC2')
        child.expect('BASIC2', timeout=15)

        # Open file - since SY: is assigned to DM1:, this should go to DM1:
        open_cmd = f'OPEN "[1,2]{filename}" AS FILE #1%, ACCESS SCRATCH, ALLOW NONE'
        child.sendline(open_cmd)
        idx = child.expect(['BASIC2', r'\?'], timeout=60)
        if idx == 1:
            print(f"    Error opening {filename}")
            child.expect('BASIC2', timeout=10)

        # Dimension the virtual array
        child.sendline(f'DIM #1%, {dim_spec}')
        child.expect('BASIC2', timeout=60)

        # Initialize if needed
        if init_cmd:
            child.sendline(init_cmd)
            child.expect('BASIC2', timeout=10)

        # Write some data to force file allocation
        if 'R$' in dim_spec:
            child.sendline('R$(1%)=STRING$(512%,32%)')
            child.expect('BASIC2', timeout=10)
        elif 'M$' in dim_spec:
            child.sendline('M$(1%)=STRING$(20%,32%)')
            child.expect('BASIC2', timeout=10)
        elif 'C$' in dim_spec:
            child.sendline('C$(1%)=STRING$(512%,32%)')
            child.expect('BASIC2', timeout=10)
        elif 'B$' in dim_spec:
            child.sendline('B$(1%)=STRING$(512%,32%)')
            child.expect('BASIC2', timeout=10)
        elif 'S$' in dim_spec:
            child.sendline('S$(1%)=STRING$(60%,32%)')
            child.expect('BASIC2', timeout=10)

        # Close file
        child.sendline('CLOSE #1%')
        child.expect('BASIC2', timeout=10)

        # Exit BASIC
        child.sendline('EXIT')
        child.expect(r'\$ ', timeout=10)

        print(f"    {filename} created")

    # Remove the device assignment
    dcl_cmd('DEASSIGN SY:')

    # Step 5: Verify all files are on DM1:
    print("\n" + "=" * 60)
    print("Step 5: Verifying All Files")
    print("=" * 60)

    dcl_cmd('DIR/SIZE DM1:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC', 15)
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK', 10)

    # Check SY: for leaked files
    print("\n--- Checking SY: for any leaked files ---")
    dcl_cmd('DIR SY:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC', 15)

    # Step 6: Test game
    print("\n" + "=" * 60)
    print("Step 6: Testing ADVENT Game")
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
    ], timeout=90)

    result_map = {
        0: "WELCOME MESSAGE",
        1: "NAME PROMPT",
        2: "NAME PROMPT",
        3: "GAME PROMPT",
        4: "INITIALIZING",
        5: "STOPPED AT ERROR",
        6: "NOT VALID FILE",
        7: "OTHER ERROR",
        8: "DCL PROMPT",
        9: "TIMEOUT"
    }

    print(f"\n*** Got: {result_map.get(idx, 'UNKNOWN')} (index {idx}) ***")

    if idx in [0, 1, 2, 3, 4]:
        print("\n*** GAME IS STARTING! ***")
        time.sleep(3)
        child.sendline('TEST')
        time.sleep(5)
        child.sendline('LOOK')
        time.sleep(3)
    elif idx == 5:
        time.sleep(2)

    time.sleep(2)
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
