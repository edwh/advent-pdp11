#!/usr/bin/env python3
"""Check ADVINI source on disk vs local source."""

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

    # Check for ADVINI source files
    print("\n=== Check ADVINI files ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVINI.*', wait=2)

    # TYPE the source file
    print("\n=== ADVINI.SUB source ===")
    send_cmd(sock, 'TYPE DM1:[1,2]ADVINI.SUB', wait=5)

    # Also check the main ADVENT source to see line 29000
    print("\n=== ADVENT.B2S lines 25000-29100 (error handling) ===")
    # Can't easily extract lines, so just TYPE the whole thing
    # Actually, let's write a quick test program that traps the error

    # Write a test BASIC program to test file opens
    print("\n=== Test file access ===")
    send_cmd(sock, 'BASIC', wait=3)

    # Try opening files like ADVINI does
    cmds = [
        'ON ERROR GOTO 1000',
        'OPEN "_KB11:" AS FILE #1',
        'PRINT "KB11 opened OK"',
        'CLOSE #1',
        'GOTO 2000',
        '1000 PRINT "Error ";ERR;" at line ";ERL',
        'RESUME 2000',
        '2000 PRINT "Done"',
        'RUN'
    ]
    for cmd in cmds:
        send_cmd(sock, cmd, wait=1)

    send_cmd(sock, 'EXIT', wait=2)

    sock.close()

if __name__ == '__main__':
    main()
