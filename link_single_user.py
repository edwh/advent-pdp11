#!/usr/bin/env python3
"""Link and test single-user ADVENT."""

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

    # Wait for system to be ready and show banner
    time.sleep(5)

    # Read any initial output
    sock.setblocking(False)
    try:
        data = sock.recv(4096)
        print(data.decode('latin-1', errors='replace'), end='')
    except BlockingIOError:
        pass
    sock.setblocking(True)

    # Now do login - wait for User: prompt
    time.sleep(3)
    send_cmd(sock, '', wait=3)  # Press Enter to wake up
    send_cmd(sock, '[1,2]', wait=3)
    send_cmd(sock, 'Digital1977', wait=3)

    # Skip past "Jobs detached" menu by pressing Enter
    send_cmd(sock, '', wait=3)

    # Setup
    send_cmd(sock, 'ASSIGN DM1:[1,2] MSG:', wait=3)

    # Check that the single-user files exist
    print("\n=== Check source files ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVENT.B2S', wait=3)
    send_cmd(sock, 'DIR DM1:[1,2]ADVINI.OBJ', wait=3)

    # Compile ADVENT.B2S if OBJ doesn't exist
    print("\n=== Compile ADVENT.B2S ===")
    send_cmd(sock, 'BASIC/BP2 DM1:[1,2]ADVENT.B2S', wait=60)
    time.sleep(5)
    send_cmd(sock, '', wait=3)

    print("\n=== Check OBJ files ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVENT.OBJ', wait=3)

    # Delete old TSK and link
    print("\n=== Link game ===")
    send_cmd(sock, 'DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK', wait=3)
    send_cmd(sock, 'LINK/BP2/CODE=DATA_SPACE/STRUCTURE', wait=5)
    send_cmd(sock, 'DM1:[1,2]ADVENT,DM1:[1,2]ADVDSP,DM1:[1,2]ADVFND,DM1:[1,2]ADVOUT,DM1:[1,2]ADVSHT', wait=5)
    send_cmd(sock, '', wait=5)  # Root COMMON
    send_cmd(sock, 'DM1:[1,2]ADVINI!', wait=5)
    send_cmd(sock, 'DM1:[1,2]ADVNOR!', wait=5)
    send_cmd(sock, 'DM1:[1,2]ADVCMD!', wait=5)
    send_cmd(sock, 'DM1:[1,2]ADVODD!', wait=5)
    send_cmd(sock, 'DM1:[1,2]ADVMSG,DM1:[1,2]ADVTDY!', wait=5)
    send_cmd(sock, 'DM1:[1,2]ADVBYE!', wait=5)
    send_cmd(sock, 'DM1:[1,2]ADVNPC!', wait=5)
    send_cmd(sock, 'DM1:[1,2]ADVPUZ', wait=5)
    send_cmd(sock, '', wait=60)  # End - wait longer for linking

    time.sleep(10)
    send_cmd(sock, '', wait=5)

    print("\n=== Check TSK ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVENT.TSK', wait=3)

    # Run
    print("\n=== Run game ===")
    result = send_cmd(sock, 'RUN DM1:[1,2]ADVENT', wait=30)

    time.sleep(10)
    send_cmd(sock, '', wait=5)

    # Try commands
    print("\n=== Try commands ===")
    send_cmd(sock, 'LOOK', wait=10)
    send_cmd(sock, 'HELP', wait=10)
    send_cmd(sock, 'NORTH', wait=10)

    sock.close()

if __name__ == '__main__':
    main()
