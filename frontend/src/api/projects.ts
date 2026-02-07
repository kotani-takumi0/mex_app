import { apiGet, apiPost, apiPut, apiDelete } from './client';
import { Project, ProjectCreateRequest } from '../types';

export const getProjects = () => apiGet<{ projects: Project[] }>('/projects');
export const getProject = (id: string) => apiGet<Project>(`/projects/${id}`);
export const createProject = (data: ProjectCreateRequest) =>
  apiPost<Project, ProjectCreateRequest>('/projects', data);
export const updateProject = (id: string, data: Partial<ProjectCreateRequest>) =>
  apiPut<Project, Partial<ProjectCreateRequest>>(`/projects/${id}`, data);
export const deleteProject = (id: string) => apiDelete<{ status: string }>(`/projects/${id}`);
