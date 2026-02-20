/**
 * Step 2: Notion MCP サーバー接続
 *
 * 変更理由: Notion公式のHTTP MCPエンドポイントが提供されたため、
 * Integration作成・トークン設定等の手順が不要になった。
 * コマンド1つ + ブラウザ認証で完結するシンプルな手順に変更。
 */
import React from 'react';
import {
  LuNotebook,
  LuCircleCheck,
  LuTerminal,
  LuInfo,
} from 'react-icons/lu';
import { CommandBlock } from '../../common/CommandBlock';
import type { StepProps } from './types';

export const NotionMcpStep: React.FC<StepProps> = ({
  onMarkCompleted,
  onMarkSkipped,
  isCompleted,
  isSkipped,
}) => {
  return (
    <div className="setup-step">
      <div className="setup-step-header">
        <div className="setup-step-icon setup-step-icon--notion">
          <LuNotebook size={20} />
        </div>
        <div>
          <h2 className="setup-step-title">Notion MCP サーバー</h2>
          <p className="setup-step-subtitle">
            Notionと連携して、ドキュメントや学習リソースを管理します。
          </p>
        </div>
        {isCompleted && (
          <span className="setup-step-badge setup-step-badge--done">
            <LuCircleCheck size={14} /> 完了
          </span>
        )}
      </div>

      <div className="setup-step-section">
        <h3>
          <LuTerminal size={14} />
          1. Claude Code に登録
        </h3>
        <p>以下のコマンドを実行するだけでNotion MCPサーバーが追加されます。</p>
        <CommandBlock command="claude mcp add --transport http notion https://mcp.notion.com/mcp" />
      </div>

      <div className="setup-step-section">
        <h3>2. ブラウザで認証</h3>
        <p>
          初回利用時にブラウザが開き、Notionアカウントでの認証とアクセス許可を求められます。
          許可すると自動的に接続が完了します。
        </p>
        <div className="setup-step-info">
          <LuInfo size={14} />
          <span>Integration の作成やトークンの設定は不要です。</span>
        </div>
      </div>

      {!isCompleted && !isSkipped && (
        <div className="setup-step-footer">
          <button
            type="button"
            className="setup-step-btn setup-step-btn--primary"
            onClick={onMarkCompleted}
          >
            <LuCircleCheck size={14} />
            セットアップ完了
          </button>
          <button
            type="button"
            className="setup-step-btn setup-step-btn--ghost"
            onClick={onMarkSkipped}
          >
            スキップ
          </button>
        </div>
      )}
    </div>
  );
};
