(function () {
  'use strict';
  if (window.__uinLoaded) return;
  window.__uinLoaded = true;

  // ── State ────────────────────────────────────────────────
  let isActive   = false;
  let sessionId  = null;
  let userLang   = 'en';
  let speechRate = 1.0;
  let gender     = 'FEMALE';

  const orb      = new window.UIN_Orb();
  const executor = new window.UIN_Executor();
  const recorder = new window.UIN_Recorder();

  // ── Boot ─────────────────────────────────────────────────
  async function init() {
    const s = await chrome.storage.local.get([
      'sessionId', 'lang', 'speechRate', 'voiceGender',
    ]);
    sessionId  = s.sessionId  || crypto.randomUUID();
    userLang   = s.lang       || navigator.language.split('-')[0] || 'en';
    speechRate = s.speechRate || 1.0;
    gender     = s.voiceGender || 'FEMALE';
    await chrome.storage.local.set({ sessionId });

    orb.setState('idle');
    orb.onActivate(activate);

    document.addEventListener('keydown', (e) => {
      if (e.altKey && e.key === 'n' && !isActive) {
        e.preventDefault();
        activate();
      }
      if (e.key === 'Escape' && isActive) {
        recorder.stop();
        orb.setState('idle');
        isActive = false;
      }
    });
  }

  // ── Main Flow ─────────────────────────────────────────────
  async function activate() {
    if (isActive) return;
    isActive = true;
    playTone(880, 440, 150);
    orb.setState('listening');

    try {
      // Capture screen + record voice in parallel
      const [captureResult, audioBase64] = await Promise.all([
        captureScreen(),
        recorder.start(6000, (t) => orb.setCountdown(t)),
      ]);

      if (captureResult.error) throw new Error(captureResult.error);

      // Compress screenshot
      const screenshot = await window.UIN_compressScreenshot(
        captureResult.screenshot
      );

      // Extract DOM snapshot
      const domSnapshot = window.UIN_getDOMSnapshot();

      orb.setState('processing');

      // Call API
      const { url: apiBase } = await chrome.runtime.sendMessage({
        type: 'GET_API_BASE',
      });

      const response = await fetch(`${apiBase}/v1/navigate/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          screenshot,
          audio_buffer: audioBase64,
          url:          location.href,
          dom_snapshot: domSnapshot,
          session_id:   sessionId,
          lang_hint:    userLang,
          speech_rate:  speechRate,
          voice_gender: gender,
        }),
      });

      if (!response.ok) throw new Error(`API ${response.status}`);

      // Read SSE stream
      await window.UIN_readStream(response, {

        transcript: (data) => {
          orb.setState('processing', `Heard: ${data.text}`);
          if (data.lang) userLang = data.lang;
        },

        action: async (data) => {
          // Execute DOM action IMMEDIATELY — don't wait for audio
          if (data.action && data.action.type !== 'none') {
            await executor.execute(data.action);
          }
        },

        response: async (data) => {
          orb.setState('speaking');
          if (data.audio && await playAudio(data.audio, speechRate)) {
            return;
          }
          if (data.text) {
            await speakFallback(data.text, data.lang || userLang);
          }
        },

        progress: async (data) => {
          orb.setState('processing', data.text);
          if (data.audio) await playAudio(data.audio, speechRate);
        },

        error: async (data) => {
          orb.setState('error');
          if (data.audio && await playAudio(data.audio, speechRate)) {
            return;
          }
          await speakFallback(data.text, userLang);
        },

        done: () => {
          setTimeout(() => orb.setState('idle'), 1500);
        },
      });

    } catch (err) {
      console.error('[UIN]', err);
      orb.setState('error');
      await speakFallback(getFallback(userLang), userLang);
    } finally {
      isActive = false;
    }
  }

  // ── Helpers ───────────────────────────────────────────────
  async function captureScreen() {
    return chrome.runtime.sendMessage({ type: 'CAPTURE_SCREEN' });
  }

  async function playAudio(base64, rate = 1.0) {
    try {
      const binary = atob(base64);
      const bytes  = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
      }

      const blob = new Blob([bytes], { type: 'audio/mpeg' });
      const url  = URL.createObjectURL(blob);

      return await new Promise((resolve) => {
        const audio = new Audio();
        let settled = false;

        const finish = (ok) => {
          if (settled) return;
          settled = true;
          audio.pause();
          audio.src = '';
          URL.revokeObjectURL(url);
          resolve(ok);
        };

        audio.preload = 'auto';
        audio.playbackRate = rate;
        audio.onended = () => finish(true);
        audio.onerror = () => finish(false);
        audio.src = url;

        const playPromise = audio.play();
        if (playPromise?.catch) {
          playPromise.catch(() => finish(false));
        }
      });
    } catch (err) {
      console.warn('[UIN] Audio playback failed', err);
      return false;
    }
  }

  async function speakFallback(text, lang) {
    const map = {
      en:'en-US', hi:'hi-IN', gu:'gu-IN', ta:'ta-IN',
      te:'te-IN', bn:'bn-IN', mr:'mr-IN', kn:'kn-IN',
      ml:'ml-IN', pa:'pa-IN', ar:'ar-XA', es:'es-ES',
    };
    return new Promise((resolve) => {
      chrome.tts.speak(text, {
        lang: map[lang] || 'en-US',
        rate: speechRate,
        onEvent: (e) => {
          if (e.type === 'end' || e.type === 'error') resolve();
        },
      });
    });
  }

  function playTone(startHz, endHz, ms) {
    try {
      const ctx  = new AudioContext();
      const osc  = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.setValueAtTime(startHz, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(endHz, ctx.currentTime + ms / 1000);
      gain.gain.setValueAtTime(0.3, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + ms / 1000);
      osc.start();
      osc.stop(ctx.currentTime + ms / 1000);
    } catch (_) {}
  }

  const FALLBACKS = {
    en: 'Something went wrong. Please try again.',
    hi: 'कुछ गलत हो गया। कृपया दोबारा कोशिश करें।',
    gu: 'કંઈક ખોટું થઈ ગયું. ફરી પ્રયાસ કરો.',
    ta: 'ஏதோ தவறாகிவிட்டது. மீண்டும் முயற்சிக்கவும்.',
    te: 'ఏదో తప్పు జరిగింది. మళ్ళీ ప్రయత్నించండి.',
    bn: 'কিছু ভুল হয়েছে। আবার চেষ্টা করুন।',
    mr: 'काहीतरी चुकले. पुन्हा प्रयत्न करा.',
    kn: 'ಏನೋ ತಪ್ಪಾಗಿದೆ. ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.',
    ml: 'എന്തോ തെറ്റ് സംഭവിച്ചു. വീണ്ടും ശ്രമിക്കുക.',
    pa: 'ਕੁਝ ਗਲਤ ਹੋ ਗਿਆ। ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।',
    ar: 'حدث خطأ ما. يرجى المحاولة مرة أخرى.',
  };

  function getFallback(lang) {
    return FALLBACKS[lang] || FALLBACKS['en'];
  }

  init().catch(console.error);
})();
