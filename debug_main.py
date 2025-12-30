#!/usr/bin/env python3
"""Debug main ADVENT program to see where it fails after ADVINI."""

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

    # Create a simple test program that just calls ADVINI and continues
    print("\n=== Create test program ===")
    send_cmd(sock, 'DELETE/NOCONFIRM DM1:[1,2]TEST.B2S', wait=1)
    send_cmd(sock, 'DELETE/NOCONFIRM DM1:[1,2]TEST.OBJ', wait=1)
    send_cmd(sock, 'CREATE DM1:[1,2]TEST.B2S', wait=1)

    # Simple test program that calls ADVINI and does basic I/O
    lines = [
        '1\tON ERROR GOTO 25000 &',
        '\\\tCOMMON ACC$(8%)=7%,AR$=80%,C%,C$=10%,CRLF$=2%, &',
        '\tFLAG%(8%),HP%(8%),LEVEL%(8%),KB%(8%),NAM$(8%)=30%,NO.OF.USERS%, &',
        '\tXP.(8%),STUN(8%), &',
        '\tNPCMESS$(8%)=40%,OB$(8%,9%)=30%,PASS$(8%)=10%, &',
        '\tROOM%(8%),SENT.KB%,SENT.MESS$=80%,SENT.PROG%,SENT.PROJ%, &',
        '\tUSER%,CI$=1%,WEAPON$(8%)=20%,WEAPON%(8%), &',
        '\tATT.LEVEL%(10%),DEF.LEVEL%(10%),MON.HP%(10%),MON.DAM%(10%), &',
        '\tSPEC$(10%)=6%,MON.ROOM%(10%),MON.XP%(10%),RUN.ACC$=9%,MMM$=128%, &',
        '\tBLIND%(8%),USER1%,SPY%(10%),FATIGUE%(10%)',
        '',
        '10\tPRINT "TEST: Calling ADVINI..." &',
        '\\\tCALL ADVINI &',
        '\\\tPRINT "TEST: ADVINI returned!"',
        '',
        '20\tPRINT "TEST: Setting up FIELD on KB..." &',
        '\\\tFIELD #1%, 128% AS BUF$',
        '',
        '30\tPRINT "TEST: Setting up FIELD on DTA..." &',
        '\\\tFIELD #3%, 1% AS ROOM$, 16% AS EX$, 83% AS PEOPLE$, 100% AS OBJECT$, 312% AS DESC$',
        '',
        '40\tPRINT "TEST: Setting up DIM on MON..." &',
        '\\\tDIM #5%, MONSTER$(10000%)=20%',
        '',
        '50\tPRINT "TEST: Setting up DIM on CHR..." &',
        '\\\tDIM #7%, CHARACTER$(100%)=512%',
        '',
        '60\tPRINT "TEST: All setup complete!"',
        '',
        '100\tPRINT "Enter a command (or QUIT to exit): "; &',
        '\\\tLINPUT #1%, COM$ &',
        '\\\tPRINT "TEST: You entered: ";COM$ &',
        '\\\tGOTO 200 IF CVT$$(COM$,32%)="QUIT" &',
        '\\\tGOTO 100',
        '',
        '200\tPRINT "TEST: Exiting..." &',
        '\\\tCLOSE #I% FOR I%=1% TO 12% &',
        '\\\tEND',
        '',
        '25000\tPRINT "TEST ERROR:";ERR;" at line";ERL &',
        '\\\tRESUME 200',
        '',
        '32767\tEND',
    ]

    for line in lines:
        sock.sendall((line + '\r').encode('latin-1'))
        time.sleep(0.2)

    sock.sendall(b'\x1a')
    time.sleep(1)
    send_cmd(sock, '', wait=1)

    # Compile
    print("\n=== Compile TEST ===")
    result = send_cmd(sock, 'BASIC/BP2 DM1:[1,2]TEST.B2S', wait=30)

    time.sleep(5)
    send_cmd(sock, '', wait=2)

    # Link - simple link without overlays
    print("\n=== Link TEST ===")
    send_cmd(sock, 'DELETE/NOCONFIRM DM1:[1,2]TEST.TSK', wait=1)
    send_cmd(sock, 'LINK/BP2/CODE=DATA_SPACE DM1:[1,2]TEST,DM1:[1,2]ADVINI', wait=30)

    time.sleep(5)
    send_cmd(sock, '', wait=2)

    # Check TSK
    print("\n=== Check TSK ===")
    send_cmd(sock, 'DIR DM1:[1,2]TEST.TSK', wait=2)

    # Run
    print("\n=== Run TEST ===")
    result = send_cmd(sock, 'RUN DM1:[1,2]TEST', wait=10)

    time.sleep(5)
    send_cmd(sock, '', wait=3)

    # Try commands
    print("\n=== Try input ===")
    send_cmd(sock, 'hello', wait=5)
    send_cmd(sock, 'QUIT', wait=5)

    sock.close()

if __name__ == '__main__':
    main()
