/**
 * Checkout成功ページ
 * Stripe Checkout完了後のリダイレクト先
 */
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { LuCircleCheck, LuLoader } from 'react-icons/lu';
import { useAuth } from '../../contexts/AuthContext';
import { PageHeader } from '../common/PageHeader';
import './BillingSuccessPage.css';

export const BillingSuccessPage: React.FC = () => {
  const { refreshUser } = useAuth();
  const [refreshing, setRefreshing] = useState(true);

  useEffect(() => {
    const refresh = async () => {
      await refreshUser();
      setRefreshing(false);
    };
    refresh();
  }, [refreshUser]);

  return (
    <div className="page-container billing-success-page">
      <PageHeader
        title="アップグレード完了"
        description="Proプランへのアップグレードが完了しました。"
      />

      <div className="billing-success-card">
        <div className="billing-success-icon">
          {refreshing ? (
            <LuLoader size={48} className="spin" />
          ) : (
            <LuCircleCheck size={48} />
          )}
        </div>

        <h2 className="billing-success-title">
          {refreshing ? 'プラン情報を更新中...' : 'Proプランへようこそ!'}
        </h2>

        <p className="billing-success-description">
          プロジェクト無制限、クイズ生成無制限、GPT-4oモデルが利用可能になりました。
        </p>

        <Link to="/dashboard" className="billing-success-link">
          ダッシュボードへ
        </Link>
      </div>
    </div>
  );
};
