#!/usr/bin/env python3
"""Manually boot RSTS/E - improved version."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Manual RSTS/E Boot v2")
    print("=" * 60)

    # Connect to console port
    child = pexpect.spawn('telnet localhost 2322', encoding='latin-1')
    child.logfile = sys.stdout

    try:
        child.expect('Connected', timeout=10)
    except pexpect.TIMEOUT:
        print("\n*** Cannot connect ***")
        return False

    time.sleep(3)
    child.sendline('')
    time.sleep(2)

    # Keep trying until we get past date prompt
    for attempt in range(10):
        idx = child.expect(["Today's date?", "Current time?", "Start timesharing", "Option:", "User:", "OPR>", r'\$ ', pexpect.TIMEOUT], timeout=10)
        print(f"\n*** Attempt {attempt}, idx={idx} ***")

        if idx == 0:  # Today's date?
            print(">>> Sending date")
            child.sendline('1-JAN-92')
            time.sleep(2)
        elif idx == 1:  # Current time?
            print(">>> Sending time")
            child.sendline('12:00')
            time.sleep(2)
        elif idx == 2:  # Start timesharing?
            print(">>> Starting timesharing")
            child.sendline('Y')
            time.sleep(2)
        elif idx == 3:  # Option:
            print(">>> Accepting default option")
            child.sendline('')
            time.sleep(2)
        elif idx in [4, 5, 6]:  # User:, OPR>, or $
            print(">>> System ready!")
            break
        elif idx == 7:  # Timeout
            print(">>> Timeout, sending CR")
            child.sendline('')
            time.sleep(1)

    # Check if system is responding
    time.sleep(2)
    child.sendline('')
    time.sleep(2)

    print("\n*** Checking system state ***")
    idx = child.expect(["User:", "OPR>", r'\$ ', "date", pexpect.TIMEOUT], timeout=10)
    print(f"\n*** Final state idx={idx} ***")

    child.close()

    print("\n" + "=" * 60)
    print("Boot sequence completed")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
