import { MexApiClient, ProjectSummary } from '../api-client.js';

export const listProjectsTool = {
  name: 'list_projects',
  description: 'MEX Appに登録されているプロジェクトの一覧を取得します。',
  inputSchema: {
    type: 'object',
    properties: {},
    required: [],
  },
};

export async function handleListProjects(client: MexApiClient): Promise<ProjectSummary[]> {
  return client.listProjects();
}
