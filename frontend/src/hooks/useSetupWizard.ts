/**
 * セットアップウィザードの状態管理hook
 *
 * 変更理由: 3ステップウィザード（MEX / Notion / NotebookLM）の
 * 完了・スキップ状態を localStorage に永続化し、
 * currentStep は初回非完了ステップから自動算出する。
 */
import { useState, useCallback, useMemo } from 'react';

const STORAGE_KEY = 'mex_setup_wizard_state';
const TOTAL_STEPS = 3;
const STEP_IDS = [0, 1, 2] as const;

interface PersistedState {
  readonly completedSteps: readonly number[];
  readonly skippedSteps: readonly number[];
}

function loadState(): PersistedState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { completedSteps: [], skippedSteps: [] };
    const parsed = JSON.parse(raw);
    return {
      completedSteps: Array.isArray(parsed.completedSteps) ? parsed.completedSteps : [],
      skippedSteps: Array.isArray(parsed.skippedSteps) ? parsed.skippedSteps : [],
    };
  } catch {
    return { completedSteps: [], skippedSteps: [] };
  }
}

function saveState(state: PersistedState) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function firstIncompleteStep(state: PersistedState): number {
  for (const id of STEP_IDS) {
    if (!state.completedSteps.includes(id) && !state.skippedSteps.includes(id)) {
      return id;
    }
  }
  return STEP_IDS[STEP_IDS.length - 1];
}

export function useSetupWizard() {
  const [persisted, setPersisted] = useState<PersistedState>(loadState);
  const [currentStep, setCurrentStep] = useState<number>(() => firstIncompleteStep(loadState()));

  const update = useCallback((next: PersistedState) => {
    setPersisted(next);
    saveState(next);
  }, []);

  const markCompleted = useCallback(
    (step: number) => {
      const next: PersistedState = {
        completedSteps: persisted.completedSteps.includes(step)
          ? persisted.completedSteps
          : [...persisted.completedSteps, step],
        skippedSteps: persisted.skippedSteps.filter((s) => s !== step),
      };
      update(next);
    },
    [persisted, update],
  );

  const markSkipped = useCallback(
    (step: number) => {
      const next: PersistedState = {
        completedSteps: persisted.completedSteps.filter((s) => s !== step),
        skippedSteps: persisted.skippedSteps.includes(step)
          ? persisted.skippedSteps
          : [...persisted.skippedSteps, step],
      };
      update(next);
    },
    [persisted, update],
  );

  const goNext = useCallback(() => {
    setCurrentStep((prev) => Math.min(prev + 1, TOTAL_STEPS - 1));
  }, []);

  const goBack = useCallback(() => {
    setCurrentStep((prev) => Math.max(prev - 1, 0));
  }, []);

  const goToStep = useCallback((step: number) => {
    if (step >= 0 && step < TOTAL_STEPS) {
      setCurrentStep(step);
    }
  }, []);

  const isAllDone = useMemo(() => {
    return STEP_IDS.every(
      (id) => persisted.completedSteps.includes(id) || persisted.skippedSteps.includes(id),
    );
  }, [persisted]);

  const stepStatus = useCallback(
    (step: number): 'pending' | 'active' | 'completed' | 'skipped' => {
      if (persisted.completedSteps.includes(step)) return 'completed';
      if (persisted.skippedSteps.includes(step)) return 'skipped';
      if (step === currentStep) return 'active';
      return 'pending';
    },
    [persisted, currentStep],
  );

  return {
    currentStep,
    totalSteps: TOTAL_STEPS,
    completedSteps: persisted.completedSteps,
    skippedSteps: persisted.skippedSteps,
    markCompleted,
    markSkipped,
    goNext,
    goBack,
    goToStep,
    isAllDone,
    stepStatus,
  } as const;
}
