/**
 * ユーザー名設定モーダル
 *
 * username が未設定のユーザーに対して初回表示する。
 * 公開ポートフォリオ URL（/p/:username）を機能させるために必要。
 */
import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { updateProfile } from '../../api/auth';
import { useAuth } from '../../contexts/AuthContext';
import './UsernameSetupModal.css';

const USERNAME_REGEX = /^[a-z0-9][a-z0-9\-]{1,28}[a-z0-9]$/;

export const UsernameSetupModal: React.FC = () => {
  const { user, setUser } = useAuth();
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  // username が設定済み or スキップ済みなら非表示
  if (!user || user.username || dismissed) return null;

  const handleChange = (value: string) => {
    const normalized = value.toLowerCase().replace(/[^a-z0-9\-]/g, '');
    setUsername(normalized);
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!USERNAME_REGEX.test(username)) {
      setError('英小文字・数字・ハイフンのみ、3〜30文字で入力してください');
      return;
    }

    setIsSubmitting(true);
    const { data, error: apiError } = await updateProfile({ username });
    setIsSubmitting(false);

    if (apiError) {
      setError(apiError);
      return;
    }

    if (data) {
      setUser(data);
      toast.success('ユーザー名を設定しました');
    }
  };

  return (
    <div className="username-modal-overlay">
      <div className="username-modal">
        <h2>ユーザー名を設定</h2>
        <p className="modal-description">
          公開ポートフォリオのURLに使われます。あとから変更できます。
        </p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">ユーザー名</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => handleChange(e.target.value)}
              placeholder="例: takumi-dev"
              maxLength={30}
              autoFocus
            />
            {username && (
              <div className="username-preview">
                公開URL: <strong>/p/{username}</strong>
              </div>
            )}
            {error && <div className="error-text">{error}</div>}
            <div className="hint">英小文字・数字・ハイフン、3〜30文字</div>
          </div>

          <div className="username-modal-actions">
            <button
              type="button"
              className="btn-skip"
              onClick={() => setDismissed(true)}
            >
              あとで
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={isSubmitting || username.length < 3}
            >
              {isSubmitting ? '設定中...' : '設定する'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
