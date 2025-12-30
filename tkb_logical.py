#!/usr/bin/env python3
"""Build ADVENT.TSK using logical name to shorten paths."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - Using Logical Name")
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

    # Create short logical name for DM1:[1,2]
    print("\n=== Creating logical name A: for DM1:[1,2] ===")
    dcl_cmd('ASSIGN DM1:[1,2] A:')

    # Install BP2RES
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    dcl_cmd('DELETE/NOCONFIRM A:ADVENT.TSK')

    # Now use A: instead of DM1:[1,2] - much shorter!
    # A:ADVENT = 8 chars vs DM1:[1,2]ADVENT = 16 chars
    print("\n=== Running TKB with A: logical ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)
    time.sleep(1)

    # All files with short A: prefix
    # A:name,A:name2,... should fit in 80 chars if we limit the count
    # 80 chars / 10 chars per file = ~8 files per line max

    # Line format: output/FP=file1,file2,file3,file4,file5,file6,file7,lib/LB
    # Let's try 6 files + library on first line

    # Actually, we still need overlays. Let me try with just a few files first
    # to see if logical names work
    cmd = 'A:ADVENT/FP=A:ADVENT,A:ADVINI,A:ADVOUT,A:ADVNOR,A:ADVCMD,A:ADVODD,SY:[1,1]BP2OTS/LB'
    print(f"\n>>> Command ({len(cmd)} chars): {cmd}")
    child.sendline(cmd)
    time.sleep(3)

    # Handle response
    done = False
    iterations = 0
    while not done and iterations < 20:
        iterations += 1
        idx = child.expect([
            'Enter Options:',
            'TKB>',
            'FATAL',
            'undefined',
            'overflow',
            'syntax',
            r'\$ ',
            pexpect.TIMEOUT
        ], timeout=180)

        print(f"\n*** idx={idx} ***")

        if idx == 0:  # Enter Options
            child.sendline('')
            time.sleep(2)
        elif idx == 1:  # TKB>
            child.sendline('/')
            time.sleep(2)
        elif idx == 6:  # $ prompt
            done = True
        elif idx == 3:  # undefined
            print("\n*** Undefined symbols ***")
            child.expect('TKB>', timeout=60)
            child.sendline('/')
            time.sleep(2)
        elif idx == 4:  # overflow
            print("\n*** Address overflow - need overlays ***")
            child.expect(['TKB>', r'\$ '], timeout=60)
            done = True
        elif idx in [2, 5, 7]:
            print(f"\n*** Error: idx={idx} ***")
            done = True

    time.sleep(2)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    child.sendline('DIR/SIZE A:ADVENT.TSK')
    child.expect(r'\$ ', timeout=15)

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** SUCCESS! ADVENT.TSK created! ***")
    else:
        print("\n*** ADVENT.TSK not found (likely due to address overflow) ***")

    # Deassign
    dcl_cmd('DEASSIGN A:')

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
