/**
 * ランディングページ
 * 未認証ユーザー向けの紹介ページ
 *
 * 変更理由:
 * - ヒーローを「機能説明」→「痛み共感」型コピーに刷新
 * - CSS-onlyのブラウザモックアップでプロダクトを視覚化
 * - ペインポイントセクション追加でターゲットの共感を獲得
 * - Step 3をクイズ→学習ハブに更新（現在の機能に合わせて）
 * - 中間CTAセクション追加
 * - Pricingのクイズ参照を修正
 */
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  LuCheck,
  LuSparkles,
  LuArrowRight,
  LuBookOpen,
} from 'react-icons/lu';
import { ClaudeIcon, NotionIcon, NotebookLMIcon, MexIcon } from './BrandIcons';
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

      {/* ===== ヒーロー: 痛み共感型 ===== */}
      <section className="landing-hero" aria-labelledby="hero-title">
        <div className="landing-hero-inner">
          <p className="hero-pain-hook" aria-hidden="true">
            &ldquo;これ、AIに書かせただけじゃないの？&rdquo;
          </p>
          <h1 id="hero-title" className="hero-title">
            その質問に、胸を張って
            <br />
            答えられるポートフォリオを。
          </h1>
          <p className="hero-description">
            開発過程を自動記録し、技術ドキュメントを自動生成。
            「本当に理解している」と伝えられる、新しいポートフォリオを作ろう。
          </p>
          <div className="hero-actions">
            <button className="cta-button" onClick={goToAuth}>
              無料で始める
              <LuArrowRight size={16} />
            </button>
            <span className="hero-note">
              クレジットカード不要 / 2プロジェクトまで無料
            </span>
          </div>
        </div>
      </section>

      {/* ===== プロダクトプレビュー: CSS-onlyモックアップ ===== */}
      <section className="landing-preview" aria-label="プロダクトプレビュー">
        <div className="preview-browser">
          <div className="preview-browser-bar">
            <div className="preview-dots">
              <span className="dot dot-red" />
              <span className="dot dot-yellow" />
              <span className="dot dot-green" />
            </div>
            <div className="preview-url">
              <span className="preview-lock">&#x1f512;</span>
              mex.app/p/takumi
            </div>
          </div>
          <div className="preview-content">
            {/* ポートフォリオヘッダー */}
            <div className="mock-header">
              <div className="mock-avatar" />
              <div className="mock-header-text">
                <div className="mock-name">takumi</div>
                <div className="mock-bio-line" />
              </div>
            </div>

            {/* プロジェクトカード */}
            <div className="mock-projects">
              <div className="mock-project-card mock-project-featured">
                <div className="mock-project-title">MEX App</div>
                <div className="mock-tags">
                  <span className="mock-tag tag-react">React</span>
                  <span className="mock-tag tag-python">FastAPI</span>
                  <span className="mock-tag tag-ts">TypeScript</span>
                </div>
                <div className="mock-stat">
                  <span className="mock-stat-dot" />
                  開発記録 12件
                </div>
              </div>
              <div className="mock-project-card">
                <div className="mock-project-title">Blog App</div>
                <div className="mock-tags">
                  <span className="mock-tag tag-next">Next.js</span>
                  <span className="mock-tag tag-prisma">Prisma</span>
                </div>
                <div className="mock-stat">
                  <span className="mock-stat-dot" />
                  開発記録 8件
                </div>
              </div>
            </div>

            {/* 開発記録エントリ + Notion連携 */}
            <div className="mock-devlog">
              <div className="mock-devlog-header">
                <span className="mock-devlog-label">開発記録</span>
                <span className="mock-service-badge badge-notion">Notion 連携</span>
              </div>
              <div className="mock-devlog-entry">
                <div className="mock-entry-header">
                  <span className="mock-entry-dot" />
                  <span className="mock-entry-title">
                    React Router の実装とルーティング設計
                  </span>
                </div>
                <div className="mock-entry-body">
                  <div className="mock-text-line w80" />
                  <div className="mock-text-line w60" />
                </div>
                {/* 「学んだこと」ハイライト ― MEXの核心 */}
                <div className="mock-learned">
                  <span className="mock-learned-label">学んだこと</span>
                  <div className="mock-learned-text">
                    &ldquo;ネストされたルートの設計で、Outlet
                    を使ったレイアウト共有パターンを理解した…&rdquo;
                  </div>
                </div>
              </div>
            </div>

            {/* 学習ハブ — NotebookLM連携を可視化 */}
            <div className="mock-learning-hub">
              <div className="mock-devlog-header">
                <span className="mock-devlog-label">学習ハブ</span>
                <span className="mock-service-badge badge-notebooklm">NotebookLM</span>
              </div>
              <div className="mock-learning-items">
                <div className="mock-learning-item">
                  <span className="mock-learning-icon">&#x1f399;</span>
                  <span className="mock-learning-name">音声オーバービュー</span>
                  <span className="mock-learning-meta">12:34</span>
                </div>
                <div className="mock-learning-item">
                  <span className="mock-learning-icon">&#x1f4dd;</span>
                  <span className="mock-learning-name">フラッシュカード</span>
                  <span className="mock-learning-meta">8枚</span>
                </div>
                <div className="mock-learning-item">
                  <span className="mock-learning-icon">&#x1f4c4;</span>
                  <span className="mock-learning-name">学習ノート</span>
                  <span className="mock-learning-meta">自動生成</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== ペインポイント ===== */}
      <section className="landing-pain" aria-labelledby="pain-title">
        <h2 id="pain-title" className="section-title">
          こんな経験、ありませんか？
        </h2>
        <div className="pain-grid">
          <div className="pain-card">
            <blockquote className="pain-quote">
              &ldquo;ポートフォリオ見ました。でも、ここの実装、説明できますか？&rdquo;
            </blockquote>
            <p className="pain-desc">
              面接で技術的な深掘りをされて、うまく答えられなかった。
            </p>
          </div>
          <div className="pain-card">
            <blockquote className="pain-quote">
              &ldquo;GitHub見たけど、AI生成っぽいコードが多いね&rdquo;
            </blockquote>
            <p className="pain-desc">
              コードがあるだけでは、自分の理解度は伝わらない。
            </p>
          </div>
          <div className="pain-card">
            <blockquote className="pain-quote">
              &ldquo;他のスクール卒業生と、何が違うの？&rdquo;
            </blockquote>
            <p className="pain-desc">
              同じ技術スタック、同じような成果物。差別化できない。
            </p>
          </div>
        </div>
      </section>

      {/* ===== 特徴（4枚・2x2、各カードに連携サービスバッジ） ===== */}
      <section className="landing-features" aria-labelledby="features-title">
        <h2 id="features-title" className="section-title">
          MEXが解決します
        </h2>
        <div className="features-grid">
          <div className="feature-card">
            <span className="feature-badge badge-claude">Claude Code</span>
            <div className="feature-icon-circle icon-claude">
              <ClaudeIcon size={28} />
            </div>
            <h3>開発過程の自動記録</h3>
            <p>
              MCPサーバーでAI開発の過程を自動キャプチャ。手入力の手間なく、
              いつ・何を・どう作ったかが残ります。
            </p>
          </div>
          <div className="feature-card">
            <span className="feature-badge badge-notion">Notion</span>
            <div className="feature-icon-circle icon-notion">
              <NotionIcon size={28} />
            </div>
            <h3>技術ドキュメント自動生成</h3>
            <p>
              コミットからNotionに教育的ドキュメントを自動生成。
              WHY・HOWの解説とQ&Aで、使った技術を深く理解できます。
            </p>
          </div>
          <div className="feature-card">
            <span className="feature-badge badge-notebooklm">NotebookLM</span>
            <div className="feature-icon-circle icon-notebooklm">
              <NotebookLMIcon size={28} />
            </div>
            <h3>学習コンテンツで理解を深める</h3>
            <p>
              NotebookLMが音声オーバービュー、フラッシュカード、学習ノートを自動生成。
              耳から・目から、多角的に技術を身につけます。
            </p>
          </div>
          <div className="feature-card">
            <span className="feature-badge badge-mex">MEX</span>
            <div className="feature-icon-circle icon-mex">
              <MexIcon size={28} />
            </div>
            <h3>理解を自分の言葉で証明</h3>
            <p>
              学んだことを自分の言葉でアプリに記録。
              面接官が「本当に理解しているか」を判別できるポートフォリオです。
            </p>
          </div>
        </div>
      </section>

      {/* ===== 使い方 ===== */}
      <section className="landing-steps" aria-labelledby="steps-title">
        <h2 id="steps-title" className="section-title">
          使い方
        </h2>
        <ol className="steps-list">
          <li className="step-item">
            <span className="step-number">1</span>
            <div>
              <h3>プロジェクトを作成</h3>
              <p>
                開発中のプロジェクトを登録し、MCP Serverを接続。
              </p>
            </div>
          </li>
          <li className="step-item">
            <span className="step-number">2</span>
            <div>
              <h3>開発しながら自動記録</h3>
              <p>
                Claude Codeで開発するだけで、過程が自動的にMEXに記録されます。
              </p>
            </div>
          </li>
          <li className="step-item">
            <span className="step-number">3</span>
            <div>
              <h3>学んで、理解を記録</h3>
              <p>
                自動生成されたドキュメントと学習コンテンツで復習し、理解を自分の言葉でポートフォリオに残します。
              </p>
            </div>
          </li>
        </ol>
      </section>

      {/* ===== 中間CTA ===== */}
      <section className="landing-midcta" aria-label="登録を促すセクション">
        <div className="midcta-inner">
          <LuBookOpen size={32} className="midcta-icon" />
          <h2 className="midcta-title">
            「作れる」から「理解している」へ
          </h2>
          <p className="midcta-description">
            あなたの開発過程が、そのまま最強のポートフォリオになる。
          </p>
          <button className="cta-button" onClick={goToAuth}>
            無料で始める
            <LuArrowRight size={16} />
          </button>
        </div>
      </section>

      {/* ===== 料金プラン ===== */}
      <section className="landing-pricing" aria-labelledby="pricing-title">
        <h2 id="pricing-title" className="section-title">
          料金プラン
        </h2>
        <div className="pricing-cards">
          <div className="pricing-card featured">
            <div className="pricing-badge">まずは無料で</div>
            <h3>Free</h3>
            <div className="price">
              &yen;0<span className="price-period">/月</span>
            </div>
            <ul className="pricing-features">
              <li>
                <LuCheck size={16} className="check-icon" /> プロジェクト2件
              </li>
              <li>
                <LuCheck size={16} className="check-icon" /> 学習コンテンツ生成
              </li>
              <li>
                <LuCheck size={16} className="check-icon" /> 公開ポートフォリオ
              </li>
              <li>
                <LuCheck size={16} className="check-icon" /> 開発記録の自動保存
              </li>
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
              <li>
                <LuCheck size={16} className="check-icon" /> プロジェクト無制限
              </li>
              <li>
                <LuCheck size={16} className="check-icon" /> 学習コンテンツ 無制限
              </li>
              <li>
                <LuCheck size={16} className="check-icon" /> 高精度AIモデル
              </li>
              <li>
                <LuCheck size={16} className="check-icon" /> PDFエクスポート（予定）
              </li>
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
          <span className="footer-copy">
            &copy; 2026 MEX App. All rights reserved.
          </span>
        </div>
      </footer>
    </div>
  );
};
