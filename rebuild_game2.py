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

    def dcl_cmd(cmd, timeout=30):
        child.sendline(cmd)
        child.expect(r'\$ ', timeout=timeout)
        time.sleep(0.5)

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
    child.expect(['Ready', 'ready', 'BASIC', pexpect.TIMEOUT], timeout=15)

    child.sendline('OLD DM1:[1,3]ADVINI.SUB')
    time.sleep(2)
    child.expect(['Ready', 'ready', 'BASIC', pexpect.TIMEOUT], timeout=10)

    child.sendline('SET NOWARNING')
    time.sleep(1)
    child.expect(['Ready', 'ready', 'BASIC', pexpect.TIMEOUT], timeout=10)

    child.sendline('COMPILE')
    time.sleep(10)
    child.expect(['Ready', 'ready', 'BASIC', 'error', 'Error', pexpect.TIMEOUT], timeout=60)
    print("\n*** Compile done ***")

    # Exit BP2
    child.sendline('BYE')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # Copy OBJ to [1,2]
    print("\n=== Copying OBJ file ===")
    child.sendline('COPY DM1:[1,3]ADVINI.OBJ DM1:[1,2]ADVINI.OBJ')
    time.sleep(2)
    idx = child.expect([r'\$ ', 'OK to replace', pexpect.TIMEOUT], timeout=15)
    if idx == 1:
        child.sendline('Y')
        time.sleep(2)
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # Check existing files
    print("\n=== Checking existing OBJ files ===")
    dcl_cmd('DIR DM1:[1,2]*.OBJ')

    # Link the game with TKB
    print("\n=== Linking game with TKB ===")
    child.sendline('RUN $TKB')
    time.sleep(2)
    child.expect([r'TKB>', pexpect.TIMEOUT], timeout=10)

    child.sendline('DM1:[1,2]ADVENT/FP=DM1:[1,3]ADVENT.ODL')
    time.sleep(3)
    child.expect([r'TKB>', pexpect.TIMEOUT], timeout=30)

    child.sendline('/')
    time.sleep(10)
    idx = child.expect([r'\$ ', r'TKB>', 'error', 'Error', pexpect.TIMEOUT], timeout=180)
    print(f"\nLink result: idx={idx}")

    # If still at TKB prompt, exit
    if idx == 1:
        child.sendline(chr(26))
        time.sleep(2)
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # Check if ADVENT.TSK was created
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR DM1:[1,2]ADVENT.TSK')

    # Try running the game
    print("\n=== Try running game ===")
    child.sendline('RUN DM1:[1,2]ADVENT')
    time.sleep(10)
    # Wait longer for game to start or error
    idx = child.expect([r'\$ ', 'error', 'Error', 'Welcome', 'ADVENT', 'What is', pexpect.TIMEOUT], timeout=30)
    print(f"\nRun result: idx={idx}")

    # Whatever state we're in, try to get back to prompt
    time.sleep(2)
    child.sendcontrol('c')
    time.sleep(2)
    child.sendline('')
    time.sleep(1)

    child.close()
    print("\n*** Done ***")
    return True

if __name__ == '__main__':
    main()
