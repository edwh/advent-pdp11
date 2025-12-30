#!/usr/bin/env python3
"""Transfer source file using PIP/COPY and input redirection."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Transfer using PIP method")
    print("=" * 60)

    # Read the combined source file
    with open('/tmp/ALLSUBS.B2S', 'r') as f:
        content = f.read()

    print(f"Source file has {len(content)} characters")

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

    # Try using EDIT command which might handle multi-line input better
    print("\n=== Using EDIT to create file ===")
    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ALLSUBS.B2S')

    # Start TECO or EDT editor
    child.sendline('EDIT/TECO DM1:[1,2]ALLSUBS.B2S')
    time.sleep(2)

    # Check if TECO started (usually shows * prompt)
    idx = child.expect([r'\*', 'Error', pexpect.TIMEOUT], timeout=10)
    print(f"\n*** EDIT result: idx={idx} ***")

    if idx == 0:
        print("TECO started, entering text...")
        # TECO insert mode
        child.sendline('HK')  # Kill all text
        time.sleep(0.5)
        child.sendline('I')   # Insert mode

        # Disable logging during transfer
        child.logfile = None

        # Send lines one by one
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line = line.rstrip('\r')
            if len(line) > 250:
                line = line[:250]
            child.send(line + '\r\n')
            time.sleep(0.03)

            if (i + 1) % 100 == 0:
                print(f"  Sent {i+1}/{len(lines)} lines...")
            if (i + 1) % 500 == 0:
                time.sleep(1)

        # Re-enable logging
        child.logfile = sys.stdout

        # End insert mode (ESC ESC), exit (EX)
        print("\n  Ending insert mode...")
        child.sendcontrol('[')  # ESC
        time.sleep(0.5)
        child.sendcontrol('[')  # ESC
        time.sleep(1)

        # Save and exit
        child.sendline('EX')
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

        # Check file
        dcl_cmd('DIR/SIZE DM1:[1,2]ALLSUBS.B2S')

        if 'Total of' in child.before:
            print("\n*** File created! ***")
        else:
            print("\n*** File not created ***")

    else:
        print("TECO not available, trying different approach")

        # Try just concatenating existing OBJ files
        # Actually, let's try the simpler approach: compile fewer modules

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
