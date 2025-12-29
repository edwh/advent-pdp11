#!/usr/bin/env python3
"""Autoboot RSTS/E - handle boot prompts using telnetlib"""

import telnetlib
import time
import sys

HOST = "localhost"
PORT = 2322

def send_slow(tn, text):
    """Send text character by character with small delays"""
    for char in text:
        tn.write(char.encode('ascii'))
        time.sleep(0.05)

def main():
    print("Waiting for SIMH to start...")
    time.sleep(3)

    print(f"Connecting to {HOST}:{PORT}...")
    try:
        tn = telnetlib.Telnet(HOST, PORT, timeout=30)
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

    print("Connected. Waiting for Option prompt...")

    # Wait for Option prompt
    try:
        tn.read_until(b"Option:", timeout=60)
        print("Got Option prompt, sending linefeed...")
        time.sleep(1)
        tn.write(b"\n")  # linefeed
    except Exception as e:
        print(f"Failed at Option: {e}")
        sys.exit(1)

    # Wait for date prompt
    try:
        tn.read_until(b"DD-MMM-YY", timeout=30)
        print("Got date prompt, sending date...")
        time.sleep(1)
        send_slow(tn, "21-DEC-76")
        tn.write(b"\n")
    except Exception as e:
        print(f"Failed at date: {e}")
        sys.exit(1)

    # Wait for time prompt (format: "12:01 AM?")
    try:
        tn.read_until(b"AM?", timeout=30)
        print("Got time prompt, sending time...")
        time.sleep(1)
        send_slow(tn, "12:00 AM")
        tn.write(b"\n")
    except Exception as e:
        print(f"Failed at time: {e}")
        sys.exit(1)

    # Wait for Command File prompt
    try:
        tn.read_until(b"Command File", timeout=30)
        print("Got Command File prompt, sending enter...")
        time.sleep(1)
        tn.write(b"\n")
    except Exception as e:
        print(f"Failed at Command File: {e}")
        sys.exit(1)

    # Wait for boot to complete
    print("Waiting for RSTS/E to finish booting...")
    time.sleep(10)

    print("RSTS/E boot complete!")
    tn.close()
    sys.exit(0)

if __name__ == "__main__":
    main()
