#!/usr/bin/env python3
"""Link with all subs in ONE overlay segment."""

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

    # Delete old TSK
    print("\n=== Delete old TSK ===")
    send_cmd(sock, 'DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK', wait=2)

    # LINK/BP2/STRUCTURE output-file
    print("\n=== LINK/BP2/STRUCTURE ===")
    send_cmd(sock, 'LINK/BP2/STRUCTURE DM1:[1,2]ADVENT', wait=3)

    # Root COMMON areas: leave blank (uses default)
    send_cmd(sock, '', wait=2)

    # Overlay: ALL subroutines in ONE overlay (comma separated = same overlay)
    # Use + to continue line
    send_cmd(sock, 'DM1:[1,2]ADVINI,DM1:[1,2]ADVOUT,DM1:[1,2]ADVNOR+', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVCMD,DM1:[1,2]ADVODD,DM1:[1,2]ADVMSG+', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVBYE,DM1:[1,2]ADVSHT,DM1:[1,2]ADVNPC+', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVPUZ,DM1:[1,2]ADVDSP,DM1:[1,2]ADVFND+', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVTDY', wait=3)

    # End overlays with blank line
    send_cmd(sock, '', wait=5)

    # Wait for linking
    time.sleep(30)
    send_cmd(sock, '', wait=5)

    print("\n=== Check for TSK ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVENT.TSK', wait=2)

    # Try running
    print("\n=== Try running ===")
    send_cmd(sock, 'RUN DM1:[1,2]ADVENT', wait=15)

    time.sleep(5)
    send_cmd(sock, '', wait=2)

    sock.close()

if __name__ == '__main__':
    main()
