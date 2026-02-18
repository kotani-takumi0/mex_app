/**
 * クイズページ
 * プロジェクトの開発ログから4択クイズを生成し、技術理解度を確認する。
 * 403レスポンス時はUpgradePromptを表示。
 */
import React, { useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  LuArrowLeft,
  LuCheck,
  LuCircleCheck,
  LuCircleX,
  LuLoader,
  LuSparkles,
} from 'react-icons/lu';
import { generateQuiz, getQuizQuestions, answerQuiz } from '../../api/quiz';
import { getProject } from '../../api/projects';
import { QuizQuestion, QuizAnswerResponse, Project } from '../../types';
import { PageHeader } from '../common/PageHeader';
import { EmptyState } from '../common/EmptyState';
import { UpgradePrompt } from '../common/UpgradePrompt';
import './QuizPage.css';

interface AnsweredQuestion {
  questionId: string;
  selectedAnswer: number;
  result: QuizAnswerResponse;
}

export const QuizPage: React.FC = () => {
  const { id: projectId } = useParams();
  const [project, setProject] = useState<Project | null>(null);
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [answered, setAnswered] = useState<Map<string, AnsweredQuestion>>(new Map());
  const [selectedOptions, setSelectedOptions] = useState<Map<string, number>>(new Map());
  const [submittingId, setSubmittingId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showUpgrade, setShowUpgrade] = useState(false);

  const fetchData = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);

    const [projectResult, quizResult] = await Promise.all([
      getProject(projectId),
      getQuizQuestions(projectId),
    ]);

    if (projectResult.data) {
      setProject(projectResult.data);
    }
    if (quizResult.data) {
      setQuestions(quizResult.data.questions);
    }
    setIsLoading(false);
  }, [projectId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleGenerate = async () => {
    if (!projectId) return;
    setIsGenerating(true);

    const { data, error, status } = await generateQuiz(projectId, {
      count: 5,
      difficulty: 'medium',
    });

    setIsGenerating(false);

    if (status === 403) {
      setShowUpgrade(true);
      return;
    }

    if (error) {
      toast.error(error);
      return;
    }

    if (data) {
      setQuestions(data.questions);
      setAnswered(new Map());
      setSelectedOptions(new Map());
      toast.success(`${data.total_generated}問のクイズを生成しました`);
    }
  };

  const handleSelectOption = (questionId: string, optionIndex: number) => {
    if (answered.has(questionId)) return;
    setSelectedOptions((prev) => {
      const next = new Map(prev);
      next.set(questionId, optionIndex);
      return next;
    });
  };

  const handleAnswer = async (questionId: string) => {
    const selected = selectedOptions.get(questionId);
    if (selected === undefined) return;

    setSubmittingId(questionId);

    const { data, error } = await answerQuiz(questionId, {
      selected_answer: selected,
    });

    setSubmittingId(null);

    if (error) {
      toast.error(error);
      return;
    }

    if (data) {
      setAnswered((prev) => {
        const next = new Map(prev);
        next.set(questionId, {
          questionId,
          selectedAnswer: selected,
          result: data,
        });
        return next;
      });
    }
  };

  const answeredCount = answered.size;
  const correctCount = Array.from(answered.values()).filter((a) => a.result.is_correct).length;

  if (isLoading) {
    return (
      <div className="page-container">
        <PageHeader title="理解度チェック" description="読み込み中..." />
      </div>
    );
  }

  return (
    <div className="page-container">
      {showUpgrade && (
        <UpgradePrompt
          message="Freeプランではクイズ生成は月2回までです。Proプランにアップグレードすると無制限に生成できます。"
          onClose={() => setShowUpgrade(false)}
        />
      )}

      <PageHeader
        title="理解度チェック"
        description={project ? `${project.title} の技術理解度を確認` : '開発ログから生成された4択クイズ'}
        action={
          <Link to={projectId ? `/projects/${projectId}` : '/dashboard'} className="edit-link">
            <LuArrowLeft size={16} />
            プロジェクトに戻る
          </Link>
        }
      />

      <section className="quiz-generate">
        <div className="quiz-generate-card">
          <p>
            開発ログに基づいて、使用した技術の本質的な理解を問う4択クイズを生成します。
          </p>
          <button
            className="submit-btn"
            onClick={handleGenerate}
            disabled={isGenerating}
          >
            {isGenerating ? (
              <>
                <LuLoader size={16} className="submit-btn-icon" />
                生成中...
              </>
            ) : (
              <>
                <LuSparkles size={16} />
                クイズを生成する（5問）
              </>
            )}
          </button>
        </div>
      </section>

      {questions.length === 0 ? (
        <EmptyState
          icon={LuSparkles}
          title="クイズがまだありません"
          description="上のボタンから開発ログに基づいたクイズを生成してみましょう。ドキュメントが1件以上必要です。"
        />
      ) : (
        <>
          {answeredCount > 0 && (
            <div className="quiz-summary">
              回答済み {answeredCount} / {questions.length} 問
              {answeredCount === questions.length && (
                <span className="quiz-summary-score">
                  &nbsp;&mdash;&nbsp;正解率 {Math.round((correctCount / answeredCount) * 100)}%
                </span>
              )}
            </div>
          )}

          <div className="quiz-cards">
            {questions.map((q, index) => {
              const answer = answered.get(q.id);
              const selected = selectedOptions.get(q.id);
              const isSubmitting = submittingId === q.id;

              return (
                <div key={q.id} className="quiz-card">
                  <div className="quiz-header">
                    <span className="quiz-index">Q{index + 1}</span>
                    <span className="quiz-tech">{q.technology}</span>
                  </div>
                  <p className="quiz-question">{q.question}</p>

                  <div className="quiz-options">
                    {q.options.map((option, optIdx) => {
                      let optionClass = 'quiz-option';
                      if (answer) {
                        optionClass += ' answered';
                        if (optIdx === answer.result.correct_answer) {
                          optionClass += ' correct';
                        } else if (optIdx === answer.selectedAnswer && !answer.result.is_correct) {
                          optionClass += ' incorrect';
                        }
                      } else if (selected === optIdx) {
                        optionClass += ' selected';
                      }

                      return (
                        <label
                          key={optIdx}
                          className={optionClass}
                          onClick={() => handleSelectOption(q.id, optIdx)}
                        >
                          <input
                            type="radio"
                            name={`quiz-${q.id}`}
                            checked={selected === optIdx || answer?.selectedAnswer === optIdx}
                            onChange={() => handleSelectOption(q.id, optIdx)}
                            disabled={!!answer}
                          />
                          <span>{option}</span>
                          {answer && optIdx === answer.result.correct_answer && (
                            <LuCircleCheck size={16} className="option-icon correct" />
                          )}
                          {answer && optIdx === answer.selectedAnswer && !answer.result.is_correct && optIdx !== answer.result.correct_answer && (
                            <LuCircleX size={16} className="option-icon incorrect" />
                          )}
                        </label>
                      );
                    })}
                  </div>

                  {!answer && (
                    <button
                      className="answer-btn"
                      onClick={() => handleAnswer(q.id)}
                      disabled={selected === undefined || isSubmitting}
                    >
                      {isSubmitting ? (
                        <>
                          <LuLoader size={14} className="submit-btn-icon" />
                          判定中...
                        </>
                      ) : (
                        '回答する'
                      )}
                    </button>
                  )}

                  {answer && (
                    <div className={`answer-result ${answer.result.is_correct ? 'correct' : 'incorrect'}`}>
                      <strong>
                        {answer.result.is_correct ? (
                          <><LuCheck size={16} /> 正解！</>
                        ) : (
                          <><LuCircleX size={16} /> 不正解</>
                        )}
                      </strong>
                      <p>{answer.result.explanation}</p>
                      <div className="score-update">
                        {answer.result.score_update.technology}: {answer.result.score_update.previous_score}%
                        → {answer.result.score_update.new_score}%
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
};
