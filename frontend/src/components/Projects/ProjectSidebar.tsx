/**
 * プロジェクトサイドバー
 * メタ情報（ステータス・公開設定・URL・技術タグ）をタブ切り替えに
 * 依存しない固定位置に表示する。Linear/GitHub の右サイドバーパターン。
 *
 * モバイルではメインコンテンツの上にカードとして表示される。
 */
import React from 'react';
import { LuCheck, LuLoader, LuPlus, LuTag, LuExternalLink, LuCopy } from 'react-icons/lu';
import { Project, TechDocument } from '../../types';
import { useAuth } from '../../contexts/AuthContext';
import './ProjectSidebar.css';

interface ProjectSidebarProps {
  readonly project: Project;
  readonly documents: TechDocument[];
  readonly isToggling: boolean;
  readonly onTogglePublic: () => void;
}

export const ProjectSidebar: React.FC<ProjectSidebarProps> = ({
  project,
  documents,
  isToggling,
  onTogglePublic,
}) => {
  const { user } = useAuth();
  const mcpCount = documents.filter((d) => d.source === 'notion').length;
  const manualCount = documents.filter((d) => d.source === 'manual').length;

  const publicUrl = user?.username
    ? `${window.location.origin}/p/${user.username}/${project.id}`
    : null;

  const handleCopyUrl = () => {
    if (!publicUrl) return;
    navigator.clipboard.writeText(publicUrl);
  };

  return (
    <aside className="project-sidebar">
      <div className="sidebar-section">
        <span className="sidebar-label">ステータス</span>
        <span className={`status-badge ${project.status}`}>
          {project.status === 'completed'
            ? '完了'
            : project.status === 'archived'
            ? '保管'
            : '進行中'}
        </span>
      </div>

      <div className="sidebar-section">
        <span className="sidebar-label">公開設定</span>
        <button className="toggle-public" onClick={onTogglePublic} disabled={isToggling}>
          {isToggling ? (
            <LuLoader size={14} className="spin" />
          ) : project.is_public ? (
            <LuCheck size={14} />
          ) : (
            <LuPlus size={14} />
          )}
          {project.is_public ? '公開中' : '非公開'}
        </button>
        {project.is_public && publicUrl && (
          <button className="sidebar-copy-url" onClick={handleCopyUrl} title="URLをコピー">
            <LuCopy size={12} />
            <span className="sidebar-url-text">{publicUrl.replace(/^https?:\/\//, '')}</span>
          </button>
        )}
      </div>

      <div className="sidebar-divider" />

      <div className="sidebar-section">
        <span className="sidebar-label">リポジトリ</span>
        {project.repository_url ? (
          <a href={project.repository_url} target="_blank" rel="noreferrer" className="sidebar-link">
            <LuExternalLink size={12} />
            {new URL(project.repository_url).pathname.slice(1)}
          </a>
        ) : (
          <span className="sidebar-empty">未登録</span>
        )}
      </div>

      <div className="sidebar-section">
        <span className="sidebar-label">デモ</span>
        {project.demo_url ? (
          <a href={project.demo_url} target="_blank" rel="noreferrer" className="sidebar-link">
            <LuExternalLink size={12} />
            {new URL(project.demo_url).hostname}
          </a>
        ) : (
          <span className="sidebar-empty">未登録</span>
        )}
      </div>

      <div className="sidebar-divider" />

      <div className="sidebar-section">
        <span className="sidebar-label">技術スタック</span>
        {project.technologies.length === 0 ? (
          <span className="sidebar-empty">未登録</span>
        ) : (
          <div className="sidebar-tech">
            {project.technologies.map((tech) => (
              <span key={tech} className="tech-pill">
                <LuTag size={10} />
                {tech}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="sidebar-divider" />

      <div className="sidebar-section">
        <span className="sidebar-label">ドキュメント</span>
        <div className="sidebar-stats">
          <span className="sidebar-stat-total">{project.devlog_count}件</span>
          {(mcpCount > 0 || manualCount > 0) && (
            <span className="sidebar-stat-breakdown">
              MCP {mcpCount} / 手動 {manualCount}
            </span>
          )}
        </div>
      </div>
    </aside>
  );
};
