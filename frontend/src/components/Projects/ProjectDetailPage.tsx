/**
 * プロジェクト詳細ページ
 */
import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  LuArrowRight,
  LuCheck,
  LuLoader,
  LuPlus,
  LuSparkles,
  LuTag,
} from 'react-icons/lu';
import { getProject, updateProject } from '../../api/projects';
import { getDevLogs, createDevLog } from '../../api/devlogs';
import { DevLogEntry, Project } from '../../types';
import { PageHeader } from '../common/PageHeader';
import { EmptyState } from '../common/EmptyState';
import './ProjectDetailPage.css';

const entryTypeOptions = [
  { value: 'code_generation', label: 'コード生成' },
  { value: 'debug', label: 'デバッグ' },
  { value: 'design_decision', label: '設計判断' },
  { value: 'learning', label: '学び' },
  { value: 'error_resolution', label: 'エラー解決' },
];

export const ProjectDetailPage: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [devlogs, setDevlogs] = useState<DevLogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);

  const [entryType, setEntryType] = useState('learning');
  const [summary, setSummary] = useState('');
  const [detail, setDetail] = useState('');
  const [technologies, setTechnologies] = useState('');

  const projectId = id || '';

  const techTags = useMemo(() =>
    technologies
      .split(',')
      .map((tech) => tech.trim())
      .filter((tech) => tech.length > 0),
    [technologies]
  );

  useEffect(() => {
    const fetchData = async () => {
      if (!projectId) return;
      setIsLoading(true);
      const projectResult = await getProject(projectId);
      if (projectResult.error) {
        toast.error(projectResult.error);
        setIsLoading(false);
        return;
      }
      setProject(projectResult.data || null);

      const devlogResult = await getDevLogs(projectId);
      if (devlogResult.error) {
        toast.error(devlogResult.error);
      } else {
        setDevlogs(devlogResult.data?.entries || []);
      }
      setIsLoading(false);
    };

    fetchData();
  }, [projectId]);

  const handleCreateDevlog = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId) return;

    setIsSubmitting(true);
    const { data, error } = await createDevLog(projectId, {
      entry_type: entryType,
      summary,
      detail: detail || undefined,
      technologies: techTags,
      source: 'manual',
    });

    if (error) {
      toast.error(error);
    } else if (data) {
      toast.success('開発ログを追加しました');
      setDevlogs((prev) => [data, ...prev]);
      setProject((prev) => (prev ? { ...prev, devlog_count: prev.devlog_count + 1 } : prev));
      setSummary('');
      setDetail('');
      setTechnologies('');
    }
    setIsSubmitting(false);
  };

  const togglePublic = async () => {
    if (!project) return;
    setIsToggling(true);
    const { data, error } = await updateProject(project.id, {
      is_public: !project.is_public,
    });
    if (error) {
      toast.error(error);
    } else if (data) {
      setProject(data);
      toast.success(data.is_public ? '公開に設定しました' : '非公開に設定しました');
    }
    setIsToggling(false);
  };

  if (isLoading) {
    return (
      <div className="page-container">
        <PageHeader title="プロジェクト" description="読み込み中..." />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="page-container">
        <EmptyState
          icon={LuSparkles}
          title="プロジェクトが見つかりません"
          description="プロジェクト一覧から選択してください。"
          action={{
            label: 'ダッシュボードへ戻る',
            onClick: () => navigate('/dashboard'),
          }}
        />
      </div>
    );
  }

  return (
    <div className="page-container">
      <PageHeader
        title={project.title}
        description={project.description || 'プロジェクト概要を追加してください。'}
        action={
          <button className="quiz-link" onClick={() => navigate(`/projects/${project.id}/quiz`)}>
            クイズに挑戦
            <LuArrowRight size={16} />
          </button>
        }
      />

      <section className="project-summary">
        <div className="summary-card">
          <div className="summary-row">
            <span className="summary-label">ステータス</span>
            <span className={`status-badge ${project.status}`}>
              {project.status === 'completed'
                ? '完了'
                : project.status === 'archived'
                ? '保管'
                : '進行中'}
            </span>
          </div>
          <div className="summary-row">
            <span className="summary-label">公開設定</span>
            <button className="toggle-public" onClick={togglePublic} disabled={isToggling}>
              {isToggling ? <LuLoader size={14} /> : project.is_public ? <LuCheck size={14} /> : <LuPlus size={14} />}
              {project.is_public ? '公開中' : '非公開'}
            </button>
          </div>
          <div className="summary-row">
            <span className="summary-label">開発ログ</span>
            <span>{project.devlog_count}件</span>
          </div>
          <div className="summary-row">
            <span className="summary-label">クイズスコア</span>
            <span>{project.quiz_score === null ? '未実施' : `${project.quiz_score}%`}</span>
          </div>
        </div>

        <div className="summary-card">
          <div className="summary-row">
            <span className="summary-label">リポジトリ</span>
            {project.repository_url ? (
              <a href={project.repository_url} target="_blank" rel="noreferrer">
                {project.repository_url}
              </a>
            ) : (
              <span>未登録</span>
            )}
          </div>
          <div className="summary-row">
            <span className="summary-label">デモ</span>
            {project.demo_url ? (
              <a href={project.demo_url} target="_blank" rel="noreferrer">
                {project.demo_url}
              </a>
            ) : (
              <span>未登録</span>
            )}
          </div>
          <div className="summary-row">
            <span className="summary-label">技術</span>
            <div className="summary-tech">
              {project.technologies.length === 0 && <span>未登録</span>}
              {project.technologies.map((tech) => (
                <span key={tech} className="tech-pill">
                  <LuTag size={12} />
                  {tech}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="devlog-section">
        <div className="section-header">
          <h2>開発ログ</h2>
        </div>

        {devlogs.length === 0 ? (
          <EmptyState
            icon={LuSparkles}
            title="開発ログがまだありません"
            description="下のフォームから最初のログを追加しましょう。"
          />
        ) : (
          <div className="devlog-list">
            {devlogs.map((entry) => (
              <div key={entry.id} className="devlog-card">
                <div className="devlog-header">
                  <span className="devlog-type">{entry.entry_type}</span>
                  <span className="devlog-date">
                    {new Date(entry.created_at).toLocaleString('ja-JP')}
                  </span>
                </div>
                <p className="devlog-summary">{entry.summary}</p>
                {entry.detail && <p className="devlog-detail">{entry.detail}</p>}
                <div className="devlog-tech">
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

      <section className="devlog-form-section">
        <div className="section-header">
          <h2>手動でログを追加</h2>
        </div>
        <form className="devlog-form" onSubmit={handleCreateDevlog}>
          <div className="form-group">
            <label htmlFor="entryType">作業種別</label>
            <select id="entryType" value={entryType} onChange={(e) => setEntryType(e.target.value)}>
              {entryTypeOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="summary">要約</label>
            <input
              id="summary"
              type="text"
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              placeholder="例: React RouterでSPA遷移を実装"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="detail">詳細</label>
            <textarea
              id="detail"
              value={detail}
              onChange={(e) => setDetail(e.target.value)}
              placeholder="具体的な実装や学びを記録"
              rows={3}
            />
          </div>
          <div className="form-group">
            <label htmlFor="technologies">使用技術（カンマ区切り）</label>
            <input
              id="technologies"
              type="text"
              value={technologies}
              onChange={(e) => setTechnologies(e.target.value)}
              placeholder="React Router, TypeScript"
            />
          </div>
          <button type="submit" className="submit-btn" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <LuLoader className="submit-btn-icon" size={18} />
                追加中...
              </>
            ) : (
              '開発ログを追加'
            )}
          </button>
        </form>
      </section>
    </div>
  );
};
