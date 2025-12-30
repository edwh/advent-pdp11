#!/usr/bin/env python3
"""Create and compile a test program to debug ADVINI issues."""

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

    # Setup
    send_cmd(sock, 'ASSIGN DM1:[1,2] MSG:', wait=2)

    # Unrestrict KB devices
    print("\n=== Unrestrict devices ===")
    for i in range(13):
        send_cmd(sock, f'SET DEVICE KB{i}: /NORESTRICT', wait=0.5)

    # Create a test program
    print("\n=== Create test program ===")
    send_cmd(sock, 'CREATE DM1:[1,2]TEST.B2S', wait=1)

    # Write a simple test program
    test_program = [
        '1\tON ERROR GOTO 1000',
        '10\tPRINT "Test program starting..."',
        '20\tJ$=SYS(CHR$(12%))',
        '21\tPRINT "SYS 12 OK"',
        '30\tRUN.ACC$="["+NUM1$(ASCII(RIGHT(J$,6%)))+","+NUM1$(ASCII(RIGHT(J$,5%)))+"]"',
        '31\tPRINT "RUN.ACC$ = ";RUN.ACC$',
        '40\tPRINT "Trying to open _KB11:..."',
        '50\tOPEN "_KB11:" AS FILE #1%',
        '51\tPRINT "KB11 opened OK!"',
        '60\tPRINT "Trying data files..."',
        '70\tOPEN "_DM1:"+RUN.ACC$+"ADVENT.DTA" AS FILE #3%',
        '71\tPRINT "ADVENT.DTA opened OK!"',
        '80\tCLOSE #1',
        '81\tCLOSE #3',
        '90\tPRINT "All tests passed!"',
        '100\tSTOP',
        '1000\tPRINT "ERROR ";ERR;" at line ";ERL',
        '1010\tSTOP',
        '32767\tEND',
    ]

    for line in test_program:
        sock.sendall((line + '\r').encode('latin-1'))
        time.sleep(0.3)

    # End file
    sock.sendall(b'\x1a')
    time.sleep(1)
    send_cmd(sock, '', wait=1)

    # Show the file
    print("\n=== Show test program ===")
    send_cmd(sock, 'TYPE DM1:[1,2]TEST.B2S', wait=3)

    # Compile it
    print("\n=== Compile ===")
    send_cmd(sock, 'BP2COM DM1:[1,2]TEST', wait=10)

    # Link it
    print("\n=== Link ===")
    send_cmd(sock, 'LINK/BP2 DM1:[1,2]TEST', wait=10)

    # Run it
    print("\n=== Run ===")
    result = send_cmd(sock, 'RUN DM1:[1,2]TEST', wait=10)

    time.sleep(3)
    send_cmd(sock, '', wait=2)

    sock.close()

if __name__ == '__main__':
    main()
