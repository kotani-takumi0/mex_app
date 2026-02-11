import { MexApiClient, DevLogEntryResponse } from '../api-client.js';
import { MexConfig, LocalProjectConfig } from '../config.js';

export const saveDocumentTool = {
  name: 'save_document',
  description: `Notion MCPなどで生成した技術ドキュメントのURLをMEX Appに記録します。`,
  inputSchema: {
    type: 'object',
    properties: {
      project_id: {
        type: 'string',
        description: '保存先のプロジェクトID',
      },
      title: {
        type: 'string',
        description: 'ドキュメントのタイトル',
      },
      category: {
        type: 'string',
        enum: ['tutorial', 'design', 'debug_guide', 'learning', 'reference'],
        description: 'ドキュメントのカテゴリ',
      },
      technologies: {
        type: 'array',
        items: { type: 'string' },
        description: 'ドキュメントに関連する技術・ライブラリ名',
      },
      source_url: {
        type: 'string',
        description: 'NotionドキュメントのURL',
      },
    },
    required: ['title', 'technologies', 'category', 'source_url'],
  },
};

export interface SaveDocumentArgs {
  project_id?: string;
  title: string;
  technologies: string[];
  category: 'tutorial' | 'design' | 'debug_guide' | 'learning' | 'reference';
  source_url: string;
}

export async function handleSaveDocument(
  client: MexApiClient,
  config: MexConfig,
  args: SaveDocumentArgs,
  localConfig: LocalProjectConfig | null,
): Promise<DevLogEntryResponse> {
  const projectId = args.project_id ?? localConfig?.project_id;
  if (!projectId) {
    throw new Error('project_id が指定されておらず、.mex.json も見つかりません。project_id を指定するか、プロジェクトルートに .mex.json を配置してください。');
  }

  const trimmedSourceUrl = args.source_url.trim();

  return client.saveDocument(projectId, {
    source: 'mcp',
    entry_type: args.category,
    summary: args.title,
    detail: undefined,
    technologies: args.technologies,
    ai_tool: config.ai_tool,
    metadata: { source_url: trimmedSourceUrl },
  });
}
