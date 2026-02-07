import { MexApiClient, DevLogEntryResponse } from '../api-client.js';
import { MexConfig } from '../config.js';

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
    required: ['project_id', 'entry_type', 'summary', 'technologies'],
  },
};

export interface RecordDevActivityArgs {
  project_id: string;
  entry_type: string;
  summary: string;
  detail?: string;
  technologies: string[];
}

export async function handleRecordDevActivity(
  client: MexApiClient,
  config: MexConfig,
  args: RecordDevActivityArgs,
): Promise<DevLogEntryResponse> {
  return client.recordDevLog(args.project_id, {
    source: 'mcp',
    entry_type: args.entry_type,
    summary: args.summary,
    detail: args.detail,
    technologies: args.technologies,
    ai_tool: config.ai_tool,
  });
}
