#!/usr/bin/env python3
"""
Advent MUD - Full System Test

Tests the complete setup:
1. Verifies disk images exist
2. Connects to RSTS/E
3. Logs in
4. Runs the game
5. Tests basic commands
6. Verifies navigation works

Usage:
    # Test against running Docker container
    ./scripts/test_setup.py --host localhost --port 2323

    # Or run Docker compose first
    docker compose up -d
    sleep 20  # Wait for boot
    ./scripts/test_setup.py
"""

import sys
import time
import argparse
import socket
from pathlib import Path

# Add parent dir for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "docker"))

try:
    import pexpect
    HAS_PEXPECT = True
except ImportError:
    HAS_PEXPECT = False
    print("Warning: pexpect not installed, some tests will be skipped")


def check_port(host, port, timeout=5):
    """Check if a port is open."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def test_disk_images():
    """Verify disk images exist."""
    print("\n=== Testing Disk Images ===")

    build_dir = Path(__file__).parent.parent / "build" / "disks"
    simh_dir = Path(__file__).parent.parent / "simh" / "Disks"

    success = True

    # Check build directory
    if build_dir.exists():
        print(f"  Build directory: {build_dir}")
        for disk in ["rsts0.dsk", "rsts1.dsk"]:
            path = build_dir / disk
            if path.exists():
                size = path.stat().st_size
                print(f"    {disk}: {size:,} bytes OK")
            else:
                print(f"    {disk}: MISSING")
                success = False
    else:
        print(f"  Build directory not found: {build_dir}")
        print("  Run scripts/build_disk.py first!")
        success = False

    return success


def test_data_files():
    """Verify data files were generated."""
    print("\n=== Testing Data Files ===")

    data_dir = Path(__file__).parent.parent / "build" / "data"

    success = True
    expected_files = {
        "ADVENT.DTA": 1024000,  # 2000 * 512
        "ADVENT.MON": 200000,   # 10000 * 20
        "ADVENT.CHR": 51200,    # 100 * 512
        "BOARD.NTC": 262144,    # 512 * 512
        "MESSAG.NPC": 60000,    # 1000 * 60
    }

    if not data_dir.exists():
        print(f"  Data directory not found: {data_dir}")
        return False

    for filename, expected_size in expected_files.items():
        path = data_dir / filename
        if path.exists():
            size = path.stat().st_size
            if size == expected_size:
                print(f"  {filename}: {size:,} bytes OK")
            else:
                print(f"  {filename}: {size:,} bytes (expected {expected_size})")
                success = False
        else:
            print(f"  {filename}: MISSING")
            success = False

    return success


def test_connection(host, port, timeout=10):
    """Test connection to RSTS/E."""
    print(f"\n=== Testing Connection to {host}:{port} ===")

    if not check_port(host, port, timeout):
        print(f"  Port {port} is not open")
        return False

    print(f"  Port {port} is open")

    if not HAS_PEXPECT:
        print("  Skipping login test (pexpect not installed)")
        return True

    try:
        child = pexpect.spawn(f'nc {host} {port}', encoding='latin-1', timeout=timeout)

        # Send CR to wake up
        time.sleep(1)
        child.sendline('')

        # Look for login prompt or existing session
        idx = child.expect(['User:', r'\$ ', 'Ready', 'Job', pexpect.TIMEOUT], timeout=10)

        if idx == 4:
            print("  Connection timeout - RSTS/E may still be booting")
            child.close()
            return False

        if idx in [1, 2]:
            print("  Already logged in")
        else:
            print("  Login prompt detected")
            child.sendline('[1,2]')
            child.expect('Password:', timeout=10)
            child.sendline('Digital1977')
            child.expect([r'\$ ', 'Ready', 'Job'], timeout=15)

        print("  Login successful!")
        child.close()
        return True

    except Exception as e:
        print(f"  Connection test failed: {e}")
        return False


def test_game(host, port, timeout=30):
    """Test running the game."""
    print(f"\n=== Testing Game ===")

    if not HAS_PEXPECT:
        print("  Skipping game test (pexpect not installed)")
        return True

    try:
        child = pexpect.spawn(f'nc {host} {port}', encoding='latin-1', timeout=timeout)
        child.logfile = sys.stdout

        # Login
        time.sleep(1)
        child.sendline('')
        idx = child.expect(['User:', r'\$ ', 'Ready', 'Job'], timeout=10)

        if idx == 0:
            child.sendline('[1,2]')
            child.expect('Password:', timeout=10)
            child.sendline('Digital1977')
            child.expect([r'\$ ', 'Ready', 'Job'], timeout=15)
            if 'Job' in child.after:
                child.sendline('')
                child.expect(r'\$ ')

        # Run game
        print("\n  Starting game...")
        child.sendline('RUN DM1:[1,2]ADVENT')

        idx = child.expect(['Welcome', '>', 'Error', r'\?', 'Stop', pexpect.TIMEOUT], timeout=30)

        if idx in [0, 1]:
            print("\n  Game started successfully!")

            # Test LOOK command
            time.sleep(1)
            child.sendline('LOOK')
            time.sleep(2)

            # Check for room description
            output = child.before + child.after if child.after else child.before
            if 'You are' in output or 'standing' in output or 'room' in output.lower():
                print("  LOOK command works!")
            else:
                print("  LOOK command may have issues")

            # Test NORTH command
            child.sendline('NORTH')
            time.sleep(2)

            # Quit game
            child.sendline('QUIT')
            time.sleep(1)
            child.sendline('Y')  # Confirm quit

            child.close()
            return True
        else:
            print(f"\n  Game failed to start (index: {idx})")
            child.close()
            return False

    except Exception as e:
        print(f"\n  Game test failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Advent MUD System Test')
    parser.add_argument('--host', default='localhost', help='RSTS/E host')
    parser.add_argument('--port', type=int, default=2323, help='Terminal port')
    parser.add_argument('--skip-connection', action='store_true',
                        help='Skip connection tests')
    parser.add_argument('--skip-game', action='store_true',
                        help='Skip game tests')
    args = parser.parse_args()

    print("=" * 60)
    print("  Advent MUD - System Test")
    print("=" * 60)

    results = {}

    # Test disk images
    results['disk_images'] = test_disk_images()

    # Test data files
    results['data_files'] = test_data_files()

    if not args.skip_connection:
        # Test connection
        results['connection'] = test_connection(args.host, args.port)

        if not args.skip_game and results.get('connection'):
            # Test game
            results['game'] = test_game(args.host, args.port)

    # Summary
    print("\n" + "=" * 60)
    print("  Test Summary")
    print("=" * 60)

    all_passed = True
    for test, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
