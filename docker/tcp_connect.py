#!/usr/bin/env python3
"""
TCP Connect - A netcat replacement with proper socket cleanup.

Sets SO_LINGER with timeout=0 to send RST instead of FIN on close.
This prevents CLOSE_WAIT states that block SIMH's single-connection console.

Usage: tcp_connect.py <host> <port>
"""

import sys
import socket
import select
import struct
import os
import signal

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <host> <port>", file=sys.stderr)
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Set SO_LINGER with timeout=0 to send RST instead of FIN on close.
    # This immediately tears down the connection on both sides,
    # preventing CLOSE_WAIT states on the server (SIMH).
    # struct linger { int l_onoff; int l_linger; }
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))

    # Also set TCP_NODELAY to reduce latency
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    # Set socket to non-blocking for select
    sock.setblocking(False)

    # Handle signals gracefully
    def signal_handler(sig, frame):
        sock.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    try:
        # Connect (non-blocking, so use select)
        try:
            sock.connect((host, port))
        except BlockingIOError:
            # Connection in progress, wait for it
            pass

        # Wait for connection to complete (5 second timeout)
        _, writable, _ = select.select([], [sock], [], 5.0)
        if not writable:
            print(f"Connection to {host}:{port} timed out", file=sys.stderr)
            sock.close()
            sys.exit(1)

        # Check if connection succeeded
        err = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if err != 0:
            print(f"Connection failed: {os.strerror(err)}", file=sys.stderr)
            sock.close()
            sys.exit(1)

        # Set stdin to non-blocking
        import fcntl
        flags = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, flags | os.O_NONBLOCK)

        # Main loop - copy data bidirectionally
        while True:
            readable, _, _ = select.select([sock, sys.stdin], [], [], 1.0)

            for fd in readable:
                if fd is sock:
                    # Data from socket -> stdout
                    try:
                        data = sock.recv(4096)
                        if not data:
                            # Server closed connection
                            return
                        sys.stdout.buffer.write(data)
                        sys.stdout.buffer.flush()
                    except (ConnectionResetError, BrokenPipeError):
                        return

                elif fd is sys.stdin:
                    # Data from stdin -> socket
                    try:
                        data = sys.stdin.buffer.read(4096)
                        if not data:
                            # EOF on stdin
                            return
                        sock.sendall(data)
                    except (BlockingIOError, IOError):
                        pass
                    except (ConnectionResetError, BrokenPipeError):
                        return

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    finally:
        # Close socket - this will send RST due to SO_LINGER setting
        sock.close()

if __name__ == '__main__':
    main()
