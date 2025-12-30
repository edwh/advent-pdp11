#!/usr/bin/env python3
"""Manually boot RSTS/E and complete setup."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Manual RSTS/E Boot")
    print("=" * 60)

    # Connect to console port
    child = pexpect.spawn('telnet localhost 2322', encoding='latin-1')
    child.logfile = sys.stdout

    try:
        child.expect('Connected', timeout=10)
    except pexpect.TIMEOUT:
        print("\n*** Cannot connect ***")
        return False

    time.sleep(2)
    child.sendline('')
    time.sleep(1)

    # Handle date prompt
    idx = child.expect(["Today's date?", "User:", "OPR>", r'\$ ', pexpect.TIMEOUT], timeout=30)
    print(f"\n*** idx={idx} ***")

    if idx == 0:
        child.sendline('1-JAN-92')
        time.sleep(1)
        idx2 = child.expect(["Current time?", "User:", pexpect.TIMEOUT], timeout=30)
        if idx2 == 0:
            child.sendline('12:00')
            time.sleep(1)

        # Handle timesharing prompts
        done = False
        while not done:
            idx3 = child.expect([
                "Start timesharing?",
                "Option:",
                "User:",
                r'\$ ',
                "OPR>",
                pexpect.TIMEOUT
            ], timeout=60)

            print(f"\n*** idx3={idx3} ***")

            if idx3 == 0:
                child.sendline('Y')
            elif idx3 == 1:
                child.sendline('')
            elif idx3 in [2, 3, 4]:
                done = True
            else:
                done = True

    # If we see User: prompt, we're at login
    time.sleep(3)
    print("\n*** System appears ready ***")

    child.close()

    print("\n" + "=" * 60)
    print("Boot sequence completed")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
