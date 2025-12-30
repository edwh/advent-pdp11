#!/usr/bin/env python3
"""Check DECnet status on RSTS/E."""

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

    print("\n=== Checking DECnet ===")
    send_cmd(sock, 'SHOW NETWORK', wait=3)
    send_cmd(sock, 'DIR SY:[0,*]*.*/SIZE', wait=3)
    send_cmd(sock, 'DIR SY:[*,*]NCP*.*', wait=2)
    send_cmd(sock, 'DIR SY:[*,*]NFT*.*', wait=2)
    send_cmd(sock, 'DIR SY:[*,*]FAL*.*', wait=2)

    sock.close()

if __name__ == '__main__':
    main()
