/**
 * アップグレードプロンプト
 * Freeプランの制限に到達した際に表示するモーダル
 */
import React, { useState } from 'react';
import { LuSparkles, LuX, LuCheck, LuLoader } from 'react-icons/lu';
import { createCheckout } from '../../api/billing';
import './UpgradePrompt.css';

interface UpgradePromptProps {
  message: string;
  onClose: () => void;
}

const PRO_BENEFITS = [
  'プロジェクト無制限',
  'クイズ生成無制限',
  '高精度GPT-4oモデルで質の高い問題',
  'PDFエクスポート（予定）',
];

export const UpgradePrompt: React.FC<UpgradePromptProps> = ({ message, onClose }) => {
  const [loading, setLoading] = useState(false);

  const handleUpgrade = async () => {
    setLoading(true);
    const origin = window.location.origin;
    const { data, error } = await createCheckout(
      `${origin}/billing/success`,
      `${origin}/billing/cancel`,
    );
    setLoading(false);

    if (error) {
      return;
    }

    if (data?.checkout_url) {
      window.location.href = data.checkout_url;
    }
  };

  return (
    <div className="upgrade-overlay" onClick={onClose}>
      <div className="upgrade-modal" onClick={(e) => e.stopPropagation()}>
        <button className="upgrade-close" onClick={onClose} aria-label="閉じる">
          <LuX size={20} />
        </button>

        <div className="upgrade-icon-circle">
          <LuSparkles size={28} />
        </div>

        <h2 className="upgrade-title">Proプランにアップグレード</h2>
        <p className="upgrade-message">{message}</p>

        <ul className="upgrade-benefits">
          {PRO_BENEFITS.map((benefit) => (
            <li key={benefit}>
              <LuCheck size={16} className="upgrade-check" />
              {benefit}
            </li>
          ))}
        </ul>

        <div className="upgrade-price">
          <span className="upgrade-price-amount">&yen;780</span>
          <span className="upgrade-price-period">/月</span>
        </div>
        <p className="upgrade-price-annual">年間プランなら &yen;7,800（2ヶ月分おトク）</p>

        <div className="upgrade-actions">
          <button className="upgrade-cta" onClick={handleUpgrade} disabled={loading}>
            {loading ? (
              <>
                <LuLoader size={16} className="spin" />
                処理中...
              </>
            ) : (
              <>
                <LuSparkles size={16} />
                アップグレードする
              </>
            )}
          </button>
          <button className="upgrade-cancel" onClick={onClose}>
            あとで
          </button>
        </div>
      </div>
    </div>
  );
};
