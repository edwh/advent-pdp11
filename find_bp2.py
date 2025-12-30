#!/usr/bin/env python3
"""Find BP2 compiler location."""

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
        idx = child.expect(['User:', r'\$ ', 'Job number', 'Password:', pexpect.TIMEOUT], timeout=30)
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

    def dcl_cmd(cmd, timeout=30):
        child.sendline(cmd)
        child.expect(r'\$ ', timeout=timeout)
        time.sleep(0.5)

    # Search for BP2 compiler
    print("\n=== Search for BP2COM ===")
    child.sendline('DIRECTORY SY:BP2*.*')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    print("\n=== Search in SY:[0,1] ===")
    child.sendline('DIRECTORY SY:[0,1]BP2*.*')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    print("\n=== Search for compiler-related files ===")
    child.sendline('DIRECTORY SY:[0,1]*COM*.*')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    print("\n=== Check HELP for BASIC ===")
    child.sendline('HELP BASIC')
    time.sleep(3)
    idx = child.expect([r'\$ ', 'Topic', pexpect.TIMEOUT], timeout=15)
    if idx == 1:
        child.sendcontrol('z')
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    print("\n=== Try BASIC command ===")
    child.sendline('BASIC')
    time.sleep(2)
    idx = child.expect(['>', 'Ready', r'\$ ', pexpect.TIMEOUT], timeout=15)
    print(f"BASIC result: idx={idx}")
    if idx in [0, 1]:
        child.sendcontrol('z')
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    print("\n=== Search all system executables ===")
    child.sendline('DIRECTORY SY:[0,1]*.TSK')
    time.sleep(5)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    print("\n=== Check SHOW SYSTEM or similar ===")
    dcl_cmd('SHOW RUNTIME')

    child.close()
    print("\n*** DONE ***")
    return True

if __name__ == '__main__':
    main()
