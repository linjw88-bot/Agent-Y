import { useQuery } from '@tanstack/react-query'
import { knowledgeApi, industryApi } from '../services/api'

export default function KnowledgePage() {
  const industriesQuery = useQuery({
    queryKey: ['industries'],
    queryFn: industryApi.list,
  })

  const knowledgeQuery = useQuery({
    queryKey: ['knowledge'],
    queryFn: () => knowledgeApi.list(),
  })

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8 dark:text-white">知识库</h1>

      {industriesQuery.isLoading || knowledgeQuery.isLoading ? (
        <div className="text-gray-500 dark:text-slate-400">加载中...</div>
      ) : (
        <div className="space-y-8">
          {industriesQuery.data?.map((industry: { id: number; name: string; description?: string }) => {
            const industryKnowledge = knowledgeQuery.data?.filter(
              (k: { industry_id: number }) => k.industry_id === industry.id
            )

            return (
              <div key={industry.id} className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-md">
                <h2 className="text-xl font-bold mb-2 dark:text-white">{industry.name}</h2>
                {industry.description && (
                  <p className="text-gray-600 dark:text-slate-400 text-sm mb-4">
                    {industry.description}
                  </p>
                )}
                <div className="space-y-3">
                  {industryKnowledge?.map((item: { id: number; title: string; content: string; category?: string }) => (
                    <div key={item.id} className="border border-gray-100 dark:border-slate-600 rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-medium text-gray-800 dark:text-slate-200">{item.title}</h3>
                          {item.content && (
                            <p className="text-sm text-gray-500 dark:text-slate-400 mt-1">
                              {item.content.slice(0, 200)}...
                            </p>
                          )}
                        </div>
                        {item.category && (
                          <span className="text-xs bg-gray-100 dark:bg-slate-700 text-gray-600 dark:text-slate-300 px-2 py-1 rounded">
                            {item.category}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}