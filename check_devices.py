#!/usr/bin/env python3
"""Check available devices and permissions."""

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

    # Show all devices
    print("\n=== Show devices ===")
    send_cmd(sock, 'SHOW DEVICES', wait=3)

    # Show our current job info
    print("\n=== Current job info ===")
    send_cmd(sock, 'SHOW JOB', wait=2)

    # Show account privileges
    print("\n=== Account privileges ===")
    send_cmd(sock, 'SHOW ACCOUNT', wait=2)

    # Check if KB11 is a valid device
    print("\n=== KB11 device ===")
    send_cmd(sock, 'SHOW DEVICE KB11:', wait=2)

    # Check KB devices
    print("\n=== All KB devices ===")
    for i in range(8):
        send_cmd(sock, f'SHOW DEVICE KB{i}:', wait=1)

    sock.close()

if __name__ == '__main__':
    main()
