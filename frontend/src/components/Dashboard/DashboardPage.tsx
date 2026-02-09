/**
 * ダッシュボードページ
 * ポートフォリオ概要と最近のプロジェクト、スキルスコアを表示
 */
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  LuBookOpen,
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
            新規案件
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
              <div className="stat-label">案件数</div>
              <div className="stat-value">{data.stats.total_projects}</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">
                <LuBookOpen size={20} />
              </div>
              <div className="stat-label">開発記録</div>
              <div className="stat-value">{data.stats.total_devlog_entries}</div>
            </div>
          </section>

          <section className="dashboard-section">
            <div className="section-header">
              <h2>最近の案件</h2>
            </div>
            {data.recent_projects.length === 0 ? (
              <EmptyState
                icon={LuFolderKanban}
                title="まだ案件がありません"
                description="最初の案件を作成して開発記録を残しましょう。"
                action={{
                  label: '新規案件を作成',
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
                      <span>
                        理解度 {project.quiz_score === null ? '未実施' : `${project.quiz_score}%`}
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
              <h2>技能上位</h2>
            </div>
            {data.top_skills.length === 0 ? (
              <div className="skill-empty">設問に回答すると技能得点が表示されます。</div>
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
