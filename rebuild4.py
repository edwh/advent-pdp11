#!/usr/bin/env python3
"""Rebuild ADVINI with fixed device reference - using BP2COM directly."""

import pexpect
import sys
import time

# The modified ADVINI source with _DM1: instead of _DK1:
ADVINI_SOURCE = '''1	SUB ADVINI &
\\	COMMON ACC$(8%)=7%,AR$=80%,C%,C$=10%,CRLF$=2%, &
	FLAG%(8%),HP%(8%),LEVEL%(8%),KB%(8%),NAM$(8%)=30%,NO.OF.USERS%, &
	XP.(8%),STUN(8%), &
	NPCMESS$(8%)=40%,OB$(8%,9%)=30%,PASS$(8%)=10%, &
	ROOM%(8%),SENT.KB%,SENT.MESS$=80%,SENT.PROG%,SENT.PROJ%, &
	USER%,CI$=1%,WEAPON$(8%)=20%,WEAPON%(8%), &
	ATT.LEVEL%(10%),DEF.LEVEL%(10%),MON.HP%(10%),MON.DAM%(10%), &
	SPEC$(10%)=6%,MON.ROOM%(10%),MON.XP%(10%),RUN.ACC$=9%,MMM$=128%, &
	BLIND%(8%),USER1%,SPY%(10%),FATIGUE%(10%) &
\\	ON ERROR GOTO 25000 &

10	J$=SYS(CHR$(12%)) &
\\	RUN.ACC$="["+NUM1$(ASCII(RIGHT(J$,6%)))+","+NUM1$(ASCII(RIGHT(J$,5%))) &
	+"]" &
\\	J$=SYS(CHR$(6%)+CHR$(-13%)+CHR$(-1%)+CHR$(-1%)+CHR$(8%)+ &
	STRING$(2%,0%)+CHR$(-1%)+CHR$(31%)) &
!\\	J$=SYS(CHR$(6%)+CHR$(-20%)+CHR$(0%)) &
\\	RANDOMIZE &
\\	NO.OF.USERS%=0% &
\\	CRLF$=CHR$(13%)+CHR$(10%) &
\\	CI$=CHR$(9%) &
\\	J$=SYS(CHR$(6%)+CHR$(22%)+CHR$(1%)+CHR$(0%)+"ADVENT"+STRING$(11%,0%)+ &
	CHR$(3%)+CHR$(0%)+CHR$(0%)+CHR$(10%)) &

20	J$=SYS(CHR$(6%)+CHR$(7%)+CHR$(128%)) &
\\	OPEN "_KB11:" AS FILE #1% &
\\	J$=SYS(CHR$(6%)+CHR$(10%)+STRING$(20%,0%)+"KB"+CHR$(11%)) &
\\	OPEN "_DM1:"+RUN.ACC$+"ADVENT.DTA" AS FILE #3%, MODE 257% &
\\	OPEN "_DM1:"+RUN.ACC$+"ADVENT.MON" AS FILE #5%, &
	ACCESS MODIFY, &
	ALLOW NONE &
\\	OPEN "_DM1:"+RUN.ACC$+"BOARD.NTC" AS FILE #6% &
\\	OPEN "_DM1:"+RUN.ACC$+"ADVENT.CHR" AS FILE #7% &
\\	OPEN "_DM1:"+RUN.ACC$+"MESSAG.NPC" AS FILE #9% , MODE 4096% &
\\	J$=SYS(CHR$(6%)+CHR$(-26%)+CHR$(7%)+CHR$(128%)) &
\\	J$=STRING$(32%,0%) &
\\	J$=J$+CHR$(I%) FOR I%=32% TO 64% &
\\	J$=J$+STRING$(26%,ASCII('M')) &
\\	J$=J$+CHR$(I%) FOR I%=91% TO 96% &
\\	J$=J$+STRING$(26%,ASCII('M')) &
\\	J$=J$+CHR$(I%) FOR I%=123% TO 127% &
\\	MMM$=J$ &
	! Used for GAG in a couple of subprograms. &
\\	SUBEXIT &

25000	! ERRORS &
	&
	&
	IF ERR=16 AND ERR=10 THEN PRINT "ADVENT already running." &
\\	STOP &
\\	RESUME 20 &

29000	OPEN "MSG:LOG1.95" AS FILE #4%, MODE 2% &
\\	PRINT #4%, "ADVINI : ";RIGHT(SYS(CHR$(6%)+CHR$(9%)+CHR$(ERR)),3%); &
	" at line";ERL;" at ";TIME$(0%) &
\\	CLOSE #4% &
\\	STOP &

32767	SUBEND &
'''

