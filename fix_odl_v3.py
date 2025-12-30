#!/usr/bin/env python3
"""Create ODL file using COPY and EDT substitute."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Create ODL File Using EDT Substitute")
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

    # First, let's check what the original source ODL looked like
    # It references SY:[1,2] but we need DM1:[1,2]
    # The source ODL file was uploaded to DM1:[1,3] earlier

    # Let's see if the src ADVENT.ODL uses SY: - we can copy from that
    # and substitute SY: with DM1:

    # Copy the original ODL from source files (if it exists)
    print("\n=== Looking for source ODL ===")

    # Check if any .ODL exists on DM1:[1,3]
    dcl_cmd('DIR DM1:[1,3]*.ODL')

    # The source files were uploaded - check if ADVINI.SUB exists
    dcl_cmd('DIR DM1:[1,3]ADVINI.SUB')

    # Since the ODL file is corrupt/deleted, let's create it using BASIC
    # with line-oriented output
    print("\n=== Creating ODL file with BASIC ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    # Try to create a file using line output
    lines = [
        "10 OPEN 'DM1:[1,3]ADVENT.ODL' FOR OUTPUT AS FILE #1%",
        "20 PRINT #1%, CHR$(9%);'.ROOT ADVENT-LIBR-*(SUBS)'",
        "30 PRINT #1%, 'SUBS:';CHR$(9%);'.FCTR *(INI,OUT,NOR,CMD,ODD,MSG,BYE,SHT,NPC,PUZ,DSP,FND,TDY)'",
        "40 PRINT #1%, 'INI:';CHR$(9%);'.FCTR DM1:[1,2]ADVINI'",
        "50 PRINT #1%, 'OUT:';CHR$(9%);'.FCTR DM1:[1,2]ADVOUT'",
        "60 PRINT #1%, 'NOR:';CHR$(9%);'.FCTR DM1:[1,2]ADVNOR'",
        "70 PRINT #1%, 'CMD:';CHR$(9%);'.FCTR DM1:[1,2]ADVCMD'",
        "80 PRINT #1%, 'ODD:';CHR$(9%);'.FCTR DM1:[1,2]ADVODD'",
        "90 PRINT #1%, 'MSG:';CHR$(9%);'.FCTR DM1:[1,2]ADVMSG'",
        "100 PRINT #1%, 'BYE:';CHR$(9%);'.FCTR DM1:[1,2]ADVBYE'",
        "110 PRINT #1%, 'SHT:';CHR$(9%);'.FCTR DM1:[1,2]ADVSHT'",
        "120 PRINT #1%, 'NPC:';CHR$(9%);'.FCTR DM1:[1,2]ADVNPC'",
        "130 PRINT #1%, 'PUZ:';CHR$(9%);'.FCTR DM1:[1,2]ADVPUZ'",
        "140 PRINT #1%, 'DSP:';CHR$(9%);'.FCTR DM1:[1,2]ADVDSP'",
        "150 PRINT #1%, 'FND:';CHR$(9%);'.FCTR DM1:[1,2]ADVFND'",
        "160 PRINT #1%, 'TDY:';CHR$(9%);'.FCTR DM1:[1,2]ADVTDY'",
        "170 PRINT #1%, 'LIBR:';CHR$(9%);'.FCTR LB:BP2OTS/LB'",
        "180 PRINT #1%, CHR$(9%);'.END'",
        "190 CLOSE #1%",
        "200 END",
    ]

    for line in lines:
        child.sendline(line)
        child.expect('BASIC2', timeout=10)
        time.sleep(0.2)

    # List the program
    child.sendline('LIST')
    child.expect('BASIC2', timeout=10)

    # Run it
    child.sendline('RUN')
    idx = child.expect(['BASIC2', r'\?'], timeout=30)
    if idx == 1:
        print("\n*** BASIC RUN ERROR ***")
        child.expect('BASIC2', timeout=10)

    child.sendline('EXIT')
    child.expect(r'\$ ', timeout=10)

    # Check the ODL file
    print("\n=== Verifying ODL ===")
    dcl_cmd('DIR/SIZE DM1:[1,3]ADVENT.ODL')
    dcl_cmd('TYPE DM1:[1,3]ADVENT.ODL')

    # Now try TKB
    print("\n=== Running TKB ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)

    child.sendline('DM1:[1,2]ADVENT/FP=DM1:[1,3]ADVENT.ODL')

    # Handle TKB prompts
    while True:
        idx = child.expect(['TKB>', 'Enter Options:', r'\$ ', 'FATAL', pexpect.TIMEOUT], timeout=120)
        if idx == 0:
            child.sendline('/')
        elif idx == 1:
            child.sendline('')
        elif idx == 2:
            break
        elif idx == 3:
            print("\n*** TKB FATAL ***")
            child.expect(['TKB>', r'\$ '], timeout=30)
            child.sendcontrol('z')
            child.expect(r'\$ ', timeout=10)
            break
        elif idx == 4:
            print("\n*** TKB timeout ***")
            break

    print("\n=== Checking result ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    child.close()
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
