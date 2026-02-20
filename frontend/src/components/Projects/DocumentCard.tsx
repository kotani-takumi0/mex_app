/**
 * ドキュメントカードコンポーネント
 * 個別ドキュメントの表示を担当。sourceバッジ（MCP自動/手動）を含む。
 *
 * ProjectDetailPage から抽出した理由:
 * - カード表示ロジックの独立化で保守性向上
 * - source（notion/manual）の視覚的区別を追加
 */
import React from 'react';
import { LuExternalLink } from 'react-icons/lu';
import { TechDocument } from '../../types';
import { getCategoryLabel, getCategoryClassName } from '../../utils/category';

interface DocumentCardProps {
  readonly document: TechDocument;
  readonly onClick: (document: TechDocument) => void;
}

export const DocumentCard: React.FC<DocumentCardProps> = ({ document, onClick }) => {
  const handleClick = () => onClick(document);
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onClick(document);
    }
  };

  return (
    <div
      className="devlog-card devlog-card--clickable"
      role="button"
      tabIndex={0}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
    >
      <div className="devlog-header">
        <div className="devlog-header-main">
          <span className={`devlog-type ${getCategoryClassName(document.category)}`}>
            {getCategoryLabel(document.category)}
          </span>
          <span className={`source-badge source-badge--${document.source === 'notion' ? 'mcp' : 'manual'}`}>
            {document.source === 'notion' ? 'MCP' : '手動'}
          </span>
        </div>
        <span className="devlog-date">
          {new Date(document.created_at).toLocaleString('ja-JP')}
        </span>
      </div>
      <p className="devlog-summary">{document.title}</p>
      <p className="devlog-detail">
        {document.content?.trim() || 'Notionを読んで学んだことを書こう'}
      </p>
      <div className="devlog-tech">
        {document.technologies.map((tech) => (
          <span key={tech} className="tech-pill">
            {tech}
          </span>
        ))}
      </div>
      {document.source_url && (
        <div className="document-source-link-wrap">
          <a
            className="document-source-link"
            href={document.source_url}
            target="_blank"
            rel="noreferrer"
            onClick={(event) => event.stopPropagation()}
          >
            <LuExternalLink size={14} />
            {document.source_url}
          </a>
        </div>
      )}
    </div>
  );
};
