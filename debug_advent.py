#!/usr/bin/env python3
"""Debug ADVENT initialization - check files and run the game."""

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

    # Check all data files that ADVINI needs
    print("\n=== Check required data files ===")
    files_needed = [
        'ADVENT.DTA',
        'ADVENT.MON',
        'BOARD.NTC',
        'ADVENT.CHR',
        'MESSAG.NPC'
    ]
    for f in files_needed:
        send_cmd(sock, f'DIR/FULL DM1:[1,2]{f}', wait=2)

    # Check LOG1.95
    print("\n=== Check log file ===")
    send_cmd(sock, 'DIR DM1:[1,2]LOG1.95', wait=2)

    # Create it if it doesn't exist
    print("\n=== Create log file if needed ===")
    send_cmd(sock, 'CREATE DM1:[1,2]LOG1.95', wait=1)
    sock.sendall(b'\x1a')  # Ctrl+Z
    time.sleep(1)
    send_cmd(sock, '', wait=1)

    # Check MSG: logical assignment
    print("\n=== Check MSG: logical ===")
    send_cmd(sock, 'SHOW LOGICAL MSG:', wait=2)

    # Assign MSG: to DM1:[1,2]
    print("\n=== Assign MSG: ===")
    send_cmd(sock, 'ASSIGN DM1:[1,2] MSG:', wait=2)
    send_cmd(sock, 'SHOW LOGICAL MSG:', wait=2)

    # Check if game TSK exists
    print("\n=== Check game executable ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVENT.TSK', wait=2)

    # Run the game
    print("\n=== Run ADVENT ===")
    result = send_cmd(sock, 'RUN DM1:[1,2]ADVENT', wait=10)

    # Wait and try some commands
    time.sleep(5)
    send_cmd(sock, '', wait=3)

    # Try game commands
    print("\n=== Try commands ===")
    send_cmd(sock, 'help', wait=3)
    send_cmd(sock, 'look', wait=3)
    send_cmd(sock, 'quit', wait=3)

    # Check log file for errors
    print("\n=== Check error log ===")
    send_cmd(sock, 'TYPE DM1:[1,2]LOG1.95', wait=3)

    sock.close()

if __name__ == '__main__':
    main()
