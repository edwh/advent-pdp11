#!/usr/bin/env python3
"""Build ADVENT.TSK with proper overlay structure."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - With Overlay Structure")
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

    # Delete old files
    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK')
    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ADVENT.ODL')

    # Create ODL file using BASIC
    print("\n=== Creating ODL file ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    # Create ODL with overlay structure
    # Main root contains ADVENT (main program)
    # Each subroutine goes in its own overlay segment
    odl_lines = [
        "10 OPEN 'DM1:[1,2]ADVENT.ODL' FOR OUTPUT AS FILE #1%",
        '20 T$=CHR$(9%)',
        # Root segment: main program and library
        '30 PRINT #1%,T$;".ROOT ADVENT-LIBR-*(SEGS)"',
        # Library segment
        '40 PRINT #1%,"LIBR:";T$;".FCTR SY:[1,1]BP2OTS/LB"',
        # Subroutine segments - grouped in overlays
        '50 PRINT #1%,"SEGS:";T$;".FCTR *(OV1,OV2,OV3,OV4,OV5)"',
        # Overlay 1: ADVINI, ADVOUT, ADVNOR
        '60 PRINT #1%,"OV1:";T$;".FCTR DM1:[1,2]ADVINI,DM1:[1,2]ADVOUT,DM1:[1,2]ADVNOR"',
        # Overlay 2: ADVCMD, ADVODD, ADVMSG
        '70 PRINT #1%,"OV2:";T$;".FCTR DM1:[1,2]ADVCMD,DM1:[1,2]ADVODD,DM1:[1,2]ADVMSG"',
        # Overlay 3: ADVBYE, ADVSHT, ADVNPC
        '80 PRINT #1%,"OV3:";T$;".FCTR DM1:[1,2]ADVBYE,DM1:[1,2]ADVSHT,DM1:[1,2]ADVNPC"',
        # Overlay 4: ADVPUZ, ADVDSP, ADVFND
        '90 PRINT #1%,"OV4:";T$;".FCTR DM1:[1,2]ADVPUZ,DM1:[1,2]ADVDSP,DM1:[1,2]ADVFND"',
        # Overlay 5: ADVTDY
        '100 PRINT #1%,"OV5:";T$;".FCTR DM1:[1,2]ADVTDY"',
        '110 PRINT #1%,T$;".END"',
        '120 CLOSE #1%',
        '130 PRINT "ODL file created"',
        '140 END',
    ]

    for line in odl_lines:
        child.sendline(line)
        time.sleep(0.15)

    time.sleep(1)
    child.sendline('RUN')
    child.expect(['created', 'BASIC2', pexpect.TIMEOUT], timeout=30)
    time.sleep(1)

    child.sendcontrol('z')
    child.expect(['BASIC2', r'\$ '], timeout=10)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Show ODL file
    print("\n=== ODL file contents ===")
    dcl_cmd('TYPE DM1:[1,2]ADVENT.ODL')

    # Run TKB with ODL
    print("\n=== Running TKB ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)

    # Use ODL file
    child.sendline('DM1:[1,2]ADVENT/FP,DM1:[1,2]ADVENT=DM1:[1,2]ADVENT,@DM1:[1,2]ADVENT.ODL')

    # Handle TKB prompts
    while True:
        idx = child.expect([
            'TKB>',
            'Enter Options:',
            'FATAL',
            'error',
            'undefined',
            'overflow',
            r'\$ ',
            pexpect.TIMEOUT
        ], timeout=180)

        if idx == 0:
            # TKB prompt - send / to end
            child.sendline('/')
        elif idx == 1:
            # Options prompt - accept defaults
            child.sendline('')
        elif idx == 6:
            # DCL prompt - done
            print("\n*** TKB completed ***")
            break
        elif idx in [2, 3, 4, 5]:
            print(f"\n*** TKB Error (idx={idx}) ***")
            # Try to exit
            time.sleep(2)
            continue
        elif idx == 7:
            print("\n*** Timeout ***")
            break

    time.sleep(2)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    # Check if file exists
    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** ADVENT.TSK exists! ***")

        # Setup devices
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
            'cave',
            'ADVENT',
            r'\?',
            r'\$ ',
            pexpect.TIMEOUT
        ], timeout=90)

        result_map = {
            0: "WELCOME",
            1: "NAME PROMPT",
            2: "NAME",
            3: "GAME PROMPT",
            4: "CAVERN",
            5: "ADVENT MSG",
            6: "ERROR",
            7: "DCL PROMPT",
            8: "TIMEOUT"
        }

        print(f"\n*** Got: {result_map.get(idx, 'UNKNOWN')} (idx={idx}) ***")
    else:
        print("\n*** ADVENT.TSK not found ***")

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
