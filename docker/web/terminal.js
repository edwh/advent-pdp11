/**
 * ADVENT MUD Terminal Controller
 * Event-driven status via polling /api/status
 */

(function() {
    'use strict';

    // Polling configuration
    const POLL_INTERVAL = 500;  // Poll every 500ms
    const MAX_POLL_TIME = 60000;  // Fallback timeout after 60 seconds

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
    let pollStartTime = null;
    let lastStatus = null;

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
     * Enable user input
     */
    function enableInput() {
        stopPolling();
        inputBlocker?.classList.remove('active');
        connectionOverlay?.classList.remove('active');
        waitMessage?.classList.add('hidden');
        isReady = true;

        try {
            terminalFrame?.focus();
            terminalFrame?.contentWindow?.focus();
        } catch (e) {}
    }

    /**
     * Start connection sequence
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
        if (!isReady && waitMessage) {
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
     * Initialize
     */
    function init() {
        setTimeout(startConnectionSequence, 300);
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

})();
