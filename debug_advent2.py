#!/usr/bin/env python3
"""Debug ADVENT - clean up old jobs, check errors."""

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
    sock.settimeout(60)

    time.sleep(2)
    send_cmd(sock, '', wait=2)
    send_cmd(sock, '[1,2]', wait=2)
    send_cmd(sock, 'Digital1977', wait=2)
    send_cmd(sock, '', wait=2)

    # Show all jobs
    print("\n=== Show jobs ===")
    send_cmd(sock, 'SYSTAT', wait=3)

    # Kill old ADVENT jobs - need to be careful here
    # Let's first try just running fresh

    # Assign MSG: first
    print("\n=== Setup ===")
    send_cmd(sock, 'ASSIGN DM1:[1,2] MSG:', wait=2)

    # Check error log
    print("\n=== Error log before run ===")
    send_cmd(sock, 'TYPE MSG:LOG1.95', wait=2)

    # Clear error log
    print("\n=== Clear error log ===")
    send_cmd(sock, 'DELETE/NOCONFIRM MSG:LOG1.95', wait=2)
    send_cmd(sock, 'CREATE MSG:LOG1.95', wait=1)
    sock.sendall(b'\x1a')
    time.sleep(1)
    send_cmd(sock, '', wait=1)

    # Check data file format - maybe the files need to be proper format
    print("\n=== Check ADVENT.DTA format ===")
    send_cmd(sock, 'DIR/FULL MSG:ADVENT.DTA', wait=2)

    # Try to read first record
    print("\n=== Try BASIC to check file ===")
    send_cmd(sock, 'BASIC', wait=3)
    send_cmd(sock, '', wait=2)

    # Simple BASIC program to check file
    send_cmd(sock, 'OPEN "DM1:[1,2]ADVENT.DTA" AS FILE #1', wait=2)
    send_cmd(sock, 'FIELD #1, 512 AS A$', wait=2)
    send_cmd(sock, 'GET #1', wait=2)
    send_cmd(sock, 'PRINT LEN(A$)', wait=2)
    send_cmd(sock, 'CLOSE #1', wait=2)

    # Exit BASIC
    send_cmd(sock, 'EXIT', wait=2)

    # Run the game
    print("\n=== Run ADVENT ===")
    send_cmd(sock, 'RUN DM1:[1,2]ADVENT', wait=10)

    time.sleep(3)
    send_cmd(sock, '', wait=2)

    # Check error log after run
    print("\n=== Error log after run ===")
    send_cmd(sock, 'TYPE MSG:LOG1.95', wait=3)

    sock.close()

if __name__ == '__main__':
    main()
