#!/usr/bin/env python3
"""Try LINK with files on command line using shorter paths."""

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

    # First, set default to DM1:[1,2] to use shorter paths
    print("\n=== Set default device/directory ===")
    send_cmd(sock, 'SET DEFAULT DM1:[1,2]', wait=2)

    # Delete old TSK
    print("\n=== Delete old TSK ===")
    send_cmd(sock, 'DELETE/NOCONFIRM ADVENT.TSK', wait=2)

    # Try LINK with shorter file specs (just names, no device/dir)
    # Split into multiple LINK commands? No, that won't work.
    # Try using @ command file?

    # Actually, try using wildcard for ADV*.OBJ
    print("\n=== Try LINK with wildcard ===")
    send_cmd(sock, 'LINK/BP2 ADVENT=ADVENT,ADV*.OBJ', wait=30)

    time.sleep(10)
    send_cmd(sock, '', wait=3)

    print("\n=== Check for TSK ===")
    send_cmd(sock, 'DIR ADVENT.TSK', wait=2)

    # If that didn't work, try explicit short names
    print("\n=== Try explicit short names ===")
    send_cmd(sock, 'DELETE/NOCONFIRM ADVENT.TSK', wait=2)

    # Main + first batch of subs
    send_cmd(sock, 'LINK/BP2 ADVENT=ADVENT,ADVINI,ADVOUT,ADVNOR,ADVCMD,ADVODD', wait=30)
    time.sleep(10)
    send_cmd(sock, '', wait=3)

    print("\n=== Check ===")
    send_cmd(sock, 'DIR ADVENT.TSK', wait=2)

    sock.close()

if __name__ == '__main__':
    main()
