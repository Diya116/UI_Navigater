// ============================================================
// UI Navigator — Popup Settings Logic
// Manages: language, speech rate, voice gender, session stats
// ============================================================

'use strict';

// ── State ──────────────────────────────────────────────────
let selectedGender = 'FEMALE';

// Test phrases in each language
const TEST_PHRASES = {
  auto: 'Hello! I am UI Navigator, your accessibility assistant.',
  en:   'Hello! I am UI Navigator, your accessibility assistant.',
  hi:   'नमस्ते! मैं UI नेविगेटर हूँ, आपका सहायक।',
  gu:   'નમસ્તે! હું UI નેવિગેટર છું, તમારો સહાયક.',
  ta:   'வணக்கம்! நான் UI நேவிகேட்டர், உங்கள் உதவியாளர்.',
  te:   'నమస్కారం! నేను UI నావిగేటర్, మీ సహాయకుడు.',
  bn:   'নমস্কার! আমি UI নেভিগেটর, আপনার সহকারী।',
  mr:   'नमस्कार! मी UI नेव्हिगेटर आहे, तुमचा सहाय्यक.',
  kn:   'ನಮಸ್ಕಾರ! ನಾನು UI ನ್ಯಾವಿಗೇಟರ್, ನಿಮ್ಮ ಸಹಾಯಕ.',
  ml:   'നമസ്കാരം! ഞാൻ UI നാവിഗേറ്റർ ആണ്, നിങ്ങളുടെ സഹായി.',
  pa:   'ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ UI ਨੇਵੀਗੇਟਰ ਹਾਂ, ਤੁਹਾਡਾ ਸਹਾਇਕ।',
  ar:   'مرحباً! أنا UI Navigator، مساعدك.',
  es:   '¡Hola! Soy UI Navigator, tu asistente.',
  fr:   'Bonjour! Je suis UI Navigator, votre assistant.',
  de:   'Hallo! Ich bin UI Navigator, Ihr Assistent.',
  pt:   'Olá! Sou UI Navigator, seu assistente.',
  zh:   '你好！我是UI导航器，您的助手。',
  ja:   'こんにちは！私はUIナビゲーターです。',
};

// Language code → BCP-47 for chrome.tts
const LANG_BCP47 = {
  auto: 'en-US',
  en:   'en-US', hi: 'hi-IN', gu: 'gu-IN',
  ta:   'ta-IN', te: 'te-IN', bn: 'bn-IN',
  mr:   'mr-IN', kn: 'kn-IN', ml: 'ml-IN',
  pa:   'pa-IN', ar: 'ar-XA', es: 'es-ES',
  fr:   'fr-FR', de: 'de-DE', pt: 'pt-BR',
  zh:   'zh-CN', ja: 'ja-JP',
};

// ── DOM refs ───────────────────────────────────────────────
const $  = (id) => document.getElementById(id);
const langSel      = $('lang');
const rateSlider   = $('speechRate');
const rateDisplay  = $('rateDisplay');
const btnSave      = $('btnSave');
const saveMsg      = $('saveMsg');
const btnTest      = $('btnTest');
const statusDot    = $('statusDot');
const btnClear     = $('btnClearSession');
const statRequests = $('statRequests');
const statLang     = $('statLang');
const statSession  = $('statSession');

// ── Load saved settings on popup open ─────────────────────
async function loadSettings() {
  const stored = await chrome.storage.local.get([
    'lang', 'speechRate', 'voiceGender',
    'sessionId', 'requestCount', 'detectedLang',
  ]);

  // Language
  if (stored.lang) langSel.value = stored.lang;

  // Speech rate
  if (stored.speechRate) {
    rateSlider.value      = stored.speechRate;
    rateDisplay.textContent = `${parseFloat(stored.speechRate).toFixed(1)}×`;
  }

  // Voice gender
  if (stored.voiceGender) {
    selectedGender = stored.voiceGender;
    updateGenderButtons(selectedGender);
  }

  // Stats
  statRequests.textContent = stored.requestCount || '0';
  statLang.textContent     = (stored.detectedLang || stored.lang || 'auto').toUpperCase();

  // Session ID (show last 4 chars only)
  if (stored.sessionId) {
    statSession.textContent = stored.sessionId.slice(-4).toUpperCase();
  }

  // Check API connectivity
  checkAPIStatus();
}

