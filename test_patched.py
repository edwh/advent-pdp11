#!/usr/bin/env python3
"""Test the patched game."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Testing patched ADVENT game")
    print("=" * 60)

    child = pexpect.spawn('telnet localhost 2323', encoding='latin-1')
    child.logfile = sys.stdout

    try:
        child.expect('Connected to the PDP-11', timeout=10)
    except pexpect.TIMEOUT:
        print("ERROR: Could not connect")
        return False

    time.sleep(2)
    child.sendline('')
    time.sleep(1)

    # Login
    while True:
        idx = child.expect(['User:', r'\$ ', 'Job number', 'Password:', pexpect.TIMEOUT], timeout=30)
        if idx == 0:
            child.sendline('[1,2]')
        elif idx == 1:
            break
        elif idx == 2:
            child.sendline('')
        elif idx == 3:
            child.sendline('Digital1977')
        elif idx == 4:
            child.sendline('')
        time.sleep(1)

    print("\n*** Logged in ***")

    def dcl_cmd(cmd, timeout=30):
        child.sendline(cmd)
        child.expect(r'\$ ', timeout=timeout)
        time.sleep(0.5)

    # Install BP2RES
    print("\n=== Installing BP2RES ===")
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    dcl_cmd('ASSIGN DM1:[1,2] A:')

    # Check for ADVENT.TSK
    print("\n=== Checking ADVENT.TSK ===")
    dcl_cmd('DIR A:ADVENT.TSK')

    # Try running existing ADVENT.TSK first
    print("\n=== Running ADVENT.TSK ===")
    child.sendline('RUN A:ADVENT')
    time.sleep(5)

    idx = child.expect(['#', 'Stop', 'Error', 'error', r'\$ ', pexpect.TIMEOUT], timeout=30)
    print(f"\n*** Run result: idx={idx} ***")

    if idx == 0:
        print("\n*** Got # prompt! Testing commands ***")
        child.sendline('LOOK')
        time.sleep(3)
        idx2 = child.expect(['#', 'What', 'room', 'Room', 'dark', r'\$ ', pexpect.TIMEOUT], timeout=15)
        print(f"\n*** LOOK result: idx={idx2} ***")

        if idx2 in [0, 2, 3, 4]:
            print("\n*** SUCCESS! Game is working! ***")
            child.sendline('HELP')
            time.sleep(3)
            child.expect(['#', r'\$ ', pexpect.TIMEOUT], timeout=15)

        child.sendcontrol('c')
        time.sleep(2)
    elif idx == 1:
        print("\n*** Game stopped - need to recompile ***")

    child.expect([r'\$ ', 'User:', pexpect.TIMEOUT], timeout=15)

    # If game didn't work, recompile ADVINI and rebuild
    if idx != 0:
        print("\n=== Game didn't work - need to recompile ===")

        # Verify ADVINI.SUB has _DM1: now
        print("\n=== Checking ADVINI.SUB for _DM1: ===")
        child.sendline('TYPE A:ADVINI.SUB')
        time.sleep(5)
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    dcl_cmd('DEASSIGN A:')
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
