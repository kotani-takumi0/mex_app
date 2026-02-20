/**
 * 設定ページ
 * プロフィール編集とMCPトークン管理を提供
 */
import React, { useEffect, useRef, useState } from 'react';
import { useLocation, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  LuUser,
  LuKey,
  LuCopy,
  LuRefreshCw,
  LuTrash2,
  LuLoader,
  LuCheck,
  LuCrown,
  LuSparkles,
  LuCable,
  LuCircleCheck,
  LuTerminal,
  LuInfo,
} from 'react-icons/lu';
import { useAuth } from '../../contexts/AuthContext';
import {
  updateProfile,
  createApiToken,
  listMcpTokens,
  revokeMcpToken,
} from '../../api/auth';
import { getPlanInfo, createCheckout, createPortal, type PlanInfo } from '../../api/billing';
import { MCPTokenInfo } from '../../types';
import { PageHeader } from '../common/PageHeader';
import { CommandBlock, copyToClipboard } from '../common/CommandBlock';
import './SettingsPage.css';

const USERNAME_REGEX = /^[a-z0-9][a-z0-9-]{1,28}[a-z0-9]$/;

const formatDateTime = (value: string | null) => {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '-';
  return date.toLocaleString('ja-JP');
};

export const SettingsPage: React.FC = () => {
  const { user, setUser } = useAuth();
  const location = useLocation();
  const mcpSetupRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (location.hash === '#mcp-setup' && mcpSetupRef.current) {
      mcpSetupRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [location.hash]);

  const [displayName, setDisplayName] = useState('');
  const [username, setUsername] = useState('');
  const [bio, setBio] = useState('');
  const [githubUrl, setGithubUrl] = useState('');
  const [profileError, setProfileError] = useState('');
  const [profileSaving, setProfileSaving] = useState(false);

  const [tokenName, setTokenName] = useState('');
  const [tokenResult, setTokenResult] = useState<{ token: string; tokenId: string; expiresInDays: number } | null>(null);
  const [tokenCreating, setTokenCreating] = useState(false);
  const [tokenCopied, setTokenCopied] = useState(false);

  const [tokens, setTokens] = useState<MCPTokenInfo[]>([]);
  const [tokensLoading, setTokensLoading] = useState(false);
  const [tokensError, setTokensError] = useState('');
  const [revokingId, setRevokingId] = useState<string | null>(null);

  const [planInfo, setPlanInfo] = useState<PlanInfo | null>(null);
  const [planLoading, setPlanLoading] = useState(false);
  const [billingLoading, setBillingLoading] = useState(false);

  useEffect(() => {
    if (!user) return;
    setDisplayName(user.display_name || '');
    setUsername(user.username || '');
    setBio(user.bio || '');
    setGithubUrl(user.github_url || '');
  }, [user]);

  const fetchTokens = async () => {
    setTokensLoading(true);
    setTokensError('');
    const { data, error } = await listMcpTokens();
    if (error) {
      setTokensError(error);
    } else {
      setTokens(data?.tokens || []);
    }
    setTokensLoading(false);
  };

  useEffect(() => {
    fetchTokens();
  }, []);

  const fetchPlanInfo = async () => {
    setPlanLoading(true);
    const { data } = await getPlanInfo();
    if (data) {
      setPlanInfo(data);
    }
    setPlanLoading(false);
  };

  useEffect(() => {
    fetchPlanInfo();
  }, []);

  const handleUpgrade = async () => {
    setBillingLoading(true);
    const origin = window.location.origin;
    const { data, error } = await createCheckout(
      `${origin}/billing/success`,
      `${origin}/billing/cancel`,
    );
    setBillingLoading(false);

    if (error) {
      toast.error(error);
      return;
    }
    if (data?.checkout_url) {
      window.location.href = data.checkout_url;
    }
  };

  const handleManageSubscription = async () => {
    setBillingLoading(true);
    const { data, error } = await createPortal(window.location.href);
    setBillingLoading(false);

    if (error) {
      toast.error(error);
      return;
    }
    if (data?.portal_url) {
      window.location.href = data.portal_url;
    }
  };

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileError('');

    const trimmedName = displayName.trim();
    if (!trimmedName) {
      setProfileError('表示名を入力してください');
      return;
    }

    const normalizedUsername = username.trim().toLowerCase();
    if (normalizedUsername.length === 0 && user?.username) {
      setProfileError('ユーザー名は空にできません');
      return;
    }
    if (normalizedUsername.length > 0 && !USERNAME_REGEX.test(normalizedUsername)) {
      setProfileError('英小文字・数字・ハイフンのみ、3〜30文字で入力してください');
      return;
    }

    setProfileSaving(true);
    const payload = {
      display_name: trimmedName,
      bio: bio.trim(),
      github_url: githubUrl.trim(),
      ...(normalizedUsername.length > 0 ? { username: normalizedUsername } : {}),
    };

    const { data, error } = await updateProfile(payload);
    setProfileSaving(false);

    if (error) {
      setProfileError(error);
      return;
    }

    if (data) {
      setUser(data);
      toast.success('プロフィールを更新しました');
    }
  };

  const handleCreateToken = async (e: React.FormEvent) => {
    e.preventDefault();
    setTokenCreating(true);
    setTokenCopied(false);

    const name = tokenName.trim();
    const { data, error } = await createApiToken(name || undefined);
    setTokenCreating(false);

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
      toast.success('MCPトークンを発行しました');
      fetchTokens();
    }
  };

  const handleCopyToken = async () => {
    if (!tokenResult) return;
    try {
      await copyToClipboard(tokenResult.token);
      setTokenCopied(true);
      toast.success('トークンをコピーしました');
    } catch {
      toast.error('コピーに失敗しました');
    }
  };

  const handleRevoke = async (tokenId: string) => {
    setRevokingId(tokenId);
    const { error } = await revokeMcpToken(tokenId);
    setRevokingId(null);

    if (error) {
      toast.error(error);
      return;
    }

    toast.success('トークンを無効化しました');
    fetchTokens();
  };

  return (
    <div className="page-container settings-page">
      <PageHeader
        title="設定"
        description="プロフィールとMCPトークンを管理します。"
      />

      <section className="settings-section">
        <div className="settings-section-header">
          <div>
            <h2 className="settings-section-title">
              {planInfo?.plan === 'pro' ? <LuCrown size={18} /> : <LuSparkles size={18} />}
              プラン管理
            </h2>
            <p className="settings-section-description">
              現在のプランと利用状況を確認できます。
            </p>
          </div>
        </div>

        {planLoading ? (
          <div className="plan-loading">
            <LuLoader size={16} className="spin" /> 読み込み中...
          </div>
        ) : planInfo ? (
          <div className="plan-info-grid">
            <div className="plan-current">
              <span className="plan-label">現在のプラン</span>
              <span className={`plan-badge ${planInfo.plan === 'pro' ? 'plan-badge-pro' : 'plan-badge-free'}`}>
                {planInfo.plan === 'pro' ? 'Pro' : 'Free'}
              </span>
            </div>

            {planInfo.plan === 'free' && (
              <>
                <div className="plan-usage-row">
                  <span className="plan-usage-label">プロジェクト</span>
                  <span className="plan-usage-value">
                    {planInfo.project_count} / {planInfo.project_limit}
                  </span>
                </div>
              </>
            )}

            <div className="plan-usage-row">
              <span className="plan-usage-label">LLMモデル</span>
              <span className="plan-usage-value">{planInfo.llm_model}</span>
            </div>

            {planInfo.plan === 'pro' && planInfo.current_period_end && (
              <div className="plan-usage-row">
                <span className="plan-usage-label">次回請求日</span>
                <span className="plan-usage-value">
                  {formatDateTime(planInfo.current_period_end)}
                </span>
              </div>
            )}

            <div className="plan-actions">
              {planInfo.plan === 'free' ? (
                <button
                  className="settings-primary-btn"
                  onClick={handleUpgrade}
                  disabled={billingLoading}
                >
                  {billingLoading ? (
                    <>
                      <LuLoader size={16} className="spin" />
                      処理中...
                    </>
                  ) : (
                    <>
                      <LuSparkles size={16} />
                      Proにアップグレード
                    </>
                  )}
                </button>
              ) : (
                <button
                  className="settings-secondary-btn"
                  onClick={handleManageSubscription}
                  disabled={billingLoading}
                >
                  {billingLoading ? (
                    <>
                      <LuLoader size={16} className="spin" />
                      処理中...
                    </>
                  ) : (
                    'サブスクリプション管理'
                  )}
                </button>
              )}
            </div>
          </div>
        ) : null}
      </section>

      <section className="settings-section">
        <div className="settings-section-header">
          <div>
            <h2 className="settings-section-title">
              <LuUser size={18} />
              プロフィール
            </h2>
            <p className="settings-section-description">
              公開ポートフォリオに表示される情報を編集できます。
            </p>
          </div>
        </div>

        <form className="settings-form" onSubmit={handleProfileSubmit}>
          <div className="form-group">
            <label htmlFor="displayName">表示名</label>
            <input
              id="displayName"
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="例: Takumi"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="username">ユーザー名</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="例: takumi-dev"
              maxLength={30}
            />
            <div className="settings-hint">
              公開URL: {username ? <strong>/p/{username}</strong> : '未設定'}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="bio">自己紹介</label>
            <textarea
              id="bio"
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              placeholder="どんな開発に取り組んでいるかを簡潔に"
              rows={4}
            />
          </div>

          <div className="form-group">
            <label htmlFor="githubUrl">GitHub URL</label>
            <input
              id="githubUrl"
              type="url"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              placeholder="https://github.com/username"
            />
          </div>

          {profileError && <div className="settings-error">{profileError}</div>}

          <div className="settings-actions">
            <button type="submit" className="settings-primary-btn" disabled={profileSaving}>
              {profileSaving ? (
                <>
                  <LuLoader size={16} className="spin" />
                  保存中...
                </>
              ) : (
                'プロフィールを保存'
              )}
            </button>
          </div>
        </form>
      </section>

      <section className="settings-section" id="mcp-setup" ref={mcpSetupRef}>
        <div className="settings-section-header">
          <div>
            <h2 className="settings-section-title">
              <LuCable size={18} />
              MCPセットアップガイド
            </h2>
            <p className="settings-section-description">
              MCPを設定すると、開発ログが自動的にポートフォリオに記録されます。
            </p>
          </div>
        </div>

        <div className="mcp-setup-steps">
          <div className="mcp-setup-step">
            <div className="mcp-setup-step-number">1</div>
            <div className="mcp-setup-step-content">
              <h3 className="mcp-setup-step-title">MCPとは？</h3>
              <p className="mcp-setup-step-description">
                MCP（Model Context Protocol）は、AIツール（Claude Code など）と外部サービスをつなぐ仕組みです。
                設定すると、開発中の活動が自動で記録されポートフォリオに反映されます。
              </p>
            </div>
          </div>

          <div className={`mcp-setup-step ${tokens.some((t) => !t.revoked_at) ? 'mcp-setup-step--done' : ''}`}>
            <div className="mcp-setup-step-number">
              {tokens.some((t) => !t.revoked_at) ? <LuCircleCheck size={16} /> : '2'}
            </div>
            <div className="mcp-setup-step-content">
              <h3 className="mcp-setup-step-title">トークンを発行する</h3>
              <p className="mcp-setup-step-description">
                {tokens.some((t) => !t.revoked_at)
                  ? '有効なトークンがあります。次のステップに進みましょう。'
                  : '下のMCPトークンセクションで「新しいトークンを発行」してください。発行後にトークン文字列をコピーしておきます。'}
              </p>
              {!tokens.some((t) => !t.revoked_at) && (
                <a href="#mcp-tokens" className="mcp-setup-step-link">
                  トークンを発行する ↓
                </a>
              )}
            </div>
          </div>

          <div className="mcp-setup-step">
            <div className="mcp-setup-step-number">3</div>
            <div className="mcp-setup-step-content">
              <h3 className="mcp-setup-step-title">CLIでセットアップ</h3>
              <p className="mcp-setup-step-description">
                ターミナルで以下のコマンドを実行し、ガイドに従ってトークンを設定します。
              </p>
              <CommandBlock command="npx -p mex-mcp-server mex-setup" />
            </div>
          </div>

          <div className="mcp-setup-step">
            <div className="mcp-setup-step-number">4</div>
            <div className="mcp-setup-step-content">
              <h3 className="mcp-setup-step-title">
                <LuTerminal size={14} />
                Claude Codeに登録
              </h3>
              <p className="mcp-setup-step-description">
                Claude Code を使っている場合は、以下のコマンドでMCPサーバーを登録します。
              </p>
              <CommandBlock command="claude mcp add mex -- npx mex-mcp-server" />
            </div>
          </div>
        </div>

        <div className="mcp-setup-note">
          <div className="mcp-setup-note-icon">
            <LuInfo size={16} />
          </div>
          <div className="mcp-setup-note-content">
            <strong>トークンの設定は1アカウントにつき1回でOK</strong>
            <p>
              発行したトークンは明示的に無効化しない限り有効です。
              ただしトークンはデバイスごとにローカル保存されるため、別のPCや環境では再セットアップが必要です。
            </p>
          </div>
        </div>

        <div className="mcp-setup-wizard-link">
          <Link to="/setup" className="mcp-setup-step-link">
            <LuCable size={14} />
            Notion・NotebookLM も含むフルセットアップウィザードを開く →
          </Link>
        </div>
      </section>

      <section className="settings-section" id="mcp-tokens">
        <div className="settings-section-header">
          <div>
            <h2 className="settings-section-title">
              <LuKey size={18} />
              MCPトークン
            </h2>
            <p className="settings-section-description">
              MCPサーバーから開発ログを送信するための長寿命トークンを管理します。
            </p>
          </div>
          <button
            type="button"
            className="settings-ghost-btn"
            onClick={fetchTokens}
            disabled={tokensLoading}
          >
            {tokensLoading ? <LuLoader size={16} className="spin" /> : <LuRefreshCw size={16} />}
            再読み込み
          </button>
        </div>

        <form className="token-create-form" onSubmit={handleCreateToken}>
          <div className="form-group">
            <label htmlFor="tokenName">トークン名（任意）</label>
            <input
              id="tokenName"
              type="text"
              value={tokenName}
              onChange={(e) => setTokenName(e.target.value)}
              placeholder="例: MacBook Pro"
              maxLength={100}
            />
          </div>
          <button type="submit" className="settings-primary-btn" disabled={tokenCreating}>
            {tokenCreating ? (
              <>
                <LuLoader size={16} className="spin" />
                発行中...
              </>
            ) : (
              '新しいトークンを発行'
            )}
          </button>
        </form>

        {tokenResult && (
          <div className="token-result">
            <div className="token-result-header">
              <strong>新しいトークン</strong>
              <span>有効期限: {tokenResult.expiresInDays}日</span>
            </div>
            <div className="token-result-meta">
              トークンID: {tokenResult.tokenId || '未記録'}
            </div>
            <code className="token-value">{tokenResult.token}</code>
            <div className="token-actions">
              <button type="button" className="settings-secondary-btn" onClick={handleCopyToken}>
                {tokenCopied ? <LuCheck size={16} /> : <LuCopy size={16} />}
                {tokenCopied ? 'コピー済み' : 'コピーする'}
              </button>
              <span className="token-note">このトークンは再表示できません。</span>
            </div>
          </div>
        )}

        <div className="token-list">
          <h3>発行済みトークン</h3>
          {tokensError && <div className="settings-error">{tokensError}</div>}
          {tokensLoading ? (
            <div className="token-empty">読み込み中...</div>
          ) : tokens.length === 0 ? (
            <div className="token-empty">まだトークンがありません。</div>
          ) : (
            tokens.map((token) => (
              <div
                key={token.id}
                className={`token-row ${token.revoked_at ? 'revoked' : ''}`}
              >
                <div className="token-meta">
                  <div className="token-name">
                    {token.name || '名称未設定'}
                  </div>
                  <div className="token-sub">
                    <span>scope: {token.scope}</span>
                    <span>発行: {formatDateTime(token.created_at)}</span>
                    {token.revoked_at ? (
                      <span>無効化: {formatDateTime(token.revoked_at)}</span>
                    ) : (
                      <span className="token-active">有効</span>
                    )}
                  </div>
                </div>
                <button
                  type="button"
                  className="settings-danger-btn"
                  onClick={() => handleRevoke(token.id)}
                  disabled={!!token.revoked_at || revokingId === token.id}
                >
                  {revokingId === token.id ? (
                    <>
                      <LuLoader size={16} className="spin" />
                      無効化中...
                    </>
                  ) : (
                    <>
                      <LuTrash2 size={16} />
                      {token.revoked_at ? '無効化済み' : '無効化'}
                    </>
                  )}
                </button>
              </div>
            ))
          )}
        </div>
      </section>
    </div>
  );
};
