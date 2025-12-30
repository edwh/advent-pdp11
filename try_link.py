#!/usr/bin/env python3
"""Try LINK command instead of TKB."""

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

    # Check LINK command
    print("\n=== HELP LINK ===")
    send_cmd(sock, 'HELP LINK', wait=5)

    # Exit any submenus
    send_cmd(sock, '', wait=1)
    send_cmd(sock, '', wait=1)

    # Check for BP2 LINK
    print("\n=== HELP LINK/BP2 ===")
    send_cmd(sock, 'HELP LINK /BP2', wait=3)
    send_cmd(sock, '', wait=1)

    # Try direct LINK command without ODL
    print("\n=== Try LINK/BP2 ===")
    # LINK/BP2 output=input1,input2,...
    link_cmd = 'LINK/BP2 DM1:[1,2]ADVENT=DM1:[1,2]ADVENT,DM1:[1,2]ADVINI,DM1:[1,2]ADVOUT,DM1:[1,2]ADVNOR,DM1:[1,2]ADVCMD,DM1:[1,2]ADVODD,DM1:[1,2]ADVMSG,DM1:[1,2]ADVBYE,DM1:[1,2]ADVSHT,DM1:[1,2]ADVNPC,DM1:[1,2]ADVPUZ,DM1:[1,2]ADVDSP,DM1:[1,2]ADVFND,DM1:[1,2]ADVTDY'
    send_cmd(sock, link_cmd, wait=60)

    time.sleep(30)
    send_cmd(sock, '', wait=5)

    # Check result
    print("\n=== Check for TSK ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVENT.TSK', wait=2)

    # If that didn't work, try with /STRUCTURE for overlays
    print("\n=== Try with /STRUCTURE ===")
    send_cmd(sock, 'LINK/BP2/STRUCTURE DM1:[1,2]ADVENT=DM1:[1,2]ADVENT,DM1:[1,2]ADVINI,DM1:[1,2]ADVOUT,DM1:[1,2]ADVNOR,DM1:[1,2]ADVCMD,DM1:[1,2]ADVODD,DM1:[1,2]ADVMSG,DM1:[1,2]ADVBYE,DM1:[1,2]ADVSHT,DM1:[1,2]ADVNPC,DM1:[1,2]ADVPUZ,DM1:[1,2]ADVDSP,DM1:[1,2]ADVFND,DM1:[1,2]ADVTDY', wait=60)

    time.sleep(30)
    send_cmd(sock, '', wait=5)

    print("\n=== Final check ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVENT.TSK', wait=2)

    sock.close()

if __name__ == '__main__':
    main()
