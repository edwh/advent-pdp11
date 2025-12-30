#!/usr/bin/env python3
"""Create ODL file using EDT editor and rebuild ADVENT.TSK."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Creating ODL with EDT and Rebuilding ADVENT.TSK")
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

    # Install BP2RES library first
    print("\n=== Installing BP2RES library ===")
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Check current ODL content
    print("\n=== Current ADVENT.ODL content ===")
    dcl_cmd('TYPE DM1:[1,3]ADVENT.ODL')

    # Delete old ODL
    dcl_cmd('DELETE/NOCONFIRM DM1:[1,3]ADVENT.ODL')

    # Use EDT to create the ODL file
    print("\n=== Creating ADVENT.ODL with EDT ===")
    child.sendline('EDT DM1:[1,3]ADVENT.ODL')

    # EDT starts in command mode, switch to line insert mode
    idx = child.expect([r'\*', 'Input file'], timeout=15)
    if idx == 1:
        child.expect(r'\*', timeout=10)

    # Insert the ODL content line by line
    child.sendline('INSERT')

    # ODL lines - EDT uses line-at-a-time input
    odl_lines = [
        '\t.ROOT ADVENT-LIBR-*(SUBS)',
        'SUBS:\t.FCTR *(INI,OUT,NOR,CMD,ODD,MSG,BYE,SHT,NPC,PUZ,DSP,FND,TDY)',
        'INI:\t.FCTR DM1:[1,2]ADVINI',
        'OUT:\t.FCTR DM1:[1,2]ADVOUT',
        'NOR:\t.FCTR DM1:[1,2]ADVNOR',
        'CMD:\t.FCTR DM1:[1,2]ADVCMD',
        'ODD:\t.FCTR DM1:[1,2]ADVODD',
        'MSG:\t.FCTR DM1:[1,2]ADVMSG',
        'BYE:\t.FCTR DM1:[1,2]ADVBYE',
        'SHT:\t.FCTR DM1:[1,2]ADVSHT',
        'NPC:\t.FCTR DM1:[1,2]ADVNPC',
        'PUZ:\t.FCTR DM1:[1,2]ADVPUZ',
        'DSP:\t.FCTR DM1:[1,2]ADVDSP',
        'FND:\t.FCTR DM1:[1,2]ADVFND',
        'TDY:\t.FCTR DM1:[1,2]ADVTDY',
        'LIBR:\t.FCTR LB:BP2OTS/LB',
        '\t.END'
    ]

    for line in odl_lines:
        # Send line and wait for next line prompt
        child.sendline(line)
        time.sleep(0.2)

    # Exit insert mode with Ctrl+Z and save
    child.sendcontrol('z')
    child.expect(r'\*', timeout=10)

    # Write (save) and exit
    child.sendline('EXIT')
    child.expect(r'\$ ', timeout=10)

    # Verify the ODL file
    print("\n=== Verifying ADVENT.ODL ===")
    dcl_cmd('TYPE DM1:[1,3]ADVENT.ODL')
    dcl_cmd('DIR DM1:[1,3]ADVENT.ODL')

    # Now run TKB
    print("\n=== Running TKB ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)

    child.sendline('DM1:[1,2]ADVENT/FP=DM1:[1,3]ADVENT.ODL')

    # Handle TKB prompts
    build_success = False
    while True:
        idx = child.expect(['TKB>', 'Enter Options:', r'\$ ', 'FATAL', 'error', pexpect.TIMEOUT], timeout=120)
        if idx == 0:
            child.sendline('/')
        elif idx == 1:
            child.sendline('')
        elif idx == 2:
            build_success = True
            break
        elif idx in [3, 4]:
            print(f"\n*** TKB ERROR (idx={idx}) ***")
            child.expect(r'\$ ', timeout=30)
            break
        elif idx == 5:
            print("\n*** TKB timeout ***")
            break

    print("\n=== Verifying ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    if build_success:
        print("\n*** BUILD SUCCESSFUL! ***")

    child.close()
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return build_success

if __name__ == '__main__':
    main()
