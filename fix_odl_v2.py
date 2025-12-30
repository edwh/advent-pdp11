#!/usr/bin/env python3
"""Fix ODL file by copying source ODL and modifying with EDT."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Fixing ODL - Copy and Modify Approach")
    print("=" * 60)

    child = pexpect.spawn('telnet localhost 2323', encoding='latin-1')
    child.logfile = sys.stdout

    # Wait for connection
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

    # Install BP2RES library
    print("\n=== Installing BP2RES library ===")
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Check if we have the source ODL file with overlays
    print("\n=== Checking for source ODL files ===")
    dcl_cmd('DIR DM1:[1,3]ADVENT.ODL')

    # Check if the original source ODL is in src directory
    # Let's try the built-in BP2 example ODL files as reference
    dcl_cmd('DIR SY:[1,1]*.ODL')

    # Try using TKB with inline specification instead of ODL file
    print("\n=== Trying TKB with command-line overlay specification ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)

    # Try building without overlays first - simpler approach
    # Link main program with all subroutines
    print("\n--- Attempting non-overlay build ---")
    child.sendline('DM1:[1,2]ADVENT=DM1:[1,2]ADVENT,DM1:[1,2]ADVINI,DM1:[1,2]ADVOUT,DM1:[1,2]ADVNOR')
    child.expect('TKB>', timeout=30)

    child.sendline('DM1:[1,2]ADVCMD,DM1:[1,2]ADVODD,DM1:[1,2]ADVMSG,DM1:[1,2]ADVBYE')
    child.expect('TKB>', timeout=30)

    child.sendline('DM1:[1,2]ADVSHT,DM1:[1,2]ADVNPC,DM1:[1,2]ADVPUZ,DM1:[1,2]ADVDSP')
    child.expect('TKB>', timeout=30)

    child.sendline('DM1:[1,2]ADVFND,DM1:[1,2]ADVTDY,LB:BP2OTS/LB')
    child.expect('TKB>', timeout=30)

    child.sendline('/')

    # Wait for TKB to process
    while True:
        idx = child.expect(['TKB>', 'Enter Options:', r'\$ ', 'FATAL', pexpect.TIMEOUT], timeout=120)
        if idx == 0:
            child.sendline('/')
        elif idx == 1:
            child.sendline('')
        elif idx == 2:
            break
        elif idx == 3:
            print("\n*** TKB FATAL ERROR ***")
            child.expect(['TKB>', r'\$ '], timeout=30)
            # Exit TKB
            child.sendline('')
            child.sendcontrol('z')
            child.expect(r'\$ ', timeout=10)
            break
        elif idx == 4:
            print("\n*** TKB timeout ***")
            break

    print("\n=== Checking result ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    child.close()
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
