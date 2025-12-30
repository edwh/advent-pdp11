#!/usr/bin/env python3
"""Link with exact ODL structure from original."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Link with Exact ODL Structure")
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

    # Use LINK /STRUCTURE with exact structure from ODL
    # ODL structure:
    # Root: ADVENT
    # OVLY: *(A,B,C,D,E) means 5 parallel overlays
    # A: ADVINI,ADVOUT,ADVNOR
    # B: ADVCMD,ADVODD,ADVMSG
    # C: ADVBYE,ADVSHT,ADVNPC
    # D: ADVPUZ,ADVDSP,ADVFND
    # E: ADVTDY

    print("\n=== LINK /STRUCTURE ===")
    child.sendline('LINK/BP2/STRUCTURE/EXECUTABLE=A:ADVENT/MAP A:ADVENT')
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
            r'illegal',         # 7
            pexpect.TIMEOUT     # 8
        ], timeout=60)

        print(f"\n*** iter={iter_count} idx={idx} ***")

        if idx == 0:  # Root COMMON
            child.sendline('')
            time.sleep(1)

        elif idx == 1:  # Root files
            # Root = ADVENT only (matching ODL)
            child.sendline('A:ADVENT')
            time.sleep(2)

        elif idx == 2:  # Root PSECTs
            child.sendline('')
            time.sleep(1)

        elif idx == 3:  # Overlay
            overlay_num += 1
            # Exact structure from ODL:
            if overlay_num == 1:
                # A: ADVINI,ADVOUT,ADVNOR
                child.sendline('A:ADVINI,A:ADVOUT,A:ADVNOR')
                time.sleep(2)
            elif overlay_num == 2:
                # B: ADVCMD,ADVODD,ADVMSG
                child.sendline('A:ADVCMD,A:ADVODD,A:ADVMSG')
                time.sleep(2)
            elif overlay_num == 3:
                # C: ADVBYE,ADVSHT,ADVNPC
                child.sendline('A:ADVBYE,A:ADVSHT,A:ADVNPC')
                time.sleep(2)
            elif overlay_num == 4:
                # D: ADVPUZ,ADVDSP,ADVFND
                child.sendline('A:ADVPUZ,A:ADVDSP,A:ADVFND')
                time.sleep(2)
            elif overlay_num == 5:
                # E: ADVTDY
                child.sendline('A:ADVTDY')
                time.sleep(2)
            else:
                # End overlays
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
            print("\n*** Undefined symbols (continuing) ***")
            time.sleep(1)

        elif idx == 7:  # illegal
            print("\n*** Illegal something ***")
            time.sleep(1)

        elif idx == 8:  # Timeout
            child.sendline('')
            time.sleep(1)

    # Check result
    print("\n=== Checking result ===")
    child.sendline('DIR/SIZE A:ADVENT.TSK')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** SUCCESS! ADVENT.TSK created! ***")

        # Try running it
        print("\n=== Testing ADVENT ===")
        child.sendline('RUN A:ADVENT')
        time.sleep(5)
        idx = child.expect(['#', ':', 'Stop', 'Error', 'trap', r'\$ ', pexpect.TIMEOUT], timeout=30)
        print(f"\n*** Run result: idx={idx} ***")

        if idx == 0:  # # prompt
            print("\n*** Got game prompt! ***")
            child.sendline('LOOK')
            time.sleep(2)
            child.expect(['#', r'\$ ', pexpect.TIMEOUT], timeout=15)
            child.sendcontrol('c')
            time.sleep(1)
        elif idx == 1:  # : prompt
            print("\n*** Got : prompt ***")
            child.sendcontrol('c')
            time.sleep(1)
        elif idx == 2:  # Stop
            print("\n*** Stop at line ***")
            child.sendcontrol('c')
            time.sleep(1)

        child.expect([r'\$ ', 'User:', pexpect.TIMEOUT], timeout=15)
    else:
        print("\n*** ADVENT.TSK NOT created ***")
        # Check map
        child.sendline('TYPE A:ADVENT.MAP')
        time.sleep(3)
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

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
