/**
 * ドット型進捗インジケーター
 *
 * 変更理由: フルスクリーンオンボーディングに合わせ、
 * 水平ピル型ステッパーからコンパクトなドット+コネクターラインに変更。
 * ナビゲーション中央に配置して邪魔にならないサイズにする。
 */
import React from 'react';
import { LuCircleCheck, LuMinus } from 'react-icons/lu';
import './SetupStepper.css';

const TOTAL = 3;

interface Props {
  readonly currentStep: number;
  readonly stepStatus: (step: number) => 'pending' | 'active' | 'completed' | 'skipped';
  readonly onStepClick: (step: number) => void;
}

export const SetupStepper: React.FC<Props> = ({ currentStep, stepStatus, onStepClick }) => {
  return (
    <nav className="setup-stepper" aria-label="セットアップ進捗">
      {Array.from({ length: TOTAL }, (_, idx) => {
        const status = stepStatus(idx);
        const isClickable = status === 'completed' || status === 'skipped' || idx === currentStep;

        return (
          <React.Fragment key={idx}>
            {idx > 0 && (
              <div
                className={`stepper-line ${
                  stepStatus(idx - 1) === 'completed' ? 'stepper-line--done' : ''
                }`}
              />
            )}
            <button
              type="button"
              className={`stepper-dot stepper-dot--${status}`}
              onClick={() => isClickable && onStepClick(idx)}
              disabled={!isClickable}
              aria-current={idx === currentStep ? 'step' : undefined}
              aria-label={`ステップ ${idx + 1}`}
            >
              {status === 'completed' ? (
                <LuCircleCheck size={14} />
              ) : status === 'skipped' ? (
                <LuMinus size={12} />
              ) : null}
            </button>
          </React.Fragment>
        );
      })}
    </nav>
  );
};
