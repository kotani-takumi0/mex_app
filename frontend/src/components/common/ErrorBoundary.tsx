import React from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
}

export class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  ErrorBoundaryState
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          padding: '2rem',
          fontFamily: 'var(--font-family-base, sans-serif)',
          color: 'var(--color-text-primary, #1a1a1a)',
        }}>
          <h1 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>
            予期しないエラーが発生しました
          </h1>
          <p style={{
            color: 'var(--color-text-secondary, #666)',
            marginBottom: '1.5rem',
            textAlign: 'center',
          }}>
            ページの再読み込みをお試しください。問題が続く場合はサポートまでご連絡ください。
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: 'var(--color-primary, #2563eb)',
              color: '#fff',
              border: 'none',
              borderRadius: 'var(--radius-md, 8px)',
              cursor: 'pointer',
              fontSize: '1rem',
            }}
          >
            ページを再読み込み
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
