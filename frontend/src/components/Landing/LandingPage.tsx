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
            開発過程を自動記録し、理解度を証明する新しいポートフォリオ。
            完成物だけでは伝わらない努力と学びを企業に届けます。
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
            <h3>理解度チェック</h3>
            <p>
              使用した技術の理解度を4択クイズで確認。
              苦手分野を可視化し、学び直しの指針にできます。
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon-circle">
              <LuLayoutDashboard size={28} />
            </div>
            <h3>新しいポートフォリオ</h3>
            <p>
              「完成物 + 過程 + 理解度」をまとめて提示。
              AI時代でも技術理解を証明できるポートフォリオを作れます。
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
              $0<span className="price-period">/月</span>
            </div>
            <ul className="pricing-features">
              <li><LuCheck size={16} className="check-icon" /> 開発ログの自動記録</li>
              <li><LuCheck size={16} className="check-icon" /> 理解度チェッククイズ</li>
              <li><LuCheck size={16} className="check-icon" /> 公開ポートフォリオ</li>
            </ul>
            <button className="cta-button" onClick={goToAuth}>
              無料で始める
            </button>
          </div>
          <div className="pricing-card">
            <div className="pricing-badge upcoming">
              <LuSparkles size={14} /> Coming Soon
            </div>
            <h3>Pro</h3>
            <div className="price muted">
              近日公開
            </div>
            <ul className="pricing-features">
              <li><LuCheck size={16} className="check-icon" /> 高度な分析レポート</li>
              <li><LuCheck size={16} className="check-icon" /> 追加テンプレート</li>
              <li><LuCheck size={16} className="check-icon" /> 優先サポート</li>
            </ul>
            <button className="cta-button secondary" disabled>
              通知を受け取る
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
