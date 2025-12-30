#!/usr/bin/env python3
"""Incrementally link modules to find the overflow point."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Incremental Link Test")
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
    idx = child.expect(['User:', r'\$ ', 'Job number', '#'], timeout=30)
    if idx == 0:
        child.sendline('[1,2]')
        child.expect('Password:', timeout=10)
        child.sendline('Digital1977')
        idx2 = child.expect(['Job number', r'\$ '], timeout=15)
        if idx2 == 0:
            child.sendline('')
    elif idx == 2:
        child.sendline('')
    elif idx == 3:
        # In game still - send Ctrl+C
        child.sendcontrol('c')
        time.sleep(1)

    child.expect([r'\$ ', 'User:'], timeout=30)
    if 'User' in child.before or 'User' in child.after:
        child.sendline('[1,2]')
        child.expect('Password:', timeout=10)
        child.sendline('Digital1977')
        idx2 = child.expect(['Job number', r'\$ '], timeout=15)
        if idx2 == 0:
            child.sendline('')
        child.expect(r'\$ ', timeout=30)

    print("\n*** At $ prompt ***")

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

    # Create logical name
    dcl_cmd('ASSIGN DM1:[1,2] A:')

    # Try different module combinations to find maximum that will link
    # Order modules by size (blocks):
    # ADVSHT: 5, ADVFND: 6, ADVOUT: 6, ADVINI: 11, ADVDSP: 14
    # ADVNPC: 20, ADVBYE: 23, ADVPUZ: 27, ADVTDY: 34, ADVMSG: 47
    # ADVODD: 50, ADVENT: 76, ADVNOR: 98, ADVCMD: 101

    module_sets = [
        # Test 1: Base + command modules
        ('Test1_cmd', 'A:ADVENT,A:ADVINI,A:ADVOUT,A:ADVCMD'),
        # Test 2: Base + ADVNOR
        ('Test2_nor', 'A:ADVENT,A:ADVINI,A:ADVOUT,A:ADVNOR'),
        # Test 3: All small modules
        ('Test3_small', 'A:ADVENT,A:ADVINI,A:ADVOUT,A:ADVSHT,A:ADVFND,A:ADVDSP'),
        # Test 4: Small + medium
        ('Test4_med', 'A:ADVENT,A:ADVINI,A:ADVOUT,A:ADVNPC,A:ADVBYE,A:ADVPUZ'),
        # Test 5: Try without ADVENT (smaller main)
        ('Test5_no_advent', 'A:ADVINI,A:ADVOUT,A:ADVSHT,A:ADVFND,A:ADVNOR'),
    ]

    for name, modules in module_sets:
        print(f"\n=== {name}: {modules} ===")
        dcl_cmd(f'DELETE/NOCONFIRM A:{name}.TSK')

        child.sendline(f'LINK/BP2/EXECUTABLE=A:{name}/MAP A:{modules}')
        time.sleep(3)

        # Check for prompts or completion
        idx = child.expect([r'\$ ', 'Files:', 'overflow', 'undefined', pexpect.TIMEOUT], timeout=120)
        print(f"\n*** {name} result: idx={idx} ***")

        if idx == 1:  # Files prompt
            child.sendline('')  # Accept no more files
            time.sleep(2)
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=60)
        elif idx == 2:  # overflow
            print(f"*** {name} OVERFLOW ***")
            time.sleep(2)
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)
        elif idx == 3:  # undefined
            print(f"*** {name} has undefined symbols ***")
            time.sleep(2)
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

        # Check if TSK exists
        child.sendline(f'DIR/SIZE A:{name}.TSK')
        time.sleep(2)
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

        if 'Total of' in child.before and 'blocks' in child.before:
            print(f"\n*** {name}.TSK CREATED ***")
        else:
            print(f"\n*** {name}.TSK NOT CREATED ***")

    # Now try with /STRUCTURE for overlays
    print("\n=== Testing LINK /STRUCTURE ===")
    dcl_cmd('DELETE/NOCONFIRM A:ADVFULL.TSK')

    child.sendline('LINK/BP2/STRUCTURE/EXECUTABLE=A:ADVFULL/MAP A:')
    time.sleep(3)

    done = False
    state = 'start'
    overlay_num = 0

    while not done:
        idx = child.expect([
            r'Root COMMON',     # 0
            r'Root files',      # 1
            r'Root PSECTs',     # 2
            r'Overlay:',        # 3
            r'\$ ',             # 4
            r'overflow',        # 5
            r'undefined',       # 6
            pexpect.TIMEOUT     # 7
        ], timeout=60)

        print(f"\n*** Structure idx={idx}, state={state} ***")

        if idx == 0:  # Root COMMON
            child.sendline('')
            time.sleep(1)
            state = 'common_done'

        elif idx == 1:  # Root files
            # Minimal root
            child.sendline('A:ADVENT')
            time.sleep(2)
            state = 'root_done'

        elif idx == 2:  # Root PSECTs
            child.sendline('')
            time.sleep(1)
            state = 'psects_done'

        elif idx == 3:  # Overlay
            overlay_num += 1
            # Put each module group in separate overlay
            if overlay_num == 1:
                child.sendline('A:ADVINI,A:ADVOUT,A:ADVSHT,A:ADVFND')
                time.sleep(2)
            elif overlay_num == 2:
                child.sendline('A:ADVDSP,A:ADVNPC,A:ADVBYE,A:ADVPUZ')
                time.sleep(2)
            elif overlay_num == 3:
                child.sendline('A:ADVTDY,A:ADVMSG,A:ADVODD')
                time.sleep(2)
            elif overlay_num == 4:
                child.sendline('A:ADVNOR')
                time.sleep(2)
            elif overlay_num == 5:
                child.sendline('A:ADVCMD')
                time.sleep(2)
            else:
                child.sendline('')  # End
                time.sleep(2)

        elif idx == 4:  # $ - done
            done = True

        elif idx == 5:  # overflow
            print("\n*** OVERFLOW in overlay ***")
            time.sleep(2)
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)
            done = True

        elif idx == 6:  # undefined
            print("\n*** Undefined symbols ***")
            time.sleep(1)

        elif idx == 7:  # Timeout
            child.sendline('')
            time.sleep(1)

    # Check result
    child.sendline('DIR/SIZE A:ADVFULL.TSK')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** ADVFULL.TSK CREATED! ***")
    else:
        print("\n*** ADVFULL.TSK NOT CREATED ***")

    dcl_cmd('DEASSIGN A:')
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
