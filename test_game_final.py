#!/usr/bin/env python3
"""Test the game with proper device assignment."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Test Game with Proper Device Assignment")
    print("=" * 60)

    child = pexpect.spawn('telnet localhost 2323', encoding='latin-1')
    child.logfile = sys.stdout

    try:
        child.expect('Connected to the PDP-11', timeout=10)
    except pexpect.TIMEOUT:
        print("\n*** Cannot connect ***")
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
            child.sendline('')
    elif idx == 2:
        child.sendline('')

    child.expect(r'\$ ', timeout=30)
    print("\n*** Logged in ***")

    def dcl_cmd(cmd, timeout=15):
        child.sendline(cmd)
        child.expect(r'\$ ', timeout=timeout)
        time.sleep(0.3)

    # Install BP2RES
    print("\n=== Installing BP2RES library ===")
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Check current files
    print("\n=== Files on SY:[1,2] ===")
    dcl_cmd('DIR/SIZE SY:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC')

    print("\n=== Files on DM1:[1,2] ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC')

    # Copy files from SY: to DM1: using COPY/NOCONFIRM
    print("\n=== Copying files from SY: to DM1: ===")
    for f in ['ADVENT.MON', 'ADVENT.CHR', 'BOARD.NTC', 'MESSAG.NPC']:
        child.sendline(f'COPY/NOCONFIRM SY:[1,2]{f} DM1:[1,2]{f}')
        idx = child.expect([r'\$ ', 'replace', pexpect.TIMEOUT], timeout=15)
        if idx == 1:
            child.sendline('Y')
            child.expect(r'\$ ', timeout=15)
        time.sleep(0.3)

    # Verify DM1: files
    print("\n=== Files on DM1:[1,2] after copy ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC')

    # Assign DK1: to DM1: (the game uses _DK1:)
    print("\n=== Assigning DK1: to DM1: ===")
    dcl_cmd('ASSIGN DM1: DK1:')

    # Also assign DK0: to SY: for REFRSH.CTL (line 173 of ADVMSG.SUB)
    dcl_cmd('ASSIGN SY: DK0:')

    # Test the game
    print("\n" + "=" * 60)
    print("TESTING ADVENT GAME")
    print("=" * 60)

    child.sendline('RUN DM1:[1,2]ADVENT')

    idx = child.expect([
        'Welcome',
        'What is your',
        'name',
        '>',
        'INITIALIZING',
        'Cannot',
        'Stop',
        'ADVENT',
        r'\?',
        r'\$ ',
        pexpect.TIMEOUT
    ], timeout=90)

    result_map = {
        0: "WELCOME",
        1: "NAME PROMPT",
        2: "NAME",
        3: "GAME PROMPT",
        4: "INITIALIZING",
        5: "CANNOT",
        6: "STOPPED",
        7: "ADVENT MSG",
        8: "ERROR",
        9: "DCL PROMPT",
        10: "TIMEOUT"
    }

    print(f"\n*** Got: {result_map.get(idx, 'UNKNOWN')} (idx={idx}) ***")

    if idx in [0, 1, 2, 3, 4, 7]:
        print("\n*** GAME IS STARTING! ***")
        time.sleep(3)
        # See what happens
        print("\n*** Waiting for more output... ***")
        try:
            idx2 = child.expect([r'name', '>', r'\?', 'Welcome', 'INITIALIZING', pexpect.TIMEOUT], timeout=30)
            print(f"\n*** Second expect: {idx2} ***")
        except:
            pass

        # Try entering a name
        print("\n*** Trying to enter name 'TEST' ***")
        child.sendline('TEST')
        time.sleep(5)

        # See final state
        try:
            idx3 = child.expect(['>', r'\?', 'Password', 'Welcome', pexpect.TIMEOUT], timeout=30)
            print(f"\n*** Third expect: {idx3} ***")
        except:
            pass

    time.sleep(3)
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
