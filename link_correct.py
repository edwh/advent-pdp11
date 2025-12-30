#!/usr/bin/env python3
"""LINK with correct syntax - just comma-separated files."""

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

    # Delete old TSK
    print("\n=== Delete old TSK ===")
    send_cmd(sock, 'DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK', wait=2)

    # LINK with correct syntax: LINK/BP2 file1,file2,file3...
    # Output name is derived from first file
    # Split into shorter commands - try with first 6 modules
    print("\n=== LINK/BP2 with correct syntax ===")

    # Try just the minimum needed first
    cmd = 'LINK/BP2 DM1:[1,2]ADVENT,DM1:[1,2]ADVINI'
    send_cmd(sock, cmd, wait=30)
    time.sleep(10)
    send_cmd(sock, '', wait=3)

    print("\n=== Check ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVENT.TSK', wait=2)

    # If that worked, try more files
    print("\n=== Try with more files ===")
    send_cmd(sock, 'DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK', wait=2)

    # Use continuation? Or try interactive mode
    # LINK/BP2 then prompts for Files:
    send_cmd(sock, 'LINK/BP2', wait=3)

    # Should prompt "Files:"
    send_cmd(sock, 'DM1:[1,2]ADVENT,DM1:[1,2]ADVINI,DM1:[1,2]ADVOUT', wait=5)
    send_cmd(sock, 'DM1:[1,2]ADVNOR,DM1:[1,2]ADVCMD,DM1:[1,2]ADVODD', wait=5)
    send_cmd(sock, 'DM1:[1,2]ADVMSG,DM1:[1,2]ADVBYE,DM1:[1,2]ADVSHT', wait=5)
    send_cmd(sock, 'DM1:[1,2]ADVNPC,DM1:[1,2]ADVPUZ,DM1:[1,2]ADVDSP', wait=5)
    send_cmd(sock, 'DM1:[1,2]ADVFND,DM1:[1,2]ADVTDY', wait=5)

    # Blank to end
    send_cmd(sock, '', wait=30)

    time.sleep(20)
    send_cmd(sock, '', wait=5)

    print("\n=== Final check ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVENT.TSK', wait=2)

    # Try running
    print("\n=== Try running ===")
    send_cmd(sock, 'RUN DM1:[1,2]ADVENT', wait=15)

    time.sleep(10)
    send_cmd(sock, '', wait=3)

    sock.close()

if __name__ == '__main__':
    main()
