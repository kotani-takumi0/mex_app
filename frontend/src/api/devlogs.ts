import { apiGet, apiPost, apiPut, apiDelete } from './client';
import { DevLogEntry, DevLogCreateRequest } from '../types';

export const getDevLogs = (projectId: string) =>
  apiGet<{ entries: DevLogEntry[]; total: number }>(`/devlogs/${projectId}`);
export const createDevLog = (projectId: string, data: DevLogCreateRequest) =>
  apiPost<DevLogEntry, DevLogCreateRequest>(`/devlogs/${projectId}/entries`, data);
export const updateDevLog = (entryId: string, data: Partial<DevLogCreateRequest>) =>
  apiPut<DevLogEntry, Partial<DevLogCreateRequest>>(`/devlogs/entries/${entryId}`, data);
export const deleteDevLog = (entryId: string) => apiDelete<{ status: string }>(`/devlogs/entries/${entryId}`);
