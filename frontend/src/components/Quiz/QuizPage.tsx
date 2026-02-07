/**
 * クイズページ
 */
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { LuLoader, LuSparkles } from 'react-icons/lu';
import { generateQuiz, getQuizQuestions, answerQuiz } from '../../api/quiz';
import { QuizQuestion, QuizAnswerResponse } from '../../types';
import { PageHeader } from '../common/PageHeader';
import { EmptyState } from '../common/EmptyState';
import './QuizPage.css';

export const QuizPage: React.FC = () => {
  const { id } = useParams();
  const projectId = id || '';
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [results, setResults] = useState<Record<string, QuizAnswerResponse>>({});
  const [answeringId, setAnsweringId] = useState<string | null>(null);

  const [count, setCount] = useState(5);
  const [difficulty, setDifficulty] = useState('medium');
  const [technologies, setTechnologies] = useState('');

  useEffect(() => {
    const fetchQuestions = async () => {
      if (!projectId) return;
      const { data, error } = await getQuizQuestions(projectId);
      if (error) {
        toast.error(error);
      } else if (data) {
        setQuestions(data.questions);
      }
    };
    fetchQuestions();
  }, [projectId]);

  const handleGenerate = async () => {
    if (!projectId) return;
    setIsGenerating(true);

    const techList = technologies
      .split(',')
      .map((tech) => tech.trim())
      .filter((tech) => tech.length > 0);

    const { data, error } = await generateQuiz(projectId, {
      count,
      difficulty,
      technologies: techList.length ? techList : undefined,
    });

    if (error) {
      toast.error(error);
    } else if (data) {
      toast.success('クイズを生成しました');
      setQuestions(data.questions);
      setResults({});
      setAnswers({});
    }

    setIsGenerating(false);
  };

  const handleAnswer = async (questionId: string) => {
    const selected = answers[questionId];
    if (selected === undefined) {
      toast.error('選択肢を選んでください');
      return;
    }

    setAnsweringId(questionId);
    const { data, error } = await answerQuiz(questionId, { selected_answer: selected });
    if (error) {
      toast.error(error);
    } else if (data) {
      setResults((prev) => ({ ...prev, [questionId]: data }));
      toast.success(data.is_correct ? '正解です' : '不正解です');
    }
    setAnsweringId(null);
  };

  return (
    <div className="page-container">
      <PageHeader
        title="理解度チェック"
        description="開発ログから生成された4択クイズで理解度を確認しましょう。"
      />

      <section className="quiz-generate">
        <div className="quiz-generate-card">
          <div className="form-group">
            <label htmlFor="count">問題数</label>
            <input
              id="count"
              type="number"
              min={1}
              max={20}
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
            />
          </div>
          <div className="form-group">
            <label htmlFor="difficulty">難易度</label>
            <select id="difficulty" value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
              <option value="easy">easy</option>
              <option value="medium">medium</option>
              <option value="hard">hard</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="technologies">対象技術（任意）</label>
            <input
              id="technologies"
              type="text"
              value={technologies}
              onChange={(e) => setTechnologies(e.target.value)}
              placeholder="React Router, TypeScript"
            />
          </div>
          <button className="submit-btn" onClick={handleGenerate} disabled={isGenerating}>
            {isGenerating ? (
              <>
                <LuLoader className="submit-btn-icon" size={18} />
                生成中...
              </>
            ) : (
              'クイズを生成'
            )}
          </button>
        </div>
      </section>

      <section className="quiz-list">
        {questions.length === 0 ? (
          <EmptyState
            icon={LuSparkles}
            title="クイズがまだありません"
            description="上のフォームからクイズを生成してください。"
          />
        ) : (
          <div className="quiz-cards">
            {questions.map((q, index) => {
              const result = results[q.id];
              return (
                <div key={q.id} className="quiz-card">
                  <div className="quiz-header">
                    <span className="quiz-index">Q{index + 1}</span>
                    <span className="quiz-tech">{q.technology}</span>
                  </div>
                  <p className="quiz-question">{q.question}</p>
                  <div className="quiz-options">
                    {q.options.map((option, idx) => (
                      <label key={`${q.id}-${idx}`} className={`quiz-option ${result ? 'answered' : ''}`}>
                        <input
                          type="radio"
                          name={`quiz-${q.id}`}
                          value={idx}
                          checked={answers[q.id] === idx}
                          onChange={() => setAnswers((prev) => ({ ...prev, [q.id]: idx }))}
                          disabled={!!result}
                        />
                        <span>{option}</span>
                      </label>
                    ))}
                  </div>
                  {!result && (
                    <button
                      className="answer-btn"
                      onClick={() => handleAnswer(q.id)}
                      disabled={answeringId === q.id}
                    >
                      {answeringId === q.id ? '送信中...' : '回答する'}
                    </button>
                  )}
                  {result && (
                    <div className={`answer-result ${result.is_correct ? 'correct' : 'incorrect'}`}>
                      <strong>{result.is_correct ? '正解' : '不正解'}</strong>
                      <p>{result.explanation}</p>
                      <div className="score-update">
                        {result.score_update.technology} スコア: {result.score_update.previous_score.toFixed(1)} →{' '}
                        {result.score_update.new_score.toFixed(1)}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
};
