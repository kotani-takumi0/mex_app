/**
 * アプリ初期ローディング画面
 * 認証チェック中に表示するフルページローディング
 */
import React from 'react';
import './AppLoadingScreen.css';

export const AppLoadingScreen: React.FC = () => {
  return (
    <div className="app-loading-screen">
      <div className="app-loading-content">
        <div className="app-loading-brand">MEX App</div>
        <div className="app-loading-dots">
          <span className="app-loading-dot" />
          <span className="app-loading-dot" />
          <span className="app-loading-dot" />
        </div>
      </div>
    </div>
  );
};
