window.UIN_Recorder = class {
  constructor() {
    this.mediaRecorder = null;
    this.chunks        = [];
    this.stream        = null;
  }

  async start(durationMs = 6000, onTick) {
    this.stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount:     1,
        sampleRate:       16000,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl:  true,
      },
    });

    this.chunks = [];
    this.mediaRecorder = new MediaRecorder(this.stream, {
      mimeType: 'audio/webm;codecs=opus',
    });

    this.mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) this.chunks.push(e.data);
    };

    this.mediaRecorder.start(100);

    // Countdown ticks for orb timer
    let remaining = Math.ceil(durationMs / 1000);
    const interval = setInterval(() => {
      remaining--;
      onTick?.(remaining);
      if (remaining <= 0) clearInterval(interval);
    }, 1000);

    return new Promise((resolve) => {
      this.mediaRecorder.onstop = async () => {
        clearInterval(interval);
        this.stream.getTracks().forEach(t => t.stop());
        const blob   = new Blob(this.chunks, { type: 'audio/webm' });
        const buffer = await blob.arrayBuffer();
        const bytes  = new Uint8Array(buffer);
        let binary   = '';
        bytes.forEach(b => binary += String.fromCharCode(b));
        resolve(btoa(binary));
      };
      setTimeout(() => this.stop(), durationMs);
    });
  }

  stop() {
    if (this.mediaRecorder?.state === 'recording') {
      this.mediaRecorder.stop();
    }
  }
};