#!/usr/bin/env python3
"""Fix ADVINI source - remove trailing & from SUBEND."""

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

    # Delete and recreate
    print("\n=== Create fixed ADVINI.SUB ===")
    send_cmd(sock, 'DELETE/NOCONFIRM DM1:[1,2]ADVINI.SUB', wait=1)
    send_cmd(sock, 'CREATE DM1:[1,2]ADVINI.SUB', wait=1)

    # Properly formatted lines - removed SYS() call on line 28 that referenced KB11
    # and fixed the SUBEND line
    lines = [
        '1\tSUB ADVINI &',
        '\\\tCOMMON ACC$(8%)=7%,AR$=80%,C%,C$=10%,CRLF$=2%, &',
        '\tFLAG%(8%),HP%(8%),LEVEL%(8%),KB%(8%),NAM$(8%)=30%,NO.OF.USERS%, &',
        '\tXP.(8%),STUN(8%), &',
        '\tNPCMESS$(8%)=40%,OB$(8%,9%)=30%,PASS$(8%)=10%, &',
        '\tROOM%(8%),SENT.KB%,SENT.MESS$=80%,SENT.PROG%,SENT.PROJ%, &',
        '\tUSER%,CI$=1%,WEAPON$(8%)=20%,WEAPON%(8%), &',
        '\tATT.LEVEL%(10%),DEF.LEVEL%(10%),MON.HP%(10%),MON.DAM%(10%), &',
        '\tSPEC$(10%)=6%,MON.ROOM%(10%),MON.XP%(10%),RUN.ACC$=9%,MMM$=128%, &',
        '\tBLIND%(8%),USER1%,SPY%(10%),FATIGUE%(10%) &',
        '\\\tON ERROR GOTO 25000',
        '',
        '10\tJ$=SYS(CHR$(12%)) &',
        '\\\tRUN.ACC$="["+NUM1$(ASCII(RIGHT(J$,6%)))+","+NUM1$(ASCII(RIGHT(J$,5%)))+"]" &',
        '\\\tJ$=SYS(CHR$(6%)+CHR$(-13%)+CHR$(-1%)+CHR$(-1%)+CHR$(8%)+STRING$(2%,0%)+CHR$(-1%)+CHR$(31%)) &',
        '\\\tRANDOMIZE &',
        '\\\tNO.OF.USERS%=0% &',
        '\\\tCRLF$=CHR$(13%)+CHR$(10%) &',
        '\\\tCI$=CHR$(9%) &',
        '\\\tJ$=SYS(CHR$(6%)+CHR$(22%)+CHR$(1%)+CHR$(0%)+"ADVENT"+STRING$(11%,0%)+CHR$(3%)+CHR$(0%)+CHR$(0%)+CHR$(10%))',
        '',
        '20\tJ$=SYS(CHR$(6%)+CHR$(7%)+CHR$(128%)) &',
        '\\\tOPEN "_KB:" AS FILE #1% &',
        '\\\tOPEN "_DM1:"+RUN.ACC$+"ADVENT.DTA" AS FILE #3%, MODE 257% &',
        '\\\tOPEN "_DM1:"+RUN.ACC$+"ADVENT.MON" AS FILE #5%, ACCESS MODIFY, ALLOW NONE &',
        '\\\tOPEN "_DM1:"+RUN.ACC$+"BOARD.NTC" AS FILE #6% &',
        '\\\tOPEN "_DM1:"+RUN.ACC$+"ADVENT.CHR" AS FILE #7% &',
        '\\\tOPEN "_DM1:"+RUN.ACC$+"MESSAG.NPC" AS FILE #9%, MODE 4096% &',
        '\\\tJ$=SYS(CHR$(6%)+CHR$(-26%)+CHR$(7%)+CHR$(128%)) &',
        '\\\tJ$=STRING$(32%,0%) &',
        "\\\tJ$=J$+CHR$(I%) FOR I%=32% TO 64% &",
        "\\\tJ$=J$+STRING$(26%,ASCII('M')) &",
        '\\\tJ$=J$+CHR$(I%) FOR I%=91% TO 96% &',
        "\\\tJ$=J$+STRING$(26%,ASCII('M')) &",
        '\\\tJ$=J$+CHR$(I%) FOR I%=123% TO 127% &',
        '\\\tMMM$=J$ &',
        '\\\tSUBEXIT',
        '',
        '25000\tON ERROR GOTO 32767 &',
        '\\\tOPEN "MSG:LOG1.95" AS FILE #4%, MODE 2% &',
        '\\\tPRINT #4%, "ADVINI : ";ERR;" at line";ERL;" at ";TIME$(0%) &',
        '\\\tCLOSE #4% &',
        '\\\tSTOP',
        '',
        '32767\tSUBEND',
    ]

    for line in lines:
        sock.sendall((line + '\r').encode('latin-1'))
        time.sleep(0.2)

    sock.sendall(b'\x1a')
    time.sleep(1)
    send_cmd(sock, '', wait=1)

    # Compile
    print("\n=== Compile ===")
    result = send_cmd(sock, 'BASIC/BP2 DM1:[1,2]ADVINI.SUB', wait=30)

    time.sleep(5)
    send_cmd(sock, '', wait=2)

    # Check OBJ
    print("\n=== Check files ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVINI.*', wait=2)

    # If compiled, relink and run
    print("\n=== Relink ===")
    send_cmd(sock, 'DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK', wait=2)
    send_cmd(sock, 'LINK/BP2/CODE=DATA_SPACE/STRUCTURE', wait=3)
    send_cmd(sock, 'DM1:[1,2]ADVENT,DM1:[1,2]ADVDSP,DM1:[1,2]ADVFND,DM1:[1,2]ADVOUT,DM1:[1,2]ADVSHT', wait=3)
    send_cmd(sock, '', wait=3)  # Root COMMON
    send_cmd(sock, 'DM1:[1,2]ADVINI!', wait=3)
    send_cmd(sock, 'DM1:[1,2]ADVNOR!', wait=3)
    send_cmd(sock, 'DM1:[1,2]ADVCMD!', wait=3)
    send_cmd(sock, 'DM1:[1,2]ADVODD!', wait=3)
    send_cmd(sock, 'DM1:[1,2]ADVMSG,DM1:[1,2]ADVTDY!', wait=3)
    send_cmd(sock, 'DM1:[1,2]ADVBYE!', wait=3)
    send_cmd(sock, 'DM1:[1,2]ADVNPC!', wait=3)
    send_cmd(sock, 'DM1:[1,2]ADVPUZ', wait=3)
    send_cmd(sock, '', wait=30)  # End

    time.sleep(10)
    send_cmd(sock, '', wait=5)

    print("\n=== Check TSK ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVENT.TSK', wait=2)

    # Run
    print("\n=== Run ===")
    send_cmd(sock, 'DELETE/NOCONFIRM MSG:LOG1.95', wait=1)
    send_cmd(sock, 'CREATE MSG:LOG1.95', wait=1)
    sock.sendall(b'\x1a')
    time.sleep(1)
    send_cmd(sock, '', wait=1)

    result = send_cmd(sock, 'RUN DM1:[1,2]ADVENT', wait=15)

    time.sleep(5)
    send_cmd(sock, '', wait=3)

    # Try commands
    print("\n=== Try commands ===")
    send_cmd(sock, 'look', wait=5)
    send_cmd(sock, 'n', wait=5)

    # Check log
    print("\n=== Log ===")
    send_cmd(sock, 'TYPE MSG:LOG1.95', wait=3)

    sock.close()

if __name__ == '__main__':
    main()
