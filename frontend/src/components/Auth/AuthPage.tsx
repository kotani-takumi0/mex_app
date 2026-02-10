/**
 * 認証ページ（ログイン/登録切り替え）
 *
 * 変更理由: navigate('/dashboard')でログイン後遷移。
 * toast.success()で成功通知、ローディングスピナー、aria-live対応。
 */
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { LuLoader } from 'react-icons/lu';
import { useAuth } from '../../contexts/AuthContext';
import { login, register } from '../../api/auth';
import './AuthPage.css';

export const AuthPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { setUser } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isLogin) {
        const result = await login({ email, password });
        if (result.data) {
          setUser(result.data.user);
          toast.success('ログインしました');
          navigate('/dashboard');
        } else {
          setError(result.error || 'ログインに失敗しました');
        }
      } else {
        if (!displayName.trim()) {
          setError('表示名を入力してください');
          setLoading(false);
          return;
        }
        const result = await register({ email, password, display_name: displayName });
        if (result.data) {
          setUser(result.data.user);
          toast.success('アカウントを作成しました');
          navigate('/dashboard');
        } else {
          setError(result.error || '登録に失敗しました');
        }
      }
    } catch {
      setError('通信エラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <Link to="/" className="auth-brand-link">
          <h1 className="auth-title">MEX App</h1>
        </Link>
        <p className="auth-subtitle">AI開発ポートフォリオプラットフォーム</p>

        <div className="auth-tabs">
          <button
            className={`auth-tab ${isLogin ? 'active' : ''}`}
            onClick={() => { setIsLogin(true); setError(null); }}
          >
            ログイン
          </button>
          <button
            className={`auth-tab ${!isLogin ? 'active' : ''}`}
            onClick={() => { setIsLogin(false); setError(null); }}
          >
            新規登録
          </button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {!isLogin && (
            <div className="form-group">
              <label htmlFor="displayName">表示名</label>
              <input
                id="displayName"
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="Your Name"
                required={!isLogin}
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">メールアドレス</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">パスワード</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="8文字以上"
              minLength={8}
              required
            />
          </div>

          {error && (
            <div className="auth-error" role="alert" aria-live="polite">
              {error}
            </div>
          )}

          <button type="submit" className="auth-submit" disabled={loading}>
            {loading ? (
              <>
                <LuLoader className="auth-spinner" size={16} />
                処理中...
              </>
            ) : (
              isLogin ? 'ログイン' : '登録'
            )}
          </button>
        </form>

        <Link to="/" className="auth-back-link">
          トップに戻る
        </Link>
      </div>
    </div>
  );
};
