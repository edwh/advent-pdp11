#!/usr/bin/env python3
"""Run ADVENT on fresh system."""

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

    # Show jobs - should be clean
    print("\n=== Jobs ===")
    result = send_cmd(sock, 'SYSTAT', wait=3)

    # Assign MSG:
    print("\n=== Setup ===")
    send_cmd(sock, 'ASSIGN DM1:[1,2] MSG:', wait=2)

    # Check if log file exists, create if needed
    send_cmd(sock, 'DIR MSG:LOG1.95', wait=2)

    # Create log file
    send_cmd(sock, 'CREATE MSG:LOG1.95', wait=1)
    sock.sendall(b'\x1a')
    time.sleep(1)
    send_cmd(sock, '', wait=1)

    # Check data files exist
    print("\n=== Check data files ===")
    send_cmd(sock, 'DIR MSG:ADVENT.DTA MSG:ADVENT.MON MSG:ADVENT.CHR MSG:BOARD.NTC MSG:MESSAG.NPC', wait=3)

    # Run the game
    print("\n=== Run ADVENT ===")
    result = send_cmd(sock, 'RUN DM1:[1,2]ADVENT', wait=15)

    time.sleep(5)
    send_cmd(sock, '', wait=3)

    # Try some commands
    print("\n=== Try commands ===")
    send_cmd(sock, 'look', wait=5)
    send_cmd(sock, 'help', wait=5)
    send_cmd(sock, 'n', wait=5)

    # Check log
    print("\n=== Check log ===")
    send_cmd(sock, 'TYPE MSG:LOG1.95', wait=3)

    sock.close()

if __name__ == '__main__':
    main()
