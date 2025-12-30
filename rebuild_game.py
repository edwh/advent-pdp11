#!/usr/bin/env python3
"""Rebuild ADVINI and link the game."""

import pexpect
import sys
import time

def main():
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
    for _ in range(10):
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

    # Install BP2 library
    print("\n=== Installing BP2 library ===")
    child.sendline('RUN $UTLMGR')
    time.sleep(2)
    child.expect([r'>', 'UTLMGR', pexpect.TIMEOUT], timeout=10)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    time.sleep(2)
    child.expect([r'>', pexpect.TIMEOUT], timeout=10)
    child.sendline(chr(26))  # Ctrl+Z
    time.sleep(1)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # Compile ADVINI.SUB
    print("\n=== Compiling ADVINI.SUB ===")
    child.sendline('RUN $BP2IC2')
    time.sleep(3)
    child.expect(['Ready', 'ready', pexpect.TIMEOUT], timeout=15)

    child.sendline('OLD DM1:[1,3]ADVINI.SUB')
    time.sleep(2)
    child.expect(['Ready', 'ready', pexpect.TIMEOUT], timeout=10)

    child.sendline('SET NOWARNING')
    time.sleep(1)
    child.expect(['Ready', 'ready', pexpect.TIMEOUT], timeout=10)

    child.sendline('COMPILE')
    time.sleep(5)
    idx = child.expect(['Ready', 'ready', 'error', 'Error', pexpect.TIMEOUT], timeout=60)
    print(f"\nCompile result: idx={idx}")

    # Copy OBJ to [1,2]
    child.sendline('COPY DM1:[1,3]ADVINI.OBJ DM1:[1,2]ADVINI.OBJ')
    time.sleep(3)
    child.expect(['Ready', 'ready', 'OK to replace', pexpect.TIMEOUT], timeout=15)
    if 'OK to replace' in child.before or 'OK to replace' in child.after:
        child.sendline('Y')
        time.sleep(2)
        child.expect(['Ready', 'ready', pexpect.TIMEOUT], timeout=10)

    # Exit BP2
    child.sendline('BYE')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # Link the game with TKB
    print("\n=== Linking game with TKB ===")
    child.sendline('RUN $TKB')
    time.sleep(2)
    child.expect([r'TKB>', pexpect.TIMEOUT], timeout=10)

    child.sendline('DM1:[1,2]ADVENT/FP=DM1:[1,3]ADVENT.ODL')
    time.sleep(3)
    child.expect([r'TKB>', pexpect.TIMEOUT], timeout=30)

    child.sendline('/')
    time.sleep(5)
    idx = child.expect([r'\$ ', 'error', 'Error', pexpect.TIMEOUT], timeout=120)
    print(f"\nLink result: idx={idx}")

    # Check if ADVENT.TSK was created
    print("\n=== Checking for ADVENT.TSK ===")
    child.sendline('DIR DM1:[1,2]ADVENT.TSK')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # Try running the game
    print("\n=== Try running game ===")
    child.sendline('RUN DM1:[1,2]ADVENT')
    time.sleep(5)
    idx = child.expect([r'\$ ', 'error', 'Error', 'ADVENT', pexpect.TIMEOUT], timeout=30)
    print(f"\nRun result: idx={idx}")

    # Send Ctrl+C to exit if game started
    child.sendcontrol('c')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    child.close()
    print("\n*** Done ***")
    return True

if __name__ == '__main__':
    main()
