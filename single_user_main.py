#!/usr/bin/env python3
"""Create single-user version of main ADVENT program."""

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

    # Create single-user ADVENT.B2S
    print("\n=== Create single-user ADVENT.B2S ===")
    send_cmd(sock, 'DELETE/NOCONFIRM DM1:[1,2]ADVENT.B2S', wait=1)
    send_cmd(sock, 'DELETE/NOCONFIRM DM1:[1,2]ADVENT.OBJ', wait=1)
    send_cmd(sock, 'CREATE DM1:[1,2]ADVENT.B2S', wait=1)

    # Single-user version - uses LINPUT instead of GET...RECORD
    # Removed message receiver code
    # Using double quotes in Python, single quotes in BP2 where needed
    lines = [
        "1\tON ERROR GOTO 25000 &",
        "\\\tCOMMON ACC$(8%)=7%,AR$=80%,C%,C$=10%,CRLF$=2%, &",
        "\tFLAG%(8%),HP%(8%),LEVEL%(8%),KB%(8%),NAM$(8%)=30%,NO.OF.USERS%, &",
        "\tXP.(8%),STUN(8%), &",
        "\tNPCMESS$(8%)=40%,OB$(8%,9%)=30%,PASS$(8%)=10%, &",
        "\tROOM%(8%),SENT.KB%,SENT.MESS$=80%,SENT.PROG%,SENT.PROJ%, &",
        "\tUSER%,CI$=1%,WEAPON$(8%)=20%,WEAPON%(8%), &",
        "\tATT.LEVEL%(10%),DEF.LEVEL%(10%),MON.HP%(10%),MON.DAM%(10%), &",
        "\tSPEC$(10%)=6%,MON.ROOM%(10%),MON.XP%(10%),RUN.ACC$=9%,MMM$=128%, &",
        "\tBLIND%(8%),USER1%,SPY%(10%),FATIGUE%(10%)",
        "",
        "10\tCALL ADVINI &",
        "\\\tFIELD #1%, 128% AS BUF$ &",
        "\\\tFIELD #3%, 1% AS ROOM$, 16% AS EX$, 83% AS PEOPLE$, 100% AS OBJECT$, 312% AS DESC$ &",
        "\\\tDIM #5%, MONSTER$(10000%)=20% &",
        "\\\tDIM #7%, CHARACTER$(100%)=512% &",
        "\\\tUSER%=1% &",
        "\\\tKB%(1%)=0% &",
        "\\\tNO.OF.USERS%=1%",
        "",
        "15\tCOM.LIST$= &",
        '\t"/LOOK      /NORTH     /EAST      /SOUTH     /WEST      "+ &',
        '\t"/INVENTORY /STATUS    /GET       /TAKE      /PICK      "+ &',
        '\t"/DROP      /THROW     /TELL      /SHOUT     /DRAW      "+ &',
        '\t"/SHEATH    /HIT       /LT        /QUIT      /WEAPON    "+ &',
        '\t"/READ      /WRITE     /WIPE      /EAT       /OPEN      "+ &',
        '\t"/HELP      /ROB       /RING      /USE       /PRAY      "+ &',
        '\t"/ANNOUNCE  /TELEPORT  /ROOM      /LIST      /INVISIBLE "+ &',
        '\t"/HEAL      /FIREBALL  /STUN      /ZAP       /SEND      "+ &',
        '\t"/PASS      /HOLD      /UNSTUN    /SUMMON    /KISS      "+ &',
        '\t"/COMMUNE   /BLESS     /CREATE    /MAKE      /SPY       "+ &',
        '\t"/BELLOW    /VALUE     /CALL      /GAG       /BLIND     "+ &',
        '\t"/MESSAGE   /REST      "',
        "",
        '20\tPRINT "Welcome to ADVENT!" &',
        '\\\tPRINT "Type LOOK to see your surroundings." &',
        '\\\tPRINT "Type HELP for commands." &',
        '\\\tPRINT "Type QUIT to exit." &',
        "\\\tPRINT",
        "",
        "25\tIF ROOM%(USER%)=0% THEN ROOM%(USER%)=449%",
        "",
        "28\tGET #3%, RECORD ROOM%(USER%) &",
        "\\\tGOTO 24990 IF ROOM$<>CHR$(ROOM%(USER%)) &",
        "\\\tCALL ADVDSP",
        "",
        '30\tJ$="> " &',
        '\\\tJ$="-]--- " IF FLAG%(USER%) AND 2%^0% &',
        "\\\tPRINT &",
        "\\\tPRINT J$; &",
        "\\\tLINPUT #1%, COM$ &",
        "\\\tCOM$=CVT$$(COM$,1%+4%+8%+32%+128%)",
        "",
        "41\tGOSUB 21000 &",
        "\\\tGOTO 50 UNLESS C% &",
        "\\\tCALL ADVNOR IF C%>=1% AND C%<=19% &",
        "\\\tCALL ADVCMD IF C%>19% AND C%<45% &",
        "\\\tCALL ADVODD IF C%>=45% &",
        "\\\tFIELD #3%, 1% AS ROOM$, 16% AS EX$, 83% AS PEOPLE$, 100% AS OBJECT$, 312% AS DESC$",
        "",
        "50\tGOTO 500 IF HP%(USER%)<=0% &",
        "\\\tGOTO 30",
        "",
        "500\tCALL ADVBYE &",
        "\\\tGOTO 32767",
        "",
        "15050\tDEF* FNEDIT$(X$,B$) &",
        "\\\tA$=X$ &",
        "\\\tZ%=1%",
        "",
        "15060\tGOTO 15070 UNLESS INSTR(1%,A$,B$) &",
        "\\\tY%=INSTR(1%,A$,B$) &",
        "\\\tA$=LEFT(A$,Y%-1%)+RIGHT(A$,Y%+LEN(B$))",
        "",
        "15070\tFNEDIT$=A$ &",
        "\\\tFNEND",
        "",
        "15080\tDEF* FNGRAB$(O$,P$) &",
        '\\\tO%=INSTR(1%,CVT$$(O$,36%),CVT$$(P$,36%)) &',
        '\\\tGOTO 15090 IF MID(O$,II%,1%)="/" FOR II%=O% TO 1% STEP -1% &',
        "\\\tOO%=1% &",
        "\\\tGOTO 15100",
        "",
        "15090\tOO%=II%+1%",
        "",
        '15100\tFNGRAB$=MID(O$,OO%,INSTR(OO%,O$,"/")-OO%) &',
        "\\\tFNEND",
        "",
        "15110\tDEF* FNCLEAR$ &",
        "\\\tIF FLAG%(USER%) AND 1% THEN HP%(USER%)=HP%(USER%)*3%/4% &",
        "\\\tFLAG%(USER%)=FLAG%(USER%)-1%",
        "",
        "15120\tFNEND",
        "",
        "15140\tDEF* FNGMD%(R%) &",
        "\\\tG.R%=R%",
        "",
        "15150\tFNEND",
        "",
        "15160\tDEF* FNSMD%(R%) &",
        "\\\tFNEND",
        "",
        '21000\tJ%=INSTR(1%,COM$," ") &',
        "\\\tIF J%=0% THEN J$=COM$ &",
        '\\\tAR$="" &',
        "\\\tGOTO 21020",
        "",
        "21010\tJ$=LEFT(COM$,J%-1%) &",
        "\\\tAR$=RIGHT(COM$,J%+1%)",
        "",
        # Line 21020 - check for empty string
        "21020\tIF FATIGUE%(USER%)<=0% AND LEN(CVT$$(J$,255%))>0% THEN &",
        '\\\tPRINT "You are too tired." &',
        "\\\tC%=0% &",
        "\\\tRETURN",
        "",
        # Line 21021 - find command in list
        "21021\tJ%=INSTR(1%,COM.LIST$,CHR$(47%)+J$) &",
        "\\\tIF LEN(J$)=0% THEN C%=0% &",
        "\\\tFATIGUE%(USER%)=FATIGUE%(USER%)+1% IF FATIGUE%(USER%)<50% &",
        '\\\tPRINT "Fatigue : ";NUM1$(FATIGUE%(USER%)) &',
        "\\\tRETURN",
        "",
        # Line 21025 - check for custom command
        "21025\tIF INSTR(1%,DESC$,CHR$(47%)+CHR$(67%)+J$) THEN C$=J$ &",
        "\\\tC%=0% &",
        "\\\tCALL ADVPUZ &",
        "\\\tRETURN",
        "",
        # Line 21026 - unknown command
        "21026\tIF J%=0% THEN C%=0% &",
        '\\\tPRINT "You cannot do that." &',
        "\\\tRETURN",
        "",
        # Line 21030 - calculate command number
        "21030\tC%=(J%-1%)/11%+1% &",
        "\\\tC$=CVT$$(MID(COM.LIST$,J%+1%,10%),128%) &",
        '\\\tCALL ADVPUZ IF INSTR(1%,DESC$,"$/O/") &',
        "\\\tRETURN",
        "",
        # Corrupt room handler
        '24990\tPRINT "You got stuck in a corrupt room. Setting to start." &',
        "\\\tROOM%(USER%)=449% &",
        "\\\tGET #3%, RECORD ROOM%(USER%) &",
        "\\\tCALL ADVDSP &",
        "\\\tGOTO 30",
        "",
        # Error handler
        '25000\tPRINT "Error ";ERR;" at line ";ERL &',
        "\\\tRESUME 32767",
        "",
        '32767\tPRINT "ADVENT shutting down." &',
        "\\\tCLOSE #I% FOR I%=1% TO 12% &",
        "\\\tEND",
    ]

    for line in lines:
        sock.sendall((line + '\r').encode('latin-1'))
        time.sleep(0.2)

    sock.sendall(b'\x1a')
    time.sleep(1)
    send_cmd(sock, '', wait=1)

    # Compile
    print("\n=== Compile ===")
    result = send_cmd(sock, 'BASIC/BP2 DM1:[1,2]ADVENT.B2S', wait=60)

    time.sleep(5)
    send_cmd(sock, '', wait=2)

    # Check OBJ
    print("\n=== Check files ===")
    send_cmd(sock, 'DIR DM1:[1,2]ADVENT.*', wait=2)

    sock.close()

if __name__ == '__main__':
    main()
