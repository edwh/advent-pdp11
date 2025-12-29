# Advent MUD - PDP-11/RSTS-E in Docker
# A 1987 multi-user dungeon game running on emulated vintage hardware

FROM rattydave/alpine-simh:latest

LABEL maintainer="Edward Hibbert"
LABEL description="1987 Advent MUD running on SIMH PDP-11 with RSTS/E"

# Install ttyd for web terminal, expect for auto-login, inetutils-telnet for proper telnet
RUN apk add --no-cache ttyd bash expect inetutils-telnet

# Create directories
RUN mkdir -p /opt/advent/disks /opt/advent/source /opt/advent/data

# Copy RSTS/E disk images
COPY simh/Disks/*.dsk /opt/advent/disks/

# Copy game source files
COPY src/ /opt/advent/source/
COPY data/ /opt/advent/data/

# Copy SIMH configuration
COPY docker/pdp11.ini /opt/advent/

# Create startup and helper scripts
COPY docker/start.sh /opt/advent/
COPY docker/game_connect.exp /opt/advent/
COPY docker/admin_connect.sh /opt/advent/
COPY docker/autoboot.exp /opt/advent/
RUN chmod +x /opt/advent/start.sh /opt/advent/game_connect.exp /opt/advent/admin_connect.sh /opt/advent/autoboot.exp

WORKDIR /opt/advent

# Expose web terminal ports
# 7681 = Game interface (auto-login to Advent)
# 7682 = Admin interface (raw RSTS/E console)
EXPOSE 7681 7682

# Start ttyd with SIMH
CMD ["/opt/advent/start.sh"]
