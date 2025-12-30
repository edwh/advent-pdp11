#!/usr/bin/env python3
"""Check and create data files needed by the game."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Check and Create Data Files")
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
        # In game - exit
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

    # Create logical name
    dcl_cmd('ASSIGN DM1:[1,2] A:')

    # Check what files exist
    print("\n=== Existing data files ===")
    child.sendline('DIR/SIZE A:*.DTA,A:*.MON,A:*.NTC,A:*.CHR,A:*.NPC')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    # The game needs these files:
    # ADVENT.DTA - main data file (should exist)
    # ADVENT.MON - monster data
    # BOARD.NTC - notice board
    # ADVENT.CHR - character data
    # MESSAG.NPC - NPC messages

    # Check ADVENT.MAP for undefined symbols
    print("\n=== Undefined symbols from map ===")
    child.sendline('SEARCH A:ADVENT.MAP "undefined"')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    # Try to see the global symbols section
    print("\n=== Global symbols ===")
    child.sendline('TYPE A:ADVENT.MAP')
    time.sleep(3)
    for _ in range(8):
        idx = child.expect(['Press RETURN', r'\$ ', pexpect.TIMEOUT], timeout=10)
        if idx == 0:
            child.sendline('')
            time.sleep(1)
        else:
            break

    dcl_cmd('DEASSIGN A:')
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
