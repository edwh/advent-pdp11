#!/usr/bin/env python3
"""Try using PIP to create proper file format."""

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

    # Check available commands
    print("\n=== Looking for file format tools ===")
    send_cmd(sock, 'HELP SET FILE', wait=3)

    # Check PIP options
    print("\n=== Check PIP ===")
    send_cmd(sock, 'HELP PIP', wait=3)

    # Try using FIT (File Interchange Tool) if available
    print("\n=== Check FIT ===")
    send_cmd(sock, 'DIR SY:FIT*.*', wait=2)

    # Maybe we can use COPY with special options?
    print("\n=== Check COPY options ===")
    send_cmd(sock, 'HELP COPY', wait=5)

    # Another idea: use LINK/BP2 instead of TKB
    # BP2 has a BUILD command that handles linking
    print("\n=== Check LINK command ===")
    send_cmd(sock, 'HELP LINK', wait=5)

    sock.close()

if __name__ == '__main__':
    main()
