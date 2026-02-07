/**
 * プロジェクト新規作成ページ
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { LuLoader } from 'react-icons/lu';
import { createProject } from '../../api/projects';
import { PageHeader } from '../common/PageHeader';
import './ProjectFormPage.css';

const statusOptions = [
  { value: 'in_progress', label: '進行中' },
  { value: 'completed', label: '完了' },
  { value: 'archived', label: '保管' },
];

export const ProjectFormPage: React.FC = () => {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [technologies, setTechnologies] = useState('');
  const [repositoryUrl, setRepositoryUrl] = useState('');
  const [demoUrl, setDemoUrl] = useState('');
  const [status, setStatus] = useState('in_progress');
  const [isPublic, setIsPublic] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    const techList = technologies
      .split(',')
      .map((tech) => tech.trim())
      .filter((tech) => tech.length > 0);

    const { data, error } = await createProject({
      title,
      description: description || undefined,
      technologies: techList.length ? techList : undefined,
      repository_url: repositoryUrl || undefined,
      demo_url: demoUrl || undefined,
      status,
      is_public: isPublic,
    });

    if (error) {
      toast.error(error);
    } else if (data) {
      toast.success('プロジェクトを作成しました');
      navigate(`/projects/${data.id}`);
    }

    setIsSubmitting(false);
  };

  return (
    <div className="page-container">
      <PageHeader
        title="新規プロジェクト"
        description="ポートフォリオに追加するプロジェクトを登録します。"
      />

      <form className="project-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="title">プロジェクト名</label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="例: 面接練習AIアプリ"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">概要</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="プロジェクトの目的や特徴を簡単にまとめてください"
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
            placeholder="React, TypeScript, FastAPI"
          />
        </div>

        <div className="form-group">
          <label htmlFor="repositoryUrl">GitHubリポジトリURL</label>
          <input
            id="repositoryUrl"
            type="url"
            value={repositoryUrl}
            onChange={(e) => setRepositoryUrl(e.target.value)}
            placeholder="https://github.com/user/project"
          />
        </div>

        <div className="form-group">
          <label htmlFor="demoUrl">デモURL</label>
          <input
            id="demoUrl"
            type="url"
            value={demoUrl}
            onChange={(e) => setDemoUrl(e.target.value)}
            placeholder="https://project.example.com"
          />
        </div>

        <div className="form-group">
          <label htmlFor="status">ステータス</label>
          <select id="status" value={status} onChange={(e) => setStatus(e.target.value)}>
            {statusOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group checkbox">
          <label htmlFor="isPublic">公開ポートフォリオに表示する</label>
          <input
            id="isPublic"
            type="checkbox"
            checked={isPublic}
            onChange={(e) => setIsPublic(e.target.checked)}
          />
        </div>

        <button type="submit" className="submit-btn" disabled={isSubmitting}>
          {isSubmitting ? (
            <>
              <LuLoader className="submit-btn-icon" size={18} />
              作成中...
            </>
          ) : (
            'プロジェクトを作成'
          )}
        </button>
      </form>
    </div>
  );
};
