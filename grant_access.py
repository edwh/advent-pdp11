#!/usr/bin/env python3
"""Try to grant access to KB11 device."""

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

    # Try to allocate or set permissions on KB11
    print("\n=== Try ALLOCATE KB11 ===")
    send_cmd(sock, 'ALLOCATE KB11:', wait=2)

    # Try SET DEVICE
    print("\n=== Try SET DEVICE KB11 ===")
    send_cmd(sock, 'SET DEVICE KB11:/UNRESTRICTED', wait=2)
    send_cmd(sock, 'SET DEVICE KB11: /NORESTRICTED', wait=2)

    # Check device status
    print("\n=== Check KB11 ===")
    send_cmd(sock, 'SHOW DEVICE KB11:', wait=2)

    # Help on SET DEVICE
    print("\n=== Help SET DEVICE ===")
    send_cmd(sock, 'HELP SET DEVICE', wait=3)

    # Try to run ADVENT with MSG: assigned
    print("\n=== Run ADVENT ===")
    send_cmd(sock, 'ASSIGN DM1:[1,2] MSG:', wait=2)
    send_cmd(sock, 'RUN DM1:[1,2]ADVENT', wait=10)

    time.sleep(3)
    send_cmd(sock, '', wait=2)

    sock.close()

if __name__ == '__main__':
    main()
