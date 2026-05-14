export const API = 'http://localhost:8000';

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

// Config
export const fetchConfig = () => req<any>('/api/config');
export const saveConfig = (config: any) =>
  req<any>('/api/config', { method: 'POST', body: JSON.stringify(config) });

// Pipeline
export const runStage = (stage: string) =>
  req<any>(`/api/run/${stage}`, { method: 'POST' });
export const fetchStatus = () => req<any>('/api/status');
export const fetchLogs = () => req<any>('/api/logs');

// Data
export const fetchStats = () => req<any>('/api/stats');
export const fetchTopics = () => req<any[]>('/api/topics');
export const fetchFigures = () => req<any[]>('/api/figures');
export const fetchReport = () => req<any>('/api/report');
export const resetProject = () => req<any>('/api/reset', { method: 'POST' });

// Log streaming
export function subscribeLogs(
  onLine: (line: string) => void,
  onDone?: () => void,
): () => void {
  const es = new EventSource(`${API}/api/logs/stream`);
  es.onmessage = (ev) => {
    const data = JSON.parse(ev.data);
    if (data.done) {
      onDone?.();
      es.close();
      return;
    }
    onLine(data.line);
  };
  es.onerror = () => es.close();
  return () => es.close();
}
