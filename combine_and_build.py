#!/usr/bin/env python3
"""Combine all SUB files into one and build with minimal TKB lines."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - Combined Subroutines Approach")
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
    print("\n=== Installing BP2RES ===")
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK')
    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ALLSUB.SUB')
    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ALLSUB.OBJ')

    # Create combined SUB file using PIP to concatenate
    print("\n=== Creating combined subroutine file ===")
    # Use COPY to concatenate all SUB files
    child.sendline('COPY/NOCONFIRM DM1:[1,2]ADVINI.SUB+DM1:[1,2]ADVOUT.SUB+DM1:[1,2]ADVNOR.SUB DM1:[1,2]ALLSUB.SUB')
    time.sleep(2)
    idx = child.expect([r'\$ ', 'replace', pexpect.TIMEOUT], timeout=30)
    if idx == 1:
        child.sendline('Y')
        child.expect(r'\$ ', timeout=15)

    # Append more files
    child.sendline('APPEND DM1:[1,2]ADVCMD.SUB DM1:[1,2]ALLSUB.SUB')
    child.expect(r'\$ ', timeout=30)
    child.sendline('APPEND DM1:[1,2]ADVODD.SUB DM1:[1,2]ALLSUB.SUB')
    child.expect(r'\$ ', timeout=30)
    child.sendline('APPEND DM1:[1,2]ADVMSG.SUB DM1:[1,2]ALLSUB.SUB')
    child.expect(r'\$ ', timeout=30)
    child.sendline('APPEND DM1:[1,2]ADVBYE.SUB DM1:[1,2]ALLSUB.SUB')
    child.expect(r'\$ ', timeout=30)
    child.sendline('APPEND DM1:[1,2]ADVSHT.SUB DM1:[1,2]ALLSUB.SUB')
    child.expect(r'\$ ', timeout=30)
    child.sendline('APPEND DM1:[1,2]ADVNPC.SUB DM1:[1,2]ALLSUB.SUB')
    child.expect(r'\$ ', timeout=30)
    child.sendline('APPEND DM1:[1,2]ADVPUZ.SUB DM1:[1,2]ALLSUB.SUB')
    child.expect(r'\$ ', timeout=30)
    child.sendline('APPEND DM1:[1,2]ADVDSP.SUB DM1:[1,2]ALLSUB.SUB')
    child.expect(r'\$ ', timeout=30)
    child.sendline('APPEND DM1:[1,2]ADVFND.SUB DM1:[1,2]ALLSUB.SUB')
    child.expect(r'\$ ', timeout=30)
    child.sendline('APPEND DM1:[1,2]ADVTDY.SUB DM1:[1,2]ALLSUB.SUB')
    child.expect(r'\$ ', timeout=30)

    # Show file size
    dcl_cmd('DIR/SIZE DM1:[1,2]ALLSUB.SUB')

    # Compile the combined file
    print("\n=== Compiling combined subroutines ===")
    child.sendline('COMPILE DM1:[1,2]ALLSUB.SUB')

    # Wait for compilation
    done = False
    iterations = 0
    while not done and iterations < 30:
        iterations += 1
        idx = child.expect([
            r'\$ ',
            'Error',
            'error',
            pexpect.TIMEOUT
        ], timeout=180)

        if idx == 0:
            done = True
        elif idx in [1, 2]:
            print("\n*** Compilation error ***")
            done = True
        elif idx == 3:
            print(f"\n*** Waiting for compilation ({iterations}/30) ***")

    time.sleep(2)

    # Check for ALLSUB.OBJ
    dcl_cmd('DIR/SIZE DM1:[1,2]ALLSUB.OBJ')

    if 'Total of' in child.before:
        print("\n*** ALLSUB.OBJ created! ***")

        # Run TKB with just 2 input files
        print("\n=== Running TKB ===")
        child.sendline('RUN $TKB')
        child.expect('TKB>', timeout=15)
        time.sleep(1)

        # Just 2 lines: main + combined subs, then library
        child.sendline('DM1:[1,2]ADVENT/FP,DM1:[1,2]ADVENT=DM1:[1,2]ADVENT,DM1:[1,2]ALLSUB/-')
        time.sleep(2)
        idx = child.expect(['TKB>', 'FATAL', pexpect.TIMEOUT], timeout=60)
        if idx == 1:
            print("\n*** FATAL on line 1 ***")
        else:
            child.sendline('SY:[1,1]BP2OTS/LB')
            time.sleep(2)

            # End and handle prompts
            child.sendline('/')
            time.sleep(2)

            done = False
            iterations = 0
            while not done and iterations < 10:
                iterations += 1
                idx = child.expect([
                    'Enter Options:',
                    'TKB>',
                    'FATAL',
                    'overflow',
                    r'\$ ',
                    pexpect.TIMEOUT
                ], timeout=180)

                if idx == 0:
                    child.sendline('')
                elif idx == 1:
                    child.sendline('/')
                elif idx == 4:
                    done = True
                elif idx in [2, 3, 5]:
                    print(f"\n*** Error idx={idx} ***")
                    done = True

        time.sleep(2)

        # Check for ADVENT.TSK
        print("\n=== Checking for ADVENT.TSK ===")
        dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

        if 'Total of' in child.before and 'blocks' in child.before:
            print("\n*** ADVENT.TSK exists! ***")
        else:
            print("\n*** ADVENT.TSK not found ***")
    else:
        print("\n*** ALLSUB.OBJ not found - compilation may have failed ***")

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
