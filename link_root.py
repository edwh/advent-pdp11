#!/usr/bin/env python3
"""Link all files in root (no overlays) to test."""

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

    # Use LINK/BP2/STRUCTURE - put all subs in root
    print("\n=== LINK with all in root ===")
    send_cmd(sock, 'LINK/BP2/STRUCTURE DM1:[1,2]ADVENT', wait=3)

    # Root files: main program AND all subroutines together
    # Use + to continue on same line
    send_cmd(sock, 'DM1:[1,2]ADVENT,DM1:[1,2]ADVINI,DM1:[1,2]ADVOUT+', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVNOR,DM1:[1,2]ADVCMD,DM1:[1,2]ADVODD+', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVMSG,DM1:[1,2]ADVBYE,DM1:[1,2]ADVSHT+', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVNPC,DM1:[1,2]ADVPUZ,DM1:[1,2]ADVDSP+', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVFND,DM1:[1,2]ADVTDY', wait=3)

    # Root PSECTs - leave blank
    send_cmd(sock, '', wait=2)

    # No overlays - just blank
    send_cmd(sock, '', wait=5)

    # Wait for linking
    time.sleep(20)
    send_cmd(sock, '', wait=5)

    print("\n=== Check for TSK ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVENT.TSK', wait=2)

    # Try running
    print("\n=== Try running ===")
    send_cmd(sock, 'RUN DM1:[1,2]ADVENT', wait=10)

    # Capture output
    time.sleep(5)
    send_cmd(sock, '', wait=2)

    sock.close()

if __name__ == '__main__':
    main()
