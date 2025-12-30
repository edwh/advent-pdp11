#!/usr/bin/env python3
"""Boot RSTS/E with careful timing and explicit CR handling."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Manual RSTS/E Boot - Careful Version")
    print("=" * 60)

    # Connect to console port
    child = pexpect.spawn('telnet localhost 2322', encoding='latin-1')
    child.logfile = sys.stdout

    try:
        child.expect('Connected', timeout=10)
    except pexpect.TIMEOUT:
        print("\n*** Cannot connect ***")
        return False

    print("\n*** Connected, waiting for date prompt ***")
    time.sleep(5)

    # Wait for the date prompt to appear
    child.expect("Today's date", timeout=30)
    print("\n*** Got date prompt, waiting before sending ***")
    time.sleep(2)

    # Send the date with explicit CR
    print("\n>>> Sending: 1-JAN-92<CR>")
    child.send('1-JAN-92\r')
    time.sleep(3)

    # Wait for time prompt
    print("\n*** Waiting for time prompt ***")
    idx = child.expect(["Current time", "Today's date", pexpect.TIMEOUT], timeout=30)
    print(f"\n*** idx={idx} ***")

    if idx == 0:
        print("\n*** Got time prompt, sending time ***")
        time.sleep(1)
        child.send('12:00\r')
        time.sleep(3)

        # Wait for timesharing prompt
        idx2 = child.expect(["Start timesharing", "Option:", pexpect.TIMEOUT], timeout=30)
        print(f"\n*** idx2={idx2} ***")

        if idx2 == 0:
            child.send('Y\r')
            time.sleep(3)

        # Handle option prompts
        for i in range(5):
            idx3 = child.expect(["Option:", "User:", "OPR>", pexpect.TIMEOUT], timeout=30)
            print(f"\n*** Option loop idx3={idx3} ***")
            if idx3 == 0:
                child.send('\r')
                time.sleep(1)
            elif idx3 in [1, 2]:
                print("\n*** System ready! ***")
                break
            else:
                break

    time.sleep(3)
    child.close()

    print("\n" + "=" * 60)
    print("Boot complete")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
