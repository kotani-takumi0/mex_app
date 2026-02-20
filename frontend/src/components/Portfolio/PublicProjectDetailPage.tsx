/**
 * 公開プロジェクト詳細ページ
 *
 * 面接官がプロジェクトの深堀りに使うページ。
 *
 * 変更: サイドバー＋メインの2カラム構成に変更。
 * プロジェクト情報（タイトル、説明、リンク、技術、統計）を
 * sticky サイドバーに配置し、メインエリアにドキュメント一覧を表示。
 * スクロール量を大幅削減し、プロジェクト全体像を常に把握できるように。
 */
import React, { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  LuArrowLeft,
  LuClipboardList,
  LuExternalLink,
  LuFileText,
  LuGithub,
  LuTag,
} from 'react-icons/lu';
import { getPublicProjectDetail } from '../../api/portfolio';
import { PublicProjectDetail } from '../../types';
import { getCategoryLabel, getCategoryClassName } from '../../utils/category';
import { EmptyState } from '../common/EmptyState';
import './PublicProjectDetailPage.css';

const getStatusLabel = (status: string): string => {
  switch (status) {
    case 'completed': return '完了';
    case 'archived': return '保管';
    default: return '進行中';
  }
};

const categoryColors: Record<string, string> = {
  tutorial: '#ffab2e',
  design: '#2cbb5d',
  debug_guide: '#ffc01e',
  learning: '#a855f7',
  reference: 'rgba(239, 241, 246, 0.4)',
};

export const PublicProjectDetailPage: React.FC = () => {
  const { username, projectId } = useParams();
  const [detail, setDetail] = useState<PublicProjectDetail | null>(null);

  useEffect(() => {
    const fetchDetail = async () => {
      if (!username || !projectId) return;
      const { data, error } = await getPublicProjectDetail(username, projectId);
      if (error) {
        toast.error(error);
      } else {
        setDetail(data);
        if (data) {
          document.title = `${data.project.title} — ${username} — MEX App`;
        }
      }
    };
    fetchDetail();
    return () => { document.title = 'MEX App — AI時代の技術ポートフォリオ'; };
  }, [username, projectId]);

  const categoryDistribution = useMemo(() => {
    if (!detail) return [];
    const counts: Record<string, number> = {};
    for (const entry of detail.devlog) {
      counts[entry.category] = (counts[entry.category] || 0) + 1;
    }
    return Object.entries(counts)
      .map(([category, count]) => ({ category, count }))
      .sort((a, b) => b.count - a.count);
  }, [detail]);

  if (!detail) {
    return (
      <div className="pub-detail-page">
        <EmptyState
          icon={LuClipboardList}
          title="プロジェクトが見つかりません"
          description="公開設定のプロジェクトのみ表示されます。"
        />
      </div>
    );
  }

  const { project, devlog } = detail;

  return (
    <div className="pub-detail-page">
      <div className="pub-layout">
        {/* サイドバー: プロジェクト情報を sticky で常時表示 */}
        <aside className="pub-sidebar">
          <nav className="pub-breadcrumb">
            <Link to={`/p/${username}`} className="pub-breadcrumb-link">
              <LuArrowLeft size={14} />
              {username} のポートフォリオ
            </Link>
          </nav>

          <div className="pub-project-info">
            <span className={`pub-status pub-status--${project.status}`}>
              {getStatusLabel(project.status)}
            </span>
            <h1 className="pub-project-title">{project.title}</h1>
            {project.description && (
              <p className="pub-project-desc">{project.description}</p>
            )}

            <div className="pub-project-meta">
              {project.repository_url && (
                <a
                  href={project.repository_url}
                  target="_blank"
                  rel="noreferrer"
                  className="pub-meta-link"
                >
                  <LuGithub size={14} />
                  リポジトリ
                </a>
              )}
              {project.demo_url && (
                <a
                  href={project.demo_url}
                  target="_blank"
                  rel="noreferrer"
                  className="pub-meta-link"
                >
                  <LuExternalLink size={14} />
                  デモ
                </a>
              )}
            </div>

            {project.technologies.length > 0 && (
              <div className="pub-project-tech">
                {project.technologies.map((tech) => (
                  <span key={tech} className="pub-tech-pill">
                    <LuTag size={10} />
                    {tech}
                  </span>
                ))}
              </div>
            )}
          </div>

          {devlog.length > 0 && (
            <div className="pub-stats-row">
              <div className="pub-stat-item">
                <LuFileText size={14} />
                <span className="pub-stat-num">{devlog.length}</span>
                <span className="pub-stat-text">ドキュメント</span>
              </div>
              <div className="pub-distribution-bar">
                {categoryDistribution.map(({ category, count }) => (
                  <div
                    key={category}
                    className="pub-dist-segment"
                    style={{
                      flex: count,
                      backgroundColor: categoryColors[category] || categoryColors.reference,
                    }}
                    title={`${getCategoryLabel(category as 'tutorial')} ${count}件`}
                  />
                ))}
              </div>
              <div className="pub-distribution-legend">
                {categoryDistribution.map(({ category, count }) => (
                  <span key={category} className="pub-legend-item">
                    <span
                      className="pub-legend-dot"
                      style={{ backgroundColor: categoryColors[category] || categoryColors.reference }}
                    />
                    {getCategoryLabel(category as 'tutorial')} {count}
                  </span>
                ))}
              </div>
            </div>
          )}
        </aside>

        {/* メインエリア: ドキュメント一覧 */}
        <main className="pub-main">
          <h2 className="pub-section-label">ドキュメント</h2>
          {devlog.length === 0 ? (
            <div className="pub-empty-block">ドキュメントがまだありません。</div>
          ) : (
            <div className="pub-devlog-list">
              {devlog.map((entry, index) => (
                <div key={`${entry.title}-${index}`} className="pub-devlog-card">
                  <div className="pub-devlog-top">
                    <span className={`pub-devlog-badge ${getCategoryClassName(entry.category)}`}>
                      {getCategoryLabel(entry.category)}
                    </span>
                    <span className="pub-devlog-date">
                      {new Date(entry.created_at).toLocaleDateString('ja-JP')}
                    </span>
                  </div>
                  <h3 className="pub-devlog-title">{entry.title}</h3>
                  {entry.technologies.length > 0 && (
                    <div className="pub-devlog-tech">
                      {entry.technologies.map((tech) => (
                        <span key={tech} className="pub-devlog-tech-pill">{tech}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </main>
      </div>

      <footer className="pub-back-footer">
        <Link to={`/p/${username}`} className="pub-back-link">
          <LuArrowLeft size={14} />
          ポートフォリオに戻る
        </Link>
      </footer>
    </div>
  );
};