// ── Check if backend API is reachable ─────────────────────
async function checkAPIStatus() {
  try {
    const { url } = await chrome.runtime.sendMessage({ type: 'GET_API_BASE' });
    const res = await fetch(`${url}/health`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      statusDot.classList.add('connected');
      statusDot.title = 'API connected';
    } else {
      statusDot.title = `API error: ${res.status}`;
    }
  } catch (_) {
    statusDot.title = 'API unreachable — check backend';
  }
}

// ── Gender button state ────────────────────────────────────
function updateGenderButtons(gender) {
  document.querySelectorAll('.btn-gender').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.gender === gender);
  });
}

// ── Event: speech rate slider ──────────────────────────────
rateSlider.addEventListener('input', (e) => {
  const v = parseFloat(e.target.value).toFixed(1);
  rateDisplay.textContent = `${v}×`;
});

// ── Event: gender buttons ──────────────────────────────────
document.querySelectorAll('.btn-gender').forEach((btn) => {
  btn.addEventListener('click', () => {
    selectedGender = btn.dataset.gender;
    updateGenderButtons(selectedGender);
  });
});

// ── Event: save button ─────────────────────────────────────
btnSave.addEventListener('click', async () => {
  const lang       = langSel.value;
  const speechRate = parseFloat(rateSlider.value);
  const voiceGender = selectedGender;

  await chrome.storage.local.set({ lang, speechRate, voiceGender });

  // Show confirmation
  saveMsg.classList.remove('hidden');
  saveMsg.textContent = '✓ Settings saved';
  setTimeout(() => saveMsg.classList.add('hidden'), 2500);

  // Update stats display
  statLang.textContent = lang.toUpperCase();
});

// ── Event: test voice button ───────────────────────────────
btnTest.addEventListener('click', () => {
  const lang      = langSel.value;
  const rate      = parseFloat(rateSlider.value);
  const text      = TEST_PHRASES[lang] || TEST_PHRASES['en'];
  const langCode  = LANG_BCP47[lang]   || 'en-US';

  // Stop any currently playing TTS
  chrome.tts.stop();

  btnTest.textContent = '⏸ Playing…';
  btnTest.disabled    = true;

  chrome.tts.speak(text, {
    lang:  langCode,
    rate,
    pitch: 1.0,
    onEvent: (e) => {
      if (e.type === 'end' || e.type === 'error') {
        btnTest.textContent = '🔊 Test Voice';
        btnTest.disabled    = false;
      }
    },
  });
});

// ── Event: clear session ───────────────────────────────────
btnClear.addEventListener('click', async () => {
  const confirmed = confirm(
    'Clear conversation history?\nYour language preference will be kept.'
  );
  if (!confirmed) return;

  // Clear history via API if we have a session
  try {
    const stored = await chrome.storage.local.get(['sessionId']);
    if (stored.sessionId) {
      const { url } = await chrome.runtime.sendMessage({ type: 'GET_API_BASE' });
      await fetch(`${url}/v1/session/${stored.sessionId}`, { method: 'DELETE' });
    }
  } catch (_) {}

  // Reset local stats
  await chrome.storage.local.set({ requestCount: 0 });
  statRequests.textContent = '0';

  saveMsg.classList.remove('hidden');
  saveMsg.textContent = '✓ Session cleared';
  setTimeout(() => saveMsg.classList.add('hidden'), 2000);
});

// ── Boot ───────────────────────────────────────────────────
loadSettings();