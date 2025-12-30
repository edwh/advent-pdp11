#!/usr/bin/env python3
"""Copy file from paper tape reader in RSTS/E."""

import pexpect
import sys
import time

def main():
    dest_file = sys.argv[1] if len(sys.argv) > 1 else "DM1:[1,2]ADVINI.SUB"

    print("=" * 60)
    print(f"Copying from paper tape (PR:) to {dest_file}")
    print("=" * 60)

    child = pexpect.spawn('telnet localhost 2323', encoding='latin-1')
    child.logfile = sys.stdout

    try:
        child.expect('Connected to the PDP-11', timeout=10)
    except pexpect.TIMEOUT:
        print("ERROR: Could not connect")
        return False

    time.sleep(2)
    child.sendline('')
    time.sleep(1)

    # Login
    for _ in range(10):
        idx = child.expect(['User:', r'\$ ', 'Job number', 'Password:', pexpect.TIMEOUT], timeout=30)
        if idx == 0:
            child.sendline('[1,2]')
        elif idx == 1:
            break
        elif idx == 2:
            child.sendline('')
        elif idx == 3:
            child.sendline('Digital1977')
        elif idx == 4:
            child.sendline('')
        time.sleep(1)

    print("\n*** Logged in ***")

    def dcl_cmd(cmd, timeout=30):
        child.sendline(cmd)
        child.expect(r'\$ ', timeout=timeout)
        time.sleep(0.5)

    # Delete existing file if present
    print(f"\n=== Deleting existing {dest_file} ===")
    child.sendline(f'DELETE/NOCONFIRM {dest_file}')
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # Copy from paper tape reader
    print(f"\n=== Copying from PR: to {dest_file} ===")
    child.sendline(f'COPY PR: {dest_file}')
    time.sleep(5)

    idx = child.expect([r'\$ ', 'error', 'Error', 'No such device', pexpect.TIMEOUT], timeout=60)
    print(f"\nCopy result: idx={idx}")

    if idx in [1, 2, 3]:
        print("\n*** Error during copy ***")
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

        # Try PIP instead
        print("\n=== Trying PIP PR: ===")
        child.sendline(f'PIP {dest_file}=PR:')
        time.sleep(5)
        idx2 = child.expect([r'\$ ', 'error', 'Error', pexpect.TIMEOUT], timeout=60)
        print(f"\nPIP result: idx={idx2}")

    # Verify the file exists
    print(f"\n=== Verifying {dest_file} ===")
    dcl_cmd(f'DIR {dest_file}')

    # Show file contents to verify
    print("\n=== First few lines of file ===")
    child.sendline(f'TYPE {dest_file}')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    child.close()
    print("\n*** Done ***")
    return True

if __name__ == '__main__':
    main()
