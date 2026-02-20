/**
 * スライドオーバーパネル
 * 右からスライドインするパネル。ドキュメント追加フォーム等に使用。
 * FABクリック → 右端からスライドインし、閲覧を邪魔せずにフォーム操作を実現する。
 */
import React, { useEffect } from 'react';
import { LuX } from 'react-icons/lu';
import './SlideOverPanel.css';

interface SlideOverPanelProps {
  readonly isOpen: boolean;
  readonly onClose: () => void;
  readonly title: string;
  readonly children: React.ReactNode;
}

export const SlideOverPanel: React.FC<SlideOverPanelProps> = ({
  isOpen,
  onClose,
  title,
  children,
}) => {
  useEffect(() => {
    if (!isOpen) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  return (
    <>
      <div
        className={`slide-over-backdrop ${isOpen ? 'slide-over-backdrop--visible' : ''}`}
        onClick={onClose}
        aria-hidden="true"
      />
      <aside
        className={`slide-over ${isOpen ? 'slide-over--open' : ''}`}
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <div className="slide-over-header">
          <h3 className="slide-over-title">{title}</h3>
          <button
            type="button"
            className="slide-over-close"
            onClick={onClose}
            aria-label="パネルを閉じる"
          >
            <LuX size={18} />
          </button>
        </div>
        <div className="slide-over-body">
          {children}
        </div>
      </aside>
    </>
  );
};
