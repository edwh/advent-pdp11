#!/usr/bin/env python3
"""Test different date formats for RSTS/E."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("RSTS/E Date Format Test")
    print("=" * 60)

    # Different date formats to try
    dates_to_try = [
        "1-JAN-92",     # Standard format
        "01-JAN-92",    # With leading zero
        "1-JAN-1992",   # Full year
        "01-JAN-1992",  # Full year with leading zero
        "21-DEC-76",    # Different date
        "1-Jan-92",     # Mixed case
    ]

    for date in dates_to_try:
        print(f"\n\n{'='*40}")
        print(f"Testing date: {date}")
        print('='*40)

        # Connect to console port
        child = pexpect.spawn('telnet localhost 2322', encoding='latin-1')
        child.logfile = sys.stdout

        try:
            child.expect('Connected', timeout=10)
        except pexpect.TIMEOUT:
            print("\n*** Cannot connect ***")
            continue

        time.sleep(3)

        # Wait for date prompt
        child.expect("Today's date", timeout=30)
        time.sleep(1)

        # Send the date
        print(f"\n>>> Sending: {date}")
        child.send(date + '\r')
        time.sleep(3)

        # Check what we get back
        idx = child.expect(["Current time", "Today's date", "Invalid", pexpect.TIMEOUT], timeout=10)
        print(f"\n*** Result: idx={idx} ***")

        if idx == 0:
            print(f"\n*** SUCCESS! Date format '{date}' worked! ***")
            # Complete the boot
            child.send('12:00\r')
            time.sleep(2)
            idx2 = child.expect(["Start timesharing", "Option:", pexpect.TIMEOUT], timeout=30)
            if idx2 == 0:
                child.send('Y\r')
            time.sleep(2)
            for _ in range(5):
                idx3 = child.expect(["Option:", "User:", pexpect.TIMEOUT], timeout=10)
                if idx3 == 0:
                    child.send('\r')
                elif idx3 == 1:
                    print("\n*** Boot complete! ***")
                    child.close()
                    return True
                else:
                    break

        child.close()

    print("\n*** No date format worked ***")
    return False

if __name__ == '__main__':
    main()
