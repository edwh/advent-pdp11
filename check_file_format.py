#!/usr/bin/env python3
"""Check file format attributes on RSTS/E."""

import socket
import time

def send_cmd(sock, cmd, wait=1.0):
    sock.sendall((cmd + '\r').encode('latin-1'))
    time.sleep(wait)
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

    time.sleep(2)
    send_cmd(sock, '', wait=2)
    send_cmd(sock, '[1,2]', wait=2)
    send_cmd(sock, 'Digital1977', wait=2)
    send_cmd(sock, '', wait=2)

    print("\n=== Checking file formats ===")

    # Check working ODL file (F77RST.ODL is a system file that should work)
    print("\n--- System ODL file format ---")
    send_cmd(sock, 'DIR/FULL SY:[1,2]F77RST.ODL', wait=3)

    # Check our ODL file format
    print("\n--- Our ODL file format ---")
    send_cmd(sock, 'DIR/FULL DM1:[1,2]ADVENT.ODL', wait=3)

    # Check the source ODL file format
    print("\n--- Source ODL file format ---")
    send_cmd(sock, 'DIR/FULL DM1:[1,3]ADVENT.ODL', wait=3)

    # Try copying the working system ODL as a test
    print("\n--- Copy system ODL syntax check ---")
    send_cmd(sock, 'TYPE SY:[1,2]F77RST.ODL', wait=3)

    # Maybe we need to use a different method to create ODL
    # Let's see what tools are available
    print("\n--- Looking for ODL creation tools ---")
    send_cmd(sock, 'HELP TKB', wait=5)

    sock.close()

if __name__ == '__main__':
    main()
