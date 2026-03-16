window.UIN_Orb = class {
  constructor() {
    this.root = null;
    this._inject();
  }

  _inject() {
    if (document.getElementById('uin-root')) return;
    const root = document.createElement('div');
    root.id = 'uin-root';
    root.innerHTML = `
      <div id="uin-orb"
           role="button"
           tabindex="0"
           aria-label="UI Navigator — press Alt+N to activate"
           aria-live="assertive">
        <div id="uin-ring"></div>
        <svg id="uin-icon" width="22" height="22" viewBox="0 0 24 24"
             fill="currentColor" aria-hidden="true">
          <path d="M12 14c1.66 0 3-1.34
                   3-3V5c0-1.66-1.34-3-3-3S9 3.34
                   9 5v6c0 1.66 1.34 3 3 3z"/>
          <path d="M17 11c0 2.76-2.24 5-5
                   5s-5-2.24-5-5H5c0 3.53 2.61
                   6.43 6 6.92V21h2v-3.08c3.39-.49
                   6-3.39 6-6.92h-2z"/>
        </svg>
        <div id="uin-countdown" aria-hidden="true"></div>
      </div>
      <div id="uin-toast"
           role="status"
           aria-live="polite"
           aria-atomic="true">
      </div>
    `;
    document.body.appendChild(root);
    this.root = root;
  }

  setState(state, message = '') {
    const orb   = document.getElementById('uin-orb');
    const toast = document.getElementById('uin-toast');
    if (!orb) return;

    // Remove all state classes
    orb.className = '';
    orb.classList.add(`uin-${state}`);

    const labels = {
      idle:       'UI Navigator ready — press Alt+N',
      listening:  'Listening, speak now',
      processing: 'Processing your request',
      speaking:   'Speaking response',
      error:      'Error occurred, please try again',
    };

    orb.setAttribute('aria-label', labels[state] || state);
    toast.textContent = message || labels[state] || '';
  }

  setCountdown(n) {
    const el = document.getElementById('uin-countdown');
    if (el) el.textContent = n > 0 ? n : '';
  }

  onActivate(fn) {
    const orb = document.getElementById('uin-orb');
    orb?.addEventListener('click', fn);
    orb?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        fn();
      }
    });
  }
};