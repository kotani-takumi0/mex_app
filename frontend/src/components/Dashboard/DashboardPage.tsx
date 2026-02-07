/**
 * ダッシュボードページ
 * ポートフォリオ概要と最近のプロジェクト、スキルスコアを表示
 */
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  LuLayoutDashboard,
  LuListChecks,
  LuBookOpen,
  LuSparkles,
  LuPlus,
  LuFolderKanban,
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
      <div className="page-container">
        <PageHeader title="ダッシュボード" description="読み込み中..." />
        <DashboardSkeleton />
      </div>
    );
  }

  return (
    <div className="page-container">
      <PageHeader
        title="ダッシュボード"
        description="開発の進捗と理解度をひと目で確認できます。"
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
              <div className="stat-label">開発ログ</div>
              <div className="stat-value">{data.stats.total_devlog_entries}</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">
                <LuListChecks size={20} />
              </div>
              <div className="stat-label">クイズ回答数</div>
              <div className="stat-value">{data.stats.total_quiz_answered}</div>
            </div>
            <div className="stat-card highlight">
              <div className="stat-icon">
                <LuSparkles size={20} />
              </div>
              <div className="stat-label">総合スコア</div>
              <div className="stat-value">{data.stats.overall_score.toFixed(1)}</div>
            </div>
          </section>

          <section className="dashboard-section">
            <div className="section-header">
              <h2>
                <LuLayoutDashboard size={18} />
                最近のプロジェクト
              </h2>
            </div>
            {data.recent_projects.length === 0 ? (
              <EmptyState
                icon={LuFolderKanban}
                title="まだプロジェクトがありません"
                description="最初のプロジェクトを作成して開発ログを記録しましょう。"
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
                      <span>ログ {project.devlog_count}件</span>
                      <span>
                        クイズ {project.quiz_score === null ? '未実施' : `${project.quiz_score}%`}
                      </span>
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

          <section className="dashboard-section">
            <div className="section-header">
              <h2>
                <LuSparkles size={18} />
                トップスキル
              </h2>
            </div>
            {data.top_skills.length === 0 ? (
              <div className="skill-empty">クイズに回答するとスキルスコアが表示されます。</div>
            ) : (
              <div className="skill-list">
                {data.top_skills.map((skill) => (
                  <div key={skill.technology} className="skill-card">
                    <div className="skill-header">
                      <span>{skill.technology}</span>
                      <span>{skill.score.toFixed(1)}%</span>
                    </div>
                    <div className="skill-bar">
                      <div className="skill-bar-fill" style={{ width: `${skill.score}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
};
