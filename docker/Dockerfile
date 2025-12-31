# Advent MUD - PDP-11/RSTS-E in Docker
# A 1987 multi-user dungeon game running on emulated vintage hardware
#
# Build process:
# 1. Run: make build (or python3 scripts/build_disk.py)
# 2. Run: make docker (or docker build -f docker/Dockerfile.new -t advent-mud .)
# 3. Run: make run (or docker compose -f docker-compose.new.yml up -d)

FROM rattydave/alpine-simh:latest

LABEL maintainer="Edward Hibbert"
LABEL description="1987 Advent MUD running on SIMH PDP-11 with RSTS/E"

# Install dependencies
RUN apk add --no-cache \
    ttyd \
    bash \
    python3 \
    expect \
    netcat-openbsd

# Create directories
WORKDIR /opt/advent
RUN mkdir -p disks scripts

# Copy pre-built disk images (run scripts/build_disk.py first)
# Note: kermit.dsk is optional but copied if present for file transfer
COPY build/disks/ /opt/advent/disks/
COPY simh/Disks/kermit.dsk* /opt/advent/disks/

# Copy SIMH configuration
COPY docker/pdp11.ini /opt/advent/

# Copy startup scripts
COPY docker/start.sh /opt/advent/start.sh
COPY docker/autoboot.exp /opt/advent/
COPY docker/game_connect.exp /opt/advent/
COPY docker/admin_connect.sh /opt/advent/
COPY docker/connect.py /opt/advent/scripts/

RUN chmod +x /opt/advent/*.sh /opt/advent/*.exp /opt/advent/scripts/*.py

# Expose ports:
# 7681 = Game web terminal (ttyd)
# 7682 = Admin web terminal (ttyd)
# 2322 = SIMH console (telnet)
# 2323 = RSTS/E terminal lines (telnet)
EXPOSE 7681 7682 2322 2323

# Start the system
CMD ["/opt/advent/start.sh"]
