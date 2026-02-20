/**
 * Step 1: MEX MCPサーバー接続
 *
 * 変更理由: ウィザードの最初のステップとして、MEXトークンの発行・コピーと
 * MCP サーバーの登録コマンドをガイドする。既存トークンがあれば自動完了。
 */
import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import {
  LuKey,
  LuLoader,
  LuCopy,
  LuCheck,
  LuCircleCheck,
  LuTerminal,
} from 'react-icons/lu';
import { createApiToken, listMcpTokens } from '../../../api/auth';
import { CommandBlock, copyToClipboard } from '../../common/CommandBlock';
import type { StepProps } from './types';

export const MexMcpStep: React.FC<StepProps> = ({
  onMarkCompleted,
  onMarkSkipped,
  isCompleted,
  isSkipped,
}) => {
  const [tokenName, setTokenName] = useState('');
  const [tokenResult, setTokenResult] = useState<{
    token: string;
    tokenId: string;
    expiresInDays: number;
  } | null>(null);
  const [creating, setCreating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [checking, setChecking] = useState(true);
  const [hasActiveToken, setHasActiveToken] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const check = async () => {
      setChecking(true);
      const { data } = await listMcpTokens();
      if (cancelled) return;
      const active = (data?.tokens || []).some((t) => !t.revoked_at);
      setHasActiveToken(active);
      if (active && !isCompleted) {
        onMarkCompleted();
      }
      setChecking(false);
    };
    check();
    return () => { cancelled = true; };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    const name = tokenName.trim();
    const { data, error } = await createApiToken(name || undefined);
    setCreating(false);

    if (error) {
      toast.error(error);
      return;
    }
    if (data) {
      setTokenResult({
        token: data.api_token,
        tokenId: data.token_id,
        expiresInDays: data.expires_in_days,
      });
      setTokenName('');
      setHasActiveToken(true);
      onMarkCompleted();
      toast.success('MCPトークンを発行しました');
    }
  };

  const handleCopyToken = async () => {
    if (!tokenResult) return;
    try {
      await copyToClipboard(tokenResult.token);
      setCopied(true);
      toast.success('トークンをコピーしました');
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error('コピーに失敗しました');
    }
  };

  return (
    <div className="setup-step">
      <div className="setup-step-header">
        <div className="setup-step-icon setup-step-icon--mex">
          <LuKey size={20} />
        </div>
        <div>
          <h2 className="setup-step-title">MEX MCP サーバー</h2>
          <p className="setup-step-subtitle">
            開発ログを自動でポートフォリオに記録するための接続です。
          </p>
        </div>
        {isCompleted && (
          <span className="setup-step-badge setup-step-badge--done">
            <LuCircleCheck size={14} /> 完了
          </span>
        )}
      </div>

      {checking ? (
        <div className="setup-step-loading">
          <LuLoader size={16} className="spin" /> トークンを確認中...
        </div>
      ) : (
        <>
          {hasActiveToken && !tokenResult && (
            <div className="setup-step-notice setup-step-notice--success">
              <LuCircleCheck size={16} />
              有効なトークンが見つかりました。以下のコマンドでMCPサーバーを登録してください。
            </div>
          )}

          {!hasActiveToken && (
            <>
              <div className="setup-step-section">
                <h3>1. トークンを発行</h3>
                <p>MCPサーバーがMEX Appと通信するためのトークンを発行します。</p>
                <form className="setup-step-token-form" onSubmit={handleCreate}>
                  <input
                    type="text"
                    value={tokenName}
                    onChange={(e) => setTokenName(e.target.value)}
                    placeholder="トークン名（任意）例: MacBook Pro"
                    maxLength={100}
                  />
                  <button type="submit" className="setup-step-btn setup-step-btn--primary" disabled={creating}>
                    {creating ? (
                      <><LuLoader size={14} className="spin" /> 発行中...</>
                    ) : (
                      '発行する'
                    )}
                  </button>
                </form>
              </div>
            </>
          )}

          {tokenResult && (
            <div className="setup-step-token-result">
              <div className="setup-step-token-header">
                <strong>発行されたトークン</strong>
                <span>有効期限: {tokenResult.expiresInDays}日</span>
              </div>
              <code className="setup-step-token-value">{tokenResult.token}</code>
              <div className="setup-step-token-actions">
                <button
                  type="button"
                  className="setup-step-btn setup-step-btn--secondary"
                  onClick={handleCopyToken}
                >
                  {copied ? <LuCheck size={14} /> : <LuCopy size={14} />}
                  {copied ? 'コピー済み' : 'コピーする'}
                </button>
                <span className="setup-step-token-note">このトークンは再表示できません。</span>
              </div>
            </div>
          )}

          <div className="setup-step-section">
            <h3>
              <LuTerminal size={14} />
              {hasActiveToken ? '1' : '2'}. CLIでセットアップ
            </h3>
            <p>ターミナルで以下を実行し、ガイドに従ってトークンを設定します。</p>
            <CommandBlock command="npx -p mex-mcp-server mex-setup" />
            <p className="setup-step-hint">
              API URL を聞かれたら <code>https://mex-app-backend.onrender.com/api</code> と入力してください。
            </p>
          </div>

          <div className="setup-step-section">
            <h3>
              <LuTerminal size={14} />
              {hasActiveToken ? '2' : '3'}. Claude Code に登録
            </h3>
            <p>Claude Code を使っている場合は、以下でMCPサーバーを登録します。</p>
            <CommandBlock command="claude mcp add mex -- npx mex-mcp-server" />
          </div>
        </>
      )}

      {!isCompleted && !isSkipped && !checking && (
        <div className="setup-step-footer">
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
