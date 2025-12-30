#!/usr/bin/env python3
"""Link with I/D space enabled for 128KB address space."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Link with I/D Space (128KB)")
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

    # Delete old TSK
    child.sendline('DELETE/NOCONFIRM A:ADVENT.TSK')
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # Try 1: Link with /CODE=DATA_SPACE for I/D space
    print("\n=== Test 1: LINK with /CODE=DATA_SPACE ===")
    child.sendline('LINK/BP2/CODE=DATA_SPACE/STRUCTURE/EXECUTABLE=A:ADVENT/MAP A:ADVENT')
    time.sleep(3)

    done = False
    overlay_num = 0
    max_iter = 40
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
            r'Invalid',         # 7
            pexpect.TIMEOUT     # 8
        ], timeout=60)

        print(f"\n*** iter={iter_count} idx={idx} ***")

        if idx == 0:  # Root COMMON
            child.sendline('')
            time.sleep(1)

        elif idx == 1:  # Root files
            child.sendline('A:ADVENT')
            time.sleep(2)

        elif idx == 2:  # Root PSECTs
            child.sendline('')
            time.sleep(1)

        elif idx == 3:  # Overlay
            overlay_num += 1
            if overlay_num == 1:
                child.sendline('A:ADVINI,A:ADVOUT,A:ADVNOR')
                time.sleep(2)
            elif overlay_num == 2:
                child.sendline('A:ADVCMD,A:ADVODD,A:ADVMSG')
                time.sleep(2)
            elif overlay_num == 3:
                child.sendline('A:ADVBYE,A:ADVSHT,A:ADVNPC')
                time.sleep(2)
            elif overlay_num == 4:
                child.sendline('A:ADVPUZ,A:ADVDSP,A:ADVFND')
                time.sleep(2)
            elif overlay_num == 5:
                child.sendline('A:ADVTDY')
                time.sleep(2)
            else:
                child.sendline('')
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

        elif idx == 7:  # Invalid qualifier
            print("\n*** Invalid qualifier - I/D not supported ***")
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)
            break

        elif idx == 8:  # Timeout
            child.sendline('')
            time.sleep(1)

    # Check result
    print("\n=== Checking ADVENT.TSK ===")
    child.sendline('DIR/SIZE A:ADVENT.TSK')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    created = False
    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** ADVENT.TSK created with I/D space ***")
        created = True

    if not created:
        print("\n*** First attempt failed, trying smaller overlays ***")
        # Try with more, smaller overlays
        dcl_cmd('DELETE/NOCONFIRM A:ADVENT.TSK')

        child.sendline('LINK/BP2/STRUCTURE/EXECUTABLE=A:ADVENT/MAP A:ADVENT')
        time.sleep(3)

        done = False
        overlay_num = 0
        iter_count = 0

        while not done and iter_count < 50:
            iter_count += 1
            idx = child.expect([
                r'Root COMMON',
                r'Root files',
                r'Root PSECTs',
                r'Overlay:',
                r'\$ ',
                r'overflow',
                r'undefined',
                pexpect.TIMEOUT
            ], timeout=60)

            print(f"\n*** iter={iter_count} idx={idx} ***")

            if idx == 0:  # Root COMMON
                child.sendline('')
                time.sleep(1)

            elif idx == 1:  # Root files
                # Put more in root to reduce overlay pressure
                child.sendline('A:ADVENT,A:ADVINI,A:ADVOUT')
                time.sleep(2)

            elif idx == 2:  # Root PSECTs
                child.sendline('')
                time.sleep(1)

            elif idx == 3:  # Overlay
                overlay_num += 1
                # Smaller overlay groups
                if overlay_num == 1:
                    child.sendline('A:ADVSHT,A:ADVFND')  # 5+6=11 blocks
                    time.sleep(2)
                elif overlay_num == 2:
                    child.sendline('A:ADVDSP,A:ADVNPC')  # 14+20=34 blocks
                    time.sleep(2)
                elif overlay_num == 3:
                    child.sendline('A:ADVBYE,A:ADVPUZ')  # 23+27=50 blocks
                    time.sleep(2)
                elif overlay_num == 4:
                    child.sendline('A:ADVTDY')  # 34 blocks
                    time.sleep(2)
                elif overlay_num == 5:
                    child.sendline('A:ADVMSG')  # 47 blocks
                    time.sleep(2)
                elif overlay_num == 6:
                    child.sendline('A:ADVODD')  # 50 blocks
                    time.sleep(2)
                elif overlay_num == 7:
                    child.sendline('A:ADVNOR')  # 98 blocks - alone
                    time.sleep(2)
                elif overlay_num == 8:
                    child.sendline('A:ADVCMD')  # 101 blocks - alone
                    time.sleep(2)
                else:
                    child.sendline('')
                    time.sleep(2)

            elif idx == 4:  # $
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

        # Check result again
        print("\n=== Checking ADVENT.TSK (2nd attempt) ===")
        child.sendline('DIR/SIZE A:ADVENT.TSK')
        time.sleep(2)
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

        if 'Total of' in child.before and 'blocks' in child.before:
            print("\n*** ADVENT.TSK created ***")
            created = True

    if created:
        # Try running
        print("\n=== Testing ADVENT ===")
        child.sendline('RUN A:ADVENT')
        time.sleep(5)
        idx = child.expect(['#', 'Stop', 'Error', r'\$ ', pexpect.TIMEOUT], timeout=30)
        print(f"\n*** Run result: idx={idx} ***")
        if idx == 0:
            child.sendline('LOOK')
            time.sleep(2)
            child.expect(['#', r'\$ ', pexpect.TIMEOUT], timeout=15)
            child.sendcontrol('c')
            time.sleep(1)
        child.expect([r'\$ ', 'User:', pexpect.TIMEOUT], timeout=15)

    # Re-login if needed
    idx = child.expect(['User:', r'\$ ', pexpect.TIMEOUT], timeout=5)
    if idx == 0:
        child.sendline('[1,2]')
        child.expect('Password:', timeout=10)
        child.sendline('Digital1977')
        child.expect([r'\$ ', 'Job'], timeout=15)

    dcl_cmd('DEASSIGN A:')
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
