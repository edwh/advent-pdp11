#!/usr/bin/env python3
"""Interactive ADVENT run - watch what happens."""

import socket
import time
import sys

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
    sys.stdout.flush()
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

    # Assign MSG:
    print("\n=== Setup ===")
    send_cmd(sock, 'ASSIGN DM1:[1,2] MSG:', wait=2)

    # Create log file properly
    send_cmd(sock, 'DELETE/NOCONFIRM MSG:LOG1.95', wait=1)
    send_cmd(sock, 'CREATE MSG:LOG1.95', wait=1)
    sock.sendall(b'Test log\r\x1a')
    time.sleep(1)
    send_cmd(sock, '', wait=1)

    # Check ADVENT.TSK exists
    print("\n=== Check TSK ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVENT.TSK', wait=2)

    # Run the game with longer wait
    print("\n=== Run ADVENT ===")
    result = send_cmd(sock, 'RUN DM1:[1,2]ADVENT', wait=3)

    # Wait for output
    for i in range(10):
        time.sleep(2)
        result = send_cmd(sock, '', wait=2)
        print(f"[{i}]", end='')
        sys.stdout.flush()

    # Check what it's waiting for
    print("\n=== Check state ===")
    # Try Ctrl+C to interrupt
    sock.sendall(b'\x03')
    time.sleep(2)
    result = send_cmd(sock, '', wait=2)

    print("\n=== Log ===")
    send_cmd(sock, 'TYPE MSG:LOG1.95', wait=3)

    sock.close()

if __name__ == '__main__':
    main()
