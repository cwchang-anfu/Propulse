/**
 * Main Layout Component
 * 主要布局組件（包含導航欄和側邊欄）
 */
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useStore } from '@/store/useStore';
import { Home, TrendingUp, FileText, LogOut } from 'lucide-react';

export default function Layout() {
  const location = useLocation();
  const { user, logout } = useStore();

  const navigation = [
    { name: 'Dashboard', path: '/', icon: Home },
    { name: '新聞列表', path: '/news', icon: FileText },
    { name: '歷史分析', path: '/history', icon: TrendingUp },
  ];

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 頂部導航欄 */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-2xl font-bold text-blue-600">
                  🏠 PropulseIQ
                </h1>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                {user?.email}
              </span>
              <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                {user?.subscription_tier.toUpperCase()}
              </span>
              <button
                onClick={handleLogout}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-gray-700 hover:bg-gray-100"
              >
                <LogOut className="w-4 h-4 mr-2" />
                登出
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* 主要內容區域 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 次級導航 */}
        <div className="mb-6">
          <nav className="flex space-x-4">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    inline-flex items-center px-3 py-2 rounded-md text-sm font-medium
                    ${
                      isActive
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }
                  `}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* 頁面內容 */}
        <main>
          <Outlet />
        </main>
      </div>

      {/* 頁尾 */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-500">
            <p>© 2025 PropulseIQ. All rights reserved.</p>
            <p className="mt-2">
              <Link to="/terms" className="hover:text-blue-600">使用條款</Link>
              {' · '}
              <Link to="/privacy" className="hover:text-blue-600">隱私政策</Link>
              {' · '}
              <Link to="/copyright" className="hover:text-blue-600">版權聲明</Link>
            </p>
            <p className="mt-2 text-xs">
              新聞內容著作權歸原媒體所有。本平台僅提供情緒分析服務。
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
