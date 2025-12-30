#!/usr/bin/env python3
"""Use EDT on RSTS/E to change _DK1: to _DM1: in ADVINI.SUB."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Edit ADVINI.SUB using EDT - change _DK1: to _DM1:")
    print("=" * 60)

    child = pexpect.spawn('telnet localhost 2323', encoding='latin-1')
    child.logfile = sys.stdout

    try:
        child.expect('Connected to the PDP-11', timeout=10)
    except pexpect.TIMEOUT:
        print("ERROR: Could not connect to PDP-11")
        return False

    time.sleep(2)
    child.sendline('')
    time.sleep(1)

    # Handle login
    while True:
        idx = child.expect(['User:', r'\$ ', 'Job number', 'Password:', 'disabled', pexpect.TIMEOUT], timeout=30)
        if idx == 0:
            child.sendline('[1,2]')
        elif idx == 1:
            break
        elif idx == 2:
            child.sendline('')
        elif idx == 3:
            child.sendline('Digital1977')
        elif idx == 4:
            print("\n*** Logins disabled - waiting ***")
            time.sleep(10)
            child.sendline('')
        elif idx == 5:
            child.sendline('')
        time.sleep(1)

    print("\n*** Logged in ***")

    def dcl_cmd(cmd, timeout=30):
        child.sendline(cmd)
        child.expect(r'\$ ', timeout=timeout)
        time.sleep(0.5)

    # First, check the current ADVINI.SUB
    print("\n=== Current ADVINI.SUB contents (searching for _DK1:) ===")
    dcl_cmd('ASSIGN DM1:[1,2] A:')

    # Use SEARCH command to find _DK1: occurrences
    child.sendline('SEARCH A:ADVINI.SUB "_DK1:"')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    # Now use EDT to do the substitution
    # EDT has a SUBSTITUTE command: S/old/new/
    print("\n=== Starting EDT to edit ADVINI.SUB ===")
    child.sendline('EDIT/EDT A:ADVINI.SUB')
    time.sleep(2)

    # Wait for EDT prompt (usually *)
    idx = child.expect([r'\*', 'EDT>', '>', pexpect.TIMEOUT], timeout=15)
    print(f"\nEDT start result: idx={idx}")

    if idx in [0, 1, 2]:
        # EDT is running - do global substitution
        # In EDT line mode: SUBSTITUTE/string1/string2/WHOLE
        print("\n=== Performing global substitution ===")

        # EDT command to substitute all occurrences
        # Format: SUBSTITUTE/old/new/WHOLE (or S/old/new/W)
        child.sendline('SUBSTITUTE/_DK1:/_DM1:/WHOLE')
        time.sleep(2)
        idx2 = child.expect([r'\*', '>', 'substitution', 'Substitution', pexpect.TIMEOUT], timeout=30)
        print(f"\nSubstitute result: idx={idx2}")

        # Check what happened
        time.sleep(1)

        # Do it again to make sure all are caught (EDT may only do one per line)
        for _ in range(5):  # There are 5 occurrences
            child.sendline('SUBSTITUTE/_DK1:/_DM1:/WHOLE')
            time.sleep(1)
            child.expect([r'\*', '>', pexpect.TIMEOUT], timeout=10)

        # Save and exit EDT
        print("\n=== Saving and exiting EDT ===")
        child.sendline('EXIT')
        time.sleep(2)
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)
    else:
        print("\n*** Could not start EDT ***")

    # Verify the change
    print("\n=== Verifying change - searching for _DM1: ===")
    child.sendline('SEARCH A:ADVINI.SUB "_DM1:"')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    # Also check that _DK1: is gone
    print("\n=== Verifying _DK1: is gone ===")
    child.sendline('SEARCH A:ADVINI.SUB "_DK1:"')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    # Now recompile ADVINI.SUB
    print("\n=== Installing BP2RES library ===")
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Delete old OBJ
    print("\n=== Removing old ADVINI.OBJ ===")
    child.sendline('DELETE/NOCONFIRM A:ADVINI.OBJ')
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # Compile
    print("\n=== Compiling ADVINI.SUB ===")
    child.sendline('BASIC/BP2 A:ADVINI.SUB')
    time.sleep(10)
    idx = child.expect([r'\$ ', 'Error', 'error', pexpect.TIMEOUT], timeout=120)
    print(f"\n*** Compile result: idx={idx} ***")

    if idx in [1, 2]:
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    # Check new OBJ
    print("\n=== Checking new ADVINI.OBJ ===")
    dcl_cmd('DIRECTORY/SIZE/DATE A:ADVINI.OBJ')

    dcl_cmd('DEASSIGN A:')
    child.close()

    print("\n" + "=" * 60)
    print("DONE - Check output above for results")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
