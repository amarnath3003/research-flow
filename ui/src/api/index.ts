const API = '';

async function req<T>(url: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
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

// ── Pipeline ────────────────────────────────────────────────────
export const runStage = (pid: string, stage: string) =>
  req<any>(`/api/${pid}/run/${stage}`, { method: 'POST' });
export const fetchStatus = (pid: string) => req<any>(`/api/${pid}/status`);
export const fetchLogs = (pid: string) => req<any>(`/api/${pid}/logs`);

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
    const data = JSON.parse(ev.data);
    if (data.done) { onDone?.(); es.close(); return; }
    onLine(data.line);
  };
  es.onerror = () => es.close();
  return () => es.close();
}
