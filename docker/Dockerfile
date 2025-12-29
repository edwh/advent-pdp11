# Advent MUD - PDP-11/RSTS-E in Docker
# A 1987 multi-user dungeon game running on emulated vintage hardware

FROM alpine:latest

LABEL maintainer="Edward Hibbert"
LABEL description="1987 Advent MUD running on SIMH PDP-11 with RSTS/E"

# Install build dependencies and runtime tools
RUN apk add --no-cache \
    build-base \
    git \
    ttyd \
    bash \
    curl \
    && rm -rf /var/cache/apk/*

# Build SIMH from source (for latest PDP-11 emulator)
WORKDIR /tmp
RUN git clone --depth 1 https://github.com/simh/simh.git && \
    cd simh && \
    make pdp11 && \
    cp BIN/pdp11 /usr/local/bin/ && \
    cd / && \
    rm -rf /tmp/simh

# Create directories
RUN mkdir -p /opt/advent/disks /opt/advent/tapes /opt/advent/source

# Copy RSTS/E disk images
COPY simh/Disks/*.dsk /opt/advent/disks/

# Copy game source files
COPY *.B2S *.SUB *.BAS *.MAC /opt/advent/source/
COPY data/ /opt/advent/data/

# Copy SIMH configuration
COPY docker/pdp11.ini /opt/advent/

# Create startup script
COPY docker/start.sh /opt/advent/
RUN chmod +x /opt/advent/start.sh

WORKDIR /opt/advent

# Expose web terminal port
EXPOSE 7681

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:7681/ || exit 1

# Start ttyd with SIMH
CMD ["/opt/advent/start.sh"]
