const API_BASE_URL = 'http://localhost:8000/api';

export const fetchConfig = async () => {
  const response = await fetch(`${API_BASE_URL}/config`);
  if (!response.ok) throw new Error('Failed to fetch config');
  return response.json();
};

export const saveConfig = async (config: any) => {
  const response = await fetch(`${API_BASE_URL}/config`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
  if (!response.ok) throw new Error('Failed to save config');
  return response.json();
};

export const runStage = async (stage: string) => {
  const response = await fetch(`${API_BASE_URL}/run/${stage}`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to start pipeline');
  return response.json();
};

export const fetchStatus = async () => {
  const response = await fetch(`${API_BASE_URL}/status`);
  if (!response.ok) throw new Error('Failed to fetch status');
  return response.json();
};

export const fetchLogs = async () => {
  const response = await fetch(`${API_BASE_URL}/logs`);
  if (!response.ok) throw new Error('Failed to fetch logs');
  return response.json();
};

export const fetchStats = async () => {
  const response = await fetch(`${API_BASE_URL}/stats`);
  if (!response.ok) throw new Error('Failed to fetch stats');
  return response.json();
};

export const fetchTopics = async () => {
  const response = await fetch(`${API_BASE_URL}/topics`);
  if (!response.ok) throw new Error('Failed to fetch topics');
  return response.json();
};
