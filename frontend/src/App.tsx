/**
 * メインアプリケーション
 * React Routerによるルーティング + react-hot-toast
 */
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { AppLoadingScreen } from './components/common/AppLoadingScreen';
import { Navigation } from './components/common/Navigation';
import { LandingPage } from './components/Landing/LandingPage';
import { AuthPage } from './components/Auth/AuthPage';
import { DashboardPage } from './components/Dashboard/DashboardPage';
import { ProjectFormPage } from './components/Projects/ProjectFormPage';
import { ProjectDetailPage } from './components/Projects/ProjectDetailPage';
import { PublicPortfolioPage } from './components/Portfolio/PublicPortfolioPage';
import { PublicProjectDetailPage } from './components/Portfolio/PublicProjectDetailPage';
import { SettingsPage } from './components/Settings/SettingsPage';
import { SetupWizardPage } from './components/Setup/SetupWizardPage';
import { BillingSuccessPage } from './components/Billing/BillingSuccessPage';
import { BillingCancelPage } from './components/Billing/BillingCancelPage';
import { UsernameSetupModal } from './components/common/UsernameSetupModal';
import './App.css';

const POST_AUTH_REDIRECT_KEY = 'mex_post_auth_redirect';

/**
 * PublicRoute: 未認証ユーザー専用ルート
 * 認証済みならリダイレクト（デフォルト: /dashboard）
 *
 * 新規登録後は sessionStorage のフラグを優先して遷移。
 * NOTE: フラグ削除は useEffect で実施し、レンダー中副作用を避ける。
 */
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const redirect = sessionStorage.getItem(POST_AUTH_REDIRECT_KEY);

  React.useEffect(() => {
    if (isAuthenticated && redirect) {
      sessionStorage.removeItem(POST_AUTH_REDIRECT_KEY);
    }
  }, [isAuthenticated, redirect]);

  if (isLoading) return <AppLoadingScreen />;
  if (isAuthenticated) {
    return <Navigate to={redirect || '/dashboard'} replace />;
  }

  return <>{children}</>;
};

/**
 * ProtectedRoute: 認証必須ルート
 * 未認証なら /auth にリダイレクト
 */
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return <AppLoadingScreen />;
  if (!isAuthenticated) return <Navigate to="/auth" replace />;

  return <>{children}</>;
};

/**
 * 認証済みレイアウト: ナビゲーション + メインコンテンツ
 */
const AuthenticatedLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="app">
      <Navigation />
      <main className="main-content">{children}</main>
      <UsernameSetupModal />
    </div>
  );
};

function AppRoutes() {
  return (
    <Routes>
      {/* 公開ルート */}
      <Route
        path="/"
        element={
          <PublicRoute>
            <LandingPage />
          </PublicRoute>
        }
      />
      <Route
        path="/auth"
        element={
          <PublicRoute>
            <AuthPage />
          </PublicRoute>
        }
      />

      {/* 公開ポートフォリオ */}
      <Route path="/p/:username" element={<PublicPortfolioPage />} />
      <Route path="/p/:username/:projectId" element={<PublicProjectDetailPage />} />

      {/* 認証必須ルート */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <AuthenticatedLayout>
              <DashboardPage />
            </AuthenticatedLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/projects/new"
        element={
          <ProtectedRoute>
            <AuthenticatedLayout>
              <ProjectFormPage />
            </AuthenticatedLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/projects/:id/edit"
        element={
          <ProtectedRoute>
            <AuthenticatedLayout>
              <ProjectFormPage />
            </AuthenticatedLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/projects/:id"
        element={
          <ProtectedRoute>
            <AuthenticatedLayout>
              <ProjectDetailPage />
            </AuthenticatedLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <AuthenticatedLayout>
              <SettingsPage />
            </AuthenticatedLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/setup"
        element={
          <ProtectedRoute>
            <SetupWizardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/billing/success"
        element={
          <ProtectedRoute>
            <AuthenticatedLayout>
              <BillingSuccessPage />
            </AuthenticatedLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/billing/cancel"
        element={
          <ProtectedRoute>
            <AuthenticatedLayout>
              <BillingCancelPage />
            </AuthenticatedLayout>
          </ProtectedRoute>
        }
      />

      {/* フォールバック */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <ErrorBoundary>
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              fontFamily: 'var(--font-family-base)',
              fontSize: 'var(--font-size-base)',
              borderRadius: 'var(--radius-lg)',
              padding: '12px 16px',
            },
            success: {
              iconTheme: { primary: '#4caf50', secondary: '#fff' },
            },
            error: {
              iconTheme: { primary: '#f44336', secondary: '#fff' },
            },
          }}
        />
      </AuthProvider>
    </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
