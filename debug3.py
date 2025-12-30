#!/usr/bin/env python3
"""Debug the game - handle login prompts properly."""

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

    # Handle login with multiple prompts
    while True:
        idx = child.expect(['User:', r'\$ ', 'Job number', 'Password:', '#'], timeout=30)
        if idx == 0:  # User:
            child.sendline('[1,2]')
        elif idx == 1:  # $
            break
        elif idx == 2:  # Job number
            child.sendline('')  # Get new job
        elif idx == 3:  # Password:
            child.sendline('Digital1977')
        elif idx == 4:  # # (BASIC prompt)
            print("\n*** Already at BASIC # prompt ***")
            break
        time.sleep(1)

    if idx == 1:  # At $ prompt
        print("\n*** At $ prompt ***")

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

    # Check error
    print("\n=== Error info ===")
    child.sendline('PRINT "ERR=";ERR')
    time.sleep(1)
    child.expect('#', timeout=10)

    child.sendline('PRINT "ERL=";ERL')
    time.sleep(1)
    child.expect('#', timeout=10)

    # Check the account string
    child.sendline('PRINT "RUN.ACC$=";RUN.ACC$')
    time.sleep(1)
    child.expect('#', timeout=10)

    # The file path
    child.sendline('PRINT "File=_DK1:"+RUN.ACC$+"ADVENT.DTA"')
    time.sleep(1)
    child.expect('#', timeout=10)

    # Try opening with DM1:
    print("\n=== Testing DM1: access ===")
    child.sendline('OPEN "DM1:[1,2]ADVENT.DTA" FOR INPUT AS FILE #99%')
    time.sleep(2)
    child.expect('#', timeout=10)

    # Check error after open
    child.sendline('PRINT "Open result ERR=";ERR')
    time.sleep(1)
    child.expect('#', timeout=10)

    child.sendline('CLOSE #99%')
    time.sleep(1)
    child.expect('#', timeout=10)

    # Try _DK1: - should fail
    print("\n=== Testing _DK1: access (expect fail) ===")
    child.sendline('OPEN "_DK1:[1,2]ADVENT.DTA" FOR INPUT AS FILE #98%')
    time.sleep(2)
    child.expect('#', timeout=10)

    child.sendline('PRINT "DK1 open ERR=";ERR')
    time.sleep(1)
    child.expect('#', timeout=10)

    # Try _DM1: - physical device
    print("\n=== Testing _DM1: access ===")
    child.sendline('OPEN "_DM1:[1,2]ADVENT.DTA" FOR INPUT AS FILE #97%')
    time.sleep(2)
    child.expect('#', timeout=10)

    child.sendline('PRINT "DM1 open ERR=";ERR')
    time.sleep(1)
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
