#!/usr/bin/env python3
"""Build ADVENT.TSK - try < redirect syntax."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - Redirect syntax")
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
        time.sleep(0.5)

    # Install BP2RES
    print("\n=== Installing BP2RES library ===")
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Delete old TSK
    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK')

    # Create a simplified command file that TKB can process directly
    # This is just the TKB commands, not ODL syntax
    print("\n=== Creating TKB command file ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    # Create command file with TKB commands
    cmd_lines = [
        "10 OPEN 'DM1:[1,2]TKB.CMD' FOR OUTPUT AS FILE #1%",
        "20 PRINT #1%,'DM1:[1,2]ADVENT/FP,DM1:[1,2]ADVENT=DM1:[1,2]ADVENT/-'",
        "30 PRINT #1%,'DM1:[1,2]ADVINI,DM1:[1,2]ADVOUT,DM1:[1,2]ADVNOR/-'",
        "40 PRINT #1%,'DM1:[1,2]ADVCMD,DM1:[1,2]ADVODD/-'",
        "50 PRINT #1%,'DM1:[1,2]ADVMSG,DM1:[1,2]ADVBYE/-'",
        "60 PRINT #1%,'DM1:[1,2]ADVSHT,DM1:[1,2]ADVNPC/-'",
        "70 PRINT #1%,'DM1:[1,2]ADVPUZ,DM1:[1,2]ADVDSP/-'",
        "80 PRINT #1%,'DM1:[1,2]ADVFND,DM1:[1,2]ADVTDY,SY:[1,1]BP2OTS/LB'",
        "90 PRINT #1%,'/'",
        "100 PRINT #1%,'/'",
        "110 CLOSE #1%",
        "120 PRINT 'Command file created'",
        "130 END",
    ]

    for line in cmd_lines:
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

    # Show command file
    print("\n=== Command file contents ===")
    dcl_cmd('TYPE DM1:[1,2]TKB.CMD')

    # Run TKB with input from command file using < redirect
    print("\n=== Running TKB with input redirect ===")

    # Try: RUN $TKB <DM1:[1,2]TKB.CMD
    child.sendline('RUN $TKB <DM1:[1,2]TKB.CMD')

    # Handle TKB output
    done = False
    iterations = 0
    while not done and iterations < 30:
        iterations += 1
        idx = child.expect([
            'TKB>',
            'Enter Options:',
            'FATAL',
            'error',
            'undefined',
            'overflow',
            'Invalid',
            r'\$ ',
            pexpect.TIMEOUT
        ], timeout=180)

        print(f"\n*** idx={idx} ***")

        if idx == 0:
            # TKB prompt - shouldn't happen with redirect but handle it
            child.sendline('/')
        elif idx == 1:
            child.sendline('')
        elif idx == 7:
            done = True
        elif idx in [2, 3, 4, 5, 6]:
            print(f"\n*** Error ***")
            time.sleep(1)
        elif idx == 8:
            print("\n*** Timeout ***")
            done = True

    time.sleep(2)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** ADVENT.TSK exists! ***")

        dcl_cmd('ASSIGN DM1: DK1:')
        dcl_cmd('ASSIGN SY: DK0:')

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
