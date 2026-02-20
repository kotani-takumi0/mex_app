/**
 * Step 3: NotebookLM MCP サーバー接続
 *
 * 変更理由: NotebookLM MCP CLI のインストールからログインまで、
 * 手順を順番にガイドする。Google OAuth が必要なため手動完了ボタンを提供。
 */
import React from 'react';
import {
  LuHeadphones,
  LuCircleCheck,
  LuTerminal,
  LuInfo,
} from 'react-icons/lu';
import { CommandBlock } from '../../common/CommandBlock';
import type { StepProps } from './types';

export const NotebookLmMcpStep: React.FC<StepProps> = ({
  onMarkCompleted,
  onMarkSkipped,
  isCompleted,
  isSkipped,
}) => {
  return (
    <div className="setup-step">
      <div className="setup-step-header">
        <div className="setup-step-icon setup-step-icon--nlm">
          <LuHeadphones size={20} />
        </div>
        <div>
          <h2 className="setup-step-title">NotebookLM MCP サーバー</h2>
          <p className="setup-step-subtitle">
            NotebookLMと連携して、学習コンテンツの自動生成を可能にします。
          </p>
        </div>
        {isCompleted && (
          <span className="setup-step-badge setup-step-badge--done">
            <LuCircleCheck size={14} /> 完了
          </span>
        )}
      </div>

      <div className="setup-step-notice setup-step-notice--warn">
        <LuInfo size={16} />
        <span>
          このステップではコミュニティ製の非公式パッケージ（<code>notebooklm-mcp-cli</code>）を使用します。
          Google公式のMCPサーバーは現時点で提供されていません。
          <a
            href="https://github.com/jacob-bd/notebooklm-mcp-cli"
            target="_blank"
            rel="noopener noreferrer"
            className="setup-step-notice-link"
          >
            GitHub リポジトリ
          </a>
        </span>
      </div>

      <div className="setup-step-section">
        <h3>
          <LuTerminal size={14} />
          1. CLI をインストール
        </h3>
        <p>NotebookLM MCP の CLI ツールをインストールします。</p>
        <CommandBlock command="uv tool install notebooklm-mcp-cli" />
      </div>

      <div className="setup-step-section">
        <h3>
          <LuTerminal size={14} />
          2. Claude Code に登録
        </h3>
        <p>MCPサーバーをClaude Codeに追加します。</p>
        <CommandBlock command="nlm setup add claude-code" />
      </div>

      <div className="setup-step-section">
        <h3>3. Google アカウントでログイン</h3>
        <p>以下のコマンドでブラウザが開き、Googleアカウントで認証します。</p>
        <CommandBlock command="nlm login" />
        <div className="setup-step-info">
          <LuInfo size={14} />
          <span>ブラウザで Google OAuth 認証が行われます。NotebookLM を利用している Google アカウントでログインしてください。</span>
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
