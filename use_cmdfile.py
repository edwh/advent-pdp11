#!/usr/bin/env python3
"""Create and use a command file for LINK."""

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

    # Create a command file with the LINK command
    print("\n=== Create command file ===")
    send_cmd(sock, 'CREATE DM1:[1,2]DOLINK.COM', wait=1)

    # Write LINK command - use continuation if DCL supports it
    # DCL uses - at end of line for continuation
    send_cmd(sock, '$ DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK', wait=0.5)
    send_cmd(sock, '$ LINK/BP2 DM1:[1,2]ADVENT,-', wait=0.5)
    send_cmd(sock, ' DM1:[1,2]ADVINI,DM1:[1,2]ADVOUT,DM1:[1,2]ADVNOR,-', wait=0.5)
    send_cmd(sock, ' DM1:[1,2]ADVCMD,DM1:[1,2]ADVODD,DM1:[1,2]ADVMSG,-', wait=0.5)
    send_cmd(sock, ' DM1:[1,2]ADVBYE,DM1:[1,2]ADVSHT,DM1:[1,2]ADVNPC,-', wait=0.5)
    send_cmd(sock, ' DM1:[1,2]ADVPUZ,DM1:[1,2]ADVDSP,DM1:[1,2]ADVFND,-', wait=0.5)
    send_cmd(sock, ' DM1:[1,2]ADVTDY', wait=0.5)
    send_cmd(sock, '$ DIR DM1:[1,2]ADVENT.TSK', wait=0.5)
    send_cmd(sock, '$ EXIT', wait=0.5)

    # End with Ctrl+Z
    sock.sendall(b'\x1a')
    time.sleep(1)
    send_cmd(sock, '', wait=1)

    # Show the command file
    print("\n=== Show command file ===")
    send_cmd(sock, 'TYPE DM1:[1,2]DOLINK.COM', wait=2)

    # Run the command file
    print("\n=== Execute command file ===")
    send_cmd(sock, '@DM1:[1,2]DOLINK.COM', wait=60)

    time.sleep(30)
    send_cmd(sock, '', wait=5)

    # Check result
    print("\n=== Check TSK ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVENT.TSK', wait=2)

    # Try running
    print("\n=== Try running ===")
    send_cmd(sock, 'RUN DM1:[1,2]ADVENT', wait=15)

    time.sleep(10)
    send_cmd(sock, '', wait=5)

    sock.close()

if __name__ == '__main__':
    main()
