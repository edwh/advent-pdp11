#!/bin/bash
# Direct connection to RSTS/E console for admin access
#
# Uses tcp_connect.py instead of nc because it sets SO_LINGER with timeout=0,
# which sends RST instead of FIN on close. This prevents CLOSE_WAIT states
# that would block subsequent connections to SIMH's single-connection console.
/opt/advent/tcp_connect.py localhost 2322
