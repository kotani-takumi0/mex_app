import { apiGet } from './client';
import { DashboardData } from '../types';

export const getDashboard = () => apiGet<DashboardData>('/dashboard');
