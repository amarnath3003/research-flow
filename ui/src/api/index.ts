const API = import.meta.env.VITE_API_URL ?? '';

const REQUEST_TIMEOUT = 30000;

async function req<T>(url: string, opts?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);
  try {
    const { headers: extraHeaders, ...rest } = opts ?? {};
    const res = await fetch(`${API}${url}`, {
      headers: { 'Content-Type': 'application/json', ...(extraHeaders as Record<string, string>) },
      signal: controller.signal,
      ...rest,
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`API ${res.status}: ${text}`);
    }
    const text = await res.text();
    return text ? JSON.parse(text) : (null as T);
  } finally {
    clearTimeout(timeoutId);
  }
}

// ── Projects ───────────────────────────────────────────────────
export const listProjects = () => req<any[]>('/api/projects');
export const getProject = (pid: string) => req<any>(`/api/projects/${pid}`);
export const createProject = (name: string, description?: string) =>
  req<any>('/api/projects', { method: 'POST', body: JSON.stringify({ name, description }) });
export const updateProject = (pid: string, data: any) =>
  req<any>(`/api/projects/${pid}`, { method: 'PUT', body: JSON.stringify(data) });
export const deleteProject = (pid: string) =>
  req<any>(`/api/projects/${pid}`, { method: 'DELETE' });
export const setDefaultProject = (pid: string) =>
  req<any>(`/api/projects/${pid}/set-default`, { method: 'POST' });
export const duplicateProject = (pid: string, name: string) =>
  req<any>(`/api/projects/${pid}/duplicate`, { method: 'POST', body: JSON.stringify({ name }) });

// ── Config ──────────────────────────────────────────────────────
export const fetchConfig = (pid: string) => req<any>(`/api/${pid}/config`);
export const saveConfig = (pid: string, config: any) =>
  req<any>(`/api/${pid}/config`, { method: 'POST', body: JSON.stringify(config) });

// ── Pipeline (legacy — kept for backward compat) ────────────────
export const runStage = (pid: string, stage: string) =>
  req<any>(`/api/${pid}/run/${stage}`, { method: 'POST' });
export const fetchStatus = (pid: string) => req<any>(`/api/${pid}/status`);
export const fetchLogs = (pid: string) => req<any>(`/api/${pid}/logs`);

// ── Goals (new) ─────────────────────────────────────────────────
export const listGoals = (pid: string) => req<any[]>(`/api/${pid}/goals`);
export const runGoal = (pid: string, goalId: string) =>
  req<any>(`/api/${pid}/run-goal/${goalId}`, { method: 'POST' });
export const fetchGoalStatus = (pid: string) => req<any>(`/api/${pid}/goal-status`);
export const fetchGoalResults = (pid: string) => req<any>(`/api/${pid}/goal-results`);

export function subscribeGoalLogs(
  pid: string,
  onEvent: (ev: any) => void,
  onDone?: () => void,
): () => void {
  const es = new EventSource(`/api/${pid}/goal-logs/stream`);
  es.onmessage = (ev) => {
    try {
      const data = JSON.parse(ev.data);
      if (data.done) { onDone?.(); es.close(); return; }
      onEvent(data);
    } catch { /* ignore parse errors */ }
  };
  es.onerror = () => { es.close(); onDone?.(); };
  return () => es.close();
}

// ── Refinement ─────────────────────────────────────────────────
export const fetchRefinementOptions = (pid: string) => req<any[]>(`/api/${pid}/refinement-options`);
export const runRefinement = (pid: string, refinementId: string) =>
  req<any>(`/api/${pid}/refine/${refinementId}`, { method: 'POST' });

// ── Data ────────────────────────────────────────────────────────
export const fetchStats = (pid: string) => req<any>(`/api/${pid}/stats`);
export const fetchTopics = (pid: string) => req<any[]>(`/api/${pid}/topics`);
export const fetchFigures = (pid: string) => req<any[]>(`/api/${pid}/figures`);
export const fetchReport = (pid: string) => req<any>(`/api/${pid}/report`);

// ── Log streaming ───────────────────────────────────────────────
export function subscribeLogs(
  pid: string,
  onLine: (line: string) => void,
  onDone?: () => void,
): () => void {
  const es = new EventSource(`/api/${pid}/logs/stream`);
  es.onmessage = (ev) => {
    try {
      const data = JSON.parse(ev.data);
      if (data.done) { onDone?.(); es.close(); return; }
      onLine(data.line);
    } catch { /* ignore */ }
  };
  es.onerror = () => { es.close(); onDone?.(); };
  return () => es.close();
}
