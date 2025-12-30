#!/usr/bin/env python3
"""Link with + syntax to combine files in overlays."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Link with + Syntax for Overlay Combining")
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
    if idx == 3:
        child.sendcontrol('c')
        time.sleep(1)
        idx = child.expect(['User:', r'\$ ', pexpect.TIMEOUT], timeout=15)

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
    child.sendline('DELETE/NOCONFIRM A:ADVENT.MAP')
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # Use LINK /STRUCTURE with I/D space and + syntax
    # The + at end continues the overlay, allowing multiple entries
    print("\n=== LINK /STRUCTURE with + syntax ===")
    child.sendline('LINK/BP2/CODE=DATA_SPACE/STRUCTURE/EXECUTABLE=A:ADVENT/MAP A:ADVENT')
    time.sleep(3)

    done = False
    overlay_stage = 0  # Which overlay group we're in
    file_stage = 0     # Which file within the overlay
    max_iter = 100
    iter_count = 0

    # Overlay groups matching ODL structure
    overlay_groups = [
        ['A:ADVINI', 'A:ADVOUT', 'A:ADVNOR'],      # Group A
        ['A:ADVCMD', 'A:ADVODD', 'A:ADVMSG'],      # Group B
        ['A:ADVBYE', 'A:ADVSHT', 'A:ADVNPC'],      # Group C
        ['A:ADVPUZ', 'A:ADVDSP', 'A:ADVFND'],      # Group D
        ['A:ADVTDY'],                               # Group E
    ]

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

        print(f"\n*** iter={iter_count} idx={idx} overlay={overlay_stage} file={file_stage} ***")

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
            if overlay_stage < len(overlay_groups):
                group = overlay_groups[overlay_stage]
                if file_stage < len(group):
                    # Send file with + if not last in group
                    f = group[file_stage]
                    if file_stage < len(group) - 1:
                        # Not last - continue this overlay with +
                        child.sendline(f + '+')
                        print(f"*** Sending: {f}+ ***")
                    else:
                        # Last in group - no +
                        child.sendline(f)
                        print(f"*** Sending: {f} (end of group) ***")
                        overlay_stage += 1
                        file_stage = -1  # Will be incremented to 0
                    file_stage += 1
                    time.sleep(2)
            else:
                # End overlays
                child.sendline('')
                time.sleep(2)

        elif idx == 4:  # $ - done
            done = True

        elif idx == 5:  # overflow
            print(f"\n*** OVERFLOW ***")
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
    print("\n=== Checking ADVENT.TSK ===")
    child.sendline('DIR/SIZE A:ADVENT.TSK')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** ADVENT.TSK created ***")

        # Run the game
        print("\n=== Testing ADVENT ===")
        child.sendline('RUN A:ADVENT')
        time.sleep(5)
        idx = child.expect(['#', 'Stop', 'Error', r'\$ ', pexpect.TIMEOUT], timeout=30)
        print(f"\n*** Run result: idx={idx} ***")

        if idx == 0:  # Game prompt
            print("\n*** Got game prompt! Testing commands ***")
            child.sendline('LOOK')
            time.sleep(3)
            idx2 = child.expect(['#', 'What', r'\$ ', pexpect.TIMEOUT], timeout=15)
            print(f"\n*** LOOK result: idx={idx2} ***")

            child.sendline('HELP')
            time.sleep(2)
            child.expect(['#', 'What', r'\$ ', pexpect.TIMEOUT], timeout=15)

            child.sendcontrol('c')
            time.sleep(1)

        child.expect([r'\$ ', 'User:', pexpect.TIMEOUT], timeout=15)
    else:
        print("\n*** ADVENT.TSK NOT created ***")

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
