#!/usr/bin/env python3
"""Submit TKB.CTL as a batch job to build ADVENT.TSK."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK via Batch Job")
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

    # Delete existing TSK
    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK')

    # Submit the batch job
    print("\n=== Submitting batch job ===")
    # The SUBMIT command submits a .CTL file to the batch queue
    dcl_cmd('SUBMIT DM1:[1,2]TKB.CTL', timeout=30)

    # Wait for batch job to complete
    print("\n=== Waiting for batch job ===")
    time.sleep(30)

    # Check batch queue status
    dcl_cmd('SHOW QUEUE/BATCH', timeout=15)

    # Wait more
    time.sleep(30)

    # Check TKB.LOG for results
    print("\n=== Checking TKB.LOG ===")
    dcl_cmd('TYPE DM1:[1,2]TKB.LOG', timeout=30)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** SUCCESS! ADVENT.TSK created! ***")
    else:
        print("\n*** ADVENT.TSK not found ***")

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
