#!/usr/bin/env python3
"""Build ADVENT.TSK - everything on one line, no continuation."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - Single Line Approach")
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

    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK')

    # Try with fewer files - just main + 2 subs on single line
    print("\n=== Running TKB (single line, 3 files) ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)
    time.sleep(1)

    # Single line: output,map=main,sub1,sub2,library/LB
    # Use shortest path notation possible
    cmd = 'DM1:[1,2]ADVENT/FP=DM1:[1,2]ADVENT,DM1:[1,2]ADVINI,DM1:[1,2]ADVOUT,SY:[1,1]BP2OTS/LB'
    print(f"\n>>> Command ({len(cmd)} chars): {cmd[:60]}...")
    child.sendline(cmd)
    time.sleep(3)
    idx = child.expect(['TKB>', 'Enter Options:', 'FATAL', 'undefined', 'overflow', 'error', r'\$ ', pexpect.TIMEOUT], timeout=120)
    print(f"\n*** idx={idx} ***")

    if idx == 0:  # TKB>
        child.sendline('/')
        time.sleep(2)
        idx2 = child.expect(['Enter Options:', 'TKB>', r'\$ ', pexpect.TIMEOUT], timeout=120)
        if idx2 == 0:
            child.sendline('')
            time.sleep(2)
            idx3 = child.expect(['TKB>', r'\$ ', pexpect.TIMEOUT], timeout=120)
            if idx3 == 0:
                child.sendline('/')
                child.expect(r'\$ ', timeout=60)
        elif idx2 == 1:
            child.sendline('/')
            child.expect(r'\$ ', timeout=60)
    elif idx == 1:  # Enter Options
        child.sendline('')
        time.sleep(2)
        child.expect(['TKB>', r'\$ '], timeout=120)
        child.sendline('/')
        child.expect(r'\$ ', timeout=60)
    elif idx == 3:  # undefined
        print("\n*** Undefined symbols (expected) ***")
        child.expect('TKB>', timeout=60)
        child.sendline('/')
        child.expect(r'\$ ', timeout=60)

    time.sleep(2)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** ADVENT.TSK created! ***")
    else:
        print("\n*** ADVENT.TSK not found ***")

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
