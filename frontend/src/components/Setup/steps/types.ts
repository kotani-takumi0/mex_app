/**
 * セットアップステップ共通の Props 型定義
 */
export interface StepProps {
  readonly onMarkCompleted: () => void;
  readonly onMarkSkipped: () => void;
  readonly isCompleted: boolean;
  readonly isSkipped: boolean;
}
