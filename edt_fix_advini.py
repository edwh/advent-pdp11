#!/usr/bin/env python3
"""Use EDT to fix device references in ADVINI.SUB on RSTS/E."""

import pexpect
import sys
import time

def main():
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

    # First check current content
    print("\n=== Current ADVINI.SUB content ===")
    child.sendline('TYPE DM1:[1,3]ADVINI.SUB')
    time.sleep(5)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    # Make a backup
    print("\n=== Making backup ===")
    child.sendline('COPY DM1:[1,3]ADVINI.SUB DM1:[1,3]ADVINI.BAK')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # Start EDT
    print("\n=== Starting EDT ===")
    child.sendline('EDT DM1:[1,3]ADVINI.SUB')
    time.sleep(2)

    # EDT might give various prompts
    idx = child.expect([r'\*', 'Command:', pexpect.TIMEOUT], timeout=10)
    print(f"\nEDT prompt idx: {idx}")

    if idx == 2:
        print("*** Could not start EDT ***")
        child.sendline('')
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)
        child.close()
        return False

    print("\n*** In EDT ***")

    # EDT uses SUBSTITUTE command: S/old/new/
    # WHOLE means apply to entire buffer
    # Let's try the substitute command
    print("\n=== Substitute _DK1: with _DM1: ===")
    child.sendline('SUBSTITUTE/_DK1:/_DM1:/WHOLE')
    time.sleep(3)
    idx = child.expect([r'\*', 'substitution', 'no match', 'No match', pexpect.TIMEOUT], timeout=15)
    print(f"\nSubstitute result idx: {idx}")

    # Show what we have
    print("\n=== Type whole buffer ===")
    child.sendline('TYPE WHOLE')
    time.sleep(5)
    child.expect([r'\*', pexpect.TIMEOUT], timeout=30)

    # Save and exit
    print("\n=== EXIT (save) ===")
    child.sendline('EXIT')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    # Verify the change
    print("\n=== Verify changed file ===")
    child.sendline('TYPE DM1:[1,3]ADVINI.SUB')
    time.sleep(5)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    # Compare with backup
    print("\n=== Compare with backup ===")
    child.sendline('DIFFERENCES DM1:[1,3]ADVINI.SUB DM1:[1,3]ADVINI.BAK')
    time.sleep(5)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    child.close()
    print("\n*** Done ***")
    return True

if __name__ == '__main__':
    main()
