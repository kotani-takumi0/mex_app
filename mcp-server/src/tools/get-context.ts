import { MexApiClient, DevLogEntryResponse } from '../api-client.js';
import { LocalProjectConfig } from '../config.js';

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
    required: [],
  },
};

export interface ProjectContextResult {
  project: Record<string, unknown>;
  devlogs: DevLogEntryResponse[];
}

export async function handleGetProjectContext(
  client: MexApiClient,
  projectId: string | undefined,
  localConfig: LocalProjectConfig | null,
): Promise<ProjectContextResult> {
  const resolvedId = projectId ?? localConfig?.project_id;
  if (!resolvedId) {
    throw new Error('project_id が指定されておらず、.mex.json も見つかりません。project_id を指定するか、プロジェクトルートに .mex.json を配置してください。');
  }
  const [project, devlogs] = await Promise.all([
    client.getProject(resolvedId),
    client.getDevLogs(resolvedId, 10),
  ]);

  return {
    project,
    devlogs,
  };
}
