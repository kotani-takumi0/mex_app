import { apiGet } from './client';
import { PublicPortfolio, PublicProjectDetail } from '../types';

export const getPublicPortfolio = (username: string) =>
  apiGet<PublicPortfolio>(`/portfolio/${username}`);

export const getPublicProjectDetail = (username: string, projectId: string) =>
  apiGet<PublicProjectDetail>(`/portfolio/${username}/${projectId}`);
