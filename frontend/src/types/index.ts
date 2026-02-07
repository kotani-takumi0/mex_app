/**
 * 共通型定義 - MEX App（AI開発ポートフォリオ）
 */

// ユーザー
export interface User {
  id: string;
  email: string;
  display_name: string;
  plan: 'free' | 'pro';
  username: string | null;
  bio: string | null;
  github_url: string | null;
}

// 認証レスポンス
export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// プロジェクト
export interface Project {
  id: string;
  title: string;
  description: string | null;
  technologies: string[];
  repository_url: string | null;
  demo_url: string | null;
  status: 'in_progress' | 'completed' | 'archived';
  is_public: boolean;
  devlog_count: number;
  quiz_score: number | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreateRequest {
  title: string;
  description?: string;
  technologies?: string[];
  repository_url?: string;
  demo_url?: string;
  status?: string;
  is_public?: boolean;
}

// 開発ログ
export interface DevLogEntry {
  id: string;
  project_id: string;
  source: 'mcp' | 'manual';
  entry_type: 'code_generation' | 'debug' | 'design_decision' | 'learning' | 'error_resolution';
  summary: string;
  detail: string | null;
  technologies: string[];
  ai_tool: string | null;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface DevLogCreateRequest {
  source?: 'manual' | 'mcp';
  entry_type: string;
  summary: string;
  detail?: string;
  technologies: string[];
  ai_tool?: string | null;
  metadata?: Record<string, unknown>;
}

// クイズ
export interface QuizQuestion {
  id: string;
  technology: string;
  question: string;
  options: string[];
  difficulty: 'easy' | 'medium' | 'hard';
  devlog_entry_id: string | null;
}

export interface QuizAnswerRequest {
  selected_answer: number;
  time_spent_seconds?: number;
}

export interface QuizAnswerResponse {
  is_correct: boolean;
  correct_answer: number;
  explanation: string;
  score_update: {
    technology: string;
    previous_score: number;
    new_score: number;
    total_questions: number;
    correct_answers: number;
  };
}

export interface SkillScore {
  technology: string;
  score: number;
  total_questions: number;
  correct_answers: number;
  last_assessed_at: string | null;
}

// ダッシュボード
export interface DashboardData {
  user: {
    display_name: string;
    username: string | null;
    bio: string | null;
    github_url: string | null;
  };
  stats: {
    total_projects: number;
    total_devlog_entries: number;
    total_quiz_answered: number;
    overall_score: number;
  };
  recent_projects: Project[];
  top_skills: SkillScore[];
}

// 公開ポートフォリオ
export interface PublicPortfolio {
  user: {
    display_name: string;
    bio: string | null;
    github_url: string | null;
  };
  projects: Project[];
  skills: SkillScore[];
}

export interface PublicProjectDetail {
  project: Project;
  devlog: Pick<DevLogEntry, 'entry_type' | 'summary' | 'technologies' | 'created_at'>[];
  quiz_summary: {
    total_questions: number;
    correct_answers: number;
    score: number;
    by_technology: {
      technology: string;
      score: number;
      questions: number;
      correct: number;
    }[];
  };
}
