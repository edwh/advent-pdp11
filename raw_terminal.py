#!/usr/bin/env python3
"""Raw socket terminal to RSTS/E - no telnet protocol overhead."""

import socket
import time
import sys

def send_and_wait(sock, cmd, wait=1.0, expect=None):
    """Send command and wait for response."""
    sock.sendall((cmd + '\r').encode('latin-1'))
    time.sleep(wait)

    # Read all available data
    sock.setblocking(False)
    response = b''
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
    except BlockingIOError:
        pass
    sock.setblocking(True)

    text = response.decode('latin-1', errors='replace')
    print(text, end='')
    return text

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 2323))
    sock.settimeout(30)

    print("=== Connected ===")

    # Initial connection - read banner
    time.sleep(2)
    send_and_wait(sock, '', wait=2)

    # Login sequence
    send_and_wait(sock, '[1,2]', wait=2)
    send_and_wait(sock, 'Digital1977', wait=2)
    send_and_wait(sock, '', wait=2)  # Accept new job

    print("\n=== Logged in ===")

    # Now we have direct control - let's check the ODL file
    print("\n=== Checking ADVENT.ODL ===")
    send_and_wait(sock, 'TYPE DM1:[1,3]ADVENT.ODL', wait=5)

    # Check if there's an ODL template we can use
    print("\n=== Looking for ODL files ===")
    send_and_wait(sock, 'DIR DM1:[1,3]*.ODL', wait=3)
    send_and_wait(sock, 'DIR SY:[1,2]*.ODL', wait=3)

    sock.close()
    print("\n=== Done ===")

if __name__ == '__main__':
    main()
