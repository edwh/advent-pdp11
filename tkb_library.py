#!/usr/bin/env python3
"""Build ADVENT.TSK using object library approach."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - Object Library Approach")
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

    # Delete old files
    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK')
    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ADVENT.OLB')

    # Create object library using LIBR
    print("\n=== Creating object library ===")
    child.sendline('RUN $LIBR')
    child.expect(r'\*', timeout=15)

    # Create library
    child.sendline('DM1:[1,2]ADVENT.OLB/CR')
    child.expect(r'\*', timeout=30)

    # Insert object files - one at a time
    obj_files = ['ADVINI', 'ADVOUT', 'ADVNOR', 'ADVCMD', 'ADVODD', 'ADVMSG',
                 'ADVBYE', 'ADVSHT', 'ADVNPC', 'ADVPUZ', 'ADVDSP', 'ADVFND', 'ADVTDY']

    for obj in obj_files:
        child.sendline(f'DM1:[1,2]ADVENT.OLB/IN=DM1:[1,2]{obj}')
        idx = child.expect([r'\*', 'FATAL', 'error', pexpect.TIMEOUT], timeout=30)
        if idx != 0:
            print(f"\n*** Error adding {obj} ***")
            break

    # Exit librarian
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Show library contents
    print("\n=== Library contents ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.OLB')

    # Run TKB with simplified command
    print("\n=== Running TKB ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)

    # Link main program with both libraries
    # Format: output/FP=main_program,library1/LB,library2/LB
    child.sendline('DM1:[1,2]ADVENT/FP=DM1:[1,2]ADVENT,DM1:[1,2]ADVENT/LB,SY:[1,1]BP2OTS/LB')

    # Handle TKB prompts
    done = False
    iterations = 0
    while not done and iterations < 20:
        iterations += 1
        idx = child.expect([
            'TKB>',
            'Enter Options:',
            'FATAL',
            'error',
            'undefined',
            'overflow',
            r'\$ ',
            pexpect.TIMEOUT
        ], timeout=120)

        print(f"\n*** TKB idx={idx} ***")

        if idx == 0:
            child.sendline('/')
        elif idx == 1:
            child.sendline('')
        elif idx == 6:
            print("\n*** TKB completed ***")
            done = True
        elif idx in [2, 3, 4, 5]:
            print(f"\n*** TKB Error ***")
            time.sleep(1)
        elif idx == 7:
            print("\n*** Timeout ***")
            done = True

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
    else:
        print("\n*** ADVENT.TSK not found ***")

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
