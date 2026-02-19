import { MexApiClient, DevLogEntryResponse } from '../api-client.js';
import { MexConfig, LocalProjectConfig } from '../config.js';

export const saveNotebookTool = {
  name: 'save_notebook',
  description: `NotebookLM MCPで作成したノートブック情報をMEX Appに記録します。学習ハブでノートブックを管理するために使用します。`,
  inputSchema: {
    type: 'object',
    properties: {
      project_id: {
        type: 'string',
        description: '保存先のプロジェクトID',
      },
      title: {
        type: 'string',
        description: 'ノートブックのタイトル',
      },
      notebook_id: {
        type: 'string',
        description: 'NotebookLMのノートブックID',
      },
      notebook_url: {
        type: 'string',
        description: 'NotebookLMのノートブックURL',
      },
      technologies: {
        type: 'array',
        items: { type: 'string' },
        description: 'ノートブックに関連する技術・ライブラリ名',
      },
      learning_type: {
        type: 'string',
        enum: ['flashcard', 'audio', 'summary', 'full'],
        description: '学習コンテンツの種類',
      },
      public_url: {
        type: 'string',
        description: 'NotebookLMの公開共有リンク（任意）',
      },
    },
    required: ['title', 'notebook_id', 'notebook_url', 'technologies'],
  },
};

export interface SaveNotebookArgs {
  project_id?: string;
  title: string;
  notebook_id: string;
  notebook_url: string;
  technologies: string[];
  learning_type?: 'flashcard' | 'audio' | 'summary' | 'full';
  public_url?: string;
}

export async function handleSaveNotebook(
  client: MexApiClient,
  config: MexConfig,
  args: SaveNotebookArgs,
  localConfig: LocalProjectConfig | null,
): Promise<DevLogEntryResponse> {
  const projectId = args.project_id ?? localConfig?.project_id;
  if (!projectId) {
    throw new Error('project_id が指定されておらず、.mex.json も見つかりません。project_id を指定するか、プロジェクトルートに .mex.json を配置してください。');
  }

  const trimmedNotebookUrl = args.notebook_url.trim();

  return client.saveDocument(projectId, {
    source: 'mcp',
    entry_type: 'learning',
    summary: args.title,
    detail: undefined,
    technologies: args.technologies,
    ai_tool: config.ai_tool,
    metadata: {
      notebook_id: args.notebook_id,
      notebook_url: trimmedNotebookUrl,
      learning_type: args.learning_type ?? 'full',
      public_url: args.public_url ?? null,
      source_url: trimmedNotebookUrl,
    },
  });
}
