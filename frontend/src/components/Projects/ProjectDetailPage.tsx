/**
 * プロジェクト詳細ページ
 */
import React, { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  LuCheck,
  LuExternalLink,
  LuLoader,
  LuPlus,
  LuSquarePen,
  LuSparkles,
  LuTag,
  LuTrash2,
  LuX,
} from 'react-icons/lu';
import { getProject, updateProject } from '../../api/projects';
import {
  createDocument,
  deleteDocument,
  getDocuments,
  updateDocument,
} from '../../api/devlogs';
import { Project, TechDocument } from '../../types';
import { PageHeader } from '../common/PageHeader';
import { EmptyState } from '../common/EmptyState';
import './ProjectDetailPage.css';

const categoryOptions = [
  { value: 'tutorial', label: 'チュートリアル' },
  { value: 'design', label: '設計' },
  { value: 'debug_guide', label: 'デバッグガイド' },
  { value: 'learning', label: '学習ノート' },
  { value: 'reference', label: 'リファレンス' },
] as const;

type CategoryValue = (typeof categoryOptions)[number]['value'];

const parseTechnologies = (value: string): string[] =>
  value
    .split(',')
    .map((tech) => tech.trim())
    .filter((tech) => tech.length > 0);

const getCategoryLabel = (category: TechDocument['category']): string =>
  categoryOptions.find((option) => option.value === category)?.label || category;

const getCategoryClassName = (category: TechDocument['category']): string => {
  switch (category) {
    case 'tutorial':
      return 'doc-category-tutorial';
    case 'design':
      return 'doc-category-design';
    case 'debug_guide':
      return 'doc-category-debug';
    case 'learning':
      return 'doc-category-learning';
    case 'reference':
      return 'doc-category-reference';
    default:
      return 'doc-category-reference';
  }
};

