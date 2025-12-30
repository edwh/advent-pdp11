#!/usr/bin/env python3
"""Create data files using simple BASIC commands."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Create Data Files - Simple Direct Commands")
    print("=" * 60)

    child = pexpect.spawn('telnet localhost 2323', encoding='latin-1')
    child.logfile = sys.stdout

    try:
        child.expect('Connected to the PDP-11', timeout=10)
    except pexpect.TIMEOUT:
        print("\n*** Cannot connect ***")
        return False

    time.sleep(2)
    child.sendline('')
    time.sleep(1)
    child.sendline('')
    time.sleep(1)

    # Login
    idx = child.expect(['User:', r'\$ ', 'Job number'], timeout=30)
    if idx == 0:
        child.sendline('[1,2]')
        child.expect('Password:', timeout=10)
        child.sendline('Digital1977')
        idx2 = child.expect(['Job number', r'\$ '], timeout=15)
        if idx2 == 0:
            child.sendline('')
    elif idx == 2:
        child.sendline('')

    child.expect(r'\$ ', timeout=30)
    print("\n*** Logged in ***")

    def dcl_cmd(cmd, timeout=15):
        child.sendline(cmd)
        child.expect(r'\$ ', timeout=timeout)
        time.sleep(0.3)

    # Install BP2RES
    print("\n=== Installing BP2RES library ===")
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Create each file using direct BASIC commands
    # ADVENT.DTA - 512 byte records
    print("\n=== Creating ADVENT.DTA ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    child.sendline("OPEN 'DM1:[1,2]ADVENT.DTA' FOR OUTPUT AS FILE #1%")
    child.expect('BASIC2', timeout=30)

    child.sendline("FIELD #1%, 512% AS A$")
    child.expect('BASIC2', timeout=10)

    child.sendline("LSET A$=STRING$(512%,32%)")
    child.expect('BASIC2', timeout=10)

    # Write 10 records
    child.sendline("FOR I%=1% TO 10%")
    child.expect('BASIC2', timeout=10)

    child.sendline("PUT #1%")
    child.expect('BASIC2', timeout=10)

    child.sendline("NEXT I%")
    child.expect('BASIC2', timeout=30)

    child.sendline("CLOSE #1%")
    child.expect('BASIC2', timeout=10)

    child.sendline("PRINT 'ADVENT.DTA created'")
    child.expect('BASIC2', timeout=10)

    # Exit and check
    child.sendcontrol('z')
    child.expect(['BASIC2', r'\$ '], timeout=10)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.DTA')
    dcl_cmd('DIR/SIZE SY:[1,2]ADVENT.DTA')

    # ADVENT.MON - 20 byte records
    print("\n=== Creating ADVENT.MON ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    child.sendline("OPEN 'DM1:[1,2]ADVENT.MON' FOR OUTPUT AS FILE #1%")
    child.expect('BASIC2', timeout=30)

    child.sendline("FIELD #1%, 20% AS M$")
    child.expect('BASIC2', timeout=10)

    child.sendline("LSET M$=STRING$(20%,32%)")
    child.expect('BASIC2', timeout=10)

    child.sendline("FOR I%=1% TO 10%")
    child.expect('BASIC2', timeout=10)

    child.sendline("PUT #1%")
    child.expect('BASIC2', timeout=10)

    child.sendline("NEXT I%")
    child.expect('BASIC2', timeout=30)

    child.sendline("CLOSE #1%")
    child.expect('BASIC2', timeout=10)

    child.sendcontrol('z')
    child.expect(['BASIC2', r'\$ '], timeout=10)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.MON')
    dcl_cmd('DIR/SIZE SY:[1,2]ADVENT.MON')

    # ADVENT.CHR - 512 byte records
    print("\n=== Creating ADVENT.CHR ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    child.sendline("OPEN 'DM1:[1,2]ADVENT.CHR' FOR OUTPUT AS FILE #1%")
    child.expect('BASIC2', timeout=30)

    child.sendline("FIELD #1%, 512% AS C$")
    child.expect('BASIC2', timeout=10)

    child.sendline("LSET C$=STRING$(512%,32%)")
    child.expect('BASIC2', timeout=10)

    child.sendline("FOR I%=1% TO 10%")
    child.expect('BASIC2', timeout=10)

    child.sendline("PUT #1%")
    child.expect('BASIC2', timeout=10)

    child.sendline("NEXT I%")
    child.expect('BASIC2', timeout=30)

    child.sendline("CLOSE #1%")
    child.expect('BASIC2', timeout=10)

    child.sendcontrol('z')
    child.expect(['BASIC2', r'\$ '], timeout=10)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.CHR')
    dcl_cmd('DIR/SIZE SY:[1,2]ADVENT.CHR')

    # BOARD.NTC - 514 byte records (2 + 512)
    print("\n=== Creating BOARD.NTC ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    child.sendline("OPEN 'DM1:[1,2]BOARD.NTC' FOR OUTPUT AS FILE #1%")
    child.expect('BASIC2', timeout=30)

    child.sendline("FIELD #1%, 514% AS B$")
    child.expect('BASIC2', timeout=10)

    child.sendline("LSET B$=STRING$(514%,32%)")
    child.expect('BASIC2', timeout=10)

    child.sendline("FOR I%=1% TO 10%")
    child.expect('BASIC2', timeout=10)

    child.sendline("PUT #1%")
    child.expect('BASIC2', timeout=10)

    child.sendline("NEXT I%")
    child.expect('BASIC2', timeout=30)

    child.sendline("CLOSE #1%")
    child.expect('BASIC2', timeout=10)

    child.sendcontrol('z')
    child.expect(['BASIC2', r'\$ '], timeout=10)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    dcl_cmd('DIR/SIZE DM1:[1,2]BOARD.NTC')
    dcl_cmd('DIR/SIZE SY:[1,2]BOARD.NTC')

    # MESSAG.NPC - 62 byte records (2 + 60)
    print("\n=== Creating MESSAG.NPC ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    child.sendline("OPEN 'DM1:[1,2]MESSAG.NPC' FOR OUTPUT AS FILE #1%")
    child.expect('BASIC2', timeout=30)

    child.sendline("FIELD #1%, 62% AS N$")
    child.expect('BASIC2', timeout=10)

    child.sendline("LSET N$=STRING$(62%,32%)")
    child.expect('BASIC2', timeout=10)

    child.sendline("FOR I%=1% TO 10%")
    child.expect('BASIC2', timeout=10)

    child.sendline("PUT #1%")
    child.expect('BASIC2', timeout=10)

    child.sendline("NEXT I%")
    child.expect('BASIC2', timeout=30)

    child.sendline("CLOSE #1%")
    child.expect('BASIC2', timeout=10)

    child.sendcontrol('z')
    child.expect(['BASIC2', r'\$ '], timeout=10)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    dcl_cmd('DIR/SIZE DM1:[1,2]MESSAG.NPC')
    dcl_cmd('DIR/SIZE SY:[1,2]MESSAG.NPC')

    # Final check
    print("\n=== Final file check ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC')
    dcl_cmd('DIR/SIZE SY:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC')

    # Test ADVENT
    print("\n" + "=" * 60)
    print("TESTING ADVENT GAME")
    print("=" * 60)

    child.sendline('RUN DM1:[1,2]ADVENT')

    idx = child.expect([
        'Welcome',
        'What is your',
        'name',
        '>',
        'INITIALIZING',
        'Cannot find',
        'Stop',
        r'\?',
        r'\$ ',
        pexpect.TIMEOUT
    ], timeout=90)

    result_map = {
        0: "WELCOME",
        1: "NAME PROMPT",
        2: "NAME",
        3: "GAME PROMPT",
        4: "INITIALIZING",
        5: "CANNOT FIND",
        6: "STOPPED",
        7: "ERROR",
        8: "DCL PROMPT",
        9: "TIMEOUT"
    }

    print(f"\n*** Game result: {result_map.get(idx, 'UNKNOWN')} (idx={idx}) ***")

    if idx in [0, 1, 2, 3, 4]:
        print("\n*** GAME IS WORKING! ***")
        time.sleep(2)
        child.sendline('TEST')
        time.sleep(5)

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
