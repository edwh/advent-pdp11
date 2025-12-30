#!/usr/bin/env python3
"""Create correct ODL file and rebuild ADVENT.TSK inside RSTS/E."""

import pexpect
import sys
import time

# The correct ODL content with DM1: paths
ODL_CONTENT = """\
	.ROOT ADVENT-LIBR-*(SUBS)
SUBS:	.FCTR *(INI,OUT,NOR,CMD,ODD,MSG,BYE,SHT,NPC,PUZ,DSP,FND,TDY)
INI:	.FCTR DM1:[1,2]ADVINI
OUT:	.FCTR DM1:[1,2]ADVOUT
NOR:	.FCTR DM1:[1,2]ADVNOR
CMD:	.FCTR DM1:[1,2]ADVCMD
ODD:	.FCTR DM1:[1,2]ADVODD
MSG:	.FCTR DM1:[1,2]ADVMSG
BYE:	.FCTR DM1:[1,2]ADVBYE
SHT:	.FCTR DM1:[1,2]ADVSHT
NPC:	.FCTR DM1:[1,2]ADVNPC
PUZ:	.FCTR DM1:[1,2]ADVPUZ
DSP:	.FCTR DM1:[1,2]ADVDSP
FND:	.FCTR DM1:[1,2]ADVFND
TDY:	.FCTR DM1:[1,2]ADVTDY
LIBR:	.FCTR LB:BP2OTS/LB
	.END
"""

def main():
    print("=" * 60)
    print("Fixing ODL File and Rebuilding ADVENT.TSK")
    print("=" * 60)

    child = pexpect.spawn('telnet localhost 2323', encoding='latin-1')
    child.logfile = sys.stdout

    # Wait for connection
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

    # Delete old ODL file
    dcl_cmd('DELETE/NOCONFIRM DM1:[1,3]ADVENT.ODL')

    # Create new ODL file using BASIC
    print("\n=== Creating ADVENT.ODL with correct DM1: paths ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    # Create sequential file for ODL
    child.sendline('OPEN "DM1:[1,3]ADVENT.ODL" FOR OUTPUT AS FILE #1%')
    child.expect('BASIC2', timeout=10)

    # Write each line of the ODL
    odl_lines = ODL_CONTENT.strip().split('\n')
    for line in odl_lines:
        # Escape any special characters and write
        escaped_line = line.replace('"', '""').replace('\\', '\\\\')
        child.sendline(f'PRINT #1%, "{escaped_line}"')
        child.expect('BASIC2', timeout=10)

    child.sendline('CLOSE #1%')
    child.expect('BASIC2', timeout=10)

    child.sendline('EXIT')
    child.expect(r'\$ ', timeout=10)

    # Verify the ODL file
    print("\n=== Verifying ADVENT.ODL ===")
    dcl_cmd('TYPE DM1:[1,3]ADVENT.ODL')

    # Now run TKB
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
            print("\n*** TKB FATAL ERROR ***")
            child.expect(r'\$ ', timeout=30)
            break
        elif idx == 4:
            print("\n*** TKB timeout ***")
            break

    print("\n=== Verifying ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    child.close()
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
