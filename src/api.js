// Thin fetch wrapper around the FastAPI backend.
// The bearer token is read from localStorage on every call.

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function authHeaders() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function handle(res) {
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || `Request failed (${res.status})`);
  }
  return data;
}

// Generic JSON request helper.
async function request(path, { method = "GET", body } = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  return handle(res);
}

export const api = {
  // ---- auth ----
  async login(username, password) {
    // OAuth2 password flow expects form-urlencoded data.
    const form = new URLSearchParams();
    form.append("username", username);
    form.append("password", password);
    const res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form,
    });
    return handle(res);
  },
  register: (username, password) =>
    request("/auth/register", { method: "POST", body: { username, password } }),

  // ---- subjects ----
  getSubjects: () => request("/subjects"),
  createSubject: (data) => request("/subjects", { method: "POST", body: data }),
  updateSubject: (id, data) =>
    request(`/subjects/${id}`, { method: "PUT", body: data }),
  deleteSubject: (id) => request(`/subjects/${id}`, { method: "DELETE" }),

  // ---- units ----
  getUnits: (subjectId) =>
    request(subjectId ? `/units?subject_id=${subjectId}` : "/units"),
  createUnit: (data) => request("/units", { method: "POST", body: data }),
  updateUnit: (id, data) =>
    request(`/units/${id}`, { method: "PUT", body: data }),
  deleteUnit: (id) => request(`/units/${id}`, { method: "DELETE" }),

  // ---- tasks ----
  getTasks: (unitId) =>
    request(unitId ? `/tasks?unit_id=${unitId}` : "/tasks"),
  createTask: (data) => request("/tasks", { method: "POST", body: data }),
  updateTask: (id, data) =>
    request(`/tasks/${id}`, { method: "PUT", body: data }),
  completeTask: (id) => request(`/tasks/${id}/complete`, { method: "POST" }),
  skipTask: (id) => request(`/tasks/${id}/skip`, { method: "POST" }),
  deleteTask: (id) => request(`/tasks/${id}`, { method: "DELETE" }),

  // ---- progress & workload ----
  getProgress: () => request("/progress"),
  getWorkload: () => request("/progress/workload/all"),

  // ---- reminders ----
  getReminders: () => request("/reminders"),
  createReminder: (data) =>
    request("/reminders", { method: "POST", body: data }),
  getNextReminders: () => request("/reminders/next"),
  dismissReminder: (id) =>
    request(`/reminders/${id}/dismiss`, { method: "POST" }),
  deleteReminder: (id) => request(`/reminders/${id}`, { method: "DELETE" }),
};

export { API_URL };
