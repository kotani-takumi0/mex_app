/**
 * スケルトンローダーコンポーネント
 * コンテンツ読み込み中のプレースホルダー表示
 */
import React from 'react';
import './LoadingSkeleton.css';

interface SkeletonProps {
  variant?: 'text' | 'rect' | 'circle';
  width?: string | number;
  height?: string | number;
  lines?: number;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  variant = 'text',
  width,
  height,
  lines = 1,
}) => {
  if (variant === 'text' && lines > 1) {
    return (
      <div className="skeleton-lines">
        {Array.from({ length: lines }, (_, i) => (
          <div
            key={i}
            className="skeleton skeleton-text"
            style={{
              width: i === lines - 1 ? '70%' : width || '100%',
              height: height || '14px',
            }}
          />
        ))}
      </div>
    );
  }

  return (
    <div
      className={`skeleton skeleton-${variant}`}
      style={{
        width: width || (variant === 'circle' ? '40px' : '100%'),
        height: height || (variant === 'circle' ? '40px' : variant === 'rect' ? '120px' : '14px'),
      }}
    />
  );
};

/**
 * ダッシュボード用スケルトン
 * 利用量カード3枚 + ケースリスト3行
 */
export const DashboardSkeleton: React.FC = () => {
  return (
    <div className="dashboard-skeleton">
      <div className="skeleton-usage-grid">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="skeleton-usage-card">
            <Skeleton variant="circle" width={48} height={48} />
            <Skeleton variant="text" width="60px" height="28px" />
            <Skeleton variant="text" width="80%" height="12px" />
          </div>
        ))}
      </div>
      <div className="skeleton-section-title">
        <Skeleton variant="text" width="160px" height="20px" />
      </div>
      <div className="skeleton-case-list">
        {[1, 2, 3].map((i) => (
          <div key={i} className="skeleton-case-card">
            <div className="skeleton-case-header">
              <Skeleton variant="text" width="60%" height="18px" />
              <Skeleton variant="rect" width="64px" height="24px" />
            </div>
            <Skeleton variant="text" width="100px" height="12px" />
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * 壁打ち結果用スケルトン
 */
export const SparringResultSkeleton: React.FC = () => {
  return (
    <div className="sparring-skeleton">
      <div className="skeleton-result-section">
        <Skeleton variant="text" width="180px" height="20px" />
        <div className="skeleton-case-list">
          {[1, 2].map((i) => (
            <div key={i} className="skeleton-case-card">
              <div className="skeleton-case-header">
                <Skeleton variant="text" width="50%" height="18px" />
                <Skeleton variant="rect" width="64px" height="24px" />
              </div>
              <Skeleton variant="text" lines={2} />
            </div>
          ))}
        </div>
      </div>
      <div className="skeleton-result-section">
        <Skeleton variant="text" width="120px" height="20px" />
        {[1, 2].map((i) => (
          <div key={i} className="skeleton-concern-card">
            <Skeleton variant="rect" width="80px" height="22px" />
            <Skeleton variant="text" lines={2} />
          </div>
        ))}
      </div>
      <div className="skeleton-result-section">
        <Skeleton variant="text" width="160px" height="20px" />
        {[1, 2, 3].map((i) => (
          <div key={i} className="skeleton-question-card">
            <Skeleton variant="rect" width="72px" height="22px" />
            <Skeleton variant="text" width="90%" height="16px" />
            <Skeleton variant="text" lines={2} />
          </div>
        ))}
      </div>
    </div>
  );
};
