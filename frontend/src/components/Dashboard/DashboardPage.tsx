/**
 * ダッシュボードページ
 * ポートフォリオ概要と最近のプロジェクトを表示
 */
import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  LuBookOpen,
  LuCable,
  LuNotebook,
  LuPlus,
  LuFolderKanban,
  LuX,
} from 'react-icons/lu';
import { getDashboard } from '../../api/dashboard';
import { PageHeader } from '../common/PageHeader';
import { DashboardSkeleton } from '../common/LoadingSkeleton';
import { EmptyState } from '../common/EmptyState';
import { DashboardData } from '../../types';
import './DashboardPage.css';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [mcpBannerDismissed, setMcpBannerDismissed] = useState(
    () => localStorage.getItem('mex_mcp_banner_dismissed') === 'true',
  );

  const dismissMcpBanner = () => {
    setMcpBannerDismissed(true);
    localStorage.setItem('mex_mcp_banner_dismissed', 'true');
  };

  useEffect(() => {
    const fetchDashboard = async () => {
      setIsLoading(true);
      const { data: dashboardData, error: apiError } = await getDashboard();
      if (apiError) {
        toast.error(apiError);
      } else {
        setData(dashboardData);
      }
      setIsLoading(false);
    };

    fetchDashboard();
  }, []);

  if (isLoading) {
    return (
      <div className="page-container dashboard-page">
        <PageHeader title="進捗概要" description="読み込み中..." />
        <DashboardSkeleton />
      </div>
    );
  }

  return (
    <div className="page-container dashboard-page">
      <PageHeader
        title="進捗概要"
        description="開発の進捗と最近の活動を一覧できます。"
        action={
          <button className="dashboard-cta" onClick={() => navigate('/projects/new')}>
            <LuPlus size={16} />
            新規プロジェクト
          </button>
        }
      />

      {data && (
        <>
          <section className="dashboard-stats">
            <div className="stat-card">
              <div className="stat-icon">
                <LuFolderKanban size={20} />
              </div>
              <div className="stat-label">プロジェクト数</div>
              <div className="stat-value">{data.stats.total_projects}</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">
                <LuBookOpen size={20} />
              </div>
              <div className="stat-label">ドキュメント</div>
              <div className="stat-value">{data.stats.total_devlog_entries}</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">
                <LuNotebook size={20} />
              </div>
              <div className="stat-label">ノートブック</div>
              <div className="stat-value">{data.stats.total_notebooks}</div>
            </div>
            <button
              type="button"
              className={`stat-card stat-card--mcp ${data.stats.has_mcp_tokens ? '' : 'stat-card--unconfigured'}`}
              onClick={() => navigate('/setup')}
            >
              <div className="stat-icon">
                <LuCable size={20} />
              </div>
              <div className="stat-label">MCP接続</div>
              <div className="stat-value stat-value--status">
                <span
                  className={`stat-status-dot ${data.stats.has_mcp_tokens ? 'stat-status-dot--active' : 'stat-status-dot--inactive'}`}
                />
                {data.stats.has_mcp_tokens ? '接続済み' : '未設定'}
              </div>
            </button>
          </section>

          {!mcpBannerDismissed && !data.stats.has_mcp_tokens && (
            <section className="mcp-cta-banner fadeInUp">
              <button
                type="button"
                className="mcp-cta-banner-dismiss"
                onClick={dismissMcpBanner}
                aria-label="閉じる"
              >
                <LuX size={16} />
              </button>
              <div className="mcp-cta-banner-content">
                <div className="mcp-cta-banner-icon">
                  <LuCable size={22} />
                </div>
                <div className="mcp-cta-banner-text">
                  <strong>MCPを接続して開発ログを自動記録</strong>
                  <p>Claude Code と連携すると、開発中の活動がポートフォリオに自動で記録されます。</p>
                </div>
                <Link to="/setup" className="mcp-cta-banner-action">
                  セットアップする
                </Link>
              </div>
            </section>
          )}

          <section className="dashboard-section">
            <div className="section-header">
              <h2>最近のプロジェクト</h2>
            </div>
            {data.recent_projects.length === 0 ? (
              <EmptyState
                icon={LuFolderKanban}
                title="まだプロジェクトがありません"
                description="最初のプロジェクトを作成してドキュメントを残しましょう。"
                action={{
                  label: '新規プロジェクトを作成',
                  onClick: () => navigate('/projects/new'),
                }}
              />
            ) : (
              <div className="project-grid">
                {data.recent_projects.map((project) => (
                  <button
                    key={project.id}
                    className="project-card"
                    onClick={() => navigate(`/projects/${project.id}`)}
                  >
                    <div className="project-card-header">
                      <h3>{project.title}</h3>
                      <span className={`status-badge ${project.status}`}>
                        {project.status === 'completed'
                          ? '完了'
                          : project.status === 'archived'
                          ? '保管'
                          : '進行中'}
                      </span>
                    </div>
                    <div className="project-meta">
                      <span>記録 {project.devlog_count}件</span>
                    </div>
                    <div className="project-tech">
                      {project.technologies.slice(0, 3).map((tech) => (
                        <span key={tech} className="tech-pill">
                          {tech}
                        </span>
                      ))}
                    </div>
                    <div className="project-updated">
                      更新日: {new Date(project.updated_at).toLocaleDateString('ja-JP')}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
};
