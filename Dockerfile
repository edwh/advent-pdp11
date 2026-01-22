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

# Build SIMH using makefile (use latest master for expect support + character dropping fix)
# Note: v4.0-Beta-1 had known issues with dropped input characters (GitHub issue #246)
WORKDIR /src
RUN git clone --depth 1 https://github.com/simh/simh.git && \
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
    procps \
    telnet \
    screen \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# Install ttyd (not in Debian repos, download binary)
RUN curl -sLo /usr/local/bin/ttyd https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64 && \
    chmod +x /usr/local/bin/ttyd

# Copy SIMH binary from builder
COPY --from=simh-builder /src/simh/BIN/pdp11 /usr/local/bin/pdp11

# Create directories
WORKDIR /opt/advent
RUN mkdir -p disks disks-backup scripts data src web tapes

# RSTS/E Disk Image Handling
#
# IMPORTANT: RSTS/E swap files get corrupted if the system doesn't shut down cleanly.
# This happens on docker restart, docker stop without clean SHUTUP, or any crash.
# The corruption causes "Swap file is invalid" errors on next boot.
#
# Solution: Keep pristine backup disks in disks-backup/ and restore them on each
# container start. This sacrifices persistence but ensures reliable boots.
# The entrypoint.sh copies from disks-backup/ to disks/ before starting SIMH.
#
# Source: simh/Disks/rsts_backup.dsk and rsts1_backup.dsk are the known-good images.

# RA72 disk image (pristine base OS, ADVENT will be built from source)
# Using RA72 with MSCP controller and TMSCP tape (MU0:)
# Disk image is split into 50MB parts to stay under GitHub's file size limit
# Assemble them during build
COPY simh/Disks/ra72/rstse_10_ra72.dsk.part_* /tmp/disk_parts/
RUN cat /tmp/disk_parts/rstse_10_ra72.dsk.part_* > /opt/advent/disks-backup/rstse_10_ra72.dsk && \
    rm -rf /tmp/disk_parts

# Working disk (restored from backup on each start by entrypoint.sh)
RUN cp /opt/advent/disks-backup/rstse_10_ra72.dsk /opt/advent/disks/rstse_10_ra72.dsk


# Copy data files (includes game data and generated dungeon map)
COPY build/data/ /opt/advent/data/

# Copy source files for building from source
COPY src/*.SUB src/*.B2S src/*.COM /opt/advent/src/

# Copy tape creation and room reconstruction scripts
COPY scripts/create_tape.py scripts/create_advent_tape.py /opt/advent/scripts/
COPY scripts/reconstruct_rooms.py scripts/analyze_rooms.py /opt/advent/scripts/

# Reconstruct room exits (connects all 1590 rooms) and rebuild tape
# The tape script expects generated_data/ directory - create symlink
RUN mkdir -p /opt/advent/tapes && \
    ln -s /opt/advent/data /opt/advent/generated_data && \
    python3 /opt/advent/scripts/reconstruct_rooms.py \
        --input /opt/advent/data/ADVENT.DTA \
        --map-json /opt/advent/data/dungeon_map.json && \
    python3 /opt/advent/scripts/create_advent_tape.py -o /opt/advent/tapes/advent_source.tap

# Copy build scripts
COPY scripts/migrate_data.py /opt/advent/scripts/

# Copy configuration
COPY simh/pdp11_ra72.ini /opt/advent/pdp11.ini
COPY docker/nginx.conf /etc/nginx/nginx.conf

# Copy startup scripts
COPY docker/entrypoint.sh /opt/advent/
COPY docker/build_advent.exp /opt/advent/
COPY docker/game_connect.exp /opt/advent/
COPY docker/game_session.sh /opt/advent/
COPY docker/start_game_session.exp /opt/advent/
COPY docker/start_game_session.sh /opt/advent/
COPY docker/attach_game.sh /opt/advent/
COPY docker/admin_connect.sh /opt/advent/
COPY docker/verify_ready.exp /opt/advent/
COPY docker/restart_service.sh /opt/advent/
COPY docker/kick_service.sh /opt/advent/
COPY docker/kick_console.sh /opt/advent/
COPY docker/tcp_connect.py /opt/advent/
COPY docker/screenrc /root/.screenrc

# Copy web interface
COPY docker/web/ /opt/advent/web/

# Copy documentation
COPY STATUS.md RESURRECTION.md PROVENANCE.md TECHNICAL.md CONTINUATION.md NEWADV.md /opt/advent/

# Set permissions
RUN chmod +x /opt/advent/*.sh /opt/advent/*.exp /opt/advent/*.py /opt/advent/scripts/*.py && \
    chmod 644 /opt/advent/*.md && \
    chmod 644 /opt/advent/web/*

# Expose ports
EXPOSE 8080 7681 7682 2322 2323

# Build ADVENT from source on each container start
# This ensures source code and data changes are always compiled fresh
ENV SKIP_SETUP=0

ENTRYPOINT ["/opt/advent/entrypoint.sh"]
