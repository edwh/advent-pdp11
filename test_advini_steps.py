#!/usr/bin/env python3
"""Test each step of ADVINI to find what fails."""

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
    print("\n=== Setup ===")
    for i in range(13):
        send_cmd(sock, f'SET DEVICE KB{i}: /NORESTRICT', wait=0.5)

    # Run BASIC to test each step
    print("\n=== Start BASIC ===")
    send_cmd(sock, 'BASIC', wait=3)

    # Enter immediate mode and test step by step
    # First, set up error handling
    test_lines = [
        '10 ON ERROR GOTO 1000',
        '20 PRINT "Step 1: SYS CHR$(12)"',
        '21 J$=SYS(CHR$(12%))',
        '22 PRINT "Step 1 OK"',
        '30 PRINT "Step 2: RUN.ACC$ computation"',
        '31 RUN.ACC$="["+NUM1$(ASCII(RIGHT(J$,6%)))+","+NUM1$(ASCII(RIGHT(J$,5%)))+"]"',
        '32 PRINT "RUN.ACC$ = ";RUN.ACC$',
        '40 PRINT "Step 3: OPEN _KB11:"',
        '41 OPEN "_KB11:" AS FILE #1%',
        '42 PRINT "Step 3 OK - KB11 opened"',
        '50 PRINT "Step 4: OPEN data file"',
        '51 OPEN "_DM1:"+RUN.ACC$+"ADVENT.DTA" AS FILE #3%, MODE 257%',
        '52 PRINT "Step 4 OK - ADVENT.DTA opened"',
        '60 PRINT "Step 5: OPEN ADVENT.MON"',
        '61 OPEN "_DM1:"+RUN.ACC$+"ADVENT.MON" AS FILE #5%, ACCESS MODIFY, ALLOW NONE',
        '62 PRINT "Step 5 OK"',
        '70 PRINT "All steps completed successfully!"',
        '80 CLOSE #1',
        '81 CLOSE #3',
        '82 CLOSE #5',
        '90 STOP',
        '1000 PRINT "ERROR: ";ERR;" at line ";ERL',
        '1010 RESUME 90',
        'RUN'
    ]

    for line in test_lines:
        send_cmd(sock, line, wait=1)

    time.sleep(3)
    send_cmd(sock, '', wait=2)

    # Exit BASIC
    send_cmd(sock, 'EXIT', wait=2)

    sock.close()

if __name__ == '__main__':
    main()
