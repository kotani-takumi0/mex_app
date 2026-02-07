import { apiGet, apiPost } from './client';
import { QuizQuestion, QuizAnswerRequest, QuizAnswerResponse, SkillScore } from '../types';

export const generateQuiz = (
  projectId: string,
  data: { count?: number; difficulty?: string; technologies?: string[] }
) => apiPost<{ questions: QuizQuestion[]; total_generated: number }, typeof data>(`/quiz/${projectId}/generate`, data);

export const getQuizQuestions = (projectId: string) =>
  apiGet<{ questions: QuizQuestion[]; total_generated: number }>(`/quiz/${projectId}`);

export const answerQuiz = (questionId: string, data: QuizAnswerRequest) =>
  apiPost<QuizAnswerResponse, QuizAnswerRequest>(`/quiz/${questionId}/answer`, data);

export const getSkillScores = () => apiGet<{ scores: SkillScore[] }>('/quiz/scores');
