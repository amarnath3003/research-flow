/* eslint-disable @typescript-eslint/no-explicit-any */
const API = import.meta.env.VITE_API_URL ?? '';

const REQUEST_TIMEOUT = 30000;

function apiUrl(path: string) {
  return `${API}${path}`;
}

async function req<T>(url: string, opts?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

  try {
    const { headers: extraHeaders, ...rest } = opts ?? {};
    const response = await fetch(apiUrl(url), {
      headers: { 'Content-Type': 'application/json', ...(extraHeaders as Record<string, string>) },
      signal: controller.signal,
      ...rest,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`API ${response.status}: ${text}`);
    }

    const text = await response.text();
    return text ? JSON.parse(text) : (null as T);
  } finally {
    clearTimeout(timeoutId);
  }
}

function subscribe(
  path: string,
  onMessage: (payload: any) => void,
  onDone?: () => void,
) {
  const source = new EventSource(apiUrl(path));

  source.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.done) {
        onDone?.();
        source.close();
        return;
      }
      onMessage(data);
    } catch {
      // Ignore malformed events from interrupted streams.
    }
  };

  source.onerror = () => {
    source.close();
    onDone?.();
  };

  return () => source.close();
}

export const listProjects = () => req<any[]>('/api/projects');
export const getProject = (pid: string) => req<any>(`/api/projects/${pid}`);
export const createProject = (name: string, description?: string) =>
  req<any>('/api/projects', { method: 'POST', body: JSON.stringify({ name, description }) });
export const updateProject = (pid: string, data: any) =>
  req<any>(`/api/projects/${pid}`, { method: 'PUT', body: JSON.stringify(data) });
export const deleteProject = (pid: string) => req<any>(`/api/projects/${pid}`, { method: 'DELETE' });
export const setDefaultProject = (pid: string) =>
  req<any>(`/api/projects/${pid}/set-default`, { method: 'POST' });
export const duplicateProject = (pid: string, name: string) =>
  req<any>(`/api/projects/${pid}/duplicate`, { method: 'POST', body: JSON.stringify({ name }) });

export const fetchConfig = (pid: string) => req<any>(`/api/${pid}/config`);
export const saveConfig = (pid: string, config: any) =>
  req<any>(`/api/${pid}/config`, { method: 'POST', body: JSON.stringify(config) });
export const fetchWorkspace = (pid: string) => req<any>(`/api/${pid}/workspace`);

export const runStage = (pid: string, stage: string) =>
  req<any>(`/api/${pid}/run/${stage}`, { method: 'POST' });
export const fetchStatus = (pid: string) => req<any>(`/api/${pid}/status`);
export const fetchLogs = (pid: string) => req<any>(`/api/${pid}/logs`);

export const listGoals = (pid: string) => req<any[]>(`/api/${pid}/goals`);
export const runGoal = (pid: string, goalId: string) =>
  req<any>(`/api/${pid}/run-goal/${goalId}`, { method: 'POST' });
export const fetchGoalStatus = (pid: string) => req<any>(`/api/${pid}/goal-status`);
export const fetchGoalResults = (pid: string) => req<any>(`/api/${pid}/goal-results`);

export function subscribeGoalLogs(
  pid: string,
  onEvent: (event: any) => void,
  onDone?: () => void,
) {
  return subscribe(`/api/${pid}/goal-logs/stream`, onEvent, onDone);
}

export const fetchRefinementOptions = (pid: string) => req<any[]>(`/api/${pid}/refinement-options`);
export const runRefinement = (pid: string, refinementId: string) =>
  req<any>(`/api/${pid}/refine/${refinementId}`, { method: 'POST' });

export const fetchStats = (pid: string) => req<any>(`/api/${pid}/stats`);
export const fetchTopics = (pid: string) => req<any[]>(`/api/${pid}/topics`);
export const fetchFigures = (pid: string) => req<any[]>(`/api/${pid}/figures`);
export const fetchReport = (pid: string) => req<any>(`/api/${pid}/report`);
export const fetchDataset = (pid: string, datasetId: string) =>
  req<any>(`/api/${pid}/data/${datasetId}`);

export function subscribeLogs(
  pid: string,
  onLine: (line: string) => void,
  onDone?: () => void,
) {
  return subscribe(`/api/${pid}/logs/stream`, (payload) => onLine(payload.line), onDone);
}
