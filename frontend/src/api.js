async function request(path, options) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      detail = (await res.json()).detail || detail;
    } catch {}
    throw new Error(detail);
  }
  return res.json();
}

export const getStatus = () => request("/api/status");
export const getHistory = () => request("/api/history");
export const sendMessage = (message) =>
  request("/api/chat", { method: "POST", body: JSON.stringify({ message }) });
export const resetChat = () => request("/api/reset", { method: "POST" });
