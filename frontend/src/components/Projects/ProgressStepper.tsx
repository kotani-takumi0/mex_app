/**
 * プロジェクト進行ステッパー
 * MEXのコアフロー「MCP記録 → 学習コンテンツ生成 → ポートフォリオ公開」を
 * 3段階で視覚化し、現在のステータスをユーザーに伝える。
 */
import React from 'react';
import { LuFileText, LuGraduationCap, LuGlobe } from 'react-icons/lu';
import './ProgressStepper.css';

interface ProgressStepperProps {
  readonly documentCount: number;
  readonly notebookCount: number;
  readonly isPublic: boolean;
}

interface Step {
  readonly icon: React.ReactNode;
  readonly label: string;
  readonly description: string;
  readonly completed: boolean;
}

export const ProgressStepper: React.FC<ProgressStepperProps> = ({
  documentCount,
  notebookCount,
  isPublic,
}) => {
  const steps: Step[] = [
    {
      icon: <LuFileText size={18} />,
      label: '開発を記録',
      description: documentCount > 0
        ? `${documentCount}件のドキュメント`
        : 'MCPまたは手動で記録',
      completed: documentCount > 0,
    },
    {
      icon: <LuGraduationCap size={18} />,
      label: '学習コンテンツ',
      description: notebookCount > 0
        ? `${notebookCount}件のノートブック`
        : '/learn で自動生成',
      completed: notebookCount > 0,
    },
    {
      icon: <LuGlobe size={18} />,
      label: 'ポートフォリオ公開',
      description: isPublic ? '公開中' : '公開設定をONに',
      completed: isPublic,
    },
  ];

  return (
    <div className="progress-stepper">
      {steps.map((step, index) => (
        <React.Fragment key={step.label}>
          <div className={`stepper-step ${step.completed ? 'stepper-step--done' : ''}`}>
            <div className="stepper-icon">{step.icon}</div>
            <div className="stepper-text">
              <span className="stepper-label">{step.label}</span>
              <span className="stepper-desc">{step.description}</span>
            </div>
          </div>
          {index < steps.length - 1 && (
            <div className={`stepper-connector ${step.completed ? 'stepper-connector--done' : ''}`} />
          )}
        </React.Fragment>
      ))}
    </div>
  );
};
