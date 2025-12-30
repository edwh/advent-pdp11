#!/usr/bin/env python3
"""Find the BP2 compiler."""

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

    # Search for BP2 related files
    print("\n=== Search for BP2 compiler ===")
    send_cmd(sock, 'DIR SY:[0,1]BP2*.*', wait=3)
    send_cmd(sock, 'DIR DM0:[0,1]BP2*.*', wait=3)
    send_cmd(sock, 'DIR DM0:[0,11]BP2*.*', wait=3)

    # Search for compilers in general
    print("\n=== Search for compilers ===")
    send_cmd(sock, 'DIR SY:[0,1]*.TSK', wait=3)

    # Check help
    print("\n=== Help on BASIC ===")
    send_cmd(sock, 'HELP BASIC', wait=5)
    send_cmd(sock, '', wait=2)

    # Try different compiler commands
    print("\n=== Try compiler commands ===")
    send_cmd(sock, 'BP2', wait=2)
    send_cmd(sock, 'BASIC2', wait=2)
    send_cmd(sock, 'B2C', wait=2)

    sock.close()

if __name__ == '__main__':
    main()
