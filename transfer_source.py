#!/usr/bin/env python3
"""Transfer combined source file to RSTS/E using CREATE command."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Transfer ALLSUBS.B2S to RSTS/E")
    print("=" * 60)

    # Read the combined source file
    with open('/tmp/ALLSUBS.B2S', 'r') as f:
        lines = f.readlines()

    print(f"Source file has {len(lines)} lines")

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

    # Delete existing file
    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ALLSUBS.B2S')

    # Start CREATE
    print("\n=== Creating ALLSUBS.B2S ===")
    child.sendline('CREATE DM1:[1,2]ALLSUBS.B2S')
    time.sleep(2)

    # Send lines - limit logging to avoid flooding output
    child.logfile = None  # Disable logging during transfer

    for i, line in enumerate(lines):
        # Clean the line - remove trailing newline/CR
        line = line.rstrip('\r\n')

        # RSTS/E line length limit is usually 512 chars, but terminal might be 80
        # Split long lines if needed (though BASIC source might have issues)
        if len(line) > 250:
            # Truncate very long lines
            line = line[:250]

        child.sendline(line)

        # Small delay every line to prevent buffer overflow
        time.sleep(0.05)

        # Progress indicator every 100 lines
        if (i + 1) % 100 == 0:
            print(f"  Transferred {i+1}/{len(lines)} lines...")

        # Longer pause every 500 lines
        if (i + 1) % 500 == 0:
            time.sleep(1)

    # Re-enable logging
    child.logfile = sys.stdout

    # End file with Ctrl+Z
    print(f"\n  Transferred all {len(lines)} lines, sending Ctrl+Z...")
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=30)

    # Check file was created
    print("\n=== Checking file ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ALLSUBS.B2S')

    if 'Total of' in child.before:
        print("\n*** File created successfully! ***")

        # Now compile it
        print("\n=== Compiling ALLSUBS.B2S ===")
        # Install BP2RES first
        child.sendline('RUN $UTLMGR')
        child.expect('Utlmgr>', timeout=15)
        child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
        child.expect('Utlmgr>', timeout=15)
        child.sendcontrol('z')
        child.expect(r'\$ ', timeout=10)

        # Compile with longer timeout
        child.sendline('COMPILE DM1:[1,2]ALLSUBS.B2S')
        # This might take a while
        done = False
        while not done:
            idx = child.expect([r'\$ ', 'Error', 'error', pexpect.TIMEOUT], timeout=600)
            if idx == 0:
                done = True
                print("\n*** Compilation complete ***")
            elif idx in [1, 2]:
                print("\n*** Compilation error ***")
                done = True
            else:
                print("  Still compiling...")

        # Check for .OBJ file
        dcl_cmd('DIR/SIZE DM1:[1,2]ALLSUBS.OBJ')

        if 'Total of' in child.before:
            print("\n*** ALLSUBS.OBJ created! ***")

            # Now link with just 2 files
            print("\n=== Linking ADVENT.TSK ===")
            dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK')

            child.sendline('RUN $TKB')
            child.expect('TKB>', timeout=15)
            time.sleep(1)

            # Line 1: output=main,allsubs + continuation
            child.sendline('DM1:[1,2]ADVENT/FP=DM1:[1,2]ADVENT,DM1:[1,2]ALLSUBS/-')
            time.sleep(3)
            child.expect('TKB>', timeout=30)

            # Line 2: library only
            child.sendline('SY:[1,1]BP2OTS/LB')
            time.sleep(3)
            child.expect('TKB>', timeout=30)

            # End input
            child.sendline('/')
            time.sleep(3)

            # Handle options
            done2 = False
            iterations = 0
            while not done2 and iterations < 10:
                iterations += 1
                idx = child.expect(['Enter Options:', 'TKB>', 'overflow', r'\$ ', pexpect.TIMEOUT], timeout=300)
                if idx == 0:
                    child.sendline('')
                elif idx == 1:
                    child.sendline('/')
                elif idx == 3:
                    done2 = True
                elif idx == 2:
                    print("\n*** Address overflow ***")
                    done2 = True

            time.sleep(2)

            # Check for ADVENT.TSK
            print("\n=== Checking for ADVENT.TSK ===")
            dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

            if 'Total of' in child.before and 'blocks' in child.before:
                print("\n*** SUCCESS! ADVENT.TSK created! ***")
            else:
                print("\n*** ADVENT.TSK not found ***")

    else:
        print("\n*** File not created ***")

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
