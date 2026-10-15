/**
 * Audio Module (web/js/engine/audio.js)
 * Implements a Web Audio API retro synthesizer for authentic prehistoric sound effects
 * and ambient tribal chip synth melody.
 */

export class AudioManager {
    constructor() {
        this.ctx = null;
        this.enabled = true;
        this.volume = 0.5;
        this.bgmOscillator = null;
        this.bgmGain = null;
        this.isPlayingBgm = false;
        this.initialized = false;
    }

    /**
     * Initializes AudioContext on first user interaction (click/touch/key)
     */
    initContext() {
        if (this.initialized) return;

        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) {
            console.warn('[Audio] Web Audio API not supported in this browser.');
            return;
        }

        this.ctx = new AudioCtx();
        if (this.ctx.state === 'suspended') {
            const unlock = () => {
                if (this.ctx && this.ctx.state === 'suspended') {
                    this.ctx.resume();
                }
                window.removeEventListener('click', unlock);
                window.removeEventListener('keydown', unlock);
                window.removeEventListener('touchstart', unlock);
            };
            window.addEventListener('click', unlock);
            window.addEventListener('keydown', unlock);
            window.addEventListener('touchstart', unlock);
        }

        this.initialized = true;
    }

    ensureContext() {
        if (!this.initialized) {
            this.initContext();
        }
        if (this.ctx && this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    toggleSound() {
        this.enabled = !this.enabled;
        if (!this.enabled && this.isPlayingBgm) {
            this.stopBGM();
        } else if (this.enabled && !this.isPlayingBgm) {
            this.startBGM();
        }
        return this.enabled;
    }

    /**
     * Synthesizes retro UI Click / selection sound
     */
    playClick() {
        if (!this.enabled) return;
        this.ensureContext();
        if (!this.ctx) return;

        try {
            const now = this.ctx.currentTime;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.type = 'triangle';
            osc.frequency.setValueAtTime(520, now);
            osc.frequency.exponentialRampToValueAtTime(320, now + 0.05);

            gain.gain.setValueAtTime(this.volume * 0.4, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now);
            osc.stop(now + 0.06);
        } catch (e) {
            // Ignore audio unlock issues
        }
    }

    /**
     * Synthesizes building placement / hammer thump sound
     */
    playBuild() {
        if (!this.enabled) return;
        this.ensureContext();
        if (!this.ctx) return;

        try {
            const now = this.ctx.currentTime;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.type = 'square';
            osc.frequency.setValueAtTime(220, now);
            osc.frequency.setValueAtTime(330, now + 0.04);
            osc.frequency.setValueAtTime(440, now + 0.08);

            gain.gain.setValueAtTime(this.volume * 0.5, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now);
            osc.stop(now + 0.22);
        } catch (e) {}
    }

    /**
     * Synthesizes wood chop / stone mine sound
     */
    playGather() {
        if (!this.enabled) return;
        this.ensureContext();
        if (!this.ctx) return;

        try {
            const now = this.ctx.currentTime;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(140, now);
            osc.frequency.exponentialRampToValueAtTime(70, now + 0.08);

            gain.gain.setValueAtTime(this.volume * 0.35, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.09);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now);
            osc.stop(now + 0.1);
        } catch (e) {}
    }

    /**
     * Fanfare sound for quest objective / chapter complete
     */
    playFanfare() {
        if (!this.enabled) return;
        this.ensureContext();
        if (!this.ctx) return;

        try {
            const notes = [261.63, 329.63, 392.00, 523.25]; // C4, E4, G4, C5
            notes.forEach((freq, i) => {
                const now = this.ctx.currentTime + i * 0.1;
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();

                osc.type = 'triangle';
                osc.frequency.setValueAtTime(freq, now);

                gain.gain.setValueAtTime(this.volume * 0.45, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);

                osc.connect(gain);
                gain.connect(this.ctx.destination);

                osc.start(now);
                osc.stop(now + 0.26);
            });
        } catch (e) {}
    }

    /**
     * Error buzz sound (e.g. invalid build location or insufficient resources)
     */
    playError() {
        if (!this.enabled) return;
        this.ensureContext();
        if (!this.ctx) return;

        try {
            const now = this.ctx.currentTime;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(120, now);
            osc.frequency.setValueAtTime(90, now + 0.08);

            gain.gain.setValueAtTime(this.volume * 0.5, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now);
            osc.stop(now + 0.2);
        } catch (e) {}
    }

    /**
     * Ambient retro tribal background theme (soft bass drum & pentatonic whistle)
     */
    startBGM() {
        if (!this.enabled || this.isPlayingBgm) return;
        this.ensureContext();
        if (!this.ctx) return;

        this.isPlayingBgm = true;

        // Sequence periodic gentle notes
        const melody = [220, 247, 261, 330, 392, 330, 261, 220];
        let step = 0;

        this.bgmTimer = setInterval(() => {
            if (!this.enabled || !this.isPlayingBgm || !this.ctx) return;
            try {
                const now = this.ctx.currentTime;
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();

                osc.type = 'sine';
                osc.frequency.setValueAtTime(melody[step % melody.length], now);

                gain.gain.setValueAtTime(this.volume * 0.15, now);
                gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.45);

                osc.connect(gain);
                gain.connect(this.ctx.destination);

                osc.start(now);
                osc.stop(now + 0.5);

                step++;
            } catch (e) {}
        }, 600);
    }

    stopBGM() {
        this.isPlayingBgm = false;
        if (this.bgmTimer) {
            clearInterval(this.bgmTimer);
            this.bgmTimer = null;
        }
    }
}
