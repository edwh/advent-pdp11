#!/bin/bash
#
# ADVENT MUD Game Session Script
#
# This script runs the game login expect script directly.
# Each user gets their own game session.
#

EXPECT_SCRIPT="/opt/advent/game_connect.exp"

echo ""
echo "============================================="
echo "    ADVENT MUD - 1987 Multi-User Dungeon"
echo "    Running on RSTS/E V10.1"
echo "============================================="
echo ""
echo "Connecting to the PDP-11..."
echo ""

# Configure terminal to not send LF after CR
# RSTS/E only expects CR, and treats LF as an empty command (producing "?" prompts)
stty -icrnl -onlcr -inlcr igncr 2>/dev/null || true

# Run the expect script directly - it handles login and runs ADVENT
exec "$EXPECT_SCRIPT"
