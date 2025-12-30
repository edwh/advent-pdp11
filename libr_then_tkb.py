#!/usr/bin/env python3
"""Build ADVENT.TSK using object library approach with correct RSTS/E syntax."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - Object Library Approach v2")
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
        time.sleep(0.5)

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
    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ADVSUB.OLB')

    # Create object library using LIBR
    # RSTS/E LIBR syntax: output=input1,input2,...
    print("\n=== Creating object library ===")
    child.sendline('RUN $LIBR')
    child.expect(r'\*', timeout=15)

    # Create library with all subroutine object files
    # RSTS format: library/LI:CREATE = obj1,obj2,obj3,...
    # Or maybe just: library = obj1,obj2,...

    # Let's try: output/CREATE = inputs
    child.sendline('DM1:[1,2]ADVSUB/CREATE=DM1:[1,2]ADVINI')
    idx = child.expect([r'\*', 'error', 'Ill', pexpect.TIMEOUT], timeout=30)
    print(f"\n*** After LIBR CREATE: idx={idx} ***")

    if idx in [1, 2]:
        # Try different syntax: just output=input
        print("\n*** Trying different LIBR syntax ***")
        child.sendline('DM1:[1,2]ADVSUB.OLB=DM1:[1,2]ADVINI.OBJ')
        idx = child.expect([r'\*', 'error', 'Ill', pexpect.TIMEOUT], timeout=30)
        print(f"\n*** After LIBR v2: idx={idx} ***")

    # Try adding more files
    if idx == 0:
        obj_files = ['ADVOUT', 'ADVNOR', 'ADVCMD', 'ADVODD', 'ADVMSG',
                     'ADVBYE', 'ADVSHT', 'ADVNPC', 'ADVPUZ', 'ADVDSP', 'ADVFND', 'ADVTDY']

        for obj in obj_files:
            # Try insert syntax: library/INSERT = object
            child.sendline(f'DM1:[1,2]ADVSUB/INSERT=DM1:[1,2]{obj}')
            idx = child.expect([r'\*', 'error', 'Ill', pexpect.TIMEOUT], timeout=30)
            if idx != 0:
                print(f"\n*** Error inserting {obj} ***")
                break

    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Check if library was created
    print("\n=== Checking library ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVSUB.OLB')

    if 'Total of' in child.before:
        print("\n*** Library created! ***")

        # Now link with TKB
        print("\n=== Running TKB ===")
        child.sendline('RUN $TKB')
        child.expect('TKB>', timeout=15)
        time.sleep(1)

        # Simple command: main + library + runtime library
        child.sendline('DM1:[1,2]ADVENT/FP=DM1:[1,2]ADVENT,DM1:[1,2]ADVSUB/LB,SY:[1,1]BP2OTS/LB')
        time.sleep(2)

        # Handle TKB
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
            ], timeout=180)

            print(f"\n*** TKB idx={idx} ***")

            if idx == 0:
                child.sendline('/')
            elif idx == 1:
                child.sendline('')
            elif idx == 6:
                done = True
            elif idx in [2, 3, 4, 5]:
                time.sleep(1)
            elif idx == 7:
                done = True

        time.sleep(2)

        # Check for ADVENT.TSK
        print("\n=== Checking for ADVENT.TSK ===")
        dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

        if 'Total of' in child.before and 'blocks' in child.before:
            print("\n*** ADVENT.TSK exists! ***")

            dcl_cmd('ASSIGN DM1: DK1:')
            dcl_cmd('ASSIGN SY: DK0:')

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
    else:
        print("\n*** Library not created ***")

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
