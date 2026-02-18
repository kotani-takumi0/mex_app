/**
 * Checkoutキャンセルページ
 * Stripe Checkoutキャンセル時のリダイレクト先
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { LuArrowLeft } from 'react-icons/lu';
import { PageHeader } from '../common/PageHeader';

export const BillingCancelPage: React.FC = () => {
  return (
    <div className="page-container billing-success-page">
      <PageHeader
        title="チェックアウトがキャンセルされました"
        description="決済は完了していません。いつでも再度お試しいただけます。"
      />

      <div className="billing-success-card">
        <p className="billing-success-description">
          Proプランにご興味がある場合は、設定ページからいつでもアップグレードできます。
        </p>

        <Link to="/settings" className="billing-success-link">
          <LuArrowLeft size={16} />
          設定に戻る
        </Link>
      </div>
    </div>
  );
};
