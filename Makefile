# Advent MUD - Build and Run
#
# Commands:
#   make build      - Generate disk images and data files
#   make docker     - Build Docker image
#   make run        - Start Docker container
#   make test       - Run tests
#   make stop       - Stop Docker container
#   make clean      - Clean build artifacts
#   make rebuild    - Full rebuild

.PHONY: build docker run test stop clean rebuild help

# Default target
help:
	@echo "Advent MUD - Build Commands"
	@echo ""
	@echo "  make build    - Generate disk images and data files"
	@echo "  make docker   - Build Docker image"
	@echo "  make run      - Start Docker container"
	@echo "  make test     - Run tests"
	@echo "  make stop     - Stop Docker container"
	@echo "  make logs     - Show container logs"
	@echo "  make shell    - Connect to RSTS/E terminal"
	@echo "  make clean    - Clean build artifacts"
	@echo "  make rebuild  - Full clean rebuild"
	@echo ""
	@echo "After 'make run', access via:"
	@echo "  Web game:   http://localhost:7681"
	@echo "  Web admin:  http://localhost:7682"
	@echo "  Telnet:     telnet localhost 2323"

# Build disk images and data files
build:
	@echo "=== Building disk images ==="
	python3 scripts/build_disk.py

# Build Docker image
docker: build
	@echo "=== Building Docker image ==="
	docker build -f docker/Dockerfile.new -t advent-mud .

# Run Docker container
run:
	@echo "=== Starting Advent MUD ==="
	docker compose -f docker-compose.new.yml up -d
	@echo ""
	@echo "Waiting for RSTS/E to boot..."
	@sleep 20
	@echo ""
	@echo "Advent MUD is running!"
	@echo "  Web game:   http://localhost:7681"
	@echo "  Web admin:  http://localhost:7682"
	@echo "  Telnet:     telnet localhost 2323"

# Run tests
test:
	@echo "=== Running tests ==="
	python3 scripts/test_setup.py

# Run tests with connection
test-full:
	@echo "=== Running full tests ==="
	python3 scripts/test_setup.py

# Stop Docker container
stop:
	@echo "=== Stopping Advent MUD ==="
	docker compose -f docker-compose.new.yml down

# Show logs
logs:
	docker compose -f docker-compose.new.yml logs -f

# Connect to terminal
shell:
	@echo "Connecting to RSTS/E terminal..."
	@echo "Login: [1,2] / Digital1977"
	@echo ""
	nc localhost 2323

# Clean build artifacts
clean:
	@echo "=== Cleaning build artifacts ==="
	rm -rf build/

# Full rebuild
rebuild: clean build docker
	@echo "=== Rebuild complete ==="
