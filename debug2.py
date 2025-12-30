#!/usr/bin/env python3
"""Debug the game more carefully."""

import pexpect
import sys
import time

def main():
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
    child.expect(['User:', r'\$ '], timeout=30)
    child.sendline('[1,2]')
    child.expect('Password:', timeout=10)
    child.sendline('Digital1977')
    child.expect([r'\$ ', 'Job'], timeout=30)
    if 'Job' in child.before:
        child.sendline('')
        child.expect(r'\$ ', timeout=30)

    print("\n*** Logged in ***")

    # Install BP2RES
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Run the game
    print("\n*** Running ADVENT ***")
    child.sendline('RUN DM1:[1,2]ADVENT')
    time.sleep(5)
    child.expect('#', timeout=30)

    print("\n*** At BASIC # prompt ***")

    # Now do BASIC commands
    print("\n=== PRINT ERR ===")
    child.sendline('PRINT ERR')
    time.sleep(2)
    child.expect('#', timeout=10)

    print("\n=== PRINT ERL ===")
    child.sendline('PRINT ERL')
    time.sleep(2)
    child.expect('#', timeout=10)

    print("\n=== PRINT RUN.ACC$ ===")
    child.sendline('PRINT RUN.ACC$')
    time.sleep(2)
    child.expect('#', timeout=10)

    print("\n=== Try opening file on DM1: ===")
    child.sendline('OPEN "DM1:[1,2]ADVENT.DTA" FOR INPUT AS FILE #99%')
    time.sleep(2)
    child.expect('#', timeout=10)

    child.sendline('CLOSE #99%')
    time.sleep(1)
    child.expect('#', timeout=10)

    # The game opens with _DK1: prefix
    # Let's check if DK1: or _DK1: device exists
    print("\n=== Check DK device ===")
    child.sendline('OPEN "_DK1:[1,2]ADVENT.DTA" FOR INPUT AS FILE #99%')
    time.sleep(2)
    child.expect('#', timeout=10)

    # Try DK0: on system disk
    print("\n=== Try opening with DK0: ===")
    child.sendline('OPEN "_DK0:[1,2]ADVENT.DTA" FOR INPUT AS FILE #99%')
    time.sleep(2)
    child.expect('#', timeout=10)

    # Exit
    print("\n=== Exiting ===")
    child.sendcontrol('c')
    time.sleep(2)
    child.close()

    print("\n*** DONE ***")
    return True

if __name__ == '__main__':
    main()
