const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Streams the answer, calling onChunk(text) as each piece arrives.
 * Returns the full accumulated answer once the stream ends.
 */
export async function askQuestionStream(question, onChunk) {
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (body.detail) detail = body.detail;
    } catch {
      // response wasn't JSON — keep the generic message
    }
    throw new Error(detail);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let fullText = "";
  // Sentinel the backend appends when the LLM stream dies mid-answer.
  const ERROR_MARKER = "__STREAM_ERROR__";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunkText = decoder.decode(value, { stream: true });
    const markerIndex = chunkText.indexOf(ERROR_MARKER);

    if (markerIndex !== -1) {
      const message = chunkText.slice(markerIndex + ERROR_MARKER.length).trim();
      // Don't hand the marker (or any trailing text) to the UI.
      onChunk(chunkText.slice(0, markerIndex));
      throw new Error(message || "The answer stream failed mid-way");
    }

    fullText += chunkText;
    onChunk(chunkText);
  }

  return fullText;
}

export async function checkHealth() {
  try {
    const res = await fetch(`${API_URL}/`, { method: "GET" });
    return res.ok;
  } catch {
    return false;
  }
}
