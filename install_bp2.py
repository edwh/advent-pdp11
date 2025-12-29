#!/usr/bin/env python3
"""Install BP2 runtime system in RSTS/E."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Installing BP2 Runtime System")
    print("=" * 60)

    child = pexpect.spawn('telnet localhost 2323', encoding='latin-1')
    child.logfile = sys.stdout

    # Wait for connection
    child.expect('Connected to the PDP-11', timeout=10)
    time.sleep(2)

    # Send carriage returns to wake up terminal
    child.sendline('')
    time.sleep(1)
    child.sendline('')
    time.sleep(1)

    # Login
    idx = child.expect(['User:', r'\$ ', 'Job number'], timeout=20)
    if idx == 0:
        child.sendline('[1,2]')
        child.expect('Password:', timeout=10)
        child.sendline('Digital1977')
    if idx == 2 or child.expect(['Job number', r'\$ '], timeout=15) == 0:
        child.sendline('')  # New job
    child.expect(r'\$ ', timeout=15)

    print("\n=== Checking installed runtime systems ===")
    child.sendline('SYSTAT')
    child.expect(r'\$ ', timeout=10)

    print("\n=== Trying UTLMGR ===")
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=10)

    # Show what's installed
    child.sendline('SHOW RUNTIME')
    child.expect('Utlmgr>', timeout=10)

    # Try different install commands
    print("\n=== Trying to install BP2RES ===")

    # Try with full path
    child.sendline('INSTALL/RTS SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=10)

    # Try as library
    child.sendline('INSTALL/LIBRARY BP2RES')
    child.expect('Utlmgr>', timeout=10)

    child.sendline('SHOW LIBRARY')
    child.expect('Utlmgr>', timeout=10)

    # Exit with Ctrl+Z
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    print("\n=== Testing BASIC ===")
    child.sendline('RUN $BP2IC2')
    idx = child.expect(['BASIC2', r'\$ ', 'error'], timeout=15)
    if idx == 0:
        child.sendline('PRINT "HELLO"')
        child.expect('BASIC2', timeout=5)
        child.sendline('OPEN "DM1:[1,2]T.TMP" FOR OUTPUT AS FILE #1%')
        idx = child.expect(['BASIC2', 'Unable to attach'], timeout=10)
        if idx == 0:
            print("\n*** SUCCESS! File I/O works! ***")
            child.sendline('CLOSE #1%')
            child.expect('BASIC2', timeout=5)
        else:
            print("\n*** Still getting resident library error ***")
        child.sendline('EXIT')
        child.expect(r'\$ ', timeout=5)
    else:
        print("\n*** Could not start BASIC ***")

    child.close()

if __name__ == '__main__':
    main()
