#!/usr/bin/env python3
"""Debug ADVINI with verbose output at each step."""

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

    # Create debug ADVINI with prints at every step
    print("\n=== Create debug ADVINI.SUB ===")
    send_cmd(sock, 'DELETE/NOCONFIRM DM1:[1,2]ADVINI.SUB', wait=1)
    send_cmd(sock, 'DELETE/NOCONFIRM DM1:[1,2]ADVINI.OBJ', wait=1)
    send_cmd(sock, 'CREATE DM1:[1,2]ADVINI.SUB', wait=1)

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
        '\\\tON ERROR GOTO 25000 &',
        '\\\tPRINT "ADVINI: Starting..."',
        '',
        '10\tPRINT "ADVINI: Getting job info" &',
        '\\\tJ$=SYS(CHR$(12%)) &',
        '\\\tRUN.ACC$="["+NUM1$(ASCII(RIGHT(J$,6%)))+","+NUM1$(ASCII(RIGHT(J$,5%)))+"]" &',
        '\\\tPRINT "ADVINI: Account=";RUN.ACC$ &',
        '\\\tRANDOMIZE &',
        '\\\tNO.OF.USERS%=0% &',
        '\\\tCRLF$=CHR$(13%)+CHR$(10%) &',
        '\\\tCI$=CHR$(9%)',
        '',
        '20\tPRINT "ADVINI: Opening KB..." &',
        '\\\tOPEN "_KB:" AS FILE #1% &',
        '\\\tPRINT "ADVINI: KB opened"',
        '',
        '22\tPRINT "ADVINI: Opening ADVENT.DTA..." &',
        '\\\tOPEN "_DM1:"+RUN.ACC$+"ADVENT.DTA" AS FILE #3%, MODE 257% &',
        '\\\tPRINT "ADVINI: DTA opened"',
        '',
        '24\tPRINT "ADVINI: Opening ADVENT.MON..." &',
        '\\\tOPEN "_DM1:"+RUN.ACC$+"ADVENT.MON" AS FILE #5%, ACCESS MODIFY, ALLOW NONE &',
        '\\\tPRINT "ADVINI: MON opened"',
        '',
        '26\tPRINT "ADVINI: Opening BOARD.NTC..." &',
        '\\\tOPEN "_DM1:"+RUN.ACC$+"BOARD.NTC" AS FILE #6% &',
        '\\\tPRINT "ADVINI: NTC opened"',
        '',
        '28\tPRINT "ADVINI: Opening ADVENT.CHR..." &',
        '\\\tOPEN "_DM1:"+RUN.ACC$+"ADVENT.CHR" AS FILE #7% &',
        '\\\tPRINT "ADVINI: CHR opened"',
        '',
        '30\tPRINT "ADVINI: Opening MESSAG.NPC..." &',
        '\\\tOPEN "_DM1:"+RUN.ACC$+"MESSAG.NPC" AS FILE #9%, MODE 4096% &',
        '\\\tPRINT "ADVINI: NPC opened"',
        '',
        '32\tPRINT "ADVINI: Building MMM$..." &',
        '\\\tJ$=STRING$(32%,0%) &',
        '\\\tJ$=J$+CHR$(I%) FOR I%=32% TO 64% &',
        "\\\\\\tJ$=J$+STRING$(26%,ASCII('M')) &",
        '\\\tJ$=J$+CHR$(I%) FOR I%=91% TO 96% &',
        "\\\\\\tJ$=J$+STRING$(26%,ASCII('M')) &",
        '\\\tJ$=J$+CHR$(I%) FOR I%=123% TO 127% &',
        '\\\tMMM$=J$',
        '',
        '34\tPRINT "ADVINI: Complete - returning to main" &',
        '\\\tSUBEXIT',
        '',
        '25000\tPRINT "ADVINI ERROR:";ERR;" at line";ERL &',
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

    # Relink
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
    result = send_cmd(sock, 'RUN DM1:[1,2]ADVENT', wait=20)

    time.sleep(10)
    send_cmd(sock, '', wait=5)

    sock.close()

if __name__ == '__main__':
    main()
