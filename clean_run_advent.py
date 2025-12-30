#!/usr/bin/env python3
"""Clean up old ADVENT jobs and run fresh."""

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

    # Kill all ADVENT jobs - we need to kill them by job number
    # From previous output: jobs 14, 15, 17, 19, 20, 22 are ADVENT
    print("\n=== Kill old ADVENT jobs ===")
    for job in [14, 15, 17, 19, 20, 22]:
        send_cmd(sock, f'KILL {job}', wait=1)

    # Wait for them to die
    time.sleep(2)

    # Check jobs again
    print("\n=== Check jobs ===")
    send_cmd(sock, 'SYSTAT', wait=3)

    # Kill more if needed - scan for ADVENT
    print("\n=== Kill any remaining ===")
    # Try killing jobs 13-25 that might be ADVENT
    for job in range(13, 30):
        send_cmd(sock, f'KILL {job}', wait=0.5)

    time.sleep(2)

    # Show clean state
    print("\n=== Final job state ===")
    result = send_cmd(sock, 'SYSTAT', wait=3)

    # Assign MSG:
    print("\n=== Setup ===")
    send_cmd(sock, 'ASSIGN DM1:[1,2] MSG:', wait=2)

    # Clear log
    send_cmd(sock, 'DELETE/NOCONFIRM MSG:LOG1.95', wait=1)
    send_cmd(sock, 'CREATE MSG:LOG1.95', wait=1)
    sock.sendall(b'\x1a')
    time.sleep(1)
    send_cmd(sock, '', wait=1)

    # Try running ADVENT
    print("\n=== Run ADVENT ===")
    result = send_cmd(sock, 'RUN DM1:[1,2]ADVENT', wait=15)

    time.sleep(5)
    send_cmd(sock, '', wait=3)

    # Try some commands
    print("\n=== Try commands ===")
    send_cmd(sock, 'look', wait=5)
    send_cmd(sock, 'help', wait=5)

    # Check log
    print("\n=== Check log ===")
    send_cmd(sock, 'TYPE MSG:LOG1.95', wait=3)

    sock.close()

if __name__ == '__main__':
    main()