def main():
    print("=" * 60)
    print("Rebuild ADVINI with _DM1: device (using BP2COM)")
    print("=" * 60)

    child = pexpect.spawn('telnet localhost 2323', encoding='latin-1')
    child.logfile = sys.stdout

    try:
        child.expect('Connected to the PDP-11', timeout=10)
    except pexpect.TIMEOUT:
        print("ERROR: Could not connect to PDP-11")
        return False

    time.sleep(2)
    child.sendline('')
    time.sleep(1)

    # Handle login with more robust HELP handling
    while True:
        idx = child.expect(['User:', r'\$ ', 'Job number', 'Password:', 'disabled', 'Topic', pexpect.TIMEOUT], timeout=30)
        if idx == 0:
            child.sendline('[1,2]')
        elif idx == 1:
            break
        elif idx == 2:
            child.sendline('')
        elif idx == 3:
            child.sendline('Digital1977')
        elif idx == 4:
            print("\n*** Logins disabled - waiting ***")
            time.sleep(10)
            child.sendline('')
        elif idx == 5:
            # Stuck in help
            child.sendcontrol('z')
            time.sleep(1)
        elif idx == 6:
            child.sendline('')
        time.sleep(1)

    print("\n*** Logged in ***")

    def dcl_cmd(cmd, timeout=15):
        """Execute DCL command with proper $ prompt detection."""
        child.sendline(cmd)
        # Wait for $ prompt but handle Topic? from help
        while True:
            idx = child.expect([r'\$ ', 'Topic', pexpect.TIMEOUT], timeout=timeout)
            if idx == 0:
                break
            elif idx == 1:
                child.sendcontrol('z')
                time.sleep(1)
            else:
                break
        time.sleep(0.5)

    # Install BP2RES
    print("\n=== Installing BP2RES library ===")
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Create logical name
    dcl_cmd('ASSIGN DM1:[1,2] A:')

    # Check current ADVINI files
    print("\n=== Current ADVINI files ===")
    dcl_cmd('DIRECTORY A:ADVINI.*')

    # Delete old ADVINI.SUB if exists
    print("\n=== Removing old ADVINI.SUB ===")
    child.sendline('DELETE/NOCONFIRM A:ADVINI.SUB')
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # Create new ADVINI.SUB using CREATE command
    print("\n=== Creating new ADVINI.SUB with _DM1: ===")
    child.sendline('CREATE A:ADVINI.SUB')
    time.sleep(1)

    # Send source line by line
    lines = ADVINI_SOURCE.strip().split('\n')
    for line in lines:
        child.sendline(line)
        time.sleep(0.15)

    # End with Ctrl+Z
    child.sendcontrol('z')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    # Verify the file was created
    print("\n=== Checking ADVINI.SUB ===")
    dcl_cmd('DIRECTORY A:ADVINI.SUB')

    # Delete old OBJ file
    print("\n=== Removing old ADVINI.OBJ ===")
    child.sendline('DELETE/NOCONFIRM A:ADVINI.OBJ')
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # Compile ADVINI.SUB using BP2COM directly
    print("\n=== Compiling ADVINI.SUB with BP2COM ===")
    child.sendline('RUN $BP2COM')
    time.sleep(2)

    # BP2COM prompts for source file
    idx = child.expect(['File', 'Source', '>', r'\$ ', pexpect.TIMEOUT], timeout=15)
    print(f"BP2COM prompt result: idx={idx}")

    if idx in [0, 1, 2]:
        # Provide source and object file
        child.sendline('A:ADVINI.SUB,A:ADVINI.OBJ')
        time.sleep(10)

        # Wait for compilation to complete
        idx2 = child.expect(['>', 'Error', 'error', r'\$ ', pexpect.TIMEOUT], timeout=120)
        print(f"Compile result: idx={idx2}")

        if idx2 == 0:
            # Another prompt - exit
            child.sendcontrol('z')
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)
        elif idx2 in [1, 2]:
            # Error occurred
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)
    else:
        print("Could not start BP2COM")

    # Check if new OBJ was created
    print("\n=== Checking new ADVINI.OBJ ===")
    dcl_cmd('DIRECTORY/SIZE/DATE A:ADVINI.OBJ')

    # Now rebuild ADVENT.TSK
    print("\n=== Removing old ADVENT.TSK ===")
    child.sendline('DELETE/NOCONFIRM A:ADVENT.TSK')
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # Link with I/D space
    print("\n=== Rebuilding ADVENT.TSK ===")
    child.sendline('LINK/BP2/CODE=DATA_SPACE/STRUCTURE/EXECUTABLE=A:ADVENT/MAP A:ADVENT')
    time.sleep(3)

    done = False
    overlay_num = 0
    max_iter = 50
    iter_count = 0

    while not done and iter_count < max_iter:
        iter_count += 1
        idx = child.expect([
            r'Root COMMON',
            r'Root files',
            r'Root PSECTs',
            r'Overlay:',
            r'\$ ',
            r'undefined',
            pexpect.TIMEOUT
        ], timeout=60)

        if idx == 0:
            child.sendline('')
            time.sleep(1)
        elif idx == 1:
            child.sendline('A:ADVENT')
            time.sleep(2)
        elif idx == 2:
            child.sendline('')
            time.sleep(1)
        elif idx == 3:
            overlay_num += 1
            if overlay_num == 1:
                child.sendline('A:ADVINI,A:ADVOUT,A:ADVNOR')
                time.sleep(2)
            elif overlay_num == 2:
                child.sendline('A:ADVCMD,A:ADVODD,A:ADVMSG')
                time.sleep(2)
            elif overlay_num == 3:
                child.sendline('A:ADVBYE,A:ADVSHT,A:ADVNPC')
                time.sleep(2)
            elif overlay_num == 4:
                child.sendline('A:ADVPUZ,A:ADVDSP,A:ADVFND')
                time.sleep(2)
            elif overlay_num == 5:
                child.sendline('A:ADVTDY')
                time.sleep(2)
            else:
                child.sendline('')
                time.sleep(2)
        elif idx == 4:
            done = True
        elif idx == 5:
            print("\n*** Undefined symbols ***")
            time.sleep(1)
        elif idx == 6:
            child.sendline('')
            time.sleep(1)

    # Check result
    print("\n=== Checking new ADVENT.TSK ===")
    dcl_cmd('DIRECTORY/SIZE A:ADVENT.TSK')

    # Try running it
    print("\n=== Testing ADVENT ===")
    child.sendline('RUN A:ADVENT')
    time.sleep(5)

    idx = child.expect(['#', 'Stop', 'Error', r'\$ ', pexpect.TIMEOUT], timeout=30)
    print(f"\n*** Run result: idx={idx} ***")

    if idx == 0:
        print("\n*** Got # prompt - testing LOOK command ***")
        child.sendline('LOOK')
        time.sleep(3)
        idx2 = child.expect(['#', 'What', 'room', 'Room', 'dark', r'\$ ', pexpect.TIMEOUT], timeout=15)
        print(f"\n*** LOOK result: idx={idx2} ***")

        if idx2 in [0, 2, 3, 4]:
            # Got a response, try more commands
            child.sendline('HELP')
            time.sleep(3)
            child.expect(['#', r'\$ ', pexpect.TIMEOUT], timeout=15)

        child.sendcontrol('c')
        time.sleep(1)
    elif idx == 1:
        print("\n*** Game stopped - check output above for line number ***")

    child.expect([r'\$ ', 'User:', pexpect.TIMEOUT], timeout=15)

    dcl_cmd('DEASSIGN A:')
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
