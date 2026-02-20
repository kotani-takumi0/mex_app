/**
 * プロジェクト詳細ページ
 *
 * Phase 2: タブ構成 + サイドバー + ステッパー + 分布バー
 *
 * レイアウト:
 * - デスクトップ: メインコンテンツ(flex:1) + サイドバー(300px)
 * - モバイル: サイドバー → 折りたたみカード、タブは横スクロール
 *
 * タブ構成:
 * - Overview: ステッパー + カテゴリ分布 + 最近のドキュメント
 * - Documents: ドキュメント全一覧（フィルタ付き）
 * - Learning Hub: NotebookLM連携一覧
 *
 * 変更理由:
 * - 4つの責務を1ページに詰め込んでいた構造をタブで分離
 * - メタ情報をサイドバーに固定し、タブ切り替えでも常に参照可能に
 * - FAB + SlideOverPanel でフォームの発見性を改善（Phase 1で導入済み）
 */
import React, { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { LuSparkles, LuSquarePen, LuX } from 'react-icons/lu';
import { getProject, updateProject } from '../../api/projects';
import {
  createDocument,
  deleteDocument,
  getDocuments,
  updateDocument,
} from '../../api/devlogs';
import { Project, TechDocument, DocumentCreateRequest } from '../../types';
import { PageHeader } from '../common/PageHeader';
import { EmptyState } from '../common/EmptyState';
import { FloatingActionButton } from '../common/FloatingActionButton';
import { SlideOverPanel } from '../common/SlideOverPanel';
import { TabBar, TabItem } from '../common/TabBar';
import { ProjectSidebar } from './ProjectSidebar';
import { ProgressStepper } from './ProgressStepper';
import { CategoryDistribution } from './CategoryDistribution';
import { DocumentCard } from './DocumentCard';
import { DocumentForm } from './DocumentForm';
import { LearningHubTab } from './LearningHubTab';
import './ProjectDetailPage.css';

type TabKey = 'overview' | 'documents' | 'learning';

export const ProjectDetailPage: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [project, setProject] = useState<Project | null>(null);
  const [documents, setDocuments] = useState<TechDocument[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isToggling, setIsToggling] = useState(false);
  const [activeTab, setActiveTab] = useState<TabKey>('overview');

  const [isAddPanelOpen, setIsAddPanelOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [selectedDocument, setSelectedDocument] = useState<TechDocument | null>(null);
  const [isUpdatingDocument, setIsUpdatingDocument] = useState(false);
  const [isDeletingDocument, setIsDeletingDocument] = useState(false);

  const projectId = id || '';

  const notebookEntries = useMemo(
    () => documents.filter((doc) => doc.metadata?.notebook_id),
    [documents]
  );

  const tabs: TabItem[] = useMemo(() => [
    { key: 'overview', label: 'Overview' },
    { key: 'documents', label: 'ドキュメント', count: documents.length },
    { key: 'learning', label: '学習ハブ', count: notebookEntries.length },
  ], [documents.length, notebookEntries.length]);

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

  const handleCreateDocument = async (data: DocumentCreateRequest) => {
    if (!projectId) return;
    setIsSubmitting(true);
    const { data: created, error } = await createDocument(projectId, data);
    if (error) {
      toast.error(error);
    } else if (created) {
      toast.success('ドキュメントを追加しました');
      setDocuments((prev) => [created, ...prev]);
      setProject((prev) => (prev ? { ...prev, devlog_count: prev.devlog_count + 1 } : prev));
      setIsAddPanelOpen(false);
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
  };

  const handleCloseEditModal = () => {
    if (isUpdatingDocument || isDeletingDocument) return;
    setSelectedDocument(null);
  };

  const handleUpdateDocument = async (data: DocumentCreateRequest) => {
    if (!selectedDocument) return;
    setIsUpdatingDocument(true);
    const { data: updated, error } = await updateDocument(selectedDocument.id, {
      ...data,
      metadata: selectedDocument.metadata,
    });
    if (error) {
      toast.error(error);
    } else if (updated) {
      toast.success('ドキュメントを更新しました');
      setDocuments((prev) => prev.map((entry) => (entry.id === updated.id ? updated : entry)));
      setSelectedDocument(null);
    }
    setIsUpdatingDocument(false);
  };

  const handleDeleteDocument = async () => {
    if (!selectedDocument) return;
    if (!window.confirm('このドキュメントを削除しますか？')) return;
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

  const recentDocuments = documents.slice(0, 3);

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
          </div>
        }
      />

      <div className="project-layout">
        <div className="project-main">
          <TabBar
            tabs={tabs}
            activeTab={activeTab}
            onChange={(key) => setActiveTab(key as TabKey)}
          />

          {activeTab === 'overview' && (
            <div className="tab-content">
              <ProgressStepper
                documentCount={documents.length}
                notebookCount={notebookEntries.length}
                isPublic={project.is_public}
              />
              <CategoryDistribution documents={documents} />

              <div className="overview-recent">
                <h3 className="overview-section-title">最近のドキュメント</h3>
                {recentDocuments.length === 0 ? (
                  <p className="overview-empty">
                    まだドキュメントがありません。右下の「記録する」ボタンから追加しましょう。
                  </p>
                ) : (
                  <div className="devlog-list">
                    {recentDocuments.map((document) => (
                      <DocumentCard
                        key={document.id}
                        document={document}
                        onClick={handleOpenEditModal}
                      />
                    ))}
                  </div>
                )}
                {documents.length > 3 && (
                  <button
                    className="overview-show-all"
                    onClick={() => setActiveTab('documents')}
                  >
                    すべてのドキュメントを表示 ({documents.length}件)
                  </button>
                )}
              </div>
            </div>
          )}

          {activeTab === 'documents' && (
            <div className="tab-content">
              {documents.length === 0 ? (
                <EmptyState
                  icon={LuSparkles}
                  title="ドキュメントがまだありません"
                  description="右下の「記録する」ボタンから最初のドキュメントを追加しましょう。"
                />
              ) : (
                <div className="devlog-list">
                  {documents.map((document) => (
                    <DocumentCard
                      key={document.id}
                      document={document}
                      onClick={handleOpenEditModal}
                    />
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'learning' && (
            <div className="tab-content">
              <LearningHubTab notebookEntries={notebookEntries} />
            </div>
          )}
        </div>

        <ProjectSidebar
          project={project}
          documents={documents}
          isToggling={isToggling}
          onTogglePublic={togglePublic}
        />
      </div>

      <FloatingActionButton onClick={() => setIsAddPanelOpen(true)} />

      <SlideOverPanel
        isOpen={isAddPanelOpen}
        onClose={() => setIsAddPanelOpen(false)}
        title="ドキュメントを追加"
      >
        <DocumentForm
          onSubmit={handleCreateDocument}
          isSubmitting={isSubmitting}
        />
      </SlideOverPanel>

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
            <div className="devlog-edit-form">
              <DocumentForm
                key={selectedDocument.id}
                initialDocument={selectedDocument}
                onSubmit={handleUpdateDocument}
                onDelete={handleDeleteDocument}
                isSubmitting={isUpdatingDocument}
                isDeleting={isDeletingDocument}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
