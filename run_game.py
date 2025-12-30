#!/usr/bin/env python3
"""Test running the game and check device/file access."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Test Game Execution")
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
        child.sendcontrol('c')
        time.sleep(1)
        idx = child.expect(['User:', r'\$ ', pexpect.TIMEOUT], timeout=15)

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

    # Check device names
    print("\n=== Checking devices ===")
    child.sendline('SHOW DEVICES')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    # Check what DK0: and DK1: point to
    print("\n=== Checking DK: devices ===")
    child.sendline('SHOW LOGICAL DK0:')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    child.sendline('SHOW LOGICAL DK1:')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    # Create logical name DK1: to point to DM1:
    print("\n=== Setting up DK1: = DM1: ===")
    dcl_cmd('ASSIGN DM1: DK1:')

    # Check again
    child.sendline('SHOW LOGICAL DK1:')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    # List files on DK1:[1,2]
    print("\n=== Checking DK1:[1,2] files ===")
    child.sendline('DIR DK1:[1,2]*.DTA,*.MON,*.NTC,*.CHR,*.NPC')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    # Try running the game with DK1: assigned
    print("\n=== Running ADVENT with DK1: assigned ===")
    child.sendline('RUN DM1:[1,2]ADVENT')
    time.sleep(5)

    idx = child.expect(['#', 'Stop', 'Error', r'\$ ', pexpect.TIMEOUT], timeout=30)
    print(f"\n*** Run result: idx={idx} ***")

    if idx == 0:  # Game prompt
        print("\n*** Got game prompt! Testing commands ***")
        child.sendline('LOOK')
        time.sleep(3)
        idx2 = child.expect(['#', 'What', r'\$ ', pexpect.TIMEOUT], timeout=15)
        print(f"\n*** LOOK result: idx={idx2} ***")

        if idx2 == 1:  # What?
            print("\n*** LOOK returned What? - commands not working ***")

        child.sendline('WHO')
        time.sleep(2)
        child.expect(['#', 'What', r'\$ ', pexpect.TIMEOUT], timeout=15)

        child.sendline('NORTH')
        time.sleep(2)
        child.expect(['#', 'What', r'\$ ', pexpect.TIMEOUT], timeout=15)

        child.sendcontrol('c')
        time.sleep(1)
    elif idx == 1:  # Stop
        print("\n*** Game stopped at error ***")

    child.expect([r'\$ ', 'User:', pexpect.TIMEOUT], timeout=15)

    # Re-login if needed
    idx = child.expect(['User:', r'\$ ', pexpect.TIMEOUT], timeout=5)
    if idx == 0:
        child.sendline('[1,2]')
        child.expect('Password:', timeout=10)
        child.sendline('Digital1977')
        child.expect([r'\$ ', 'Job'], timeout=15)

    dcl_cmd('DEASSIGN DK1:')
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
