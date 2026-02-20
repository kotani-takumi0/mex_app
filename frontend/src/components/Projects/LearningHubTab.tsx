/**
 * 学習ハブタブ
 * NotebookLM連携のノートブック一覧を表示。
 * 学習コンテンツがない場合は /learn コマンドの実行ガイドを表示。
 */
import React from 'react';
import { LuExternalLink, LuNotebook } from 'react-icons/lu';
import { TechDocument, NotebookInfo } from '../../types';
import { EmptyState } from '../common/EmptyState';

interface LearningHubTabProps {
  readonly notebookEntries: TechDocument[];
}

const learningTypeLabel = (type: string): string => {
  switch (type) {
    case 'flashcard': return 'フラッシュカード';
    case 'audio': return '音声ポッドキャスト';
    case 'summary': return '要約';
    case 'full': return 'フルセット';
    default: return type;
  }
};

export const LearningHubTab: React.FC<LearningHubTabProps> = ({ notebookEntries }) => {
  if (notebookEntries.length === 0) {
    return (
      <EmptyState
        icon={LuNotebook}
        title="ノートブックがまだありません"
        description="Claude Code で /learn コマンドを実行すると、NotebookLM の学習コンテンツが自動生成されます。"
      />
    );
  }

  return (
    <div className="notebook-list">
      {notebookEntries.map((entry) => {
        const meta = entry.metadata as unknown as NotebookInfo;
        return (
          <div key={entry.id} className="notebook-card">
            <div className="notebook-header">
              <h3>{entry.title}</h3>
              <span className="notebook-type">
                {learningTypeLabel(meta.learning_type || 'full')}
              </span>
            </div>
            <div className="devlog-tech">
              {entry.technologies.map((tech) => (
                <span key={tech} className="tech-pill">{tech}</span>
              ))}
            </div>
            <div className="notebook-links">
              {meta.notebook_url && (
                <a
                  href={meta.notebook_url}
                  target="_blank"
                  rel="noreferrer"
                  className="notebook-link"
                >
                  <LuExternalLink size={14} />
                  NotebookLMで開く
                </a>
              )}
              {meta.public_url && (
                <a
                  href={meta.public_url}
                  target="_blank"
                  rel="noreferrer"
                  className="notebook-link notebook-link--public"
                >
                  <LuExternalLink size={14} />
                  公開リンク
                </a>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
