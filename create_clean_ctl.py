#!/usr/bin/env python3
"""Create a clean TKB control file and submit it."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Create Clean TKB Control File and Build")
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
        time.sleep(0.5)

    # Install BP2RES first
    print("\n=== Installing BP2RES library ===")
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Delete existing files
    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK')
    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]BUILD.CTL')

    # Create new control file using EDIT
    print("\n=== Creating BUILD.CTL ===")
    child.sendline('CREATE DM1:[1,2]BUILD.CTL')
    time.sleep(1)

    # Enter the commands
    ctl_lines = [
        '$ DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK',
        '$ RUN $TKB',
        'DM1:[1,2]ADVENT/FP,DM1:[1,2]ADVENT=DM1:[1,2]ADVENT/-',
        'DM1:[1,2]ADVINI,DM1:[1,2]ADVOUT,DM1:[1,2]ADVNOR/-',
        'DM1:[1,2]ADVCMD,DM1:[1,2]ADVODD,DM1:[1,2]ADVMSG/-',
        'DM1:[1,2]ADVBYE,DM1:[1,2]ADVSHT,DM1:[1,2]ADVNPC/-',
        'DM1:[1,2]ADVPUZ,DM1:[1,2]ADVDSP,DM1:[1,2]ADVFND/-',
        'DM1:[1,2]ADVTDY,SY:[1,1]BP2OTS/LB',
        '/',
        '/',
        '$ DIR/SIZE DM1:[1,2]ADVENT.TSK',
        '$ EOJ'
    ]

    for line in ctl_lines:
        child.sendline(line)
        time.sleep(0.5)

    # End file with Ctrl+Z
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Show the file
    print("\n=== Verifying BUILD.CTL ===")
    dcl_cmd('TYPE DM1:[1,2]BUILD.CTL')

    # Submit the batch job
    print("\n=== Submitting batch job ===")
    dcl_cmd('SUBMIT DM1:[1,2]BUILD.CTL', timeout=30)

    # Wait for batch job to complete
    print("\n=== Waiting for batch job (60 seconds) ===")
    time.sleep(60)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** SUCCESS! ADVENT.TSK created! ***")
        # Show size
        dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')
    else:
        print("\n*** ADVENT.TSK not found ***")
        # Check the log
        print("\n=== Checking BUILD.LOG ===")
        dcl_cmd('TYPE DM1:[1,2]BUILD.LOG', timeout=30)

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
