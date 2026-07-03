const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

export async function fetchState() {
  const response = await fetch(`${BACKEND_URL}/api/state`);
  if (!response.ok) {
    throw new Error("Failed to load backend state");
  }
  return response.json();
}

export async function postDemo(path, body) {
  const response = await fetch(`${BACKEND_URL}${path}`, {
    method: "POST",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    throw new Error("Demo action failed");
  }
  return response.json();
}
