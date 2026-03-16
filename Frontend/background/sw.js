const API_BASE = 'https://ui-navigator-api-HASH-uc.a.run.app';

// Keep service worker alive — MV3 kills it after 30s inactivity
const keepAliveInterval = setInterval(
  () => chrome.runtime.getPlatformInfo(() => {}), 25000
);

chrome.runtime.onMessage.addListener((msg, sender, reply) => {

  // Screen capture — only background SW can do this
  if (msg.type === 'CAPTURE_SCREEN') {
    chrome.tabs.captureVisibleTab(
      sender.tab.windowId,
      { format: 'png', quality: 92 },
      (dataUrl) => {
        if (chrome.runtime.lastError) {
          reply({ error: chrome.runtime.lastError.message });
        } else {
          reply({ screenshot: dataUrl.split(',')[1] });
        }
      }
    );
    return true;
  }

  if (msg.type === 'GET_API_BASE') {
    reply({ url: API_BASE });
    return true;
  }
});