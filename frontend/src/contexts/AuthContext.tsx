/**
 * 認証コンテキスト
 * アプリ全体の認証状態を管理
 */
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { User } from '../types';
import { getAuthToken, clearAuthToken, onAuthError } from '../api/client';
import { getMe } from '../api/auth';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  setUser: () => {},
  logout: () => {},
  refreshUser: async () => {},
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const logout = useCallback(() => {
    clearAuthToken();
    setUser(null);
  }, []);

  const refreshUser = useCallback(async () => {
    const token = getAuthToken();
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    const result = await getMe();
    if (result.data) {
      setUser(result.data);
    } else {
      clearAuthToken();
      setUser(null);
    }
    setIsLoading(false);
  }, []);

  // 初回ロード時にトークンがあればユーザー情報を取得
  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  // 認証エラーリスナー
  useEffect(() => {
    const unsubscribe = onAuthError(() => {
      logout();
    });
    return unsubscribe;
  }, [logout]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        setUser,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
