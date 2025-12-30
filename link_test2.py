#!/usr/bin/env python3
"""Test linking with proper short filenames."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Link Test with Short Filenames")
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

    # Install BP2RES
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Create logical name
    dcl_cmd('ASSIGN DM1:[1,2] A:')

    # Test different module combinations
    # Use short 6-char names
    tests = [
        ('TST1', 'A:ADVENT,A:ADVINI,A:ADVOUT,A:ADVCMD'),
        ('TST2', 'A:ADVENT,A:ADVINI,A:ADVOUT,A:ADVNOR'),
        ('TST3', 'A:ADVENT,A:ADVINI,A:ADVOUT,A:ADVSHT'),
    ]

    for name, modules in tests:
        print(f"\n=== {name}: {modules} ===")
        child.sendline(f'DELETE/NOCONFIRM A:{name}.TSK')
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

        child.sendline(f'LINK/BP2/EXECUTABLE=A:{name}/MAP {modules}')
        time.sleep(5)

        idx = child.expect([r'\$ ', 'overflow', 'undefined', pexpect.TIMEOUT], timeout=120)
        print(f"\n*** {name} result: idx={idx} ***")

        if idx == 1:
            print(f"*** {name} OVERFLOW ***")
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)
        elif idx == 2:
            print(f"*** {name} undefined symbols ***")
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

        # Check if TSK exists
        child.sendline(f'DIR/SIZE A:{name}.TSK')
        time.sleep(2)
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

        if 'Total of' in child.before and 'blocks' in child.before:
            print(f"\n*** {name}.TSK CREATED ***")
        else:
            print(f"\n*** {name}.TSK NOT CREATED ***")

    # Now try to link with all modules using /STRUCTURE
    print("\n=== Full link with /STRUCTURE ===")
    child.sendline('DELETE/NOCONFIRM A:ADVGAM.TSK')
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # LINK /STRUCTURE requires filename at start
    child.sendline('LINK/BP2/STRUCTURE/EXECUTABLE=A:ADVGAM/MAP A:ADVENT')
    time.sleep(3)

    done = False
    overlay_num = 0
    max_iter = 30
    iter_count = 0

    while not done and iter_count < max_iter:
        iter_count += 1
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

        print(f"\n*** iter={iter_count} idx={idx} ***")

        if idx == 0:  # Root COMMON
            child.sendline('')
            time.sleep(1)

        elif idx == 1:  # Root files
            # Root: main program only
            child.sendline('A:ADVENT')
            time.sleep(2)

        elif idx == 2:  # Root PSECTs
            child.sendline('')
            time.sleep(1)

        elif idx == 3:  # Overlay
            overlay_num += 1
            if overlay_num == 1:
                child.sendline('A:ADVINI,A:ADVOUT')
                time.sleep(2)
            elif overlay_num == 2:
                child.sendline('A:ADVSHT,A:ADVFND,A:ADVDSP')
                time.sleep(2)
            elif overlay_num == 3:
                child.sendline('A:ADVNPC,A:ADVBYE,A:ADVPUZ')
                time.sleep(2)
            elif overlay_num == 4:
                child.sendline('A:ADVTDY,A:ADVMSG')
                time.sleep(2)
            elif overlay_num == 5:
                child.sendline('A:ADVODD')
                time.sleep(2)
            elif overlay_num == 6:
                child.sendline('A:ADVNOR')
                time.sleep(2)
            elif overlay_num == 7:
                child.sendline('A:ADVCMD')
                time.sleep(2)
            else:
                child.sendline('')  # End overlays
                time.sleep(2)

        elif idx == 4:  # $ - done
            done = True

        elif idx == 5:  # overflow
            print(f"\n*** OVERFLOW at overlay {overlay_num} ***")
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
    print("\n=== Checking result ===")
    child.sendline('DIR/SIZE A:ADVGAM.TSK')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** ADVGAM.TSK CREATED! ***")

        # Try running it
        print("\n=== Testing ADVGAM ===")
        child.sendline('RUN A:ADVGAM')
        time.sleep(5)
        idx = child.expect(['#', ':', r'\$ ', 'trap', 'Error', pexpect.TIMEOUT], timeout=30)
        print(f"\n*** Run result: idx={idx} ***")
        if idx in [0, 1]:
            # Game prompt
            child.sendline('LOOK')
            time.sleep(2)
            child.expect(['#', ':', r'\$ ', pexpect.TIMEOUT], timeout=15)
            child.sendcontrol('c')
            time.sleep(1)
        child.expect([r'\$ ', 'User:', pexpect.TIMEOUT], timeout=15)
    else:
        print("\n*** ADVGAM.TSK NOT CREATED ***")
        # Check map
        child.sendline('TYPE A:ADVGAM.MAP')
        time.sleep(3)
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    # Re-login if needed
    idx = child.expect(['User:', r'\$ ', pexpect.TIMEOUT], timeout=5)
    if idx == 0:
        child.sendline('[1,2]')
        child.expect('Password:', timeout=10)
        child.sendline('Digital1977')
        child.expect([r'\$ ', 'Job'], timeout=15)
        if 'Job' in child.before:
            child.sendline('')
            child.expect(r'\$ ', timeout=10)

    dcl_cmd('DEASSIGN A:')
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
