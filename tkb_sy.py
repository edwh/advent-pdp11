#!/usr/bin/env python3
"""Build ADVENT.TSK - copy files to SY: and link from there."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - Link from SY:")
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

    # Copy OBJ files from DM1: to SY:
    print("\n=== Copying OBJ files to SY: ===")
    obj_files = ['ADVENT', 'ADVINI', 'ADVOUT', 'ADVNOR', 'ADVCMD', 'ADVODD',
                 'ADVMSG', 'ADVBYE', 'ADVSHT', 'ADVNPC', 'ADVPUZ', 'ADVDSP',
                 'ADVFND', 'ADVTDY']

    for obj in obj_files:
        child.sendline(f'COPY/NOCONFIRM DM1:[1,2]{obj}.OBJ SY:[1,2]{obj}.OBJ')
        idx = child.expect([r'\$ ', 'replace', pexpect.TIMEOUT], timeout=15)
        if idx == 1:
            child.sendline('Y')
            child.expect(r'\$ ', timeout=15)
        time.sleep(0.3)

    # Delete old TSK on both devices
    dcl_cmd('DELETE/NOCONFIRM SY:[1,2]ADVENT.TSK')

    # Run TKB with files from SY:
    print("\n=== Running TKB (from SY:) ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)
    time.sleep(1)

    # Only 3 continuation lines, using SY: device
    tkb_lines = [
        'SY:[1,2]ADVENT/FP,SY:[1,2]ADVENT=SY:[1,2]ADVENT,SY:[1,2]ADVINI/-',
        'SY:[1,2]ADVOUT,SY:[1,2]ADVNOR,SY:[1,2]ADVCMD/-',
        'SY:[1,2]ADVMSG,SY:[1,1]BP2OTS/LB',
    ]

    for i, line in enumerate(tkb_lines):
        print(f"\n>>> [{i+1}/{len(tkb_lines)}] {line[:60]}...")
        child.sendline(line)
        time.sleep(2)

        idx = child.expect(['TKB>', 'FATAL', 'error', 'trap', pexpect.TIMEOUT], timeout=60)
        if idx == 1:
            print("\n*** FATAL error ***")
            child.sendcontrol('z')
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)
            return False
        elif idx == 3:
            print("\n*** Trap error ***")
            return False
        elif idx == 4:
            print("\n*** Timeout ***")
            return False

    # End file input
    print("\n>>> Sending: /")
    child.sendline('/')
    time.sleep(2)

    # Handle options
    idx = child.expect(['Enter Options:', 'TKB>', 'FATAL', 'undefined', r'\$ ', pexpect.TIMEOUT], timeout=120)
    print(f"\n*** After /: idx={idx} ***")

    if idx == 0:
        child.sendline('')
        time.sleep(3)
        idx2 = child.expect(['TKB>', r'\$ ', pexpect.TIMEOUT], timeout=180)
        if idx2 == 0:
            child.sendline('/')
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=120)
    elif idx == 1:
        child.sendline('/')
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=120)
    elif idx == 3:
        print("\n*** Undefined symbols - missing subroutines ***")
        child.expect('TKB>', timeout=60)
        child.sendline('/')
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=60)

    time.sleep(2)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE SY:[1,2]ADVENT.TSK')

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** ADVENT.TSK exists! ***")
    else:
        print("\n*** ADVENT.TSK not found ***")

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
