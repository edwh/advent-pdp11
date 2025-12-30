#!/usr/bin/env python3
"""Rebuild ADVENT.TSK with proper overlay structure using ODL."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Rebuild ADVENT.TSK with Overlay Structure")
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

    # Delete old TSK
    print("\n=== Deleting old ADVENT.TSK ===")
    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK')

    # Create proper ODL file
    print("\n=== Creating ODL file via BASIC ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    # Create ODL
    odl_lines = [
        "10 OPEN 'DM1:[1,2]ADVENT.ODL' FOR OUTPUT AS FILE #1%",
        '20 PRINT #1%, CHR$(9%);".ROOT ADVENT-LIBR-*(SUBS)"',
        '30 PRINT #1%, "SUBS:";CHR$(9%);".FCTR *(INI,OUT,NOR,CMD,ODD,MSG,BYE,SHT,NPC,PUZ,DSP,FND,TDY)"',
        '40 PRINT #1%, "INI:";CHR$(9%);".FCTR DM1:[1,2]ADVINI"',
        '50 PRINT #1%, "OUT:";CHR$(9%);".FCTR DM1:[1,2]ADVOUT"',
        '60 PRINT #1%, "NOR:";CHR$(9%);".FCTR DM1:[1,2]ADVNOR"',
        '70 PRINT #1%, "CMD:";CHR$(9%);".FCTR DM1:[1,2]ADVCMD"',
        '80 PRINT #1%, "ODD:";CHR$(9%);".FCTR DM1:[1,2]ADVODD"',
        '90 PRINT #1%, "MSG:";CHR$(9%);".FCTR DM1:[1,2]ADVMSG"',
        '100 PRINT #1%, "BYE:";CHR$(9%);".FCTR DM1:[1,2]ADVBYE"',
        '110 PRINT #1%, "SHT:";CHR$(9%);".FCTR DM1:[1,2]ADVSHT"',
        '120 PRINT #1%, "NPC:";CHR$(9%);".FCTR DM1:[1,2]ADVNPC"',
        '130 PRINT #1%, "PUZ:";CHR$(9%);".FCTR DM1:[1,2]ADVPUZ"',
        '140 PRINT #1%, "DSP:";CHR$(9%);".FCTR DM1:[1,2]ADVDSP"',
        '150 PRINT #1%, "FND:";CHR$(9%);".FCTR DM1:[1,2]ADVFND"',
        '160 PRINT #1%, "TDY:";CHR$(9%);".FCTR DM1:[1,2]ADVTDY"',
        '170 PRINT #1%, "LIBR:";CHR$(9%);".FCTR SY:[1,1]BP2OTS/LB"',
        '180 PRINT #1%, CHR$(9%);".END"',
        '190 CLOSE #1%',
        '200 PRINT "ODL file created"',
        '210 END',
    ]

    for line in odl_lines:
        child.sendline(line)
        time.sleep(0.15)

    time.sleep(1)
    child.sendline('RUN')
    child.expect(['created', 'BASIC2'], timeout=30)
    time.sleep(1)

    child.sendcontrol('z')
    child.expect(['BASIC2', r'\$ '], timeout=10)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Show ODL file
    print("\n=== ODL file contents ===")
    dcl_cmd('TYPE DM1:[1,2]ADVENT.ODL')

    # Run TKB with ODL
    print("\n=== Running TKB with ODL ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)

    # Use ODL file
    child.sendline('DM1:[1,2]ADVENT/FP=@DM1:[1,2]ADVENT.ODL')

    # Wait for TKB to process
    while True:
        idx = child.expect(['TKB>', 'Enter Options:', 'FATAL', 'error', 'undefined', r'\$ ', pexpect.TIMEOUT], timeout=180)
        if idx == 0:
            child.sendline('/')
        elif idx == 1:
            child.sendline('')
        elif idx == 5:
            print("\n*** Build complete ***")
            break
        elif idx in [2, 3, 4]:
            print(f"\n*** TKB Error (idx={idx}) ***")
            # Try to exit TKB
            child.sendcontrol('z')
            child.expect(['TKB>', r'\$ '], timeout=30)
            break
        elif idx == 6:
            print("\n*** TKB Timeout ***")
            break

    time.sleep(2)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    # Assign devices and test
    dcl_cmd('ASSIGN DM1: DK1:')
    dcl_cmd('ASSIGN SY: DK0:')

    # Test the game
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
        'Cannot',
        'Stop',
        'ADVENT',
        'cave',
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
        5: "CANNOT",
        6: "STOPPED",
        7: "ADVENT MSG",
        8: "CAVERN",
        9: "ERROR",
        10: "DCL PROMPT",
        11: "TIMEOUT"
    }

    print(f"\n*** Got: {result_map.get(idx, 'UNKNOWN')} (idx={idx}) ***")

    time.sleep(3)
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
