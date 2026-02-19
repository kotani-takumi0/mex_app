import { apiGet } from './client';
import { PublicPortfolio, PublicProjectDetail } from '../types';

type BackendEntryType =
  | 'tutorial'
  | 'design'
  | 'debug_guide'
  | 'learning'
  | 'reference'
  | 'code_generation'
  | 'debug'
  | 'design_decision'
  | 'error_resolution'
  | string;

interface BackendPublicProjectDetail {
  project: PublicProjectDetail['project'];
  devlog: {
    entry_type: BackendEntryType;
    summary: string;
    technologies: string[];
    created_at: string;
  }[];
}

const toCategory = (entryType: BackendEntryType): PublicProjectDetail['devlog'][number]['category'] => {
  switch (entryType) {
    case 'tutorial':
    case 'design':
    case 'debug_guide':
    case 'learning':
    case 'reference':
      return entryType;
    case 'design_decision':
      return 'design';
    case 'debug':
    case 'error_resolution':
      return 'debug_guide';
    case 'code_generation':
      return 'tutorial';
    default:
      return 'reference';
  }
};

export const getPublicPortfolio = (username: string) =>
  apiGet<PublicPortfolio>(`/portfolio/${username}`);

export const getPublicProjectDetail = async (
  username: string,
  projectId: string
): Promise<{ data: PublicProjectDetail | null; error: string | null; status?: number }> => {
  const result = await apiGet<BackendPublicProjectDetail>(`/portfolio/${username}/${projectId}`);
  if (result.error || !result.data) {
    return { ...result, data: null };
  }

  const mapped: PublicProjectDetail = {
    project: result.data.project,
    devlog: result.data.devlog.map((entry) => ({
      category: toCategory(entry.entry_type),
      title: entry.summary,
      technologies: entry.technologies,
      created_at: entry.created_at,
    })),
  };

  return {
    ...result,
    data: mapped,
  };
};
