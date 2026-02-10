import { MexApiClient, DevLogEntryResponse } from '../api-client.js';
import { MexConfig, LocalProjectConfig } from '../config.js';

export const recordDevActivityTool = {
  name: 'record_dev_activity',
  description: '開発過程をMEX Appに記録します。コード生成、バグ修正、設計判断などの作業内容を保存します。',
  inputSchema: {
    type: 'object',
    properties: {
      project_id: {
        type: 'string',
        description: '記録先のプロジェクトID',
      },
      entry_type: {
        type: 'string',
        enum: ['code_generation', 'debug', 'design_decision', 'learning', 'error_resolution'],
        description: '作業の種類',
      },
      summary: {
        type: 'string',
        description: '作業内容の要約（日本語、1〜2文）',
      },
      detail: {
        type: 'string',
        description: '詳細情報（変更したコード、使用したプロンプト等）',
      },
      technologies: {
        type: 'array',
        items: { type: 'string' },
        description: 'この作業で使用した技術名',
      },
    },
    required: ['entry_type', 'summary', 'technologies'],
  },
};

export interface RecordDevActivityArgs {
  project_id?: string;
  entry_type: string;
  summary: string;
  detail?: string;
  technologies: string[];
}

export async function handleRecordDevActivity(
  client: MexApiClient,
  config: MexConfig,
  args: RecordDevActivityArgs,
  localConfig: LocalProjectConfig | null,
): Promise<DevLogEntryResponse> {
  const projectId = args.project_id ?? localConfig?.project_id;
  if (!projectId) {
    throw new Error('project_id が指定されておらず、.mex.json も見つかりません。project_id を指定するか、プロジェクトルートに .mex.json を配置してください。');
  }
  return client.recordDevLog(projectId, {
    source: 'mcp',
    entry_type: args.entry_type,
    summary: args.summary,
    detail: args.detail,
    technologies: args.technologies,
    ai_tool: config.ai_tool,
  });
}
