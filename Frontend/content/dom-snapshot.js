window.UIN_getDOMSnapshot = function() {

  function isVisible(el) {
    if (!el) return false;
    const s = window.getComputedStyle(el);
    if (s.display === 'none' || s.visibility === 'hidden') return false;
    if (parseFloat(s.opacity) === 0) return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0
      && r.top < window.innerHeight && r.bottom > 0
      && r.left < window.innerWidth && r.right > 0;
  }

  function getElementText(el) {
    return (
      el.getAttribute('aria-label') ||
      el.getAttribute('title') ||
      el.getAttribute('placeholder') ||
      el.textContent?.trim() ||
      el.value ||
      el.alt ||
      ''
    ).slice(0, 80);
  }

  // Extract only interactive visible elements — max 60
  const INTERACTIVE = [
    'button:not([disabled])',
    'a[href]',
    'input:not([type="hidden"]):not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    '[role="button"]',
    '[role="link"]',
    '[role="checkbox"]',
    '[role="radio"]',
    '[role="menuitem"]',
    '[role="option"]',
    '[role="tab"]',
    '[role="combobox"]',
    '[tabindex]:not([tabindex="-1"])',
  ].join(',');

  const elements = [...document.querySelectorAll(INTERACTIVE)]
    .filter(isVisible)
    .slice(0, 60)
    .map((el, i) => {
      const r = el.getBoundingClientRect();
      return {
        i:           i,                                // index for LLM reference
        tag:         el.tagName.toLowerCase(),
        type:        el.type || null,
        id:          el.id || null,
        name:        el.name || null,
        cls:         [...el.classList].slice(0, 3).join(' ') || null,
        text:        getElementText(el),
        role:        el.getAttribute('role'),
        href:        el.href?.slice(0, 100) || null,
        testid:      el.getAttribute('data-testid'),
        value:       el.value || null,
        checked:     el.type === 'checkbox' ? el.checked : null,
        rect: {
          x: Math.round(r.left),
          y: Math.round(r.top),
          w: Math.round(r.width),
          h: Math.round(r.height),
        },
      };
    });

  // Page landmarks for structural context
  const landmarks = [...document.querySelectorAll(
    'h1,h2,h3,main,nav,header,footer,form,[role="main"],[role="search"]'
  )].slice(0, 15).map(el => ({
    tag:  el.tagName.toLowerCase(),
    role: el.getAttribute('role'),
    id:   el.id || null,
    text: el.textContent?.trim().slice(0, 60),
  }));

  // Focused element — important for keyboard navigation context
  const focused = document.activeElement !== document.body
    ? {
        tag:   document.activeElement.tagName.toLowerCase(),
        id:    document.activeElement.id,
        text:  getElementText(document.activeElement),
        value: document.activeElement.value || null,
      }
    : null;

  // Visible page text — top 400 chars for context
  const textNodes = [];
  const walker = document.createTreeWalker(
    document.body, NodeFilter.SHOW_TEXT
  );
  let node;
  while ((node = walker.nextNode()) && textNodes.join(' ').length < 400) {
    const t = node.textContent.trim();
    if (t.length > 3 && isVisible(node.parentElement)) {
      textNodes.push(t);
    }
  }

  return {
    title:       document.title,
    url:         location.href,
    focused,
    elements,
    landmarks,
    pageText:    textNodes.join(' ').slice(0, 400),
    scrollY:     window.scrollY,
    scrollX:     window.scrollX,
    viewport: {
      w: window.innerWidth,
      h: window.innerHeight,
      dpr: window.devicePixelRatio || 1,
    },
  };
};