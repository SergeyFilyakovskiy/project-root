// API client that connects to the backend through api-gateway (nginx → port 80)
// For dev: proxy configured in vite.config.ts to localhost:80
// All cookies are sent automatically (httpOnly JWT tokens)

const API_BASE = "/api";

export async function apiFetch(path: string, init?: RequestInit) {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    ...init,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Ошибка сервера");
  }
  if (res.status === 204) return null;
  return res.json();
}

// Auth
export const authApi = {
  login: (username: string, password: string) =>
    apiFetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username, password }),
    }),
  register: (data: { username: string; email: string; password: string; first_name?: string; last_name?: string }) =>
    apiFetch("/auth/register", { method: "POST", body: JSON.stringify(data) }),
  logout: () => apiFetch("/auth/logout", { method: "POST" }),
  refresh: () => apiFetch("/auth/refresh", { method: "POST" }),
};

// User / Profile
export const userApi = {
  me: () => apiFetch("/user/me"),
  updateMe: (data: { username?: string; email?: string }) =>
    apiFetch("/user/me", { method: "PATCH", body: JSON.stringify(data) }),
  deleteMe: () => apiFetch("/user/me", { method: "DELETE" }),
  changePassword: (old_password: string, new_password: string) =>
    apiFetch("/user/me/password", { method: "PATCH", body: JSON.stringify({ old_password, new_password }) }),
  profile: () => apiFetch("/profile/me"),
  updateProfile: (data: object) =>
    apiFetch("/profile/me", { method: "PATCH", body: JSON.stringify(data) }),
};

// Integrations
export const integrationApi = {
  list: () => apiFetch("/integrations/"),
  get: (id: string) => apiFetch(`/integrations/${id}`),
  create: (data: { name: string; platform: string; platform_config?: object }) =>
    apiFetch("/integrations/", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: object) =>
    apiFetch(`/integrations/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  delete: (id: string) => apiFetch(`/integrations/${id}`, { method: "DELETE" }),
  oauthInit: (id: string) => apiFetch(`/integrations/${id}/oauth/init`),
  tokenStatus: (id: string) => apiFetch(`/integrations/${id}/token/status`),
};

// Analytics
export const analyticsApi = {
  kpi: (integration_id: string, date_from: string, date_to: string) =>
    apiFetch(`/analytics/kpi?integration_id=${integration_id}&date_from=${date_from}&date_to=${date_to}`),
  funnel: (integration_id: string, date_from: string, date_to: string) =>
    apiFetch(`/analytics/funnel?integration_id=${integration_id}&date_from=${date_from}&date_to=${date_to}`),
  comparePeriods: (
    integration_id: string,
    period_a_from: string, period_a_to: string,
    period_b_from: string, period_b_to: string,
  ) =>
    apiFetch(`/analytics/compare/periods?integration_id=${integration_id}&period_a_from=${period_a_from}&period_a_to=${period_a_to}&period_b_from=${period_b_from}&period_b_to=${period_b_to}`),
  comparePlatforms: (integration_id: string, date_from: string, date_to: string) =>
    apiFetch(`/analytics/compare/platforms?integration_id=${integration_id}&date_from=${date_from}&date_to=${date_to}`),
  anomalies: (integration_id?: string, is_resolved?: boolean) => {
    const params = new URLSearchParams();
    if (integration_id) params.set("integration_id", integration_id);
    if (is_resolved !== undefined) params.set("is_resolved", String(is_resolved));
    return apiFetch(`/analytics/anomalies?${params}`);
  },
};
