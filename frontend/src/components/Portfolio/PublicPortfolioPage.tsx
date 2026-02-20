/**
 * 公開ポートフォリオページ
 *
 * 面接官が閲覧するページ。Editorial/magazine 調のデザインで
 * 開発者の技術的な深みを伝える。
 *
 * 改善点:
 * - イニシャルアバター + 統計バーで第一印象を強化
 * - 技術スタック全体を可視化
 * - プロジェクトカードを情報リッチに（説明文、カテゴリ分布）
 * - パンくず的なナビゲーション
 */
import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { LuGithub, LuFolderKanban, LuArrowRight, LuFileText, LuTag } from 'react-icons/lu';
import { getPublicPortfolio } from '../../api/portfolio';
import { PublicPortfolio, Project } from '../../types';
import { EmptyState } from '../common/EmptyState';
import './PublicPortfolioPage.css';

const getInitials = (name: string): string => {
  const parts = name.trim().split(/\s+/);
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return name.slice(0, 2).toUpperCase();
};

const getStatusLabel = (status: Project['status']): string => {
  switch (status) {
    case 'completed': return '完了';
    case 'archived': return '保管';
    default: return '進行中';
  }
};

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
          document.title = `${data.user.display_name} — MEX App`;
        }
      }
    };
    fetchPortfolio();
    return () => { document.title = 'MEX App — AI時代の技術ポートフォリオ'; };
  }, [username]);

  const allTechnologies = useMemo(() => {
    if (!portfolio) return [];
    const techMap = new Map<string, number>();
    for (const project of portfolio.projects) {
      for (const tech of project.technologies) {
        techMap.set(tech, (techMap.get(tech) || 0) + 1);
      }
    }
    return Array.from(techMap.entries())
      .sort((a, b) => b[1] - a[1])
      .map(([tech]) => tech);
  }, [portfolio]);

  const totalDocuments = useMemo(
    () => portfolio?.projects.reduce((sum, p) => sum + p.devlog_count, 0) || 0,
    [portfolio]
  );

  if (!portfolio) {
    return (
      <div className="portfolio-page">
        <EmptyState
          icon={LuFolderKanban}
          title="ポートフォリオが見つかりません"
          description="ユーザー名を確認してください。"
        />
      </div>
    );
  }

  return (
    <div className="portfolio-page">
      <header className="portfolio-hero">
        <div className="portfolio-hero-content">
          <div className="portfolio-avatar">
            {getInitials(portfolio.user.display_name)}
          </div>
          <div className="portfolio-identity">
            <h1 className="portfolio-name">{portfolio.user.display_name}</h1>
            {portfolio.user.bio && (
              <p className="portfolio-bio">{portfolio.user.bio}</p>
            )}
            <div className="portfolio-links">
              {portfolio.user.github_url && (
                <a
                  href={portfolio.user.github_url}
                  target="_blank"
                  rel="noreferrer"
                  className="portfolio-github"
                >
                  <LuGithub size={16} />
                  GitHub
                </a>
              )}
            </div>
          </div>
        </div>

        <div className="portfolio-stats">
          <div className="portfolio-stat">
            <span className="portfolio-stat-value">{portfolio.projects.length}</span>
            <span className="portfolio-stat-label">プロジェクト</span>
          </div>
          <div className="portfolio-stat-divider" />
          <div className="portfolio-stat">
            <span className="portfolio-stat-value">{totalDocuments}</span>
            <span className="portfolio-stat-label">ドキュメント</span>
          </div>
          <div className="portfolio-stat-divider" />
          <div className="portfolio-stat">
            <span className="portfolio-stat-value">{allTechnologies.length}</span>
            <span className="portfolio-stat-label">技術</span>
          </div>
        </div>
      </header>

      {allTechnologies.length > 0 && (
        <section className="portfolio-tech-section">
          <h2 className="portfolio-section-label">技術スタック</h2>
          <div className="portfolio-tech-cloud">
            {allTechnologies.map((tech) => (
              <span key={tech} className="portfolio-tech-pill">
                <LuTag size={10} />
                {tech}
              </span>
            ))}
          </div>
        </section>
      )}

      <section className="portfolio-projects-section">
        <h2 className="portfolio-section-label">プロジェクト</h2>
        {portfolio.projects.length === 0 ? (
          <EmptyState
            icon={LuFolderKanban}
            title="公開プロジェクトがありません"
            description="公開設定されたプロジェクトが表示されます。"
          />
        ) : (
          <div className="portfolio-project-grid">
            {portfolio.projects.map((project) => (
              <button
                key={project.id}
                className="portfolio-project-card"
                onClick={() => navigate(`/p/${username}/${project.id}`)}
              >
                <div className="portfolio-card-top">
                  <span className={`portfolio-status portfolio-status--${project.status}`}>
                    {getStatusLabel(project.status)}
                  </span>
                  <LuArrowRight size={14} className="portfolio-card-arrow" />
                </div>
                <h3 className="portfolio-card-title">{project.title}</h3>
                {project.description && (
                  <p className="portfolio-card-desc">{project.description}</p>
                )}
                <div className="portfolio-card-footer">
                  <span className="portfolio-card-docs">
                    <LuFileText size={13} />
                    {project.devlog_count}件
                  </span>
                  <div className="portfolio-card-tech">
                    {project.technologies.slice(0, 3).map((tech) => (
                      <span key={tech} className="portfolio-card-tech-pill">{tech}</span>
                    ))}
                    {project.technologies.length > 3 && (
                      <span className="portfolio-card-tech-more">
                        +{project.technologies.length - 3}
                      </span>
                    )}
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </section>

      <footer className="portfolio-footer">
        <div className="portfolio-footer-brand">MEX</div>
        <p className="portfolio-footer-text">
          AI時代の技術ポートフォリオ
        </p>
        <button className="portfolio-footer-cta" onClick={() => navigate('/auth')}>
          あなたもポートフォリオを作る
          <LuArrowRight size={14} />
        </button>
      </footer>
    </div>
  );
};
