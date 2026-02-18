/**
 * 公開ポートフォリオページ
 */
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { LuGithub, LuFolderKanban, LuArrowRight } from 'react-icons/lu';
import { getPublicPortfolio } from '../../api/portfolio';
import { PublicPortfolio } from '../../types';
import { EmptyState } from '../common/EmptyState';
import './PublicPortfolioPage.css';

export const PublicPortfolioPage: React.FC = () => {
  const { username } = useParams();
  const navigate = useNavigate();
  const [portfolio, setPortfolio] = useState<PublicPortfolio | null>(null);

  useEffect(() => {
    const fetchPortfolio = async () => {
      if (!username) return;
      const { data, error } = await getPublicPortfolio(username);
      if (error) {
        toast.error(error);
      } else {
        setPortfolio(data);
        if (data) {
          document.title = `${data.user.display_name} のポートフォリオ — MEX App`;
        }
      }
    };
    fetchPortfolio();
    return () => { document.title = 'MEX App — AI時代の技術ポートフォリオ'; };
  }, [username]);

  if (!portfolio) {
    return (
      <div className="public-page">
        <EmptyState
          icon={LuFolderKanban}
          title="ポートフォリオが見つかりません"
          description="ユーザー名を確認してください。"
        />
      </div>
    );
  }

  return (
    <div className="public-page">
      <header className="public-header">
        <div>
          <h1>{portfolio.user.display_name}</h1>
          <p>{portfolio.user.bio || '自己紹介がまだありません。'}</p>
        </div>
        {portfolio.user.github_url && (
          <a href={portfolio.user.github_url} target="_blank" rel="noreferrer" className="github-link">
            <LuGithub size={18} />
            GitHub
          </a>
        )}
      </header>

      <section className="public-section">
        <h2>プロジェクト</h2>
        {portfolio.projects.length === 0 ? (
          <EmptyState
            icon={LuFolderKanban}
            title="公開プロジェクトがありません"
            description="公開設定されたプロジェクトが表示されます。"
          />
        ) : (
          <div className="public-project-grid">
            {portfolio.projects.map((project) => (
              <button
                key={project.id}
                className="public-project-card"
                onClick={() => navigate(`/p/${username}/${project.id}`)}
              >
                <div className="public-project-header">
                  <h3>{project.title}</h3>
                  <span className={`status-badge ${project.status}`}>
                    {project.status === 'completed'
                      ? '完了'
                      : project.status === 'archived'
                      ? '保管'
                      : '進行中'}
                  </span>
                </div>
                {project.description && <p>{project.description}</p>}
                <div className="public-project-meta">
                  <span>ログ {project.devlog_count}件</span>
                  <span>クイズ {project.quiz_score === null ? '未実施' : `${project.quiz_score}%`}</span>
                </div>
                <div className="public-project-tech">
                  {project.technologies.slice(0, 4).map((tech) => (
                    <span key={tech} className="tech-pill">
                      {tech}
                    </span>
                  ))}
                </div>
              </button>
            ))}
          </div>
        )}
      </section>

      <section className="public-section">
        <h2>スキルスコア</h2>
        {portfolio.skills.length === 0 ? (
          <div className="public-skill-empty">クイズ回答がまだありません。</div>
        ) : (
          <div className="public-skill-list">
            {portfolio.skills.map((skill) => (
              <div key={skill.technology} className="public-skill-card">
                <div className="public-skill-header">
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
      <footer className="public-cta-footer">
        <p>MEX App で技術ポートフォリオを作りませんか？</p>
        <button className="public-cta-button" onClick={() => navigate('/auth')}>
          無料で始める
          <LuArrowRight size={16} />
        </button>
      </footer>
    </div>
  );
};
