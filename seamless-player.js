/* Ruheklang v1.1 – sample-genauer Audioloop mit weichem Übergang.
   Keine Bibliotheken, keine Telemetrie und keine Netzwerkdienste außer den eigenen Audiodateien. */
(() => {
  'use strict';
  class SeamlessSound {
    constructor() {
      this.context = null;
      this.gain = null;
      this.source = null;
      this.buffer = null;
      this.bufferId = null;
      this.offset = 0;
      this.startedAt = 0;
      this.playing = false;
      this.generation = 0;
      this.volume = 1;
      this.timerLeft = 0;
    }
    static get supported() {
      return !!(window.AudioContext || window.webkitAudioContext);
    }
    _ensureContext() {
      if (this.context) return;
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (!AudioContextClass) throw new Error('Web Audio nicht verfügbar');
      this.context = new AudioContextClass();
      this.gain = this.context.createGain();
      this.gain.connect(this.context.destination);
    }
    _makeSeamless(decoded) {
      const channels = Array.from({length: decoded.numberOfChannels}, (_, c) => decoded.getChannelData(c));
      const edgeLimit = Math.floor(decoded.sampleRate * 0.18);
      const quiet = i => channels.every(ch => Math.abs(ch[i]) < 0.00012);
      let first = 0, last = decoded.length;
      while (first < edgeLimit && quiet(first)) first++;
      while (last > decoded.length - edgeLimit && last > first + 2 && quiet(last - 1)) last--;
      const samples = last - first;
      const overlap = Math.min(Math.floor(decoded.sampleRate * 1.0), Math.floor(samples / 8));
      if (overlap < 128 || samples < 1000) return decoded;
      const length = samples - overlap;
      const loop = this.context.createBuffer(decoded.numberOfChannels, length, decoded.sampleRate);
      for (let c = 0; c < decoded.numberOfChannels; c++) {
        const input = channels[c];
        const output = loop.getChannelData(c);
        output.set(input.subarray(first, first + length));
        // The tail is overlapped with the beginning. The very last sample
        // is directly adjacent to the original sample at "last-overlap";
        // after that the first sample starts without any seek or decoder gap.
        for (let i = 0; i < overlap; i++) {
          const angle = (i / overlap) * Math.PI / 2;
          // Equal-power fade: avoids a recurring volume dip in random noise.
          output[i] = input[last - overlap + i] * Math.cos(angle) + input[first + i] * Math.sin(angle);
        }
      }
      return loop;
    }
    async _load(id, ticket) {
      if (this.buffer && this.bufferId === id) return;
      const response = await fetch('./assets/' + encodeURIComponent(id) + '.mp3');
      if (!response.ok) throw new Error('Klangdatei nicht verfügbar: ' + response.status);
      const bytes = await response.arrayBuffer();
      if (ticket !== this.generation) return;
      const decoded = await this.context.decodeAudioData(bytes);
      if (ticket !== this.generation) return;
      this.buffer = this._makeSeamless(decoded);
      this.bufferId = id;
      this.offset = 0;
    }
    _stopSource() {
      if (!this.source) return;
      try { this.source.stop(); } catch (_) {}
      try { this.source.disconnect(); } catch (_) {}
      this.source = null;
    }
    async play(id, volume, remainingMs) {
      if (this.playing) return true;
      const ticket = ++this.generation;
      this._ensureContext();
      // Important for Safari: resume is triggered synchronously by the user's tap,
      // before any fetching or decoding awaits.
      if ('audioSession' in navigator) {
        try { navigator.audioSession.type = 'playback'; } catch (_) {}
      }
      const resumed = this.context.resume();
      await Promise.all([resumed, this._load(id, ticket)]);
      if (ticket !== this.generation) return false;
      this._stopSource();
      const src = this.context.createBufferSource();
      src.buffer = this.buffer;
      src.loop = true;
      src.loopStart = 0;
      src.loopEnd = this.buffer.duration;
      src.connect(this.gain);
      src.start(0, Math.max(0, Math.min(this.offset, this.buffer.duration - 0.001)));
      this.startedAt = this.context.currentTime - this.offset;
      this.source = src;
      this.playing = true;
      this.setVolume(volume, remainingMs);
      return true;
    }
    setVolume(volume, remainingMs = this.timerLeft) {
      this.volume = Math.max(0, Math.min(1, Number(volume)));
      this.timerLeft = Math.max(0, Number(remainingMs) || 0);
      if (!this.gain || !this.context) return;
      const now = this.context.currentTime;
      const g = this.gain.gain;
      g.cancelScheduledValues(now);
      const fade = this.timerLeft > 0 ? Math.min(1, this.timerLeft / 15000) : 1;
      g.setValueAtTime(this.volume * fade, now);
      // Unlike JS intervals, audio automation continues even if background
      // tabs throttle their timers. The sleep fade is thus on the audio clock.
      if (this.playing && this.timerLeft > 0) {
        if (this.timerLeft > 15000) g.setValueAtTime(this.volume, now + (this.timerLeft - 15000) / 1000);
        g.linearRampToValueAtTime(0, now + this.timerLeft / 1000);
      }
    }
    pause() {
      ++this.generation;
      if (this.playing && this.buffer && this.context) {
        this.offset = ((this.context.currentTime - this.startedAt) % this.buffer.duration + this.buffer.duration) % this.buffer.duration;
      }
      this.playing = false;
      this._stopSource();
      const ticket = this.generation;
      // Defer suspension: a sound switch can resume immediately without racing
      // against an unfinished suspend() on Safari.
      queueMicrotask(() => {
        if (ticket === this.generation && !this.playing && this.context && this.context.state === 'running') {
          this.context.suspend().catch(() => {});
        }
      });
    }
    stop() {
      this.pause();
      this.offset = 0;
    }
    changeSound() {
      this.stop();
      this.buffer = null;
      this.bufferId = null;
    }
  }
  window.RuheklangSeamlessPlayer = SeamlessSound;
})();
