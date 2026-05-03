import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { conversationApi } from '../services/api'
import { useAppStore } from '../store/appStore'

export default function HistoryPage() {
  const { sessionId } = useAppStore()

  const { data: conversations, isLoading } = useQuery({
    queryKey: ['conversations', sessionId],
    queryFn: () => conversationApi.list(sessionId),
  })

  if (isLoading) {
    return <div className="text-gray-500 dark:text-slate-400">加载中...</div>
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8 dark:text-white">历史记录</h1>

      {conversations && conversations.length > 0 ? (
        <div className="space-y-4">
          {conversations.map((conv: { id: number; user_query: string; created_at?: string }) => (
            <Link
              key={conv.id}
              to={`/consultation?result=${conv.id}`}
              className="block bg-white dark:bg-slate-800 rounded-xl p-4 shadow-md hover:shadow-lg transition-shadow"
            >
              <p className="text-gray-800 dark:text-slate-200 line-clamp-2">
                {conv.user_query}
              </p>
              {conv.created_at && (
                <p className="text-sm text-gray-500 dark:text-slate-400 mt-2">
                  {new Date(conv.created_at).toLocaleString('zh-CN')}
                </p>
              )}
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center text-gray-500 dark:text-slate-400 py-12">
          暂无历史记录
        </div>
      )}
    </div>
  )
}