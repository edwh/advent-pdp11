#!/usr/bin/env python3
"""Run SIMPLE.BAS in BASIC-PLUS-2."""

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
if "User:" in data:
    send("[1,2]")
    time.sleep(1)
    recv()
    send("Digital1977")
    time.sleep(2)
    data = recv()
    # Dismiss detached jobs
    while "Job number" in data:
        send("")
        time.sleep(1)
        data = recv()

# Start BASIC
print("Starting BASIC...")
send("BASIC")
time.sleep(2)
data = recv()
print(f"BASIC: {data[-100:]}")

# Handle any job prompts
while "Job number" in data:
    send("")
    time.sleep(1)
    data = recv()

# Load program
print("Loading SIMPLE.BAS...")
send("OLD SIMPLE.BAS")
time.sleep(1)
data = recv()
print(f"OLD: {data}")

# Run
print("Running...")
send("RUN")
time.sleep(3)
data = recv()
print(f"RUN output:\n{data}")

# Exit
send("BYE")
time.sleep(1)
print(recv())

sock.close()
