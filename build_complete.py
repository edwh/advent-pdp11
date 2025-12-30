#!/usr/bin/env python3
"""Build ADVENT.TSK with all object files using TKB indirect file."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK with All Object Files")
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

    # Create TKB command file using BASIC
    print("\n=== Creating TKB command file ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    # Create a command file for TKB
    lines = [
        "10 OPEN 'DM1:[1,2]ADVENT.CMD' FOR OUTPUT AS FILE #1%",
        "20 PRINT #1%,'DM1:[1,2]ADVENT/FP,DM1:[1,2]ADVENT/-'",
        "30 PRINT #1%,'DM1:[1,2]ADVINI,DM1:[1,2]ADVOUT,DM1:[1,2]ADVNOR/-'",
        "40 PRINT #1%,'DM1:[1,2]ADVCMD,DM1:[1,2]ADVODD,DM1:[1,2]ADVMSG/-'",
        "50 PRINT #1%,'DM1:[1,2]ADVBYE,DM1:[1,2]ADVSHT,DM1:[1,2]ADVNPC/-'",
        "60 PRINT #1%,'DM1:[1,2]ADVPUZ,DM1:[1,2]ADVDSP,DM1:[1,2]ADVFND/-'",
        "70 PRINT #1%,'DM1:[1,2]ADVTDY,SY:[1,1]BP2OTS/LB'",
        "80 PRINT #1%,'/'",
        "90 PRINT #1%,''",
        "100 CLOSE #1%",
        "110 END",
    ]

    for line in lines:
        child.sendline(line)
        time.sleep(0.3)

    time.sleep(0.5)
    child.sendline('RUN')
    child.expect('BASIC2', timeout=30)

    child.sendcontrol('z')
    child.expect(['BASIC2', r'\$ '], timeout=10)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Show the command file
    print("\n=== Command file contents ===")
    dcl_cmd('TYPE DM1:[1,2]ADVENT.CMD')

    # Run TKB with the command file
    print("\n=== Running TKB with command file ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)

    child.sendline('@DM1:[1,2]ADVENT.CMD')

    # Wait for TKB to process - this may take a while
    while True:
        idx = child.expect(['TKB>', 'Enter Options:', r'\$ ', 'FATAL', 'error', 'undefined', pexpect.TIMEOUT], timeout=180)
        if idx == 0:
            # At TKB prompt - send / or empty line
            child.sendline('/')
        elif idx == 1:
            # Enter Options - accept defaults
            child.sendline('')
        elif idx == 2:
            # Done - back at DCL
            break
        elif idx in [3, 4]:
            print(f"\n*** TKB Error (idx={idx}) ***")
            child.expect(['TKB>', r'\$ '], timeout=30)
            child.sendcontrol('z')
            child.expect(r'\$ ', timeout=10)
            break
        elif idx == 5:
            print("\n*** Undefined symbols - missing files ***")
            child.expect(['TKB>', r'\$ '], timeout=60)
            break
        elif idx == 6:
            print("\n*** TKB timeout ***")
            break

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    # If exists, try running it
    child.sendline('RUN DM1:[1,2]ADVENT')
    idx = child.expect(['Welcome', 'name', '>', 'file', 'Cannot', r'\?', r'\$ ', pexpect.TIMEOUT], timeout=30)

    result_map = {0: "WELCOME", 1: "NAME PROMPT", 2: "GAME PROMPT", 3: "FILE ERROR",
                  4: "CANNOT", 5: "ERROR", 6: "DCL PROMPT", 7: "TIMEOUT"}
    print(f"\n*** Game test: {result_map.get(idx, 'UNKNOWN')} ***")

    if idx in [0, 1, 2]:
        print("\n*** GAME IS RUNNING! ***")
        time.sleep(2)

    child.close()
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