export const ProjectDetailPage: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [documents, setDocuments] = useState<TechDocument[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);

  const [category, setCategory] = useState<CategoryValue>('learning');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [technologies, setTechnologies] = useState('');
  const [sourceUrl, setSourceUrl] = useState('');

  const [selectedDocument, setSelectedDocument] = useState<TechDocument | null>(null);
  const [isUpdatingDocument, setIsUpdatingDocument] = useState(false);
  const [isDeletingDocument, setIsDeletingDocument] = useState(false);
  const [editCategory, setEditCategory] = useState<CategoryValue>('learning');
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');
  const [editTechnologies, setEditTechnologies] = useState('');
  const [editSourceUrl, setEditSourceUrl] = useState('');

  const projectId = id || '';

  const techTags = useMemo(() => parseTechnologies(technologies), [technologies]);

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

      const documentResult = await getDocuments(projectId);
      if (documentResult.error) {
        toast.error(documentResult.error);
      } else {
        setDocuments(documentResult.data?.entries || []);
      }
      setIsLoading(false);
    };

    fetchData();
  }, [projectId]);

  const handleCreateDocument = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId) return;

    const trimmedTitle = title.trim();
    if (!trimmedTitle) {
      toast.error('タイトルを入力してください');
      return;
    }

    setIsSubmitting(true);
    const { data, error } = await createDocument(projectId, {
      category,
      title: trimmedTitle,
      content: content.trim() || undefined,
      technologies: techTags,
      source_url: sourceUrl,
      source: 'manual',
    });

    if (error) {
      toast.error(error);
    } else if (data) {
      toast.success('ドキュメントを追加しました');
      setDocuments((prev) => [data, ...prev]);
      setProject((prev) => (prev ? { ...prev, devlog_count: prev.devlog_count + 1 } : prev));
      setTitle('');
      setContent('');
      setTechnologies('');
      setSourceUrl('');
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

  const handleOpenEditModal = (document: TechDocument) => {
    setSelectedDocument(document);
    setEditCategory(document.category);
    setEditTitle(document.title);
    setEditContent(document.content || '');
    setEditTechnologies(document.technologies.join(', '));
    setEditSourceUrl(document.source_url || '');
  };

  const handleCloseEditModal = () => {
    if (isUpdatingDocument || isDeletingDocument) {
      return;
    }
    setSelectedDocument(null);
  };

  const handleUpdateSelectedDocument = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDocument) return;

    const trimmedTitle = editTitle.trim();
    if (!trimmedTitle) {
      toast.error('タイトルを入力してください');
      return;
    }

    setIsUpdatingDocument(true);
    const { data, error } = await updateDocument(selectedDocument.id, {
      category: editCategory,
      title: trimmedTitle,
      content: editContent.trim() || undefined,
      technologies: parseTechnologies(editTechnologies),
      source_url: editSourceUrl,
      metadata: selectedDocument.metadata,
    });

    if (error) {
      toast.error(error);
    } else if (data) {
      toast.success('ドキュメントを更新しました');
      setDocuments((prev) => prev.map((entry) => (entry.id === data.id ? data : entry)));
      setSelectedDocument(null);
    }
    setIsUpdatingDocument(false);
  };

  const handleDeleteSelectedDocument = async () => {
    if (!selectedDocument) return;
    if (!window.confirm('このドキュメントを削除しますか？')) {
      return;
    }

    setIsDeletingDocument(true);
    const { error } = await deleteDocument(selectedDocument.id);
    if (error) {
      toast.error(error);
    } else {
      toast.success('ドキュメントを削除しました');
      setDocuments((prev) => prev.filter((entry) => entry.id !== selectedDocument.id));
      setProject((prev) =>
        prev ? { ...prev, devlog_count: Math.max(prev.devlog_count - 1, 0) } : prev
      );
      setSelectedDocument(null);
    }
    setIsDeletingDocument(false);
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
          <div className="header-actions">
            <Link to={`/projects/${project.id}/edit`} className="edit-link">
              <LuSquarePen size={16} />
              編集
            </Link>
            <Link to={`/projects/${project.id}/quiz`} className="quiz-link">
              <LuSparkles size={16} />
              理解度チェック
            </Link>
          </div>
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
              {isToggling ? (
                <LuLoader size={14} />
              ) : project.is_public ? (
                <LuCheck size={14} />
              ) : (
                <LuPlus size={14} />
              )}
              {project.is_public ? '公開中' : '非公開'}
            </button>
          </div>
          <div className="summary-row">
            <span className="summary-label">ドキュメント</span>
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
          <h2>ドキュメント</h2>
        </div>

        {documents.length === 0 ? (
          <EmptyState
            icon={LuSparkles}
            title="ドキュメントがまだありません"
            description="下のフォームから最初のドキュメントを追加しましょう。"
          />
        ) : (
          <div className="devlog-list">
            {documents.map((document) => (
              <div
                key={document.id}
                className="devlog-card devlog-card--clickable"
                role="button"
                tabIndex={0}
                onClick={() => handleOpenEditModal(document)}
                onKeyDown={(event) => {
                  if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    handleOpenEditModal(document);
                  }
                }}
              >
                <div className="devlog-header">
                  <div className="devlog-header-main">
                    <span className={`devlog-type ${getCategoryClassName(document.category)}`}>
                      {getCategoryLabel(document.category)}
                    </span>
                  </div>
                  <span className="devlog-date">
                    {new Date(document.created_at).toLocaleString('ja-JP')}
                  </span>
                </div>
                <p className="devlog-summary">{document.title}</p>
                <p className="devlog-detail">
                  {document.content?.trim() || 'Notionを読んで学んだことを書こう'}
                </p>
                <div className="devlog-tech">
                  {document.technologies.map((tech) => (
                    <span key={tech} className="tech-pill">
                      {tech}
                    </span>
                  ))}
                </div>
                {document.source_url && (
                  <div className="document-source-link-wrap">
                    <a
                      className="document-source-link"
                      href={document.source_url}
                      target="_blank"
                      rel="noreferrer"
                      onClick={(event) => event.stopPropagation()}
                    >
                      <LuExternalLink size={14} />
                      {document.source_url}
                    </a>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="devlog-form-section">
        <div className="section-header">
          <h2>ドキュメントを追加</h2>
        </div>
        <form className="devlog-form" onSubmit={handleCreateDocument}>
          <div className="form-group">
            <label htmlFor="category">カテゴリ</label>
            <select
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value as CategoryValue)}
            >
              {categoryOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="title">タイトル</label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="例: React Routerの導入手順"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="content">学んだこと</label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Notionドキュメントを読んで、学んだことを自分の言葉で書こう"
              rows={5}
            />
          </div>
          <div className="form-group">
            <label htmlFor="sourceUrl">Source URL（任意）</label>
            <input
              id="sourceUrl"
              type="url"
              value={sourceUrl}
              onChange={(e) => setSourceUrl(e.target.value)}
              placeholder="https://example.com/doc"
            />
          </div>
          <div className="form-group">
            <label htmlFor="technologies">使用技術（カンマ区切り）</label>
            <input
              id="technologies"
              type="text"
              value={technologies}
              onChange={(e) => setTechnologies(e.target.value)}
              placeholder="React, TypeScript"
            />
          </div>
          <button type="submit" className="submit-btn" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <LuLoader className="submit-btn-icon" size={18} />
                追加中...
              </>
            ) : (
              'ドキュメントを追加'
            )}
          </button>
        </form>
      </section>

      {selectedDocument && (
        <div className="devlog-modal-overlay" onClick={handleCloseEditModal}>
          <div className="devlog-modal" onClick={(event) => event.stopPropagation()}>
            <div className="devlog-modal-header">
              <h3>ドキュメントを編集</h3>
              <button
                type="button"
                className="modal-icon-btn"
                onClick={handleCloseEditModal}
                disabled={isUpdatingDocument || isDeletingDocument}
                aria-label="モーダルを閉じる"
              >
                <LuX size={18} />
              </button>
            </div>
            <form className="devlog-form devlog-edit-form" onSubmit={handleUpdateSelectedDocument}>
              <div className="form-group">
                <label htmlFor="editCategory">カテゴリ</label>
                <select
                  id="editCategory"
                  value={editCategory}
                  onChange={(e) => setEditCategory(e.target.value as CategoryValue)}
                  disabled={isUpdatingDocument || isDeletingDocument}
                >
                  {categoryOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="editTitle">タイトル</label>
                <input
                  id="editTitle"
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  disabled={isUpdatingDocument || isDeletingDocument}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="editContent">学んだこと</label>
                <textarea
                  id="editContent"
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  rows={6}
                  disabled={isUpdatingDocument || isDeletingDocument}
                />
              </div>
              <div className="form-group">
                <label htmlFor="editSourceUrl">Source URL（任意）</label>
                <input
                  id="editSourceUrl"
                  type="url"
                  value={editSourceUrl}
                  onChange={(e) => setEditSourceUrl(e.target.value)}
                  placeholder="https://example.com/doc"
                  disabled={isUpdatingDocument || isDeletingDocument}
                />
              </div>
              <div className="form-group">
                <label htmlFor="editTechnologies">使用技術（カンマ区切り）</label>
                <input
                  id="editTechnologies"
                  type="text"
                  value={editTechnologies}
                  onChange={(e) => setEditTechnologies(e.target.value)}
                  disabled={isUpdatingDocument || isDeletingDocument}
                />
              </div>

              <div className="devlog-modal-actions">
                <button type="submit" className="submit-btn" disabled={isUpdatingDocument || isDeletingDocument}>
                  {isUpdatingDocument ? (
                    <>
                      <LuLoader className="submit-btn-icon" size={16} />
                      保存中...
                    </>
                  ) : (
                    '保存'
                  )}
                </button>
                <button
                  type="button"
                  className="delete-btn"
                  onClick={handleDeleteSelectedDocument}
                  disabled={isUpdatingDocument || isDeletingDocument}
                >
                  {isDeletingDocument ? (
                    <>
                      <LuLoader className="submit-btn-icon" size={16} />
                      削除中...
                    </>
                  ) : (
                    <>
                      <LuTrash2 size={16} />
                      削除
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
