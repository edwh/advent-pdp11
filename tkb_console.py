#!/usr/bin/env python3
"""Build ADVENT.TSK using console port instead of DZ terminal."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - Via Console Port (2322)")
    print("=" * 60)

    # Connect to console port instead of DZ
    child = pexpect.spawn('telnet localhost 2322', encoding='latin-1')
    child.logfile = sys.stdout

    try:
        child.expect('Connected to the PDP-11', timeout=10)
    except pexpect.TIMEOUT:
        print("\n*** Cannot connect ***")
        return False

    time.sleep(2)
    child.sendline('')
    time.sleep(1)

    # On console, we might see a different prompt
    idx = child.expect(['$', 'User:', 'OPR>', ']', pexpect.TIMEOUT], timeout=30)
    print(f"\n*** Initial prompt idx={idx} ***")

    if idx == 1:
        # Need to login
        child.sendline('[1,2]')
        child.expect('Password:', timeout=10)
        child.sendline('Digital1977')
        child.expect(['$', 'Job'], timeout=30)

    # Try to get a DCL prompt
    child.sendline('')
    time.sleep(1)
    idx = child.expect(['$', 'OPR>', pexpect.TIMEOUT], timeout=10)

    if idx == 1:
        # OPR prompt - exit operator mode
        child.sendline('EXIT')
        child.expect('$', timeout=10)

    print("\n*** At DCL prompt ***")

    def dcl_cmd(cmd, timeout=15):
        child.sendline(cmd)
        child.expect(r'\$', timeout=timeout)
        time.sleep(0.5)

    # Install BP2RES
    print("\n=== Installing BP2RES library ===")
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$', timeout=10)

    # Delete old TSK
    dcl_cmd('DELETE/NOCONFIRM SY:[1,2]ADVENT.TSK')

    # Run TKB
    print("\n=== Running TKB (via console) ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)
    time.sleep(1)

    # Same 3 lines as before
    tkb_lines = [
        'SY:[1,2]ADVENT/FP,SY:[1,2]ADVENT=SY:[1,2]ADVENT,SY:[1,2]ADVINI/-',
        'SY:[1,2]ADVOUT,SY:[1,2]ADVNOR,SY:[1,2]ADVCMD/-',
        'SY:[1,2]ADVMSG,SY:[1,1]BP2OTS/LB',
    ]

    for i, line in enumerate(tkb_lines):
        print(f"\n>>> [{i+1}/{len(tkb_lines)}] {line[:60]}...")
        child.sendline(line)
        time.sleep(2)

        idx = child.expect(['TKB>', 'FATAL', 'error', 'trap', pexpect.TIMEOUT], timeout=60)
        if idx == 1:
            print("\n*** FATAL error ***")
            child.sendcontrol('z')
            child.expect([r'\$', pexpect.TIMEOUT], timeout=10)
            return False
        elif idx == 3:
            print("\n*** Trap error ***")
            return False
        elif idx == 4:
            print("\n*** Timeout ***")
            return False

    # End file input
    print("\n>>> Sending: /")
    child.sendline('/')
    time.sleep(2)

    # Handle options
    idx = child.expect(['Enter Options:', 'TKB>', 'FATAL', 'undefined', r'\$', pexpect.TIMEOUT], timeout=120)
    print(f"\n*** After /: idx={idx} ***")

    if idx == 0:
        child.sendline('')
        time.sleep(3)
        idx2 = child.expect(['TKB>', r'\$', pexpect.TIMEOUT], timeout=180)
        if idx2 == 0:
            child.sendline('/')
            child.expect([r'\$', pexpect.TIMEOUT], timeout=120)
    elif idx == 1:
        child.sendline('/')
        child.expect([r'\$', pexpect.TIMEOUT], timeout=120)
    elif idx == 3:
        print("\n*** Undefined symbols ***")
        child.expect('TKB>', timeout=60)
        child.sendline('/')
        child.expect([r'\$', pexpect.TIMEOUT], timeout=60)

    time.sleep(2)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE SY:[1,2]ADVENT.TSK')

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** ADVENT.TSK exists! ***")
    else:
        print("\n*** ADVENT.TSK not found ***")

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
