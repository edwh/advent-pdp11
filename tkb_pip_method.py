#!/usr/bin/env python3
"""Build ADVENT.TSK using PIP to create command file, then run TKB."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - PIP Command File Method")
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
    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ADVENT.CMD')

    # Create command file using PIP with typed input
    print("\n=== Creating TKB command file using PIP ===")
    child.sendline('PIP DM1:[1,2]ADVENT.CMD=TI:')
    time.sleep(0.5)

    # Type the TKB commands
    tkb_cmds = [
        'DM1:[1,2]ADVENT/FP,DM1:[1,2]ADVENT/-',
        'DM1:[1,2]ADVINI,DM1:[1,2]ADVOUT,DM1:[1,2]ADVNOR/-',
        'DM1:[1,2]ADVCMD,DM1:[1,2]ADVODD,DM1:[1,2]ADVMSG/-',
        'DM1:[1,2]ADVBYE,DM1:[1,2]ADVSHT,DM1:[1,2]ADVNPC/-',
        'DM1:[1,2]ADVPUZ,DM1:[1,2]ADVDSP,DM1:[1,2]ADVFND/-',
        'DM1:[1,2]ADVTDY,SY:[1,1]BP2OTS/LB',
        '/',
        '/',
    ]

    for cmd in tkb_cmds:
        child.sendline(cmd)
        time.sleep(0.3)

    # End PIP input with Ctrl-Z
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Show the command file
    print("\n=== TKB command file contents ===")
    dcl_cmd('TYPE DM1:[1,2]ADVENT.CMD')

    # Run TKB with the command file
    print("\n=== Running TKB with command file ===")
    child.sendline('TKB @DM1:[1,2]ADVENT.CMD')

    # Wait for completion
    while True:
        idx = child.expect([
            r'\$ ',
            'TKB>',
            'Enter Options:',
            'FATAL',
            'error',
            'undefined',
            pexpect.TIMEOUT
        ], timeout=180)

        if idx == 0:
            print("\n*** TKB completed ***")
            break
        elif idx == 1:
            # TKB prompt - send /
            child.sendline('/')
        elif idx == 2:
            # Options prompt - accept defaults
            child.sendline('')
        elif idx in [3, 4, 5]:
            print(f"\n*** TKB Error (idx={idx}) ***")
            child.sendcontrol('z')
            time.sleep(1)
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)
            break
        elif idx == 6:
            print("\n*** Timeout ***")
            break

    time.sleep(2)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    # Check if file exists
    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** ADVENT.TSK exists! ***")

        # Setup devices
        dcl_cmd('ASSIGN DM1: DK1:')
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

        if idx in [0, 1, 2, 3, 4, 5]:
            print("\n*** Game appears to have started! ***")
            time.sleep(5)
    else:
        print("\n*** ADVENT.TSK not found ***")

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
