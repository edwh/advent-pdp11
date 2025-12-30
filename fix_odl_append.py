#!/usr/bin/env python3
"""Fix ODL using APPEND instead of EDT."""

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

    # Create empty stream file using BASIC
    print("\n=== Creating stream format ODL via BASIC ===")
    send_cmd(sock, 'RUN $BASIC', wait=2)

    # Open file as stream output
    send_cmd(sock, 'OPEN "DM1:[1,2]ADVENT.ODL" FOR OUTPUT AS FILE #1%', wait=1)

    # Write ODL content
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
        # Escape quotes and send PRINT statement
        escaped = line.replace('"', '""')
        send_cmd(sock, f'PRINT #1%, "{escaped}"', wait=0.3)

    send_cmd(sock, 'CLOSE #1%', wait=1)
    send_cmd(sock, 'BYE', wait=1)

    # Wait for BASIC to exit
    time.sleep(2)
    send_cmd(sock, '', wait=1)

    # Check file format
    print("\n=== Check file format ===")
    send_cmd(sock, 'DIR/FULL DM1:[1,2]ADVENT.ODL', wait=2)

    # Check content
    print("\n=== Check content ===")
    send_cmd(sock, 'TYPE DM1:[1,2]ADVENT.ODL', wait=3)

    # Try TKB
    print("\n=== Try TKB ===")
    send_cmd(sock, 'RUN $TKB', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVENT/FP=DM1:[1,2]ADVENT.ODL', wait=3)
    send_cmd(sock, '/', wait=30)

    time.sleep(15)
    send_cmd(sock, '', wait=2)

    sock.sendall(b'\x1a')
    time.sleep(2)
    send_cmd(sock, '', wait=2)

    print("\n=== Check for TSK ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVENT.TSK', wait=2)

    sock.close()

if __name__ == '__main__':
    main()
