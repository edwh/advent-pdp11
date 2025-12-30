#!/usr/bin/env python3
"""Check for existing working ADVENT.TSK or other game files."""

import pexpect
import sys
import time

def main():
    child = pexpect.spawn('telnet localhost 2323', encoding='latin-1')
    child.logfile = sys.stdout

    try:
        child.expect('Connected to the PDP-11', timeout=10)
    except pexpect.TIMEOUT:
        return False

    time.sleep(2)
    child.sendline('')
    time.sleep(1)

    # Handle login
    while True:
        idx = child.expect(['User:', r'\$ ', 'Job number', 'Password:'], timeout=30)
        if idx == 0:
            child.sendline('[1,2]')
        elif idx == 1:
            break
        elif idx == 2:
            child.sendline('')
        elif idx == 3:
            child.sendline('Digital1977')
        time.sleep(1)

    print("\n*** Logged in ***")

    def dcl_cmd(cmd, timeout=15):
        child.sendline(cmd)
        child.expect(r'\$ ', timeout=timeout)
        time.sleep(0.5)

    # Search for ADVENT.TSK in various places
    print("\n=== Searching for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE SY:*.TSK')
    dcl_cmd('DIR/SIZE SY:[0,1]*.TSK')
    dcl_cmd('DIR/SIZE SY:[1,2]ADVENT.*')

    # Check DM0: too
    dcl_cmd('DIR/SIZE DM0:[1,2]ADVENT.*')

    # Check if there's a backup or original
    dcl_cmd('DIR/SIZE DM1:[1,2]*.SAV')
    dcl_cmd('DIR/SIZE DM1:[1,2]*.BAK')

    # Check current directory contents
    print("\n=== All files in DM1:[1,2] ===")
    child.sendline('DIR/SIZE DM1:[1,2]*.*')
    time.sleep(5)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    # Look for alternative builds
    print("\n=== Looking for TEST.TSK (small build) ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]TEST.TSK')

    # Try running TEST.TSK (the smaller build that was created earlier)
    print("\n=== Try running TEST.TSK ===")
    child.sendline('RUN DM1:[1,2]TEST')
    time.sleep(5)

    idx = child.expect(['#', 'Stop', 'Error', r'\$ ', pexpect.TIMEOUT], timeout=30)
    print(f"\n*** TEST result: idx={idx} ***")

    if idx == 0:
        # Got # prompt
        child.sendline('LOOK')
        time.sleep(2)
        child.expect(['#', r'\$ ', pexpect.TIMEOUT], timeout=15)
        child.sendcontrol('c')
        time.sleep(1)

    child.expect([r'\$ ', 'User:', pexpect.TIMEOUT], timeout=15)
    if 'User' in str(child.before):
        child.sendline('[1,2]')
        child.expect('Password:', timeout=10)
        child.sendline('Digital1977')
        child.expect([r'\$ ', 'Job'], timeout=15)

    child.close()
    print("\n*** DONE ***")
    return True

if __name__ == '__main__':
    main()
