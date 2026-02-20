/**
 * Floating Action Button
 * 右下に固定表示されるアクションボタン。
 * ドキュメント追加のトリガーとして使用。
 * ページ最下部に埋もれていたフォームの発見性を改善する。
 */
import React from 'react';
import { LuPlus } from 'react-icons/lu';
import './FloatingActionButton.css';

interface FloatingActionButtonProps {
  readonly onClick: () => void;
  readonly label?: string;
}

export const FloatingActionButton: React.FC<FloatingActionButtonProps> = ({
  onClick,
  label = '記録する',
}) => (
  <button
    type="button"
    className="fab"
    onClick={onClick}
    aria-label={label}
  >
    <LuPlus size={22} />
    <span className="fab-label">{label}</span>
  </button>
);
