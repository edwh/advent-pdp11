#!/usr/bin/env python3
"""Build ADVENT.TSK - all files on one line."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - All Files Single Line")
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
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK')

    # Use short device name and all files on single line
    # DM1:[1,2] = 9 chars per file spec, let's try abbreviated
    print("\n=== Running TKB (all files, single line) ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)
    time.sleep(1)

    # Put ALL object files on one line - this will be long but let's see if it works
    # Using DM1: to shorten the line
    all_objs = [
        'ADVENT', 'ADVINI', 'ADVOUT', 'ADVNOR', 'ADVCMD', 'ADVODD',
        'ADVMSG', 'ADVBYE', 'ADVSHT', 'ADVNPC', 'ADVPUZ', 'ADVDSP',
        'ADVFND', 'ADVTDY'
    ]

    # Build command with all files
    files_part = ','.join([f'DM1:[1,2]{f}' for f in all_objs])
    cmd = f'DM1:[1,2]ADVENT/FP={files_part},SY:[1,1]BP2OTS/LB'

    print(f"\n>>> Command length: {len(cmd)} chars")
    print(f">>> Command: {cmd[:100]}...")

    child.sendline(cmd)
    time.sleep(5)

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
            'too long',
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
        elif idx == 7:  # $ prompt
            done = True
        elif idx == 3:  # undefined
            print("\n*** Undefined symbols ***")
            # Print them and continue
            child.expect('TKB>', timeout=60)
            child.sendline('/')
            time.sleep(2)
        elif idx in [2, 4, 5, 6, 8]:
            print(f"\n*** Error: idx={idx} ***")
            done = True

    time.sleep(2)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    child.sendline('DIR/SIZE DM1:[1,2]ADVENT.TSK')
    child.expect(r'\$ ', timeout=15)

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** SUCCESS! ADVENT.TSK created! ***")
    else:
        print("\n*** ADVENT.TSK not found ***")

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
