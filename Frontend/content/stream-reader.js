window.UIN_readStream = async function(response, handlers) {
  const reader  = response.body.getReader();
  const decoder = new TextDecoder();
  let   buffer  = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split('\n\n');
    buffer = parts.pop(); // keep incomplete chunk

    for (const part of parts) {
      if (!part.startsWith('event:')) continue;
      const lines = part.split('\n');
      const event = lines[0].replace('event: ', '').trim();
      try {
        const data = JSON.parse(lines[1].replace('data: ', '').trim());
        await handlers[event]?.(data);
      } catch (_) {}
    }
  }
};