#!/usr/bin/env python3
"""Recreate ODL file and link the game."""

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

    # Delete old ODL
    print("\n=== Deleting old ODL ===")
    send_cmd(sock, 'DELETE/NOCONFIRM DM1:[1,2]ADVENT.ODL', wait=2)

    # Create new ODL file using CREATE
    print("\n=== Creating ADVENT.ODL ===")
    send_cmd(sock, 'CREATE DM1:[1,2]ADVENT.ODL', wait=1)

    # Send the ODL content line by line
    odl_lines = [
        '	.ROOT ADVENT-LIBR-*(SUBS)',
        'SUBS:	.FCTR *(INI,OUT,NOR,CMD,ODD,MSG,BYE,SHT,NPC,PUZ,DSP,FND,TDY)',
        'INI:	.FCTR DM1:[1,2]ADVINI',
        'OUT:	.FCTR DM1:[1,2]ADVOUT',
        'NOR:	.FCTR DM1:[1,2]ADVNOR',
        'CMD:	.FCTR DM1:[1,2]ADVCMD',
        'ODD:	.FCTR DM1:[1,2]ADVODD',
        'MSG:	.FCTR DM1:[1,2]ADVMSG',
        'BYE:	.FCTR DM1:[1,2]ADVBYE',
        'SHT:	.FCTR DM1:[1,2]ADVSHT',
        'NPC:	.FCTR DM1:[1,2]ADVNPC',
        'PUZ:	.FCTR DM1:[1,2]ADVPUZ',
        'DSP:	.FCTR DM1:[1,2]ADVDSP',
        'FND:	.FCTR DM1:[1,2]ADVFND',
        'TDY:	.FCTR DM1:[1,2]ADVTDY',
        'LIBR:	.FCTR LB:BP2OTS/LB',
        '	.END',
    ]

    for line in odl_lines:
        send_cmd(sock, line, wait=0.3)

    # End with Ctrl+Z
    sock.sendall(b'\x1a')
    time.sleep(2)
    send_cmd(sock, '', wait=1)

    # Verify ODL
    print("\n=== Verify ODL ===")
    send_cmd(sock, 'TYPE DM1:[1,2]ADVENT.ODL', wait=3)

    # Now link with TKB
    print("\n=== Running TKB ===")
    send_cmd(sock, 'RUN $TKB', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVENT/FP=DM1:[1,2]ADVENT.ODL', wait=3)
    send_cmd(sock, '/', wait=30)

    # Wait for link to complete
    time.sleep(10)
    send_cmd(sock, '', wait=2)

    # Exit TKB if needed
    sock.sendall(b'\x1a')
    time.sleep(2)
    send_cmd(sock, '', wait=1)

    # Check for TSK
    print("\n=== Check for ADVENT.TSK ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVENT.TSK', wait=2)

    # Try running
    print("\n=== Try running game ===")
    send_cmd(sock, 'RUN DM1:[1,2]ADVENT', wait=10)

    sock.close()
    print("\n=== Done ===")

if __name__ == '__main__':
    main()
