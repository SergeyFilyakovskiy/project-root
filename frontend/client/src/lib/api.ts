// API client — все запросы идут через nginx → api-gateway
// api-gateway маршрутизирует по первому сегменту пути: /{service}/{path}

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

// ─── Auth ─────────────────────────────────────────────────────────────────────
// POST /auth-service/auth/register — UserRegisterSchema:
//   email, password (8-50), username (3-30), first_name (1-50),
//   last_name? (max 50), date_of_birth (date ISO)
//
// POST /auth-service/auth/login — OAuth2PasswordRequestForm:
//   username (= email), password → куки access_token + refresh_token
export const authApi = {
  login: (username: string, password: string) =>
    apiFetch("/auth-service/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username, password }),
    }),

  register: (data: {
    email: string;
    password: string;
    username: string;
    first_name: string;
    last_name?: string;
    date_of_birth: string; // ISO date: "YYYY-MM-DD"
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
// GET  /auth-service/user/me → UserResponseSchema { id, email, role, profile, created_at }
//   profile: { id, username, first_name, last_name, date_of_birth, created_at }
//
// PATCH /auth-service/user/me — UserUpdateSchema { username?, email?, password? }
//
// DELETE /auth-service/user/me → 204
//
// PATCH /auth-service/user/me/password — UserChangePasswordSchema
//   { old_password (8-50), new_password (8-50) }
export const userApi = {
  me: () => apiFetch("/auth-service/user/me"),

  updateMe: (data: { username?: string; email?: string; password?: string }) =>
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
// GET    /integration-service/integrations/         → IntegrationListResponse { items[], total }
// POST   /integration-service/integrations/         — IntegrationCreate { platform, name, platform_config? }
// GET    /integration-service/integrations/{id}     → IntegrationResponse
// PATCH  /integration-service/integrations/{id}     — IntegrationUpdate { name?, is_active?, platform_config? }
// DELETE /integration-service/integrations/{id}     → 204
// GET    /integration-service/integrations/{id}/oauth/init   → OAuthInitResponse { auth_url }
// GET    /integration-service/integrations/{id}/token/status → TokenStatusResponse { integration_id, is_valid, expires_at }
export const integrationApi = {
  list: () => apiFetch("/integration-service/integrations/"),

  get: (id: string) => apiFetch(`/integration-service/integrations/${id}`),

  create: (data: { platform: string; name: string; platform_config?: Record<string, unknown> }) =>
    apiFetch("/integration-service/integrations/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: string, data: { name?: string; is_active?: boolean; platform_config?: Record<string, unknown> }) =>
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
    const p = new URLSearchParams({ integration_id, period_a_from, period_a_to, period_b_from, period_b_to });
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
    apiFetch(`/analytics-service/analytics/anomalies/${id}/resolve`, { method: "PATCH" }),

  timeseries: (integration_id: string, date_from: string, date_to: string) => {
    const p = new URLSearchParams({ integration_id, date_from, date_to });
    return apiFetch(`/analytics-service/analytics/timeseries?${p}`);
  },
};
