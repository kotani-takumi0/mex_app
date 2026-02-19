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

const getCategoryLabel = (
  category: PublicProjectDetail['devlog'][number]['category']
): string => {
  switch (category) {
    case 'tutorial':
      return 'チュートリアル';
    case 'design':
      return '設計';
    case 'debug_guide':
      return 'デバッグガイド';
    case 'learning':
      return '学習ノート';
    case 'reference':
      return 'リファレンス';
    default:
      return 'リファレンス';
  }
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

  const { project, devlog } = detail;

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
        <h2>ドキュメント</h2>
        {devlog.length === 0 ? (
          <div className="public-detail-empty">ドキュメントがまだありません。</div>
        ) : (
          <div className="public-devlog-list">
            {devlog.map((entry, index) => (
              <div key={`${entry.title}-${index}`} className="public-devlog-card">
                <div className="public-devlog-header">
                  <span>{getCategoryLabel(entry.category)}</span>
                  <span>{new Date(entry.created_at).toLocaleDateString('ja-JP')}</span>
                </div>
                <p>{entry.title}</p>
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
    </div>
  );
};
