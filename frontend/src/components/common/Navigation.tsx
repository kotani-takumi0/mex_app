/**
 * ナビゲーションコンポーネント
 *
 * 変更理由: React RouterのNavLinkに移行し、URL遷移対応。
 * react-iconsでアイコン追加、ハンバーガーメニューでモバイル対応。
 */
import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LuLayoutDashboard, LuPlus, LuLogOut, LuMenu, LuX, LuSettings } from 'react-icons/lu';
import { useAuth } from '../../contexts/AuthContext';
import './Navigation.css';

const pages = [
  { path: '/dashboard', label: 'ダッシュボード', icon: LuLayoutDashboard },
  { path: '/projects/new', label: '新規プロジェクト', icon: LuPlus },
  { path: '/settings', label: '設定', icon: LuSettings },
];

export const Navigation: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="main-navigation" aria-label="メインナビゲーション">
      <div className="nav-brand">
        <NavLink to="/dashboard" className="nav-brand-link">
          MEX App
        </NavLink>
      </div>

      <button
        className="nav-hamburger"
        onClick={() => setMenuOpen(!menuOpen)}
        aria-expanded={menuOpen}
        aria-label="メニュー"
      >
        {menuOpen ? <LuX size={24} /> : <LuMenu size={24} />}
      </button>

      <div className={`nav-menu ${menuOpen ? 'open' : ''}`}>
        <ul className="nav-links">
          {pages.map((page) => (
            <li key={page.path}>
              <NavLink
                to={page.path}
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                onClick={() => setMenuOpen(false)}
              >
                <page.icon className="nav-link-icon" size={18} />
                <span>{page.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>

        {user && (
          <div className="nav-user">
            <span className="user-name">{user.display_name}</span>
            <span className={`plan-badge ${user.plan}`}>
              {user.plan.toUpperCase()}
            </span>
            <button className="logout-btn" onClick={handleLogout} aria-label="ログアウト">
              <LuLogOut size={16} />
              <span className="logout-text">ログアウト</span>
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navigation;
