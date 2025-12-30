#!/usr/bin/env python3
"""Compile ADVENT.B2S and build with TKB."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Compile and Build ADVENT")
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

    def dcl_cmd(cmd, timeout=15):
        child.sendline(cmd)
        child.expect(r'\$ ', timeout=timeout)
        time.sleep(0.3)

    # Install BP2RES
    print("\n=== Installing BP2RES library ===")
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Check existing object files
    print("\n=== Checking existing object files ===")
    dcl_cmd('DIR DM1:[1,2]*.OBJ')
    dcl_cmd('DIR DM1:[1,2]ADVENT.OBJ')

    # Check if ADVENT.B2S exists in source
    print("\n=== Checking source files ===")
    dcl_cmd('DIR DM1:[1,3]ADVENT.B2S')

    # Compile ADVENT.B2S if ADVENT.OBJ doesn't exist
    print("\n=== Compiling ADVENT.B2S ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    child.sendline('OLD DM1:[1,3]ADVENT.B2S')
    child.expect('BASIC2', timeout=30)

    child.sendline('SET NOWARNING')
    child.expect('BASIC2', timeout=10)

    child.sendline('COMPILE')
    # Compile may take a while
    idx = child.expect(['BASIC2', r'\?'], timeout=120)
    if idx == 1:
        print("\n*** COMPILE ERROR ***")
        child.expect('BASIC2', timeout=30)

    # Exit BASIC
    child.sendcontrol('z')
    child.expect(['BASIC2', r'\$ '], timeout=10)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Check for ADVENT.OBJ
    print("\n=== Checking for ADVENT.OBJ ===")
    dcl_cmd('DIR DM1:[1,2]ADVENT.OBJ')
    dcl_cmd('DIR DM1:[1,3]ADVENT.OBJ')
    dcl_cmd('DIR SY:[1,2]ADVENT.OBJ')

    # Try TKB with simpler approach - no overlays
    print("\n=== Trying TKB simple build ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)

    # Exit TKB and check where ADVENT.OBJ actually is
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Search all directories
    dcl_cmd('DIR SY:ADVENT.OBJ')
    dcl_cmd('DIR DM1:ADVENT.OBJ')

    child.close()
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
