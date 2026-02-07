import { MexApiClient, DevLogEntryResponse } from '../api-client.js';

export const getProjectContextTool = {
  name: 'get_project_context',
  description: 'プロジェクトの概要と最近の開発ログを取得します。',
  inputSchema: {
    type: 'object',
    properties: {
      project_id: {
        type: 'string',
        description: 'プロジェクトID',
      },
    },
    required: ['project_id'],
  },
};

export interface ProjectContextResult {
  project: Record<string, unknown>;
  devlogs: DevLogEntryResponse[];
}

export async function handleGetProjectContext(client: MexApiClient, projectId: string): Promise<ProjectContextResult> {
  const [project, devlogs] = await Promise.all([
    client.getProject(projectId),
    client.getDevLogs(projectId, 10),
  ]);

  return {
    project,
    devlogs,
  };
}
