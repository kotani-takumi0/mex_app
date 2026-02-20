import { MexApiClient } from '../api-client.js';

export const createProjectTool = {
  name: 'create_project',
  description:
    'MEX Appに新しいプロジェクトを作成します。Claude Codeから直接プロジェクトを登録できます。',
  inputSchema: {
    type: 'object',
    properties: {
      title: {
        type: 'string',
        description: 'プロジェクト名',
      },
      description: {
        type: 'string',
        description: 'プロジェクトの概要（任意）',
      },
      technologies: {
        type: 'array',
        items: { type: 'string' },
        description: '使用技術・ライブラリ名（例: ["React", "FastAPI"]）',
      },
      repository_url: {
        type: 'string',
        description: 'GitHubリポジトリURL（任意）',
      },
    },
    required: ['title'],
  },
};

export interface CreateProjectArgs {
  title: string;
  description?: string;
  technologies?: string[];
  repository_url?: string;
}

export async function handleCreateProject(
  client: MexApiClient,
  args: CreateProjectArgs,
): Promise<Record<string, unknown>> {
  return client.createProject({
    title: args.title,
    description: args.description ?? null,
    technologies: args.technologies ?? [],
    repository_url: args.repository_url ?? null,
    status: 'in_progress',
    is_public: false,
  });
}
