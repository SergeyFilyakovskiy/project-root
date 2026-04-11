// API client — все запросы идут через nginx → api-gateway
// api-gateway маршрутизирует по первому сегменту пути: /{service}/{path}
// Доступные сервисы: auth-service, analytics-service, integration-service, scheduler-service

async function apiFetch(path: string, init?: RequestInit) {
  const res = await fetch(path, {
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

// ─── Auth ────────────────────────────────────────────────────────────────────
// Публичные пути (без токена): /auth-service/auth/register, /login, /refresh
export const authApi = {
  login: (username: string, password: string) =>
    apiFetch("/auth-service/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username, password }),
    }),

  register: (data: {
    username: string;
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
  }) =>
    apiFetch("/auth-service/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  logout: () =>
    apiFetch("/auth-service/auth/logout", { method: "POST" }),

  refresh: () =>
    apiFetch("/auth-service/auth/refresh", { method: "POST" }),
};

// ─── User ─────────────────────────────────────────────────────────────────────
export const userApi = {
  me: () => apiFetch("/auth-service/user/me"),

  updateMe: (data: { username?: string; email?: string }) =>
    apiFetch("/auth-service/user/me", {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteMe: () =>
    apiFetch("/auth-service/user/me", { method: "DELETE" }),

  changePassword: (old_password: string, new_password: string) =>
    apiFetch("/auth-service/user/me/password", {
      method: "PATCH",
      body: JSON.stringify({ old_password, new_password }),
    }),
};

// ─── Integrations ─────────────────────────────────────────────────────────────
export const integrationApi = {
  list: () => apiFetch("/integration-service/integrations/"),

  get: (id: string) => apiFetch(`/integration-service/integrations/${id}`),

  create: (data: { name: string; platform: string; platform_config?: object }) =>
    apiFetch("/integration-service/integrations/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: string, data: object) =>
    apiFetch(`/integration-service/integrations/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  delete: (id: string) =>
    apiFetch(`/integration-service/integrations/${id}`, { method: "DELETE" }),

  oauthInit: (id: string) =>
    apiFetch(`/integration-service/integrations/${id}/oauth/init`),

  tokenStatus: (id: string) =>
    apiFetch(`/integration-service/integrations/${id}/token/status`),
};

// ─── Analytics ────────────────────────────────────────────────────────────────
export const analyticsApi = {
  kpi: (integration_id: string, date_from: string, date_to: string) => {
    const p = new URLSearchParams({ integration_id, date_from, date_to });
    return apiFetch(`/analytics-service/analytics/kpi?${p}`);
  },

  funnel: (integration_id: string, date_from: string, date_to: string) => {
    const p = new URLSearchParams({ integration_id, date_from, date_to });
    return apiFetch(`/analytics-service/analytics/funnel?${p}`);
  },

  comparePeriods: (
    integration_id: string,
    period_a_from: string,
    period_a_to: string,
    period_b_from: string,
    period_b_to: string,
  ) => {
    const p = new URLSearchParams({
      integration_id,
      period_a_from,
      period_a_to,
      period_b_from,
      period_b_to,
    });
    return apiFetch(`/analytics-service/analytics/compare/periods?${p}`);
  },

  comparePlatforms: (integration_id: string, date_from: string, date_to: string) => {
    const p = new URLSearchParams({ integration_id, date_from, date_to });
    return apiFetch(`/analytics-service/analytics/compare/platforms?${p}`);
  },

  anomalies: (integration_id?: string, is_resolved?: boolean) => {
    const p = new URLSearchParams();
    if (integration_id) p.set("integration_id", integration_id);
    if (is_resolved !== undefined) p.set("is_resolved", String(is_resolved));
    return apiFetch(`/analytics-service/analytics/anomalies?${p}`);
  },

  resolveAnomaly: (id: string) =>
    apiFetch(`/analytics-service/analytics/anomalies/${id}/resolve`, {
      method: "PATCH",
    }),
};
