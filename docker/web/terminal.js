/**
 * ADVENT MUD Terminal Controller
 * Manages connection status display, input blocking, and documentation viewer
 */

(function() {
    'use strict';

    // Configuration - timing for each step (in ms)
    // These are MAXIMUM times - ideally we'd detect actual progress
    // TODO: Implement server-side status endpoint for true event-driven progress
    const STEP_TIMING = {
        connect: 3000,      // Initial connection to SIMH
        boot: 4000,         // RSTS/E detection
        login: 10000,       // Login sequence (can be slow)
        game: 8000,         // Game startup
        ready: 500          // Final transition
    };

    // DOM Elements
    const terminalFrame = document.getElementById('terminal-frame');
    const inputBlocker = document.getElementById('input-blocker');
    const connectionOverlay = document.getElementById('connection-overlay');
    const onlineLed = document.getElementById('online-led');
    const waitMessage = document.getElementById('wait-message');
    const docModal = document.getElementById('doc-modal');
    const docTitle = document.getElementById('doc-title');
    const docBody = document.getElementById('doc-body');

    // Status step elements (now inside the overlay)
    const steps = {
        connect: document.getElementById('step-connect'),
        boot: document.getElementById('step-boot'),
        login: document.getElementById('step-login'),
        game: document.getElementById('step-game'),
        ready: document.getElementById('step-ready')
    };

    // Current state
    let isReady = false;
    let connectionSequenceId = 0;

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
     * Progress to the next step
     */
    function progressStep(stepName, sequenceId) {
        if (sequenceId !== connectionSequenceId) return;

        const stepOrder = ['connect', 'boot', 'login', 'game', 'ready'];
        const currentIndex = stepOrder.indexOf(stepName);

        for (let i = 0; i < stepOrder.length; i++) {
            if (i < currentIndex) {
                updateStep(stepOrder[i], 'complete');
            } else if (i === currentIndex) {
                updateStep(stepOrder[i], 'active');
            } else {
                updateStep(stepOrder[i], 'pending');
            }
        }

        // Update overlay title
        const overlayTitle = connectionOverlay?.querySelector('h2');
        if (overlayTitle) {
            const titles = {
                connect: 'Connecting...',
                boot: 'Booting RSTS/E...',
                login: 'Logging in...',
                game: 'Starting game...',
                ready: 'Ready!'
            };
            overlayTitle.textContent = titles[stepName] || 'Connecting...';
        }

        // Update LED state
        if (stepName === 'ready') {
            onlineLed?.classList.remove('on');
            onlineLed?.classList.add('connected');
        } else {
            onlineLed?.classList.add('on');
            onlineLed?.classList.remove('connected');
        }
    }

    /**
     * Reset to initial state for reconnection
     */
    function resetState() {
        isReady = false;
        inputBlocker?.classList.add('active');
        connectionOverlay?.classList.add('active');
        if (waitMessage) {
            waitMessage.classList.remove('hidden');
            waitMessage.textContent = 'Please wait while we connect you...';
            waitMessage.style.color = '';
        }
        onlineLed?.classList.remove('connected', 'on');

        Object.keys(steps).forEach(stepName => {
            updateStep(stepName, 'pending');
        });
    }

    /**
     * Enable user input (remove blocker and overlay)
     */
    function enableInput(sequenceId) {
        if (sequenceId !== connectionSequenceId) return;

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
     * Start the connection sequence
     */
    function startConnectionSequence() {
        connectionSequenceId++;
        const thisSequenceId = connectionSequenceId;

        resetState();

        // Load the terminal iframe (triggers new ttyd session with auto-login)
        if (terminalFrame) {
            terminalFrame.src = '/terminal/';
        }

        let delay = 0;

        setTimeout(() => progressStep('connect', thisSequenceId), delay);
        delay += STEP_TIMING.connect;

        setTimeout(() => progressStep('boot', thisSequenceId), delay);
        delay += STEP_TIMING.boot;

        setTimeout(() => progressStep('login', thisSequenceId), delay);
        delay += STEP_TIMING.login;

        setTimeout(() => progressStep('game', thisSequenceId), delay);
        delay += STEP_TIMING.game;

        setTimeout(() => {
            progressStep('ready', thisSequenceId);
            enableInput(thisSequenceId);
        }, delay);
    }

    /**
     * Handle click on blocker
     */
    function handleBlockerClick(e) {
        if (!isReady && waitMessage) {
            waitMessage.style.color = '#ff6666';
            waitMessage.textContent = 'Please wait - automatic login in progress...';
            setTimeout(() => {
                if (waitMessage) {
                    waitMessage.style.color = '';
                    waitMessage.textContent = 'Please wait while we connect you...';
                }
            }, 1500);
        }
    }

    /**
     * Initialize
     */
    function init() {
        setTimeout(startConnectionSequence, 500);
        inputBlocker?.addEventListener('click', handleBlockerClick);
        connectionOverlay?.addEventListener('click', handleBlockerClick);
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
        'CONTINUATION.md': 'Continuation Guide'
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
