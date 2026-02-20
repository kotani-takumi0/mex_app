/**
 * MCPセットアップウィザード — フルスクリーン・オンボーディング
 *
 * 変更理由: 新規登録後に「設定画面の一部」ではなく、
 * ナビゲーションなしのフルスクリーン体験として
 * 1ステップずつフォーカスするウェルカムフローを提供する。
 */
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LuArrowLeft, LuArrowRight, LuCircleCheck, LuArrowRight as LuGo } from 'react-icons/lu';
import { useSetupWizard } from '../../hooks/useSetupWizard';
import { SetupStepper } from './SetupStepper';
import { MexMcpStep } from './steps/MexMcpStep';
import { NotionMcpStep } from './steps/NotionMcpStep';
import { NotebookLmMcpStep } from './steps/NotebookLmMcpStep';
import './SetupWizardPage.css';
import './steps/SetupSteps.css';

const STEP_COMPONENTS = [MexMcpStep, NotionMcpStep, NotebookLmMcpStep] as const;

export const SetupWizardPage: React.FC = () => {
  const navigate = useNavigate();
  const wizard = useSetupWizard();
  const { currentStep, totalSteps, isAllDone, stepStatus, goNext, goBack, goToStep, markCompleted, markSkipped } = wizard;

  useEffect(() => {
    if (isAllDone) {
      localStorage.setItem('mex_mcp_banner_dismissed', 'true');
    }
  }, [isAllDone]);

  const handleFinish = () => {
    localStorage.setItem('mex_mcp_banner_dismissed', 'true');
    navigate('/dashboard');
  };

  const handleSkipAll = () => {
    localStorage.setItem('mex_mcp_banner_dismissed', 'true');
    navigate('/dashboard');
  };

  const StepComponent = STEP_COMPONENTS[currentStep];

  return (
    <div className="onboarding">
      {/* 装飾グロー */}
      <div className="onboarding-glow" aria-hidden="true" />

      {/* ヘッダー */}
      <header className="onboarding-header">
        <h1 className="onboarding-brand">MEX App</h1>
        <button type="button" className="onboarding-skip-all" onClick={handleSkipAll}>
          スキップしてダッシュボードへ
          <LuGo size={14} />
        </button>
      </header>

      {isAllDone ? (
        /* ===== 完了画面 ===== */
        <div className="onboarding-body">
          <div className="onboarding-done fadeInUp">
            <div className="onboarding-done-icon">
              <LuCircleCheck size={48} />
            </div>
            <h2>セットアップ完了!</h2>
            <p>
              すべてのMCPサーバーが設定されました。<br />
              ダッシュボードに移動して開発を始めましょう。
            </p>
            <button type="button" className="onboarding-finish-btn" onClick={handleFinish}>
              ダッシュボードへ
              <LuArrowRight size={16} />
            </button>
          </div>
        </div>
      ) : (
        /* ===== ステップ画面 ===== */
        <div className="onboarding-body">
          {/* ウェルカムメッセージ */}
          <div className="onboarding-welcome">
            <p className="onboarding-welcome-label">Step {currentStep + 1} / {totalSteps}</p>
            <h2 className="onboarding-welcome-title">MCPサーバーを接続しましょう</h2>
            <p className="onboarding-welcome-desc">
              3つのサービスを接続すると、開発ログの自動記録・ドキュメント生成・学習コンテンツ作成が使えるようになります。
            </p>
          </div>

          {/* ステップカード */}
          <div className="onboarding-card">
            <StepComponent
              onMarkCompleted={() => markCompleted(currentStep)}
              onMarkSkipped={() => markSkipped(currentStep)}
              isCompleted={stepStatus(currentStep) === 'completed'}
              isSkipped={stepStatus(currentStep) === 'skipped'}
            />
          </div>

          {/* ナビゲーション */}
          <nav className="onboarding-nav">
            <button
              type="button"
              className="onboarding-nav-btn onboarding-nav-btn--back"
              onClick={goBack}
              disabled={currentStep === 0}
            >
              <LuArrowLeft size={16} />
              前へ
            </button>

            <SetupStepper
              currentStep={currentStep}
              stepStatus={stepStatus}
              onStepClick={goToStep}
            />

            <button
              type="button"
              className="onboarding-nav-btn onboarding-nav-btn--next"
              onClick={goNext}
              disabled={currentStep === totalSteps - 1}
            >
              次へ
              <LuArrowRight size={16} />
            </button>
          </nav>
        </div>
      )}
    </div>
  );
};
