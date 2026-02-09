/**
 * クイズページ（作成中）
 *
 * クイズ生成機能は現在開発中のため、Coming Soon 表示のみ。
 * 機能完成後にフォーム・回答UIを復元する。
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LuHardHat } from 'react-icons/lu';
import { PageHeader } from '../common/PageHeader';
import { EmptyState } from '../common/EmptyState';
import './QuizPage.css';

export const QuizPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="page-container">
      <PageHeader
        title="理解度チェック"
        description="開発ログから生成された4択クイズで理解度を確認できます。"
      />

      <EmptyState
        icon={LuHardHat}
        title="この機能は現在作成中です"
        description="クイズ生成機能は開発中です。今後のアップデートをお楽しみに。"
        action={{
          label: 'ダッシュボードへ戻る',
          onClick: () => navigate('/dashboard'),
        }}
      />
    </div>
  );
};
