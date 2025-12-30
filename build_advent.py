#!/usr/bin/env python3
"""Build ADVENT.TSK using BP2 BUILD command."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK using BP2 BUILD")
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

    # Start BASIC
    print("\n=== Starting BASIC ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    # Use BUILD command to link all object files
    # BUILD output=main,sub1,sub2,...
    print("\n=== Running BUILD command ===")
    build_cmd = 'BUILD DM1:[1,2]ADVENT=DM1:[1,2]ADVENT,DM1:[1,2]ADVINI,DM1:[1,2]ADVOUT,DM1:[1,2]ADVNOR,DM1:[1,2]ADVCMD,DM1:[1,2]ADVODD,DM1:[1,2]ADVMSG,DM1:[1,2]ADVBYE,DM1:[1,2]ADVSHT,DM1:[1,2]ADVNPC,DM1:[1,2]ADVPUZ,DM1:[1,2]ADVDSP,DM1:[1,2]ADVFND,DM1:[1,2]ADVTDY'

    child.sendline(build_cmd)

    # Wait for build - may take a while
    idx = child.expect(['BASIC2', r'\?', 'TKB', pexpect.TIMEOUT], timeout=180)
    if idx == 0:
        print("\n*** BUILD completed! ***")
    elif idx == 1:
        print("\n*** BUILD ERROR ***")
        child.expect('BASIC2', timeout=30)
    elif idx == 2:
        print("\n*** TKB invoked by BUILD ***")
        # Wait for TKB to finish
        child.expect(['BASIC2', r'\$ '], timeout=120)
    elif idx == 3:
        print("\n*** BUILD timeout ***")

    # Exit BASIC
    child.sendcontrol('z')
    child.expect(['BASIC2', r'\$ '], timeout=10)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')
    dcl_cmd('DIR/SIZE SY:[1,2]ADVENT.TSK')

    # If TSK exists, test it
    child.sendline('RUN DM1:[1,2]ADVENT')
    idx = child.expect(['Welcome', 'name', '>', r'\?', r'\$ ', pexpect.TIMEOUT], timeout=30)

    print(f"\n*** Game test result: {idx} ***")

    time.sleep(2)
    child.close()
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
