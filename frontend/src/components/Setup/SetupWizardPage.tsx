/**
 * MCPセットアップウィザード — フルスクリーン・オンボーディング
 *
 * 変更理由: 新規登録後に「設定画面の一部」ではなく、
 * ナビゲーションなしのフルスクリーン体験として
 * 1ステップずつフォーカスするウェルカムフローを提供する。
 *
 * 分岐: 既存プロジェクトユーザーと新規プロジェクトユーザーで
 * 導線を分けるため、最初にプロジェクトタイプ選択画面を表示する。
 * 新規ユーザーには事前準備のチェックリストを見せてからMCPセットアップに進む。
 */
import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LuArrowLeft,
  LuArrowRight,
  LuCircleCheck,
  LuArrowRight as LuGo,
  LuFolderGit2,
  LuRocket,
  LuSquareTerminal,
  LuGitBranch,
  LuFileCode2,
  LuGlobe,
} from 'react-icons/lu';
import { useSetupWizard } from '../../hooks/useSetupWizard';
import { SetupStepper } from './SetupStepper';
import { MexMcpStep } from './steps/MexMcpStep';
import { NotionMcpStep } from './steps/NotionMcpStep';
import { NotebookLmMcpStep } from './steps/NotebookLmMcpStep';
import './SetupWizardPage.css';
import './steps/SetupSteps.css';

const STEP_COMPONENTS = [MexMcpStep, NotionMcpStep, NotebookLmMcpStep] as const;

type ProjectType = 'existing' | 'new';
type GatePhase = 'select' | 'prereqs' | 'wizard';

const GATE_STORAGE_KEY = 'mex_setup_gate_phase';

function loadGatePhase(): GatePhase {
  const saved = localStorage.getItem(GATE_STORAGE_KEY);
  if (saved === 'wizard') return 'wizard';
  return 'select';
}

function saveGatePhase(phase: GatePhase) {
  localStorage.setItem(GATE_STORAGE_KEY, phase);
}

export const SetupWizardPage: React.FC = () => {
  const navigate = useNavigate();
  const wizard = useSetupWizard();
  const { currentStep, totalSteps, isAllDone, stepStatus, goNext, goBack, goToStep, markCompleted, markSkipped } = wizard;

  const [gatePhase, setGatePhase] = useState<GatePhase>(loadGatePhase);

  useEffect(() => {
    if (isAllDone) {
      localStorage.setItem('mex_mcp_banner_dismissed', 'true');
    }
  }, [isAllDone]);

  const handleFinish = () => {
    localStorage.setItem('mex_mcp_banner_dismissed', 'true');
    localStorage.removeItem(GATE_STORAGE_KEY);
    navigate('/dashboard');
  };

  const handleSkipAll = () => {
    localStorage.setItem('mex_mcp_banner_dismissed', 'true');
    localStorage.removeItem(GATE_STORAGE_KEY);
    navigate('/dashboard');
  };

  const handleSelectType = useCallback((type: ProjectType) => {
    if (type === 'existing') {
      setGatePhase('wizard');
      saveGatePhase('wizard');
    } else {
      setGatePhase('prereqs');
    }
  }, []);

  const handlePrereqsContinue = useCallback(() => {
    setGatePhase('wizard');
    saveGatePhase('wizard');
  }, []);

  const handlePrereqsBack = useCallback(() => {
    setGatePhase('select');
  }, []);

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

      {gatePhase === 'select' ? (
        /* ===== プロジェクトタイプ選択画面 ===== */
        <div className="onboarding-body">
          <div className="onboarding-welcome">
            <p className="onboarding-welcome-label">はじめに</p>
            <h2 className="onboarding-welcome-title">プロジェクトの状況を教えてください</h2>
            <p className="onboarding-welcome-desc">
              あなたの状況に合わせてセットアップをガイドします。
            </p>
          </div>

          <div className="onboarding-gate-choices">
            <button
              type="button"
              className="onboarding-gate-card"
              onClick={() => handleSelectType('existing')}
            >
              <div className="onboarding-gate-card-icon onboarding-gate-card-icon--existing">
                <LuFolderGit2 size={28} />
              </div>
              <h3>既存のプロジェクトに接続</h3>
              <p>
                GitHubリポジトリや開発環境がすでにある。
                MCPサーバーを接続して記録を始めたい。
              </p>
              <span className="onboarding-gate-card-action">
                MCPセットアップへ <LuArrowRight size={14} />
              </span>
            </button>

            <button
              type="button"
              className="onboarding-gate-card"
              onClick={() => handleSelectType('new')}
            >
              <div className="onboarding-gate-card-icon onboarding-gate-card-icon--new">
                <LuRocket size={28} />
              </div>
              <h3>新しいプロジェクトを始める</h3>
              <p>
                まだプロジェクトがない。
                環境構築から始めたい。
              </p>
              <span className="onboarding-gate-card-action">
                事前準備を確認 <LuArrowRight size={14} />
              </span>
            </button>
          </div>
        </div>

      ) : gatePhase === 'prereqs' ? (
        /* ===== 新規プロジェクト: 事前準備チェックリスト ===== */
        <div className="onboarding-body">
          <div className="onboarding-welcome">
            <p className="onboarding-welcome-label">事前準備</p>
            <h2 className="onboarding-welcome-title">MCPセットアップの前に</h2>
            <p className="onboarding-welcome-desc">
              以下の準備ができてからMCPサーバーの接続に進んでください。
            </p>
          </div>

          <div className="onboarding-card">
            <ul className="onboarding-prereqs-list">
              <li>
                <span className="onboarding-prereqs-icon"><LuSquareTerminal size={18} /></span>
                <div>
                  <strong>Claude Code をインストール</strong>
                  <p>
                    ターミナルで <code>npm install -g @anthropic-ai/claude-code</code> を実行
                  </p>
                </div>
              </li>
              <li>
                <span className="onboarding-prereqs-icon"><LuFileCode2 size={18} /></span>
                <div>
                  <strong>プロジェクトディレクトリを作成</strong>
                  <p>
                    作業フォルダを作り、プロジェクトファイル（package.json 等）を配置
                  </p>
                </div>
              </li>
              <li>
                <span className="onboarding-prereqs-icon"><LuGitBranch size={18} /></span>
                <div>
                  <strong>Git リポジトリを初期化</strong>
                  <p>
                    <code>git init</code> でバージョン管理を開始
                  </p>
                </div>
              </li>
              <li>
                <span className="onboarding-prereqs-icon"><LuGlobe size={18} /></span>
                <div>
                  <strong>GitHub にリポジトリを作成（任意）</strong>
                  <p>
                    リモートリポジトリがあるとポートフォリオとの連携がスムーズ
                  </p>
                </div>
              </li>
            </ul>
          </div>

          <nav className="onboarding-nav">
            <button
              type="button"
              className="onboarding-nav-btn onboarding-nav-btn--back"
              onClick={handlePrereqsBack}
            >
              <LuArrowLeft size={16} />
              戻る
            </button>
            <button
              type="button"
              className="onboarding-nav-btn onboarding-nav-btn--next"
              onClick={handlePrereqsContinue}
            >
              準備できた — MCPセットアップへ
              <LuArrowRight size={16} />
            </button>
          </nav>
        </div>

      ) : isAllDone ? (
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
