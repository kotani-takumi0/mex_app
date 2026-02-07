/**
 * ページヘッダーコンポーネント
 * 各ページ共通のタイトル + 説明 + アクション
 */
import React from 'react';
import './PageHeader.css';

interface PageHeaderProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  description,
  action,
}) => {
  return (
    <div className="page-header">
      <div className="page-header-text">
        <h1 className="page-header-title">{title}</h1>
        {description && (
          <p className="page-header-description">{description}</p>
        )}
      </div>
      {action && <div className="page-header-action">{action}</div>}
    </div>
  );
};
