#!/usr/bin/env python3
"""Fix ODL file format by copying from working template."""

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

    print("\n=== Fixing ODL file format ===")

    # Delete our broken ODL
    print("\n--- Deleting broken ODL ---")
    send_cmd(sock, 'DELETE/NOCONFIRM DM1:[1,2]ADVENT.ODL', wait=2)

    # Copy a working ODL as template (this preserves file format)
    print("\n--- Copying template ODL ---")
    send_cmd(sock, 'COPY SY:[1,2]F77RST.ODL DM1:[1,2]ADVENT.ODL', wait=2)

    # Check the format now
    print("\n--- Check new file format ---")
    send_cmd(sock, 'DIR/FULL DM1:[1,2]ADVENT.ODL', wait=2)

    # Now use EDT to replace content (EDT preserves file format)
    print("\n--- Starting EDT to replace content ---")
    send_cmd(sock, 'EDT DM1:[1,2]ADVENT.ODL', wait=2)

    # Delete all existing content
    send_cmd(sock, 'DELETE WHOLE', wait=1)

    # Insert new ODL content line by line
    send_cmd(sock, 'INSERT', wait=0.5)

    odl_lines = [
        '\t.ROOT ADVENT-LIBR-*(SUBS)',
        'SUBS:\t.FCTR *(INI,OUT,NOR,CMD,ODD,MSG,BYE,SHT,NPC,PUZ,DSP,FND,TDY)',
        'INI:\t.FCTR DM1:[1,2]ADVINI',
        'OUT:\t.FCTR DM1:[1,2]ADVOUT',
        'NOR:\t.FCTR DM1:[1,2]ADVNOR',
        'CMD:\t.FCTR DM1:[1,2]ADVCMD',
        'ODD:\t.FCTR DM1:[1,2]ADVODD',
        'MSG:\t.FCTR DM1:[1,2]ADVMSG',
        'BYE:\t.FCTR DM1:[1,2]ADVBYE',
        'SHT:\t.FCTR DM1:[1,2]ADVSHT',
        'NPC:\t.FCTR DM1:[1,2]ADVNPC',
        'PUZ:\t.FCTR DM1:[1,2]ADVPUZ',
        'DSP:\t.FCTR DM1:[1,2]ADVDSP',
        'FND:\t.FCTR DM1:[1,2]ADVFND',
        'TDY:\t.FCTR DM1:[1,2]ADVTDY',
        'LIBR:\t.FCTR LB:BP2OTS/LB',
        '\t.END',
    ]

    for line in odl_lines:
        send_cmd(sock, line, wait=0.3)

    # End insert mode with Ctrl+Z and exit EDT
    sock.sendall(b'\x1a')  # Ctrl+Z to end insert
    time.sleep(1)
    send_cmd(sock, '', wait=0.5)
    send_cmd(sock, 'EXIT', wait=2)  # Save and exit

    # Verify content
    print("\n--- Verify content ---")
    send_cmd(sock, 'TYPE DM1:[1,2]ADVENT.ODL', wait=3)

    # Verify format preserved
    print("\n--- Verify format preserved ---")
    send_cmd(sock, 'DIR/FULL DM1:[1,2]ADVENT.ODL', wait=2)

    # Now try TKB
    print("\n--- Try TKB ---")
    send_cmd(sock, 'RUN $TKB', wait=2)
    send_cmd(sock, 'DM1:[1,2]ADVENT/FP=DM1:[1,2]ADVENT.ODL', wait=3)
    send_cmd(sock, '/', wait=30)

    time.sleep(10)
    send_cmd(sock, '', wait=2)

    # Exit TKB
    sock.sendall(b'\x1a')
    time.sleep(2)
    send_cmd(sock, '', wait=2)

    # Check for TSK
    print("\n--- Check for ADVENT.TSK ---")
    send_cmd(sock, 'DIR DM1:[1,2]ADVENT.TSK', wait=2)

    sock.close()

if __name__ == '__main__':
    main()
