/**
 * Billing API - プラン情報取得・Checkout・Portal
 */
import { apiGet, apiPost } from './client';

export interface PlanInfo {
  plan: string;
  project_limit: number | null;
  project_count: number;
  llm_model: string;
  subscription_status: string | null;
  current_period_end: string | null;
}

interface CheckoutResponse {
  checkout_url: string;
}

interface PortalResponse {
  portal_url: string;
}

export async function getPlanInfo() {
  return apiGet<PlanInfo>('/billing/plan-info');
}

export async function createCheckout(successUrl: string, cancelUrl: string) {
  return apiPost<CheckoutResponse, { success_url: string; cancel_url: string }>(
    '/billing/checkout-session',
    { success_url: successUrl, cancel_url: cancelUrl },
  );
}

export async function createPortal(returnUrl: string) {
  return apiPost<PortalResponse, { return_url: string }>(
    '/billing/portal',
    { return_url: returnUrl },
  );
}
