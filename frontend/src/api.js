import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
  timeout: 10000,
});

export async function getHistory() {
  const response = await api.get("/sessions/history");
  return response.data;
}

export async function createSession(data) {
  const response = await api.post("/sessions/", data);
  return response.data;
}

export async function startSession(id) {
  const response = await api.patch(`/sessions/${id}/start`);
  return response.data;
}

export async function pauseSession(id, reason) {
  const response = await api.patch(`/sessions/${id}/pause`, {
    reason,
  });
  return response.data;
}

export async function resumeSession(id) {
  const response = await api.patch(`/sessions/${id}/resume`);
  return response.data;
}

export async function completeSession(id) {
  const response = await api.patch(`/sessions/${id}/complete`);
  return response.data;
}

export function getErrorMessage(error) {
  const detail = error.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => `${item.loc?.join(".")}: ${item.msg}`)
      .join("; ");
  }

  return "Could not reach the API. Check that the backend is running.";
}