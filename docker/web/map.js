/**
 * ADVENT MUD Dungeon Map Explorer
 * Interactive map showing all rooms and their connections
 */

(function() {
    'use strict';

    const mapModal = document.getElementById('map-modal');
    const roomSelect = document.getElementById('room-select');
    const roomNumberEl = document.getElementById('room-number');
    const roomDescEl = document.getElementById('room-description');
    const roomExitsEl = document.getElementById('room-exits');
    const mapStatsEl = document.getElementById('map-stats');

    let mapData = null;
    let currentRoom = null;

    const DIR_NAMES = {
        'N': 'North',
        'E': 'East',
        'S': 'South',
        'W': 'West'
    };

    /**
     * Load map data from server
     */
    async function loadMapData() {
        try {
            const response = await fetch('/data/dungeon_map.json');
            if (!response.ok) throw new Error('Map data not found');
            mapData = await response.json();
            populateRoomSelect();
            updateStats();
            return true;
        } catch (err) {
            console.error('Failed to load map data:', err);
            roomSelect.innerHTML = '<option value="">Error loading map</option>';
            return false;
        }
    }

    /**
     * Populate the room select dropdown
     */
    function populateRoomSelect() {
        if (!mapData) return;

        const rooms = Object.values(mapData.rooms).sort((a, b) => a.number - b.number);
        roomSelect.innerHTML = '';

        for (const room of rooms) {
            const opt = document.createElement('option');
            opt.value = room.number;

            // Create a short label from the description
            let label = `Room ${room.number}`;
            if (room.description) {
                const shortDesc = room.description.substring(0, 40);
                label += ` - ${shortDesc}${room.description.length > 40 ? '...' : ''}`;
            }

            // Mark starting room
            if (room.number === mapData.start_room) {
                label = `* ${label} (START)`;
            }

            opt.textContent = label;
            roomSelect.appendChild(opt);
        }

        roomSelect.addEventListener('change', () => {
            const num = parseInt(roomSelect.value);
            if (num) displayRoom(num);
        });
    }

    /**
     * Display a room's information
     */
    function displayRoom(roomNum) {
        if (!mapData || !mapData.rooms[roomNum]) return;

        currentRoom = roomNum;
        const room = mapData.rooms[roomNum];

        // Update room number
        let numText = `Room ${roomNum}`;
        if (roomNum === mapData.start_room) {
            numText += ' (Starting Room)';
        }
        roomNumberEl.textContent = numText;

        // Update description
        roomDescEl.textContent = room.description || '(No description)';

        // Update exits
        roomExitsEl.innerHTML = '';

        const exitDirs = ['N', 'E', 'S', 'W'];
        for (const dir of exitDirs) {
            const exitDiv = document.createElement('div');
            exitDiv.className = 'exit-item';

            const dest = room.all_exits[dir];
            const isReconstructed = room.reconstructed_exits && room.reconstructed_exits[dir];
            const isOriginal = room.original_exits && room.original_exits[dir];

            if (dest && dest > 0) {
                const destRoom = mapData.rooms[dest];
                const destDesc = destRoom ? destRoom.description.substring(0, 30) : 'Unknown';

                exitDiv.innerHTML = `
                    <span class="exit-dir">${DIR_NAMES[dir]}:</span>
                    <a href="#" class="exit-link ${isReconstructed ? 'reconstructed' : 'original'}"
                       onclick="goToRoom(${dest}); return false;">
                        Room ${dest}
                    </a>
                    <span class="exit-dest-desc">${destDesc}${destRoom && destRoom.description.length > 30 ? '...' : ''}</span>
                    ${isReconstructed ? '<span class="exit-reconstructed">(reconstructed)</span>' : ''}
                `;
            } else if (dest === 0) {
                exitDiv.innerHTML = `
                    <span class="exit-dir">${DIR_NAMES[dir]}:</span>
                    <span class="exit-dungeon">Exit Dungeon</span>
                `;
            } else {
                exitDiv.innerHTML = `
                    <span class="exit-dir">${DIR_NAMES[dir]}:</span>
                    <span class="exit-none">No exit</span>
                `;
            }

            roomExitsEl.appendChild(exitDiv);
        }

        // Update select
        roomSelect.value = roomNum;
    }

    /**
     * Update statistics display
     */
    function updateStats() {
        if (!mapData || !mapStatsEl) return;

        const totalRooms = Object.keys(mapData.rooms).length;
        const reachableRooms = Object.values(mapData.rooms).filter(r => r.reachable).length;
        const totalChanges = mapData.metadata.total_changes || 0;

        mapStatsEl.innerHTML = `
            <strong>Dungeon Statistics:</strong>
            ${totalRooms} rooms total |
            ${reachableRooms} reachable from start |
            ${totalChanges} reconstructed connections
        `;
    }

    /**
     * Navigate to a room
     */
    window.goToRoom = function(roomNum) {
        displayRoom(roomNum);
    };

    /**
     * Show the map modal
     */
    window.showMap = async function() {
        if (!mapData) {
            const loaded = await loadMapData();
            if (!loaded) return;
        }

        mapModal.classList.remove('hidden');
        displayRoom(mapData.start_room);
        return false;
    };

    /**
     * Close the map modal
     */
    window.closeMap = function() {
        mapModal.classList.add('hidden');
    };

    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && mapModal && !mapModal.classList.contains('hidden')) {
            closeMap();
        }
    });

    // Close when clicking outside
    mapModal?.addEventListener('click', function(e) {
        if (e.target === mapModal) closeMap();
    });

})();
