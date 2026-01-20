/**
 * ADVENT MUD Terminal Controller
 * Event-driven status via polling /api/status
 */

(function() {
    'use strict';

    // Polling configuration
    const POLL_INTERVAL = 500;  // Poll every 500ms
    const BOOT_POLL_INTERVAL = 2000;  // Poll boot status every 2s
    const MAX_POLL_TIME = 120000;  // Fallback timeout after 120 seconds

    // DOM Elements
    const terminalFrame = document.getElementById('terminal-frame');
    const inputBlocker = document.getElementById('input-blocker');
    const connectionOverlay = document.getElementById('connection-overlay');
    const onlineLed = document.getElementById('online-led');
    const waitMessage = document.getElementById('wait-message');
    const docModal = document.getElementById('doc-modal');
    const docTitle = document.getElementById('doc-title');
    const docBody = document.getElementById('doc-body');

    // Status step elements
    const steps = {
        connect: document.getElementById('step-connect'),
        boot: document.getElementById('step-boot'),
        login: document.getElementById('step-login'),
        game: document.getElementById('step-game'),
        ready: document.getElementById('step-ready')
    };

    // State
    let isReady = false;
    let pollTimer = null;
    let bootPollTimer = null;
    let pollStartTime = null;
    let lastStatus = null;
    let systemBooted = false;

    /**
     * Update a step's visual state
     */
    function updateStep(stepName, state) {
        const step = steps[stepName];
        if (!step) return;

        step.classList.remove('active', 'complete');

        if (state === 'active') {
            step.classList.add('active');
            step.querySelector('.step-icon').innerHTML = '&#8226;';
        } else if (state === 'complete') {
            step.classList.add('complete');
            step.querySelector('.step-icon').innerHTML = '&#10003;';
        } else {
            step.querySelector('.step-icon').innerHTML = '&#9675;';
        }
    }

    /**
     * Map status step to UI steps and update display
     */
    function updateFromStatus(status) {
        if (!status || !status.step) return;

        const stepOrder = ['connect', 'boot', 'login', 'game', 'ready'];
        const currentIndex = stepOrder.indexOf(status.step);

        // Handle error state
        if (status.step === 'error') {
            if (waitMessage) {
                waitMessage.textContent = status.message || 'Connection failed';
                waitMessage.style.color = '#ff6666';
            }
            // Keep overlay visible but show error
            const overlayTitle = connectionOverlay?.querySelector('h2');
            if (overlayTitle) {
                overlayTitle.textContent = 'Connection Failed';
                overlayTitle.style.color = '#ff6666';
            }
            stopPolling();
            return;
        }

        // Handle busy state - another session is active
        if (status.step === 'busy') {
            const overlayTitle = connectionOverlay?.querySelector('h2');
            if (overlayTitle) {
                overlayTitle.textContent = 'Session In Use';
                overlayTitle.style.color = '#ffaa00';
            }
            if (waitMessage) {
                waitMessage.innerHTML = 'Another session is currently active.<br><br>' +
                    '<button id="takeoverBtn" style="background: #ff6666; color: white; border: none; padding: 10px 20px; cursor: pointer; font-size: 14px; border-radius: 4px;">Take Over Session</button>' +
                    '<br><small style="color: #888; margin-top: 10px; display: block;">This will disconnect the other user.</small>';
                waitMessage.style.color = '#ffaa00';

                // Add click handler for takeover button
                const takeoverBtn = document.getElementById('takeoverBtn');
                if (takeoverBtn && !takeoverBtn.hasListener) {
                    takeoverBtn.hasListener = true;
                    takeoverBtn.addEventListener('click', function() {
                        takeoverBtn.textContent = 'Taking over...';
                        takeoverBtn.disabled = true;

                        fetch('/api/kick')
                            .then(response => response.json())
                            .then(data => {
                                // game_session.sh handles reconnection automatically
                                // Just reset UI state and keep polling for status
                                setTimeout(() => {
                                    // Reset overlay to "connecting" state
                                    const overlayTitle = connectionOverlay?.querySelector('h2');
                                    if (overlayTitle) {
                                        overlayTitle.textContent = 'Reconnecting...';
                                        overlayTitle.style.color = '';
                                    }
                                    if (waitMessage) {
                                        waitMessage.textContent = 'Taking over session...';
                                        waitMessage.style.color = '';
                                    }
                                    // Reset step indicators
                                    Object.keys(steps).forEach(stepName => {
                                        updateStep(stepName, 'pending');
                                    });
                                    updateStep('connect', 'active');
                                    // Keep polling - game_session.sh will reconnect
                                    lastStatus = null;
                                }, 500);
                            })
                            .catch(err => {
                                takeoverBtn.textContent = 'Failed - Try Again';
                                takeoverBtn.disabled = false;
                            });
                    });
                }
            }
            // Keep polling to detect when connection is available
            return;
        }

        // Update steps
        for (let i = 0; i < stepOrder.length; i++) {
            if (i < currentIndex) {
                updateStep(stepOrder[i], 'complete');
            } else if (i === currentIndex) {
                updateStep(stepOrder[i], 'active');
            } else {
                updateStep(stepOrder[i], 'pending');
            }
        }

        // Update overlay title and message
        const overlayTitle = connectionOverlay?.querySelector('h2');
        if (overlayTitle) {
            const titles = {
                connect: 'Connecting...',
                boot: 'Booting RSTS/E...',
                login: 'Logging in...',
                game: 'Starting game...',
                ready: 'Ready!'
            };
            overlayTitle.textContent = titles[status.step] || 'Connecting...';
            overlayTitle.style.color = '';
        }

        if (waitMessage) {
            waitMessage.textContent = status.message || 'Please wait...';
            waitMessage.style.color = '';
        }

        // Update LED
        if (status.step === 'ready') {
            onlineLed?.classList.remove('on');
            onlineLed?.classList.add('connected');
            enableInput();
        } else {
            onlineLed?.classList.add('on');
            onlineLed?.classList.remove('connected');
        }
    }

    /**
     * Poll the status endpoint
     */
    function pollStatus() {
        // Check if we've been polling too long
        if (pollStartTime && (Date.now() - pollStartTime > MAX_POLL_TIME)) {
            console.log('Polling timeout - enabling input anyway');
            enableInput();
            return;
        }

        fetch('/api/status')
            .then(response => {
                if (!response.ok) {
                    // Status file doesn't exist yet - keep polling
                    return null;
                }
                return response.json();
            })
            .then(status => {
                if (status) {
                    // Only update if status changed
                    if (!lastStatus || lastStatus.step !== status.step || lastStatus.message !== status.message) {
                        lastStatus = status;
                        updateFromStatus(status);
                    }

                    // Stop polling when ready
                    if (status.step === 'ready') {
                        stopPolling();
                    }
                }
            })
            .catch(err => {
                // Ignore errors - file might not exist yet
                console.log('Status poll:', err.message);
            });
    }

    /**
     * Start polling for status
     */
    function startPolling() {
        stopPolling();
        pollStartTime = Date.now();
        lastStatus = null;
        pollStatus();  // Initial poll
        pollTimer = setInterval(pollStatus, POLL_INTERVAL);
    }

    /**
     * Stop polling
     */
    function stopPolling() {
        if (pollTimer) {
            clearInterval(pollTimer);
            pollTimer = null;
        }
    }

    /**
     * Reset UI to initial state
     */
    function resetState() {
        isReady = false;
        lastStatus = null;
        inputBlocker?.classList.add('active');
        connectionOverlay?.classList.add('active');

        if (waitMessage) {
            waitMessage.classList.remove('hidden');
            waitMessage.textContent = 'Please wait while we connect you...';
            waitMessage.style.color = '';
        }

        onlineLed?.classList.remove('connected', 'on');

        const overlayTitle = connectionOverlay?.querySelector('h2');
        if (overlayTitle) {
            overlayTitle.textContent = 'Connecting...';
            overlayTitle.style.color = '';
        }

        Object.keys(steps).forEach(stepName => {
            updateStep(stepName, 'pending');
        });
    }

    /**
     * Ensure terminal fills the CRT screen
     * Font size is controlled via ttyd options (fontSize=20)
     * This just ensures the iframe fills the container
     */
    function scaleTerminal() {
        if (!terminalFrame) return;

        // Reset any previous transforms and let CSS handle sizing
        terminalFrame.style.width = '100%';
        terminalFrame.style.height = '100%';
        terminalFrame.style.transform = '';
        terminalFrame.style.left = '0';
        terminalFrame.style.top = '0';
    }

    /**
     * Enable user input
     */
    function enableInput() {
        stopPolling();
        inputBlocker?.classList.remove('active');
        connectionOverlay?.classList.remove('active');
        waitMessage?.classList.add('hidden');
        isReady = true;

        // Scale terminal to fill screen
        scaleTerminal();

        // Also scale on window resize
        window.addEventListener('resize', scaleTerminal);

        try {
            terminalFrame?.focus();
            terminalFrame?.contentWindow?.focus();
        } catch (e) {}
    }

    /**
     * Poll boot status before allowing connection
     */
    function pollBootStatus() {
        fetch('/api/boot-status')
            .then(response => {
                if (!response.ok) return null;
                return response.json();
            })
            .then(status => {
                if (!status) return;

                const overlayTitle = connectionOverlay?.querySelector('h2');

                if (status.status === 'building') {
                    // Build in progress - show detailed build message
                    if (overlayTitle) {
                        overlayTitle.textContent = 'Building ADVENT...';
                        overlayTitle.style.color = '#ffaa00';
                    }
                    if (waitMessage) {
                        let msg = status.message || 'Building from source...';
                        if (status.detail) {
                            msg += '<br><br><small style="color: #888;">' + status.detail + '</small>';
                        }
                        waitMessage.innerHTML = msg;
                        waitMessage.style.color = '#ffaa00';
                    }
                    // Show build as active
                    updateStep('connect', 'complete');
                    updateStep('boot', 'active');
                    updateStep('login', 'pending');
                    updateStep('game', 'pending');
                    updateStep('ready', 'pending');
                    // Update boot step text to show build status
                    const bootStep = steps.boot?.querySelector('.step-text');
                    if (bootStep) {
                        bootStep.textContent = 'Building from source...';
                    }
                } else if (status.status === 'booting') {
                    // System still booting - show holding message
                    if (overlayTitle) {
                        overlayTitle.textContent = 'System Starting...';
                        overlayTitle.style.color = '#ffaa00';
                    }
                    if (waitMessage) {
                        waitMessage.textContent = status.message || 'Please wait...';
                        waitMessage.style.color = '#ffaa00';
                    }
                    // Reset boot step text
                    const bootStep = steps.boot?.querySelector('.step-text');
                    if (bootStep) {
                        bootStep.textContent = 'Waiting for RSTS/E...';
                    }
                    // Show only boot step as active
                    updateStep('connect', 'pending');
                    updateStep('boot', 'active');
                    updateStep('login', 'pending');
                    updateStep('game', 'pending');
                    updateStep('ready', 'pending');
                } else if (status.status === 'ready') {
                    // System ready - start connection
                    stopBootPolling();
                    systemBooted = true;
                    startConnectionSequence();
                } else if (status.status === 'error') {
                    // Boot error
                    if (overlayTitle) {
                        overlayTitle.textContent = 'System Error';
                        overlayTitle.style.color = '#ff6666';
                    }
                    if (waitMessage) {
                        waitMessage.textContent = status.message || 'Boot failed';
                        waitMessage.style.color = '#ff6666';
                    }
                    stopBootPolling();
                }
            })
            .catch(err => {
                console.log('Boot status poll:', err.message);
            });
    }

    /**
     * Start polling boot status
     */
    function startBootPolling() {
        stopBootPolling();
        pollBootStatus();
        bootPollTimer = setInterval(pollBootStatus, BOOT_POLL_INTERVAL);
    }

    /**
     * Stop boot polling
     */
    function stopBootPolling() {
        if (bootPollTimer) {
            clearInterval(bootPollTimer);
            bootPollTimer = null;
        }
    }

    /**
     * Start connection sequence (only after boot is ready)
     */
    function startConnectionSequence() {
        resetState();

        // Load the terminal iframe (triggers new ttyd session with auto-login)
        if (terminalFrame) {
            terminalFrame.src = '/terminal/';
        }

        // Start polling for status updates
        startPolling();
    }

    /**
     * Handle click on overlay
     */
    function handleOverlayClick(e) {
        if (!systemBooted && waitMessage) {
            waitMessage.style.color = '#ffaa00';
            waitMessage.textContent = 'RSTS/E is still booting, please wait...';
            setTimeout(() => {
                if (waitMessage && !systemBooted) {
                    waitMessage.style.color = '#ffaa00';
                }
            }, 1500);
        } else if (!isReady && waitMessage) {
            waitMessage.style.color = '#ffaa00';
            waitMessage.textContent = 'Automatic login in progress...';
            setTimeout(() => {
                if (waitMessage && !isReady) {
                    waitMessage.style.color = '';
                    waitMessage.textContent = lastStatus?.message || 'Please wait...';
                }
            }, 1500);
        }
    }

    /**
     * Initialize - first check boot status
     */
    function init() {
        // Show initial state
        const overlayTitle = connectionOverlay?.querySelector('h2');
        if (overlayTitle) {
            overlayTitle.textContent = 'System Starting...';
            overlayTitle.style.color = '#ffaa00';
        }
        if (waitMessage) {
            waitMessage.textContent = 'Checking system status...';
            waitMessage.style.color = '#ffaa00';
        }

        // Start checking boot status
        setTimeout(startBootPolling, 300);
        inputBlocker?.addEventListener('click', handleOverlayClick);
        connectionOverlay?.addEventListener('click', handleOverlayClick);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // ============================================
    // DOCUMENTATION MODAL
    // ============================================

    const DOC_TITLES = {
        'RESURRECTION.md': 'The Resurrection Story',
        'PROVENANCE.md': 'File Provenance',
        'TECHNICAL.md': 'Technical Details',
        'CONTINUATION.md': 'Continuation Guide',
        'NEWADV.md': 'Guidelines for Dungeon Writers (1987)',
        'STATUS.md': 'Feature Implementation Status'
    };

    window.showDoc = function(filename) {
        if (!docModal || !docTitle || !docBody) return false;

        docTitle.textContent = DOC_TITLES[filename] || filename;
        docBody.innerHTML = '<p style="text-align:center; color: #559955;">Loading...</p>';
        docModal.classList.remove('hidden');

        fetch('/raw/' + filename)
            .then(response => {
                if (!response.ok) throw new Error('Document not found');
                return response.text();
            })
            .then(markdown => {
                if (typeof marked !== 'undefined') {
                    docBody.innerHTML = marked.parse(markdown);
                } else {
                    docBody.innerHTML = '<pre style="white-space: pre-wrap;">' +
                        markdown.replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</pre>';
                }
            })
            .catch(error => {
                docBody.innerHTML = '<p style="color: #ff6666;">Error: ' + error.message + '</p>';
            });

        return false;
    };

    window.closeDoc = function() {
        docModal?.classList.add('hidden');
    };

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && docModal && !docModal.classList.contains('hidden')) {
            closeDoc();
        }
    });

    docModal?.addEventListener('click', function(e) {
        if (e.target === docModal) closeDoc();
    });

    // ============================================
    // SESSION RESTART
    // ============================================

    // Reboot modal elements
    const rebootModal = document.getElementById('reboot-modal');

    window.restartSession = function() {
        // Show the reboot confirmation modal
        rebootModal?.classList.remove('hidden');
    };

    window.closeRebootModal = function() {
        rebootModal?.classList.add('hidden');
    };

    window.confirmReboot = function() {
        // Close the modal
        rebootModal?.classList.add('hidden');

        // Show restarting message
        const overlayTitle = connectionOverlay?.querySelector('h2');
        if (overlayTitle) {
            overlayTitle.textContent = 'Rebooting PDP-11...';
            overlayTitle.style.color = '#ffaa00';
        }
        if (waitMessage) {
            waitMessage.textContent = 'Killing SIMH and rebooting RSTS/E...';
            waitMessage.style.color = '#ffaa00';
        }

        // Show the overlay
        connectionOverlay?.classList.add('active');
        inputBlocker?.classList.add('active');

        // Reset state
        isReady = false;
        systemBooted = false;
        lastStatus = null;

        // Reset step indicators
        Object.keys(steps).forEach(stepName => {
            updateStep(stepName, 'pending');
        });

        // Clear the terminal iframe
        if (terminalFrame) {
            terminalFrame.src = 'about:blank';
        }

        // Call the restart API to kill SIMH
        fetch('/api/restart')
            .then(response => {
                console.log('Restart API called, response:', response.status);
            })
            .catch(err => {
                console.log('Restart API error (expected if connection drops):', err);
            });

        // Wait for SIMH to restart and RSTS/E to boot, then start polling
        setTimeout(function() {
            startBootPolling();
        }, 3000);
    };

    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && rebootModal && !rebootModal.classList.contains('hidden')) {
            closeRebootModal();
        }
    });

    // Close modal when clicking outside
    rebootModal?.addEventListener('click', function(e) {
        if (e.target === rebootModal) closeRebootModal();
    });

})();
