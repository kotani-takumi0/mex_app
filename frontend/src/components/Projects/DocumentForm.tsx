/**
 * ドキュメントフォームコンポーネント
 * 新規作成・編集の両方に対応。
 * フォーム状態をこのコンポーネント内に閉じ込めることで、
 * ProjectDetailPage の状態変数を削減する。
 */
import React, { useState } from 'react';
import { LuLoader, LuTrash2 } from 'react-icons/lu';
import { categoryOptions, CategoryValue, parseTechnologies } from '../../utils/category';
import { TechDocument, DocumentCreateRequest } from '../../types';

interface DocumentFormProps {
  /** 編集対象（指定時は編集モード、省略時は新規作成モード） */
  readonly initialDocument?: TechDocument;
  readonly onSubmit: (data: DocumentCreateRequest) => Promise<void>;
  readonly onDelete?: () => Promise<void>;
  readonly isSubmitting: boolean;
  readonly isDeleting?: boolean;
}

export const DocumentForm: React.FC<DocumentFormProps> = ({
  initialDocument,
  onSubmit,
  onDelete,
  isSubmitting,
  isDeleting = false,
}) => {
  const isEditMode = Boolean(initialDocument);
  const isBusy = isSubmitting || isDeleting;

  const [category, setCategory] = useState<CategoryValue>(
    initialDocument?.category || 'learning'
  );
  const [title, setTitle] = useState(initialDocument?.title || '');
  const [content, setContent] = useState(initialDocument?.content || '');
  const [technologies, setTechnologies] = useState(
    initialDocument?.technologies.join(', ') || ''
  );
  const [sourceUrl, setSourceUrl] = useState(initialDocument?.source_url || '');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const trimmedTitle = title.trim();
    if (!trimmedTitle) return;

    await onSubmit({
      category,
      title: trimmedTitle,
      content: content.trim() || undefined,
      technologies: parseTechnologies(technologies),
      source_url: sourceUrl.trim() || undefined,
      source: 'manual',
      metadata: initialDocument?.metadata,
    });

    if (!isEditMode) {
      setTitle('');
      setContent('');
      setTechnologies('');
      setSourceUrl('');
    }
  };

  return (
    <form className="devlog-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor={isEditMode ? 'editCategory' : 'category'}>カテゴリ</label>
        <select
          id={isEditMode ? 'editCategory' : 'category'}
          value={category}
          onChange={(e) => setCategory(e.target.value as CategoryValue)}
          disabled={isBusy}
        >
          {categoryOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
      <div className="form-group">
        <label htmlFor={isEditMode ? 'editTitle' : 'title'}>タイトル</label>
        <input
          id={isEditMode ? 'editTitle' : 'title'}
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="例: React Routerの導入手順"
          disabled={isBusy}
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor={isEditMode ? 'editContent' : 'content'}>学んだこと</label>
        <textarea
          id={isEditMode ? 'editContent' : 'content'}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Notionドキュメントを読んで、学んだことを自分の言葉で書こう"
          rows={isEditMode ? 6 : 5}
          disabled={isBusy}
        />
      </div>
      <div className="form-group">
        <label htmlFor={isEditMode ? 'editSourceUrl' : 'sourceUrl'}>
          Source URL（任意）
        </label>
        <input
          id={isEditMode ? 'editSourceUrl' : 'sourceUrl'}
          type="url"
          value={sourceUrl}
          onChange={(e) => setSourceUrl(e.target.value)}
          placeholder="https://example.com/doc"
          disabled={isBusy}
        />
      </div>
      <div className="form-group">
        <label htmlFor={isEditMode ? 'editTechnologies' : 'technologies'}>
          使用技術（カンマ区切り）
        </label>
        <input
          id={isEditMode ? 'editTechnologies' : 'technologies'}
          type="text"
          value={technologies}
          onChange={(e) => setTechnologies(e.target.value)}
          placeholder="React, TypeScript"
          disabled={isBusy}
        />
      </div>

      {isEditMode ? (
        <div className="devlog-modal-actions">
          <button type="submit" className="submit-btn" disabled={isBusy}>
            {isSubmitting ? (
              <>
                <LuLoader className="submit-btn-icon" size={16} />
                保存中...
              </>
            ) : (
              '保存'
            )}
          </button>
          {onDelete && (
            <button
              type="button"
              className="delete-btn"
              onClick={onDelete}
              disabled={isBusy}
            >
              {isDeleting ? (
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
          )}
        </div>
      ) : (
        <button type="submit" className="submit-btn" disabled={isBusy}>
          {isSubmitting ? (
            <>
              <LuLoader className="submit-btn-icon" size={18} />
              追加中...
            </>
          ) : (
            'ドキュメントを追加'
          )}
        </button>
      )}
    </form>
  );
};
