#!/usr/bin/env python3
"""Build ADVENT.TSK - fit all files in 2 continuation lines."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - 2 Lines Max")
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

    # Create logical name
    dcl_cmd('ASSIGN DM1:[1,2] A:')

    # Install BP2RES
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    dcl_cmd('DELETE/NOCONFIRM A:ADVENT.TSK')

    # Run TKB with 2 lines only
    # Line 1: output + first 6 files + continuation (max 80 chars)
    # Line 2: remaining 8 files + library (max 80 chars)
    print("\n=== Running TKB (2 lines only) ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)
    time.sleep(2)

    # Line 1: output + 6 object files + continuation
    # A:ADVENT/FP=A:ADVENT,A:ADVINI,A:ADVOUT,A:ADVNOR,A:ADVCMD,A:ADVODD/-
    line1 = 'A:ADVENT/FP=A:ADVENT,A:ADVINI,A:ADVOUT,A:ADVNOR,A:ADVCMD,A:ADVODD/-'
    print(f"\n>>> Line 1 ({len(line1)} chars): {line1}")
    child.sendline(line1)
    time.sleep(3)
    idx = child.expect(['TKB>', 'FATAL', pexpect.TIMEOUT], timeout=30)
    if idx == 1:
        print("\n*** FATAL on line 1 ***")
        child.close()
        return False

    # Line 2: remaining 8 files + library
    # A:ADVMSG,A:ADVBYE,A:ADVSHT,A:ADVNPC,A:ADVPUZ,A:ADVDSP,A:ADVFND,A:ADVTDY,LB:BP2OTS/LB
    # Using LB: for library (system logical name)
    line2 = 'A:ADVMSG,A:ADVBYE,A:ADVSHT,A:ADVNPC,A:ADVPUZ,A:ADVDSP,A:ADVFND,A:ADVTDY,LB:BP2OTS/LB'
    print(f"\n>>> Line 2 ({len(line2)} chars): {line2}")
    child.sendline(line2)
    time.sleep(3)
    idx = child.expect(['TKB>', 'FATAL', pexpect.TIMEOUT], timeout=30)
    if idx == 1:
        print("\n*** FATAL on line 2 ***")
        child.close()
        return False

    # End input
    print("\n>>> Sending /")
    child.sendline('/')
    time.sleep(3)

    # Handle options and linking
    done = False
    iterations = 0
    while not done and iterations < 15:
        iterations += 1
        idx = child.expect([
            'Enter Options:',
            'TKB>',
            'FATAL',
            'undefined',
            'overflow',
            r'\$ ',
            pexpect.TIMEOUT
        ], timeout=300)

        print(f"\n*** Loop idx={idx} ***")

        if idx == 0:  # Enter Options
            child.sendline('')
            time.sleep(2)
        elif idx == 1:  # TKB>
            child.sendline('/')
            time.sleep(2)
        elif idx == 5:  # $
            done = True
        elif idx == 3:  # undefined
            print("\n*** Undefined symbols ***")
            child.expect('TKB>', timeout=60)
            child.sendline('/')
        elif idx == 4:  # overflow
            print("\n*** Address overflow - code too large ***")
            child.expect(['TKB>', r'\$ '], timeout=60)
            done = True
        elif idx in [2, 6]:
            print(f"\n*** Error idx={idx} ***")
            done = True

    time.sleep(2)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    child.sendline('DIR/SIZE A:ADVENT.TSK')
    child.expect(r'\$ ', timeout=15)

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** SUCCESS! ADVENT.TSK created! ***")
    else:
        print("\n*** ADVENT.TSK not found ***")

    dcl_cmd('DEASSIGN A:')
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
