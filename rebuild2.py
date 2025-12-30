#!/usr/bin/env python3
"""Rebuild ADVINI - correct compile syntax."""

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

    # Install BP2RES
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Check what's the correct compile syntax
    print("\n=== Checking COMPILE help ===")
    child.sendline('HELP COMPILE')
    time.sleep(3)
    child.expect([r'\$ ', 'Topic', pexpect.TIMEOUT], timeout=15)
    if 'Topic' in str(child.before):
        child.sendline('')
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # Create logical name
    dcl_cmd('ASSIGN DM1:[1,2] A:')

    # First, check if ADVINI.SUB exists and its contents
    print("\n=== Checking ADVINI.SUB ===")
    child.sendline('TYPE A:ADVINI.SUB')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    # Check the current ADVINI.OBJ date
    print("\n=== Current ADVINI.OBJ ===")
    dcl_cmd('DIR/SIZE/DATE A:ADVINI.OBJ')

    # Use COMPILE command
    print("\n=== Compiling ADVINI.SUB ===")
    child.sendline('COMPILE/BP2/OBJECT=A:ADVINI A:ADVINI.SUB')
    time.sleep(15)
    idx = child.expect([r'\$ ', 'error', 'Error', pexpect.TIMEOUT], timeout=120)
    print(f"\n*** Compile result: idx={idx} ***")

    if idx == 3:
        child.sendline('')
        time.sleep(1)
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    # Check new ADVINI.OBJ date
    print("\n=== New ADVINI.OBJ ===")
    dcl_cmd('DIR/SIZE/DATE A:ADVINI.OBJ')

    dcl_cmd('DEASSIGN A:')
    child.close()

    print("\n*** DONE ***")
    return True

if __name__ == '__main__':
    main()
