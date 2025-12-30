#!/usr/bin/env python3
"""Test different compile syntaxes."""

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
    for _ in range(10):
        idx = child.expect(['User:', r'\$ ', 'Job number', 'Password:', 'disabled', pexpect.TIMEOUT], timeout=30)
        if idx == 0:
            child.sendline('[1,2]')
        elif idx == 1:
            break
        elif idx == 2:
            child.sendline('')
        elif idx == 3:
            child.sendline('Digital1977')
        elif idx == 4:
            time.sleep(10)
            child.sendline('')
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

    dcl_cmd('ASSIGN DM1:[1,2] A:')

    # Check HELP for COMPILE
    print("\n=== HELP COMPILE ===")
    child.sendline('HELP COMPILE')
    time.sleep(2)
    child.expect([r'\$ ', 'Topic', pexpect.TIMEOUT], timeout=15)
    if 'Topic' in str(child.buffer):
        child.sendline('')
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # List directory to see .OBJ and .SUB files
    print("\n=== Current files ===")
    dcl_cmd('DIR/SIZE A:ADVINI.*')

    # Try different compile syntaxes
    print("\n=== Try syntax 1: COMPILE/BP2 file ===")
    child.sendline('COMPILE/BP2 A:ADVINI.SUB')
    time.sleep(5)
    idx = child.expect([r'\$ ', 'error', 'Error', '%', pexpect.TIMEOUT], timeout=60)
    print(f"\n*** Syntax 1 result: idx={idx} ***")
    if idx != 0:
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)
    dcl_cmd('DIR/SIZE A:ADVINI.*')

    # If no OBJ, try syntax 2
    print("\n=== Try syntax 2: Run BP2COM directly ===")
    child.sendline('RUN $BP2COM')
    time.sleep(2)
    idx = child.expect(['File', 'BP2', '>', r'\$ ', pexpect.TIMEOUT], timeout=15)
    print(f"BP2COM result: idx={idx}")
    if idx in [0, 1, 2]:
        child.sendline('A:ADVINI.SUB')
        time.sleep(10)
        child.expect(['>', r'\$ ', pexpect.TIMEOUT], timeout=60)
        child.sendcontrol('z')
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)
    dcl_cmd('DIR/SIZE A:ADVINI.*')

    dcl_cmd('DEASSIGN A:')
    child.close()

    print("\n*** DONE ***")
    return True

if __name__ == '__main__':
    main()
