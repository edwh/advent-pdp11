#!/usr/bin/env python3
"""Try BP2 BUILD command instead of TKB."""

import socket
import time

def send_cmd(sock, cmd, wait=1.0):
    """Send command and wait for response."""
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

    print("=== Connected ===")
    time.sleep(2)
    send_cmd(sock, '', wait=2)
    send_cmd(sock, '[1,2]', wait=2)
    send_cmd(sock, 'Digital1977', wait=2)
    send_cmd(sock, '', wait=2)
    print("\n=== Logged in ===")

    # Start BP2 compiler
    print("\n=== Starting BP2 ===")
    send_cmd(sock, 'RUN $BP2IC2', wait=3)

    # Use BUILD command - it handles TKB internally
    # BUILD output=main,sub1,sub2,...
    print("\n=== Trying BUILD command ===")
    build_cmd = 'BUILD DM1:[1,2]ADVENT=DM1:[1,2]ADVENT,DM1:[1,2]ADVINI,DM1:[1,2]ADVOUT,DM1:[1,2]ADVNOR,DM1:[1,2]ADVCMD,DM1:[1,2]ADVODD,DM1:[1,2]ADVMSG,DM1:[1,2]ADVBYE,DM1:[1,2]ADVSHT,DM1:[1,2]ADVNPC,DM1:[1,2]ADVPUZ,DM1:[1,2]ADVDSP,DM1:[1,2]ADVFND,DM1:[1,2]ADVTDY'
    send_cmd(sock, build_cmd, wait=60)

    # Wait for build to complete
    time.sleep(30)
    send_cmd(sock, '', wait=5)

    # Exit BP2
    print("\n=== Exiting BP2 ===")
    sock.sendall(b'\x1a')  # Ctrl+Z
    time.sleep(2)
    send_cmd(sock, '', wait=2)

    # Check for TSK
    print("\n=== Check for ADVENT.TSK ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVENT.TSK', wait=2)

    # If that didn't work, try simpler approach - link without overlays
    print("\n=== Try TKB without ODL (simple link) ===")
    send_cmd(sock, 'RUN $TKB', wait=2)
    # Just link main + all subs directly
    send_cmd(sock, 'DM1:[1,2]ADVENT/FP,DM1:[1,2]ADVENT/-SP', wait=3)
    send_cmd(sock, 'DM1:[1,2]ADVINI,DM1:[1,2]ADVOUT,DM1:[1,2]ADVNOR', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVCMD,DM1:[1,2]ADVODD,DM1:[1,2]ADVMSG', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVBYE,DM1:[1,2]ADVSHT,DM1:[1,2]ADVNPC', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVPUZ,DM1:[1,2]ADVDSP,DM1:[1,2]ADVFND', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVTDY', wait=2)
    send_cmd(sock, 'LB:[1,1]BP2OTS/LB', wait=2)
    send_cmd(sock, '/', wait=30)

    time.sleep(20)
    send_cmd(sock, '', wait=3)

    # Exit TKB
    sock.sendall(b'\x1a')
    time.sleep(2)
    send_cmd(sock, '', wait=2)

    # Check again
    print("\n=== Check for ADVENT.TSK again ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVENT.TSK', wait=2)

    sock.close()
    print("\n=== Done ===")

if __name__ == '__main__':
    main()
