/**
 * 汎用タブバーコンポーネント
 * GitHub/LeetCode のタブ構成パターンを参考に、
 * ラベル + 件数バッジを表示するタブナビゲーション。
 */
import React from 'react';
import './TabBar.css';

export interface TabItem {
  readonly key: string;
  readonly label: string;
  readonly count?: number;
}

interface TabBarProps {
  readonly tabs: readonly TabItem[];
  readonly activeTab: string;
  readonly onChange: (key: string) => void;
}

export const TabBar: React.FC<TabBarProps> = ({ tabs, activeTab, onChange }) => (
  <nav className="tab-bar" role="tablist">
    {tabs.map((tab) => (
      <button
        key={tab.key}
        role="tab"
        aria-selected={activeTab === tab.key}
        className={`tab-item ${activeTab === tab.key ? 'tab-item--active' : ''}`}
        onClick={() => onChange(tab.key)}
      >
        {tab.label}
        {tab.count !== undefined && (
          <span className="tab-count">{tab.count}</span>
        )}
      </button>
    ))}
  </nav>
);
