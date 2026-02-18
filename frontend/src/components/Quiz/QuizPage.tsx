/**
 * クイズページ（作成中）
 *
 * クイズ生成機能は現在開発中のため、Coming Soon 表示のみ。
 * 機能完成後にフォーム・回答UIを復元する。
 *
 * 403レスポンスを受け取った場合はUpgradePromptを表示する準備済み。
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LuHardHat } from 'react-icons/lu';
import { PageHeader } from '../common/PageHeader';
import { EmptyState } from '../common/EmptyState';
import { UpgradePrompt } from '../common/UpgradePrompt';
import './QuizPage.css';

export const QuizPage: React.FC = () => {
  const navigate = useNavigate();
  const [showUpgrade, setShowUpgrade] = useState(false);

  return (
    <div className="page-container">
      {showUpgrade && (
        <UpgradePrompt
          message="Freeプランではクイズ生成は月2回までです。Proプランにアップグレードすると無制限に生成できます。"
          onClose={() => setShowUpgrade(false)}
        />
      )}
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
