#!/usr/bin/env python3
"""Build ADVENT.TSK using batch job submission."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - Batch Job Approach")
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

    # Create batch control file
    print("\n=== Creating batch control file ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    # Create .CTL file for batch processing
    ctl_lines = [
        "10 OPEN 'DM1:[1,2]TKB.CTL' FOR OUTPUT AS FILE #1%",
        # Job header
        "20 PRINT #1%,'$ JOB TKB/ACCOUNT:[1,2]/PASSWORD:Digital1977'",
        # Delete old TSK
        "30 PRINT #1%,'$ DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK'",
        # Run TKB
        "40 PRINT #1%,'$ RUN $TKB'",
        # TKB commands
        "50 PRINT #1%,'DM1:[1,2]ADVENT/FP,DM1:[1,2]ADVENT=DM1:[1,2]ADVENT/-'",
        "60 PRINT #1%,'DM1:[1,2]ADVINI,DM1:[1,2]ADVOUT,DM1:[1,2]ADVNOR/-'",
        "70 PRINT #1%,'DM1:[1,2]ADVCMD,DM1:[1,2]ADVODD,DM1:[1,2]ADVMSG/-'",
        "80 PRINT #1%,'DM1:[1,2]ADVBYE,DM1:[1,2]ADVSHT,DM1:[1,2]ADVNPC/-'",
        "90 PRINT #1%,'DM1:[1,2]ADVPUZ,DM1:[1,2]ADVDSP,DM1:[1,2]ADVFND/-'",
        "100 PRINT #1%,'DM1:[1,2]ADVTDY,SY:[1,1]BP2OTS/LB'",
        "110 PRINT #1%,'/'",
        "120 PRINT #1%,'/'",
        # Show result
        "130 PRINT #1%,'$ DIR/SIZE DM1:[1,2]ADVENT.TSK'",
        "140 PRINT #1%,'$ EOJ'",
        "150 CLOSE #1%",
        "160 PRINT 'Batch file created'",
        "170 END",
    ]

    for line in ctl_lines:
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

    # Show control file
    print("\n=== Control file contents ===")
    dcl_cmd('TYPE DM1:[1,2]TKB.CTL')

    # Submit batch job
    print("\n=== Submitting batch job ===")
    child.sendline('SUBMIT DM1:[1,2]TKB.CTL')
    time.sleep(3)
    child.expect(r'\$ ', timeout=30)

    # Wait for batch job to complete
    print("\n=== Waiting for batch job ===")
    for i in range(12):  # Wait up to 2 minutes
        time.sleep(10)
        child.sendline('SHOW QUEUE')
        idx = child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)
        if 'TKB' not in child.before:
            print("\n*** Batch job completed ***")
            break
        print(f"*** Waiting... ({i+1}/12) ***")

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    # Check batch log
    print("\n=== Checking batch log ===")
    dcl_cmd('TYPE DM1:[1,2]TKB.LOG', timeout=30)

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
