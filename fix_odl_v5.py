#!/usr/bin/env python3
"""Create ODL file using BASIC - fixed exit."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Create ODL File Using BASIC Program")
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

    # Create ODL using BASIC
    print("\n=== Creating ODL file with BASIC ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    # Enter program lines
    def basic_line(line):
        child.sendline(line)
        time.sleep(0.5)

    basic_line("10 OPEN 'DM1:[1,3]ADVENT.ODL' FOR OUTPUT AS FILE #1%")
    basic_line("20 T$=CHR$(9%)")
    basic_line("30 PRINT #1%,T$;'.ROOT ADVENT-LIBR-*(SUBS)'")
    basic_line("40 PRINT #1%,'SUBS:';T$;'.FCTR *(INI,OUT,NOR,CMD,ODD,MSG,BYE,SHT,NPC,PUZ,DSP,FND,TDY)'")
    basic_line("50 PRINT #1%,'INI:';T$;'.FCTR DM1:[1,2]ADVINI'")
    basic_line("60 PRINT #1%,'OUT:';T$;'.FCTR DM1:[1,2]ADVOUT'")
    basic_line("70 PRINT #1%,'NOR:';T$;'.FCTR DM1:[1,2]ADVNOR'")
    basic_line("80 PRINT #1%,'CMD:';T$;'.FCTR DM1:[1,2]ADVCMD'")
    basic_line("90 PRINT #1%,'ODD:';T$;'.FCTR DM1:[1,2]ADVODD'")
    basic_line("100 PRINT #1%,'MSG:';T$;'.FCTR DM1:[1,2]ADVMSG'")
    basic_line("110 PRINT #1%,'BYE:';T$;'.FCTR DM1:[1,2]ADVBYE'")
    basic_line("120 PRINT #1%,'SHT:';T$;'.FCTR DM1:[1,2]ADVSHT'")
    basic_line("130 PRINT #1%,'NPC:';T$;'.FCTR DM1:[1,2]ADVNPC'")
    basic_line("140 PRINT #1%,'PUZ:';T$;'.FCTR DM1:[1,2]ADVPUZ'")
    basic_line("150 PRINT #1%,'DSP:';T$;'.FCTR DM1:[1,2]ADVDSP'")
    basic_line("160 PRINT #1%,'FND:';T$;'.FCTR DM1:[1,2]ADVFND'")
    basic_line("170 PRINT #1%,'TDY:';T$;'.FCTR DM1:[1,2]ADVTDY'")
    basic_line("180 PRINT #1%,'LIBR:';T$;'.FCTR LB:BP2OTS/LB'")
    basic_line("190 PRINT #1%,T$;'.END'")
    basic_line("200 CLOSE #1%")
    basic_line("210 END")

    time.sleep(1)

    # Run it
    print("\n=== Running BASIC program ===")
    child.sendline('RUN')
    child.expect('BASIC2', timeout=30)

    # Exit BASIC - use Ctrl+Z which always exits
    child.sendcontrol('z')
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
    build_success = False
    while True:
        idx = child.expect(['TKB>', 'Enter Options:', r'\$ ', 'FATAL', pexpect.TIMEOUT], timeout=120)
        if idx == 0:
            child.sendline('/')
        elif idx == 1:
            child.sendline('')
        elif idx == 2:
            build_success = True
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

    if build_success:
        print("\n*** BUILD SUCCESSFUL! ***")

    child.close()
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return build_success

if __name__ == '__main__':
    main()
