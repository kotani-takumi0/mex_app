/**
 * カテゴリユーティリティ
 * ProjectDetailPage と PublicProjectDetailPage の両方で使用する
 * カテゴリ関連のロジックを共通化
 */
import { TechDocument } from '../types';

export const categoryOptions = [
  { value: 'tutorial', label: 'チュートリアル' },
  { value: 'design', label: '設計' },
  { value: 'debug_guide', label: 'デバッグガイド' },
  { value: 'learning', label: '学習ノート' },
  { value: 'reference', label: 'リファレンス' },
] as const;

export type CategoryValue = (typeof categoryOptions)[number]['value'];

export const getCategoryLabel = (category: TechDocument['category']): string =>
  categoryOptions.find((option) => option.value === category)?.label || category;

export const getCategoryClassName = (category: TechDocument['category']): string => {
  switch (category) {
    case 'tutorial':
      return 'doc-category-tutorial';
    case 'design':
      return 'doc-category-design';
    case 'debug_guide':
      return 'doc-category-debug';
    case 'learning':
      return 'doc-category-learning';
    case 'reference':
      return 'doc-category-reference';
    default:
      return 'doc-category-reference';
  }
};

export const parseTechnologies = (value: string): string[] =>
  value
    .split(',')
    .map((tech) => tech.trim())
    .filter((tech) => tech.length > 0);
