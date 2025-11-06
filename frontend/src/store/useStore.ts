/**
 * Zustand Global Store
 * 全域狀態管理
 */
import { create } from 'zustand';
import type { User } from '@/types';
import { apiClient } from '@/services/api';

interface AppStore {
  // 使用者狀態
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // Actions
  setUser: (user: User | null) => void;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  fetchCurrentUser: () => Promise<void>;
}

export const useStore = create<AppStore>((set) => ({
  // Initial state
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,

  // Actions
  setUser: (user) => set({ user, isAuthenticated: !!user }),

  login: async (email, password) => {
    set({ isLoading: true });
    try {
      await apiClient.login({ username: email, password });
      const user = await apiClient.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  register: async (email, password, fullName) => {
    set({ isLoading: true });
    try {
      await apiClient.register({ email, password, full_name: fullName });
      // 註冊後自動登入
      await apiClient.login({ username: email, password });
      const user = await apiClient.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: () => {
    apiClient.logout();
    set({ user: null, isAuthenticated: false });
  },

  fetchCurrentUser: async () => {
    if (!localStorage.getItem('access_token')) {
      return;
    }

    set({ isLoading: true });
    try {
      const user = await apiClient.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },
}));
