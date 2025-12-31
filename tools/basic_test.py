#!/usr/bin/env python3
"""Test running a BASIC program."""

import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(30)
sock.connect(('localhost', 2323))

def send(data):
    sock.send((data + "\r").encode('ascii'))
    time.sleep(0.3)

def recv():
    sock.settimeout(3)
    try:
        return sock.recv(4096).decode('ascii', errors='replace')
    except socket.timeout:
        return ""

# Login
time.sleep(3)
send("")
time.sleep(2)
data = recv()
print(f"Initial: {data[:100]}")

if "User:" in data:
    send("[1,2]")
    time.sleep(1)
    data = recv()
    print(f"After user: {data[:100]}")
    send("Digital1977")
    time.sleep(2)
    data = recv()
    print(f"After pass: {data[:200]}")

# Handle detached jobs - keep pressing enter to dismiss
for i in range(5):
    if "Job number" in data:
        print("Dismissing detached job prompt...")
        send("")
        time.sleep(1)
        data = recv()
        print(f"After dismiss: {data[:100]}")
    else:
        break

# Start BASIC
print("Starting BASIC...")
send("BASIC")
time.sleep(2)
data = recv()
print(f"BASIC: {data}")

# Handle more job prompts
for i in range(3):
    if "Job number" in data:
        send("")
        time.sleep(1)
        data = recv()
        print(f"After dismiss: {data[:100]}")

# Load test program
print("Loading TEST.BAS...")
send("OLD TEST.BAS")
time.sleep(1)
data = recv()
print(f"OLD: {data}")

# Run it
print("Running...")
send("RUN")
time.sleep(2)
data = recv()
print(f"RUN: {data}")

# Exit
send("BYE")
time.sleep(1)
print(recv())

sock.close()
