#!/usr/bin/env python3
"""Use TKB directly with interactive input."""

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

    # Run TKB directly
    print("\n=== Run TKB ===")
    send_cmd(sock, 'RUN $TKB', wait=2)

    # TKB prompts with "TKB>"
    # Format: output/options=input,input,...
    # Use continuation with comma at end

    # First line: output spec and start of input
    send_cmd(sock, 'DM1:[1,2]ADVENT/FP,-', wait=2)
    # Continue with input files (comma means more to come)
    send_cmd(sock, 'DM1:[1,2]ADVENT,DM1:[1,2]ADVINI,-', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVOUT,DM1:[1,2]ADVNOR,-', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVCMD,DM1:[1,2]ADVODD,-', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVMSG,DM1:[1,2]ADVBYE,-', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVSHT,DM1:[1,2]ADVNPC,-', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVPUZ,DM1:[1,2]ADVDSP,-', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVFND,DM1:[1,2]ADVTDY,-', wait=2)
    # Library
    send_cmd(sock, 'LB:[1,1]BP2OTS/LB', wait=2)

    # End TKB input with /
    send_cmd(sock, '/', wait=30)

    time.sleep(30)
    send_cmd(sock, '', wait=5)

    # Exit TKB
    sock.sendall(b'\x1a')
    time.sleep(2)
    send_cmd(sock, '', wait=2)

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
