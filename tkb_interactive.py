#!/usr/bin/env python3
"""Build ADVENT.TSK interactively, one line at a time."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - Interactive Method")
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

    # Delete old TSK if exists
    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK')

    # Run TKB
    print("\n=== Running TKB ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)

    # Send first line
    child.sendline('DM1:[1,2]ADVENT/FP,DM1:[1,2]ADVENT,DM1:[1,2]ADVINI/-')
    time.sleep(1)
    child.expect('TKB>', timeout=30)

    child.sendline('DM1:[1,2]ADVOUT,DM1:[1,2]ADVNOR,DM1:[1,2]ADVCMD/-')
    time.sleep(1)
    child.expect('TKB>', timeout=30)

    child.sendline('DM1:[1,2]ADVODD,DM1:[1,2]ADVMSG,DM1:[1,2]ADVBYE/-')
    time.sleep(1)
    child.expect('TKB>', timeout=30)

    child.sendline('DM1:[1,2]ADVSHT,DM1:[1,2]ADVNPC,DM1:[1,2]ADVPUZ/-')
    time.sleep(1)
    child.expect('TKB>', timeout=30)

    child.sendline('DM1:[1,2]ADVDSP,DM1:[1,2]ADVFND,DM1:[1,2]ADVTDY/-')
    time.sleep(1)
    child.expect('TKB>', timeout=30)

    child.sendline('SY:[1,1]BP2OTS/LB')
    time.sleep(1)
    child.expect('TKB>', timeout=30)

    # End file input
    child.sendline('/')
    time.sleep(1)

    # Wait for options prompt
    idx = child.expect(['Enter Options:', 'TKB>', 'FATAL', r'\$ '], timeout=60)
    print(f"\n*** After /: idx={idx} ***")

    if idx == 0:
        # Accept defaults
        child.sendline('')
        time.sleep(2)
        idx2 = child.expect(['TKB>', r'\$ ', pexpect.TIMEOUT], timeout=120)
        print(f"\n*** After options: idx2={idx2} ***")
        if idx2 == 0:
            child.sendline('/')
            child.expect(r'\$ ', timeout=60)
    elif idx == 1:
        child.sendline('/')
        child.expect(r'\$ ', timeout=60)
    elif idx == 2:
        print("\n*** TKB FATAL ERROR ***")
        child.sendcontrol('z')
        child.expect(r'\$ ', timeout=10)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    # Setup devices and test if task was created
    if True:
        dcl_cmd('ASSIGN DM1: DK1:')
        dcl_cmd('ASSIGN SY: DK0:')

        # Copy data files to DM1:
        print("\n=== Copying data files to DM1: ===")
        for f in ['ADVENT.MON', 'ADVENT.CHR', 'BOARD.NTC', 'MESSAG.NPC']:
            child.sendline(f'COPY/NOCONFIRM SY:[1,2]{f} DM1:[1,2]{f}')
            idx = child.expect([r'\$ ', 'replace', pexpect.TIMEOUT], timeout=15)
            if idx == 1:
                child.sendline('Y')
                child.expect(r'\$ ', timeout=15)
            time.sleep(0.3)

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
            'cave',
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
            4: "CAVERN",
            5: "ADVENT MSG",
            6: "ERROR",
            7: "DCL PROMPT",
            8: "TIMEOUT"
        }

        print(f"\n*** Got: {result_map.get(idx, 'UNKNOWN')} (idx={idx}) ***")

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
