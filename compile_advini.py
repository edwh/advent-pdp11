#!/usr/bin/env python3
"""Try different approaches to compile ADVINI."""

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

    # Setup
    send_cmd(sock, 'ASSIGN DM1:[1,2] MSG:', wait=2)

    # Check current files
    print("\n=== Current files ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVINI.*', wait=2)

    # Try renaming to .B2S
    print("\n=== Copy to .B2S ===")
    send_cmd(sock, 'COPY DM1:[1,2]ADVINI.SUB DM1:[1,2]ADVINI.B2S', wait=2)

    # Try compiling with full path and extension
    print("\n=== Try compile with .SUB extension ===")
    send_cmd(sock, 'BASIC/BP2 DM1:[1,2]ADVINI.SUB', wait=30)
    time.sleep(3)
    send_cmd(sock, '', wait=2)

    print("\n=== Try compile with .B2S extension ===")
    send_cmd(sock, 'BASIC/BP2 DM1:[1,2]ADVINI.B2S', wait=30)
    time.sleep(3)
    send_cmd(sock, '', wait=2)

    # Check OBJ
    print("\n=== Check OBJ files ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVINI.*', wait=2)

    # If still no luck, show what BP2COM uses
    print("\n=== Help on BASIC/BP2 ===")
    send_cmd(sock, 'HELP BASIC/BP2', wait=5)
    send_cmd(sock, '', wait=2)

    sock.close()

if __name__ == '__main__':
    main()
