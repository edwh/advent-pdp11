# Advent MUD - Full build from scratch
#
# This Dockerfile builds SIMH from source and builds ADVENT
# from source on first boot (takes 3-4 hours).
#
# Build: docker build -t advent-mud .
# Run:   docker run -p 8080:8080 advent-mud
#
# The image includes:
# - SIMH PDP-11 emulator (built from source)
# - Base RSTS/E V10.1 disk images (without ADVENT)
# - ADVENT source code and data files
# - setup_advent.py script that runs on first boot to build ADVENT.TSK

FROM debian:bookworm-slim AS simh-builder

# Install build dependencies for SIMH
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libpcap-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Build SIMH using makefile (use v4.0-Beta-1 for expect support)
WORKDIR /src
RUN git clone --branch v4.0-Beta-1 --depth 1 https://github.com/simh/simh.git && \
    cd simh && \
    yes n | make pdp11

# --- Runtime image ---
FROM debian:bookworm-slim

LABEL maintainer="Edward Hibbert"
LABEL description="1987 Advent MUD running on SIMH PDP-11 with RSTS/E"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    expect \
    netcat-openbsd \
    nginx-light \
    python3 \
    libpcap0.8 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install ttyd (not in Debian repos, download binary)
RUN curl -sLo /usr/local/bin/ttyd https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64 && \
    chmod +x /usr/local/bin/ttyd

# Copy SIMH binary from builder
COPY --from=simh-builder /src/simh/BIN/pdp11 /usr/local/bin/pdp11

# Create directories
WORKDIR /opt/advent
RUN mkdir -p disks scripts data src web

# Copy RSTS/E disk images with ADVENT pre-built
# Use base-os disks + SKIP_SETUP=0 if you want to build from source
COPY build/disks/rsts0.dsk /opt/advent/disks/rsts0.dsk
COPY build/disks/rsts1.dsk /opt/advent/disks/rsts1.dsk


# Copy data files for building from source
COPY build/data/ /opt/advent/data/

# Copy source files for building from source
COPY src/*.SUB src/*.B2S /opt/advent/src/

# Copy build scripts
COPY scripts/setup_advent.py /opt/advent/scripts/
COPY scripts/migrate_data.py /opt/advent/scripts/

# Copy configuration
COPY docker/pdp11.ini /opt/advent/
COPY docker/nginx.conf /etc/nginx/nginx.conf

# Copy startup scripts
COPY docker/entrypoint.sh /opt/advent/
COPY docker/game_connect.exp /opt/advent/
COPY docker/game_session.sh /opt/advent/
COPY docker/admin_connect.sh /opt/advent/

# Copy web interface
COPY docker/web/ /opt/advent/web/

# Copy documentation
COPY STATUS.md RESURRECTION.md PROVENANCE.md TECHNICAL.md CONTINUATION.md NEWADV.md /opt/advent/

# Set permissions
RUN chmod +x /opt/advent/*.sh /opt/advent/*.exp /opt/advent/scripts/*.py && \
    chmod 644 /opt/advent/*.md && \
    chmod 644 /opt/advent/web/*

# Expose ports
EXPOSE 8080 7681 7682 2322 2323

# Default: skip setup (using pre-built disk images with ADVENT)
# Set SKIP_SETUP=0 to build from source (requires base-os disk images)
ENV SKIP_SETUP=1

ENTRYPOINT ["/opt/advent/entrypoint.sh"]
