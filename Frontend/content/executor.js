window.UIN_Executor = class {

  async execute(action) {
    switch (action.type) {
      case 'click':    return this._click(action);
      case 'fill':     return this._fill(action);
      case 'scroll':   return this._scroll(action);
      case 'navigate': return (location.href = action.url);
      case 'select':   return this._select(action);
      case 'check':    return this._check(action);
      case 'focus':    return this._focus(action);
      case 'key':      return this._key(action);
    }
  }

  // ── Element finding: 4 strategies ─────────────────────────
  _find(action) {
    // 1. Exact id
    if (action.id) {
      const el = document.getElementById(action.id);
      if (el) return el;
    }
    // 2. CSS selector
    if (action.selector) {
      const el = document.querySelector(action.selector);
      if (el) return el;
    }
    // 3. data-testid
    if (action.testid) {
      const el = document.querySelector(`[data-testid="${action.testid}"]`);
      if (el) return el;
    }
    // 4. ARIA label
    if (action.aria_label) {
      const el = document.querySelector(`[aria-label="${action.aria_label}"]`);
      if (el) return el;
    }
    // 5. Visible text match on interactive elements
    if (action.text) {
      const candidates = document.querySelectorAll(
        'button,a,input,[role="button"],[role="link"]'
      );
      for (const el of candidates) {
        const t = (el.textContent || el.value || el.placeholder || '').trim();
        if (t === action.text || t.includes(action.text)) return el;
      }
    }
    // 6. Coordinate fallback (corrected for DPR + zoom)
    if (action.rect || action.coords) {
      const coords = action.rect || action.coords;
      const dpr  = window.devicePixelRatio || 1;
      const zoom = window.outerWidth / window.innerWidth;
      const x    = (coords.x || coords.left || 0) / dpr / zoom;
      const y    = (coords.y || coords.top  || 0) / dpr / zoom;
      return document.elementFromPoint(x, y);
    }
    return null;
  }

  async _click(action) {
    const el = this._find(action);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      await this._delay(250);
      el.focus();
      el.click();
      return;
    }
    // Last resort: raw MouseEvent at coordinates
    if (action.rect || action.coords) {
      const c = action.rect || action.coords;
      const target = document.elementFromPoint(c.x, c.y);
      target?.dispatchEvent(new MouseEvent('click', {
        bubbles: true, cancelable: true,
        clientX: c.x, clientY: c.y, view: window,
      }));
    }
  }

  async _fill(action) {
    const fields = action.fields?.length
      ? action.fields
      : [{ ...action }];

    for (const field of fields) {
      const input = this._find(field);
      if (!input) continue;

      input.focus();
      input.select?.();

      // React/Vue/Angular controlled input fix
      const proto  = input.tagName === 'TEXTAREA'
        ? HTMLTextAreaElement.prototype
        : HTMLInputElement.prototype;
      const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
      setter
        ? setter.call(input, field.value)
        : (input.value = field.value);

      ['input', 'change', 'blur'].forEach(e =>
        input.dispatchEvent(new Event(e, { bubbles: true }))
      );

      await this._delay(100);
    }

    if (action.submit_after) {
      await this._delay(200);
      const submit =
        document.querySelector('[type="submit"]') ||
        document.querySelector('button[type="submit"]') ||
        document.querySelector('form button:not([type="button"])');

      submit
        ? submit.click()
        : document.activeElement?.dispatchEvent(
            new KeyboardEvent('keypress', {
              key: 'Enter', keyCode: 13, bubbles: true,
            })
          );
    }
  }

  _scroll(action) {
    if (action.target_text) {
      const all = document.querySelectorAll('*');
      for (const el of all) {
        if (
          el.children.length === 0 &&
          el.textContent?.trim().includes(action.target_text)
        ) {
          el.scrollIntoView({ behavior: 'smooth', block: 'center' });
          return;
        }
      }
    }
    const amounts = {
      down: 450, up: -450, bottom: 99999, top: -99999,
    };
    window.scrollBy({
      top: amounts[action.direction] ?? 450,
      behavior: 'smooth',
    });
  }

  _select(action) {
    const el = this._find(action);
    if (!el) return;
    el.value = action.value;
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }

  _check(action) {
    const el = this._find(action);
    if (!el) return;
    if (el.checked !== (action.checked !== false)) el.click();
  }

  _focus(action) {
    const el = this._find(action);
    el?.focus();
    el?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  _key(action) {
    const target = document.activeElement || document.body;
    target.dispatchEvent(new KeyboardEvent('keydown', {
      key: action.key, bubbles: true, cancelable: true,
    }));
  }

  _delay(ms) { return new Promise(r => setTimeout(r, ms)); }
};