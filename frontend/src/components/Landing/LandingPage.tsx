/**
 * ランディングページ
 * 未認証ユーザー向けの紹介ページ
 */
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { LuZap, LuCheck, LuLayoutDashboard, LuSparkles } from 'react-icons/lu';
import './LandingPage.css';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const goToAuth = () => navigate('/auth');

  return (
    <div className="landing-page">
      <header className="landing-nav">
        <div className="landing-nav-inner">
          <span className="landing-brand">MEX App</span>
          <Link to="/auth" className="landing-login-link">
            ログイン
          </Link>
        </div>
      </header>

      <section className="landing-hero" aria-labelledby="hero-title">
        <div className="landing-hero-inner">
          <h1 id="hero-title" className="hero-title">
            AIで作ったものを、<br />自分の学びに変えよう
          </h1>
          <p className="hero-description">
            開発過程を自動記録し、技術ドキュメントを自動生成。
            学んだことを自分の言葉で残すことで、面接官に理解度を証明できます。
          </p>
          <button className="cta-button" onClick={goToAuth}>
            無料で始める
          </button>
        </div>
      </section>

      <section className="landing-features" aria-labelledby="features-title">
        <h2 id="features-title" className="section-title">特徴</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon-circle">
              <LuZap size={28} />
            </div>
            <h3>開発過程の自動記録</h3>
            <p>
              MCPサーバーでAI開発の過程を自動キャプチャ。手入力の手間なく、
              いつ・何を・どう作ったかが残ります。
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon-circle">
              <LuCheck size={28} />
            </div>
            <h3>技術ドキュメント自動生成</h3>
            <p>
              コミットからNotionに教育的ドキュメントを自動生成。
              WHY・HOWの解説と基礎〜応用のQ&Aで、使った技術を深く理解できます。
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon-circle">
              <LuLayoutDashboard size={28} />
            </div>
            <h3>自分の言葉で残すポートフォリオ</h3>
            <p>
              ドキュメントで学んだことを自分の言葉でアプリに記録。
              面接官が「本当に理解しているか」を判別できる新しいポートフォリオです。
            </p>
          </div>
        </div>
      </section>

      <section className="landing-pricing" aria-labelledby="pricing-title">
        <h2 id="pricing-title" className="section-title">料金プラン</h2>
        <div className="pricing-cards">
          <div className="pricing-card featured">
            <div className="pricing-badge">学生向け</div>
            <h3>Free</h3>
            <div className="price">
              &yen;0<span className="price-period">/月</span>
            </div>
            <ul className="pricing-features">
              <li><LuCheck size={16} className="check-icon" /> プロジェクト2件</li>
              <li><LuCheck size={16} className="check-icon" /> クイズ生成 月2回</li>
              <li><LuCheck size={16} className="check-icon" /> GPT-4o-miniモデル</li>
              <li><LuCheck size={16} className="check-icon" /> 公開ポートフォリオ</li>
            </ul>
            <button className="cta-button" onClick={goToAuth}>
              無料で始める
            </button>
          </div>
          <div className="pricing-card">
            <div className="pricing-badge upcoming">
              <LuSparkles size={14} /> Pro
            </div>
            <h3>Pro</h3>
            <div className="price">
              &yen;780<span className="price-period">/月</span>
            </div>
            <div className="price-annual">年間 &yen;7,800</div>
            <ul className="pricing-features">
              <li><LuCheck size={16} className="check-icon" /> プロジェクト無制限</li>
              <li><LuCheck size={16} className="check-icon" /> クイズ生成 無制限</li>
              <li><LuCheck size={16} className="check-icon" /> GPT-4oモデル</li>
              <li><LuCheck size={16} className="check-icon" /> PDFエクスポート（予定）</li>
            </ul>
            <button className="cta-button secondary" onClick={goToAuth}>
              Proで始める
            </button>
          </div>
        </div>
      </section>

      <footer className="landing-footer">
        <div className="landing-footer-inner">
          <span className="footer-brand">MEX App</span>
          <span className="footer-copy">&copy; 2026 MEX App. All rights reserved.</span>
        </div>
      </footer>
    </div>
  );
};
