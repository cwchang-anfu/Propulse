/**
 * PropulseIQ - Main App Component
 */
import { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useStore } from '@/store/useStore';
import Layout from '@/components/Layout';
import Dashboard from '@/pages/Dashboard';
import News from '@/pages/News';
import History from '@/pages/History';
import Login from '@/pages/Login';
import Register from '@/pages/Register';
import Terms from '@/pages/Terms';
import Privacy from '@/pages/Privacy';
import Copyright from '@/pages/Copyright';

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useStore((state) => state.isAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

function App() {
  const fetchCurrentUser = useStore((state) => state.fetchCurrentUser);

  // 初始化時檢查使用者登入狀態
  useEffect(() => {
    fetchCurrentUser();
  }, [fetchCurrentUser]);

  return (
    <Routes>
      {/* 公開路由 */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/terms" element={<Terms />} />
      <Route path="/privacy" element={<Privacy />} />
      <Route path="/copyright" element={<Copyright />} />

      {/* 受保護的路由 */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="news" element={<News />} />
        <Route path="history" element={<History />} />
      </Route>

      {/* 404 頁面 */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
