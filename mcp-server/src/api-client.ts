import { MexConfig } from './config.js';

export interface ProjectSummary {
  id: string;
  title: string;
  status: string;
  technologies: string[];
}

export interface DevLogEntryResponse {
  id: string;
  project_id: string;
  source: string;
  entry_type: string;
  summary: string;
  detail?: string | null;
  technologies: string[];
  ai_tool?: string | null;
  created_at: string;
  metadata?: Record<string, unknown>;
}

export class MexApiClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(config: MexConfig) {
    this.baseUrl = config.api_url;
    this.apiKey = config.api_key;
  }

  async listProjects(): Promise<ProjectSummary[]> {
    const result = await this.request<{ projects: ProjectSummary[] }>('/projects', 'GET');
    return result.projects;
  }

  async getProject(projectId: string): Promise<Record<string, unknown>> {
    return this.request(`/projects/${projectId}`, 'GET');
  }

  async getDevLogs(projectId: string, limit = 10): Promise<DevLogEntryResponse[]> {
    const result = await this.request<{ entries: DevLogEntryResponse[] }>(`/devlogs/${projectId}?limit=${limit}`, 'GET');
    return result.entries;
  }

  async recordDevLog(projectId: string, payload: Record<string, unknown>): Promise<DevLogEntryResponse> {
    return this.request(`/devlogs/${projectId}/entries`, 'POST', payload);
  }

  private async request<T = any>(path: string, method: 'GET' | 'POST', body?: Record<string, unknown>): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.apiKey}`,
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`API error (${response.status}): ${text}`);
    }

    return response.json() as Promise<T>;
  }
}
