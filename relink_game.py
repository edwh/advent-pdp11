#!/usr/bin/env python3
"""Relink ADVENT with the modified ADVINI."""

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

    # Delete old TSK
    print("\n=== Delete old TSK ===")
    send_cmd(sock, 'DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK', wait=2)

    # Link using LINK/BP2/CODE=DATA_SPACE/STRUCTURE
    # Same structure as before but with modified ADVINI
    print("\n=== Link game ===")
    send_cmd(sock, 'LINK/BP2/CODE=DATA_SPACE/STRUCTURE', wait=3)

    # ROOT files: ADVENT, ADVDSP, ADVFND, ADVOUT, ADVSHT
    send_cmd(sock, 'DM1:[1,2]ADVENT,DM1:[1,2]ADVDSP,DM1:[1,2]ADVFND,DM1:[1,2]ADVOUT,DM1:[1,2]ADVSHT', wait=3)

    # Root COMMON areas (blank)
    send_cmd(sock, '', wait=3)

    # Overlays - same structure as before
    overlays = [
        'DM1:[1,2]ADVINI!',    # Sibling overlay
        'DM1:[1,2]ADVNOR!',    # Sibling overlay
        'DM1:[1,2]ADVCMD!',    # Sibling overlay
        'DM1:[1,2]ADVODD!',    # Sibling overlay
        'DM1:[1,2]ADVMSG,DM1:[1,2]ADVTDY!',  # Combined overlay
        'DM1:[1,2]ADVBYE!',    # Sibling overlay
        'DM1:[1,2]ADVNPC!',    # Sibling overlay
        'DM1:[1,2]ADVPUZ',     # Last overlay (no !)
    ]

    for overlay in overlays:
        send_cmd(sock, overlay, wait=3)

    # End with blank line
    send_cmd(sock, '', wait=30)

    time.sleep(10)
    send_cmd(sock, '', wait=5)

    # Check TSK
    print("\n=== Check TSK ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVENT.TSK', wait=2)

    # Unrestrict KB devices
    print("\n=== Setup devices ===")
    for i in range(13):
        send_cmd(sock, f'SET DEVICE KB{i}: /NORESTRICT', wait=0.5)

    # Clear log
    send_cmd(sock, 'DELETE/NOCONFIRM MSG:LOG1.95', wait=1)
    send_cmd(sock, 'CREATE MSG:LOG1.95', wait=1)
    sock.sendall(b'\x1a')
    time.sleep(1)
    send_cmd(sock, '', wait=1)

    # Run the game
    print("\n=== Run ADVENT ===")
    result = send_cmd(sock, 'RUN DM1:[1,2]ADVENT', wait=15)

    time.sleep(5)
    send_cmd(sock, '', wait=3)

    # Try commands
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
