/**
 * 公開プロジェクト詳細ページ
 */
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { LuClipboardList } from 'react-icons/lu';
import { getPublicProjectDetail } from '../../api/portfolio';
import { PublicProjectDetail } from '../../types';
import { EmptyState } from '../common/EmptyState';
import './PublicProjectDetailPage.css';

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
      }
    };
    fetchDetail();
  }, [username, projectId]);

  if (!detail) {
    return (
      <div className="public-page">
        <EmptyState
          icon={LuClipboardList}
          title="プロジェクトが見つかりません"
          description="公開設定のプロジェクトのみ表示されます。"
        />
      </div>
    );
  }

  const { project, devlog, quiz_summary } = detail;

  return (
    <div className="public-page">
      <header className="public-detail-header">
        <div>
          <h1>{project.title}</h1>
          {project.description && <p>{project.description}</p>}
        </div>
        <span className={`status-badge ${project.status}`}>
          {project.status === 'completed'
            ? '完了'
            : project.status === 'archived'
            ? '保管'
            : '進行中'}
        </span>
      </header>

      <section className="public-detail-section">
        <h2>開発ログ</h2>
        {devlog.length === 0 ? (
          <div className="public-detail-empty">開発ログがまだありません。</div>
        ) : (
          <div className="public-devlog-list">
            {devlog.map((entry, index) => (
              <div key={`${entry.summary}-${index}`} className="public-devlog-card">
                <div className="public-devlog-header">
                  <span>{entry.entry_type}</span>
                  <span>{new Date(entry.created_at).toLocaleDateString('ja-JP')}</span>
                </div>
                <p>{entry.summary}</p>
                <div className="public-devlog-tech">
                  {entry.technologies.map((tech) => (
                    <span key={tech} className="tech-pill">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="public-detail-section">
        <h2>クイズスコア</h2>
        <div className="quiz-summary-card">
          <div className="quiz-summary-stat">
            <span>回答数</span>
            <strong>{quiz_summary.total_questions}</strong>
          </div>
          <div className="quiz-summary-stat">
            <span>正答数</span>
            <strong>{quiz_summary.correct_answers}</strong>
          </div>
          <div className="quiz-summary-stat">
            <span>スコア</span>
            <strong>{quiz_summary.score.toFixed(1)}%</strong>
          </div>
        </div>
        <div className="quiz-by-tech">
          {quiz_summary.by_technology.map((tech) => (
            <div key={tech.technology} className="quiz-tech-card">
              <div className="quiz-tech-header">
                <span>{tech.technology}</span>
                <span>{tech.score.toFixed(1)}%</span>
              </div>
              <div className="skill-bar">
                <div className="skill-bar-fill" style={{ width: `${tech.score}%` }} />
              </div>
              <div className="quiz-tech-meta">
                {tech.correct} / {tech.questions} 正答
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};
