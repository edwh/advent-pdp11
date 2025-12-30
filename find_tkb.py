#!/usr/bin/env python3
"""Find TKB versions and check system capabilities."""

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
    idx = child.expect(['User:', r'\$ ', 'Job number'], timeout=30)
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

    def dcl_cmd(cmd, timeout=30):
        child.sendline(cmd)
        child.expect(r'\$ ', timeout=timeout)
        time.sleep(0.5)

    # Check for TKB versions
    print("\n=== TKB files on system ===")
    dcl_cmd('DIR SY:[0,1]TKB*.*')
    dcl_cmd('DIR SY:[1,1]TKB*.*')

    # Check for LINK or other linkers
    print("\n=== LINK files ===")
    dcl_cmd('DIR SY:[0,1]LINK*.*')
    dcl_cmd('DIR SY:[1,1]LINK*.*')

    # Check for LBR (librarian)
    print("\n=== LBR/LIBR files ===")
    dcl_cmd('DIR SY:[0,1]LBR*.*')
    dcl_cmd('DIR SY:[0,1]LIBR*.*')
    dcl_cmd('DIR SY:[1,1]LBR*.*')

    # Check HELP TKB for options
    print("\n=== HELP TKB ===")
    dcl_cmd('HELP TKB', timeout=60)

    # Check if there's a FMS$ or other linking tool
    print("\n=== Other build tools ===")
    dcl_cmd('DIR SY:[0,1]*.TSK')

    child.close()
    return True

if __name__ == '__main__':
    main()
