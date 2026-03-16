window.UIN_compressScreenshot = async function(base64) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      const maxWidth = 1280;
      const scale = Math.min(1, maxWidth / img.width);
      canvas.width  = Math.round(img.width  * scale);
      canvas.height = Math.round(img.height * scale);
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      // JPEG 80% — 6x smaller than PNG, Gemini handles perfectly
      resolve(canvas.toDataURL('image/jpeg', 0.80).split(',')[1]);
    };
    img.src = `data:image/png;base64,${base64}`;
  });
};