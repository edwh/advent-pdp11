#!/usr/bin/env python3
"""Compile test program using BASIC/BP2."""

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

    # Exit help if stuck
    send_cmd(sock, '', wait=1)
    send_cmd(sock, '', wait=1)

    # Setup
    send_cmd(sock, 'ASSIGN DM1:[1,2] MSG:', wait=2)

    # Check for BP2IC2.TSK
    print("\n=== Check for BP2 compiler ===")
    send_cmd(sock, 'DIR SY:[1,2]BP2IC2.TSK', wait=2)
    send_cmd(sock, 'DIR DM0:[1,2]BP2IC2.TSK', wait=2)

    # Check if TEST.B2S exists
    print("\n=== Check test program ===")
    send_cmd(sock, 'DIR DM1:[1,2]TEST.*', wait=2)

    # Try compiling with BASIC/BP2
    print("\n=== Compile with BASIC/BP2 ===")
    result = send_cmd(sock, 'BASIC/BP2 DM1:[1,2]TEST', wait=30)

    time.sleep(5)
    send_cmd(sock, '', wait=2)

    # Check for OBJ file
    print("\n=== Check for OBJ ===")
    send_cmd(sock, 'DIR DM1:[1,2]TEST.*', wait=2)

    # Link
    print("\n=== Link ===")
    send_cmd(sock, 'LINK/BP2 DM1:[1,2]TEST', wait=20)

    time.sleep(3)
    send_cmd(sock, '', wait=2)

    # Check for TSK
    print("\n=== Check for TSK ===")
    send_cmd(sock, 'DIR DM1:[1,2]TEST.*', wait=2)

    # If TSK exists, run it
    print("\n=== Run ===")
    result = send_cmd(sock, 'RUN DM1:[1,2]TEST', wait=10)

    time.sleep(3)
    send_cmd(sock, '', wait=2)

    sock.close()

if __name__ == '__main__':
    main()
