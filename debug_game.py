#!/usr/bin/env python3
"""Debug the game interactively at BASIC prompt."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Debug Game at BASIC Prompt")
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
    idx = child.expect(['User:', r'\$ ', 'Job number', '#'], timeout=30)
    if idx == 3:
        # Already at game prompt
        print("\n*** Already at game # prompt ***")
    elif idx == 0:
        child.sendline('[1,2]')
        child.expect('Password:', timeout=10)
        child.sendline('Digital1977')
        idx2 = child.expect(['Job number', r'\$ '], timeout=15)
        if idx2 == 0:
            child.sendline('')
        child.expect(r'\$ ', timeout=30)
    elif idx == 2:
        child.sendline('')
        child.expect(r'\$ ', timeout=30)

    # If not at #, get there
    if idx != 3:
        print("\n*** Logged in, running game ***")

        # Install BP2RES
        child.sendline('RUN $UTLMGR')
        child.expect('Utlmgr>', timeout=15)
        child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
        child.expect('Utlmgr>', timeout=15)
        child.sendcontrol('z')
        child.expect(r'\$ ', timeout=10)

        # Run the game
        child.sendline('RUN DM1:[1,2]ADVENT')
        time.sleep(5)
        idx = child.expect(['#', r'\$ ', pexpect.TIMEOUT], timeout=30)

    if idx == 3 or child.before and '#' in str(child.before):
        # At BASIC prompt after STOP
        print("\n*** At BASIC # prompt - debugging ***")

        # Check what error occurred
        print("\n=== Checking error info ===")
        child.sendline('PRINT ERR')
        time.sleep(1)
        child.expect(['#', pexpect.TIMEOUT], timeout=10)

        child.sendline('PRINT ERL')
        time.sleep(1)
        child.expect(['#', pexpect.TIMEOUT], timeout=10)

        # Check what RUN.ACC$ is
        child.sendline('PRINT RUN.ACC$')
        time.sleep(1)
        child.expect(['#', pexpect.TIMEOUT], timeout=10)

        # Try to see what files the game needs
        print("\n=== Checking file paths ===")
        child.sendline('PRINT "_DK1:"+RUN.ACC$+"ADVENT.DTA"')
        time.sleep(1)
        child.expect(['#', pexpect.TIMEOUT], timeout=10)

        # Check if we can manually open a file on DM1:
        print("\n=== Testing manual file open ===")
        child.sendline('OPEN "DM1:[1,2]ADVENT.DTA" AS FILE #99%')
        time.sleep(2)
        child.expect(['#', pexpect.TIMEOUT], timeout=10)

        child.sendline('CLOSE #99%')
        time.sleep(1)
        child.expect(['#', pexpect.TIMEOUT], timeout=10)

        # The game uses _DK1: which is a physical device
        # Let's see what devices/files exist
        print("\n=== Listing DM1:[1,2] from BASIC ===")
        child.sendline('FILES "DM1:[1,2]*.*"')
        time.sleep(3)
        child.expect(['#', pexpect.TIMEOUT], timeout=15)

        # Exit BASIC cleanly
        print("\n=== Exiting ===")
        child.sendcontrol('c')
        time.sleep(1)
        child.expect([r'\$ ', 'User:', pexpect.TIMEOUT], timeout=15)

    # Re-login if needed
    idx = child.expect(['User:', r'\$ ', pexpect.TIMEOUT], timeout=5)
    if idx == 0:
        child.sendline('[1,2]')
        child.expect('Password:', timeout=10)
        child.sendline('Digital1977')
        child.expect([r'\$ ', 'Job'], timeout=15)

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
