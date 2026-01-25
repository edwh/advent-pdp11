/**
 * ADVENT AI Mode - Claude plays the game and commentates
 *
 * Claude sees the screen, decides what to do, executes commands,
 * and provides snarky commentary via TTS.
 */

(function() {
    'use strict';

    let aiRunning = false;
    let ttsVoice = null;
    let ambientAudio = null;

    /**
     * Start ambient audio using a visible player first, then hide it
     */
    function startAmbient() {
        if (ambientAudio) return;

        // Check if audio element already exists in DOM
        ambientAudio = document.getElementById('ambient-player');

        if (!ambientAudio) {
            // Create visible audio element with controls for debugging
            ambientAudio = document.createElement('audio');
            ambientAudio.id = 'ambient-player';
            ambientAudio.controls = true;  // Visible controls
            ambientAudio.loop = true;
            ambientAudio.volume = 1.0;  // Full volume - file is quiet
            ambientAudio.style.cssText = 'position:fixed; bottom:10px; left:10px; z-index:9999; opacity:0.7;';

            const source = document.createElement('source');
            source.src = 'audio/dungeon_ambient.mp3';
            source.type = 'audio/mpeg';
            ambientAudio.appendChild(source);

            document.body.appendChild(ambientAudio);
            console.log('Ambient audio element created');
        }

        // Try to play
        ambientAudio.play().then(() => {
            console.log('Ambient audio playing!');
            // Hide controls after successful play
            setTimeout(() => {
                ambientAudio.controls = false;
                ambientAudio.style.opacity = '0';
            }, 3000);
        }).catch(e => {
            console.error('Ambient play failed:', e.message);
            // Leave controls visible so user can manually start
        });
    }

    /**
     * Retry ambient audio - call this after TTS starts successfully
     */
    function retryAmbient() {
        if (ambientAudio && ambientAudio.paused) {
            console.log('Retrying ambient audio...');
            ambientAudio.play().then(() => {
                console.log('Ambient audio now playing after retry');
                ambientAudio.controls = false;
                ambientAudio.style.opacity = '0';
            }).catch(e => {
                console.error('Ambient retry failed:', e.message);
            });
        }
    }

    /**
     * Stop ambient audio
     */
    function stopAmbient() {
        if (ambientAudio) {
            ambientAudio.pause();
            ambientAudio.remove();
            ambientAudio = null;
        }
    }

    /**
     * Initialize TTS voice (prefer British)
     */
    function initTTS() {
        if (!('speechSynthesis' in window)) return;

        function findBritishVoice() {
            const voices = speechSynthesis.getVoices();
            ttsVoice = voices.find(v => v.lang === 'en-GB') ||
                       voices.find(v => v.lang.startsWith('en-GB')) ||
                       voices.find(v => v.lang === 'en-US') ||
                       voices.find(v => v.lang.startsWith('en')) ||
                       voices[0];
            if (ttsVoice) console.log('TTS voice:', ttsVoice.name, ttsVoice.lang);
        }

        if (speechSynthesis.getVoices().length > 0) {
            findBritishVoice();
        }
        speechSynthesis.addEventListener('voiceschanged', findBritishVoice);
    }

    /**
     * Speak text via TTS - returns promise that resolves when done
     */
    function speak(text) {
        return new Promise((resolve) => {
            if (!('speechSynthesis' in window) || !text) {
                resolve();
                return;
            }

            const utterance = new SpeechSynthesisUtterance(text);
            if (ttsVoice) utterance.voice = ttsVoice;
            utterance.rate = 0.95;
            utterance.pitch = 1.0;
            utterance.volume = 0.9;

            utterance.onstart = () => {
                // TTS started - good time to retry ambient audio
                retryAmbient();
            };
            utterance.onend = () => {
                console.log('TTS finished');
                resolve();
            };
            utterance.onerror = () => {
                console.log('TTS error');
                resolve();
            };

            speechSynthesis.speak(utterance);
        });
    }

    /**
     * Show commentary overlay
     */
    function showCommentary(text) {
        let el = document.getElementById('ai-commentary');
        if (!el) {
            const wrapper = document.querySelector('.terminal-wrapper');
            if (!wrapper) return;
            el = document.createElement('div');
            el.id = 'ai-commentary';
            el.className = 'ai-commentary';
            wrapper.appendChild(el);
        }

        if (text) {
            el.style.opacity = '0';
            el.innerHTML = `<span class="ai-icon">🤖</span> <span class="ai-text">${text}</span>`;
            setTimeout(() => { el.style.opacity = '1'; }, 50);
        }
    }

    /**
     * Get next action from Claude, execute, speak, then loop
     */
    async function runNextAction() {
        if (!aiRunning) return;

        try {
            const response = await fetch('/api/next');
            const data = await response.json();

            if (data.error) {
                console.warn('AI error:', data.error);
                if (data.error === 'no_api_key') {
                    showCommentary('API key missing. Create .env file with ANTHROPIC_API_KEY - see README.');
                    stopAI();
                }
                // Retry after delay
                if (aiRunning) setTimeout(runNextAction, 3000);
                return;
            }

            if (data.command) {
                console.log('AI command:', data.command);
            }

            if (data.commentary) {
                console.log('AI commentary:', data.commentary);
                showCommentary(data.commentary);
                // Wait for TTS to complete before next action
                await speak(data.commentary);
            }

            // Quick pause after speech, then get next action
            if (aiRunning) {
                setTimeout(runNextAction, 500);
            }

        } catch (e) {
            console.error('AI error:', e);
            // Retry after delay
            if (aiRunning) setTimeout(runNextAction, 3000);
        }
    }

    /**
     * Start AI mode
     */
    async function startAI() {
        if (aiRunning) return;

        console.log('Starting AI mode...');

        // Check API status first
        try {
            const status = await fetch('/api/ai-status');
            const data = await status.json();

            if (!data.has_api_key) {
                alert('Claude AI mode requires an Anthropic API key.\n\n' +
                    'To enable this feature:\n' +
                    '1. Get an API key at console.anthropic.com\n' +
                    '2. Create a .env file in the project root with:\n' +
                    '   ANTHROPIC_API_KEY=sk-ant-api03-...\n' +
                    '3. Restart the container with: docker-compose up -d\n\n' +
                    'See README.md for details.');
                return;
            }
            if (!data.has_anthropic) {
                alert('Anthropic package not installed in container.');
                return;
            }
        } catch (e) {
            alert('Cannot connect to AI service. Is the container running?');
            return;
        }

        aiRunning = true;
        initTTS();
        startAmbient();

        // Hide status panel for cleaner view
        const panel = document.querySelector('.status-panel');
        if (panel) {
            panel.dataset.wasVisible = panel.style.display || '';
            panel.style.display = 'none';
        }

        // Update button
        const btn = document.getElementById('ai-btn');
        if (btn) {
            btn.textContent = 'Stop AI';
            btn.style.background = '#660000';
        }

        showCommentary('Claude is now playing ADVENT. Sit back and enjoy the show.');
        await speak('Claude is now playing ADVENT. Sit back and enjoy the show.');

        // Start the action loop (waits for TTS between actions)
        setTimeout(runNextAction, 1500);
    }

    /**
     * Stop AI mode
     */
    function stopAI() {
        aiRunning = false;

        if ('speechSynthesis' in window) {
            speechSynthesis.cancel();
        }

        stopAmbient();

        // Restore status panel
        const panel = document.querySelector('.status-panel');
        if (panel && panel.dataset.wasVisible !== undefined) {
            panel.style.display = panel.dataset.wasVisible;
        }

        // Update button
        const btn = document.getElementById('ai-btn');
        if (btn) {
            btn.textContent = 'Claude Plays';
            btn.style.background = '#006600';
        }

        showCommentary('AI mode stopped. You have control.');
    }

    /**
     * Toggle AI mode
     */
    function toggleAI() {
        if (aiRunning) {
            stopAI();
        } else {
            startAI();
        }
    }

    /**
     * Add AI button to controls
     */
    function addAIButton() {
        const controlsBox = document.querySelector('.info-box.controls');
        if (!controlsBox) return;

        const btn = document.createElement('button');
        btn.id = 'ai-btn';
        btn.className = 'restart-btn';
        btn.textContent = 'Claude Plays';
        btn.style.marginTop = '10px';
        btn.style.background = '#006600';
        btn.onclick = toggleAI;

        const helpText = document.createElement('p');
        helpText.className = 'help-text';
        helpText.textContent = 'Let Claude play and commentate';

        controlsBox.appendChild(btn);
        controlsBox.appendChild(helpText);
    }

    /**
     * Add styles
     */
    function addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .ai-commentary {
                position: absolute;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(0, 20, 0, 0.95);
                border: 2px solid #33ff33;
                border-radius: 10px;
                padding: 15px 25px;
                font-family: 'VT323', monospace;
                font-size: 20px;
                color: #33ff33;
                max-width: 750px;
                text-align: center;
                box-shadow: 0 0 20px rgba(51, 255, 51, 0.3);
                transition: opacity 0.3s ease;
                z-index: 1000;
            }
            .ai-commentary .ai-icon { margin-right: 10px; }
            .ai-commentary .ai-text { line-height: 1.4; }
            .terminal-wrapper { position: relative; }
        `;
        document.head.appendChild(style);
    }

    /**
     * Initialize
     */
    function init() {
        addStyles();
        addAIButton();

        // Initialize TTS on first click
        document.addEventListener('click', initTTS, { once: true });

        // Export for console access
        window.startAI = startAI;
        window.stopAI = stopAI;
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
