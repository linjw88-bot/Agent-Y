import { Outlet, Link, useLocation } from 'react-router-dom'

export default function Layout() {
  const location = useLocation()

  const navItems = [
    { path: '/', label: '首页' },
    { path: '/consultation', label: '决策咨询' },
    { path: '/knowledge', label: '知识库' },
    { path: '/history', label: '历史记录' },
  ]

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900">
      <header className="bg-white dark:bg-slate-800 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-amber-600 dark:text-amber-400">
              Agent YJ V2
            </h1>
            <nav className="flex gap-6">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`text-sm font-medium transition-colors ${
                    location.pathname === item.path
                      ? 'text-amber-600 dark:text-amber-400'
                      : 'text-gray-600 dark:text-slate-400 hover:text-amber-500'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}