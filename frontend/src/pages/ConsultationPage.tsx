import { useState, useRef, useCallback, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { consultationApi } from '../services/api'
import { useAppStore } from '../store/appStore'
import ProbabilityChart from '../components/ProbabilityChart'
import RequiredInfoForm from '../components/RequiredInfoForm'
import { SkeletonCard } from '../components/Skeleton'
import type { AnalysisResult } from '../types'

type ConsultationStep = 'input' | 'info_needed' | 'analyzing' | 'result'

const POLL_INTERVAL_MS = 2000

export default function ConsultationPage() {
  const [step, setStep] = useState<ConsultationStep>('input')
  const [query, setQuery] = useState('')
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [conversationId, setConversationId] = useState<number | null>(null)
  const [identifiedIndustry, setIdentifiedIndustry] = useState<string | null>(null)
  const [requiredInfo, setRequiredInfo] = useState<string[]>([])
  const [shareUrl, setShareUrl] = useState<string | null>(null)

  const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const { generateSessionId, sessionId } = useAppStore()
  const [searchParams] = useSearchParams()

  useEffect(() => {
    const resultId = searchParams.get('result')
    if (resultId) {
      const cid = parseInt(resultId, 10)
      setConversationId(cid)
      setStep('analyzing')
      startPolling(cid)
    }
  }, [])

  const stopPolling = useCallback(() => {
    if (pollTimerRef.current !== null) {
      clearInterval(pollTimerRef.current)
      pollTimerRef.current = null
    }
  }, [])

  const startPolling = useCallback((cid: number) => {
    stopPolling()
    pollTimerRef.current = setInterval(async () => {
      try {
        const data = await consultationApi.getResult(cid)
        if (data.status === 'done') {
          stopPolling()
          setResult(data as unknown as AnalysisResult)
          setStep('result')
        }
      } catch {
        stopPolling()
        toast.error('获取结果失败')
        setStep('input')
      }
    }, POLL_INTERVAL_MS)
  }, [stopPolling])

  const submitQueryMutation = useMutation({
    mutationFn: async (q: string) => {
      const sid = sessionId || generateSessionId()
      return consultationApi.submitQuery(q, sid)
    },
    onSuccess: (data) => {
      if (data.can_proceed) {
        setConversationId(data.conversation_id)
        setStep('analyzing')
        startPolling(data.conversation_id)
      } else {
        setConversationId(data.conversation_id)
        setIdentifiedIndustry(data.identified_industry?.name)
        setRequiredInfo(data.required_info || [])
        setStep('info_needed')
      }
    },
    onError: () => {
      toast.error('提交失败，请稍后重试')
    },
  })

  const submitInfoMutation = useMutation({
    mutationFn: async (answers: Record<string, string>) => {
      return consultationApi.submitInfo(conversationId!, answers)
    },
    onSuccess: () => {
      setStep('analyzing')
      startPolling(conversationId!)
    },
    onError: () => {
      toast.error('提交失败，请稍后重试')
    },
  })

  const handleSubmit = () => {
    if (query.trim()) {
      submitQueryMutation.mutate(query)
    }
  }

  const handleInfoSubmit = (answers: Record<string, string>) => {
    submitInfoMutation.mutate(answers)
  }

  const handleShare = () => {
    if (!result) return
    const markdown = generateMarkdown(result, conversationId)
    navigator.clipboard.writeText(markdown).then(() => {
      toast.success('分析结果已复制到剪贴板')
    }).catch(() => {
      toast.error('复制失败，请手动复制')
    })
    if (conversationId) {
      const url = `${window.location.origin}/consultation?result=${conversationId}`
      setShareUrl(url)
    }
  }

  const reset = () => {
    stopPolling()
    setStep('input')
    setQuery('')
    setResult(null)
    setConversationId(null)
    setShareUrl(null)
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-center mb-8 dark:text-white">决策咨询</h1>

      <div className="flex justify-center mb-8">
        <div className="flex items-center gap-2">
          {(['input', 'info_needed', 'analyzing', 'result'] as ConsultationStep[]).map((label, i) => {
            const currentIndex = { input: 0, info_needed: 1, analyzing: 2, result: 3 }[step]
            const labels = ['输入问题', '补充信息', '深度分析中', '查看结果']
            return (
              <div key={label} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors ${
                  i <= currentIndex
                    ? 'bg-amber-500 text-white'
                    : 'bg-gray-200 dark:bg-slate-700 text-gray-500 dark:text-slate-400'
                }`}>
                  {i + 1}
                </div>
                <span className="ml-2 text-sm hidden md:inline dark:text-slate-300">{labels[i]}</span>
                {i < 3 && <div className="w-8 h-0.5 bg-gray-200 dark:bg-slate-700 mx-2" />}
              </div>
            )
          })}
        </div>
      </div>

      {step === 'input' && (
        <div className="bg-white dark:bg-slate-800 dark:border dark:border-slate-700 rounded-xl p-6 shadow-md animate-fade-in">
          <label className="block mb-4">
            <span className="text-lg font-medium dark:text-white">描述您面临的决策问题：</span>
            <textarea
              className="mt-2 w-full p-4 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent resize-none"
              rows={6}
              placeholder="例如：我现在有一笔闲钱，是应该投入股市还是配置一些债券基金？风险承受能力一般，希望在未来3-5年获得稳定收益。"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </label>
          <button
            onClick={handleSubmit}
            disabled={!query.trim() || submitQueryMutation.isPending}
            className="w-full bg-gradient-to-r from-amber-500 to-amber-600 text-white py-3 rounded-lg font-medium hover:from-amber-600 hover:to-amber-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {submitQueryMutation.isPending ? '提交中...' : '提交咨询'}
          </button>
        </div>
      )}

      {step === 'info_needed' && (
        <div className="animate-fade-in">
          <div className="bg-amber-50 dark:bg-amber-950/40 dark:text-amber-200 rounded-xl p-4 mb-6 border border-amber-200 dark:border-amber-800">
            <p className="text-amber-800 dark:text-amber-300">
              <span className="font-bold">行业识别：</span>
              {identifiedIndustry || '待确认'}
            </p>
            <p className="text-amber-600 dark:text-amber-400 text-sm mt-1">
              为了给您更精准的分析，请补充以下信息：
            </p>
          </div>
          <RequiredInfoForm
            questions={requiredInfo}
            onSubmit={handleInfoSubmit}
            onSkip={() => {
              const emptyAnswers: Record<string, string> = {}
              requiredInfo.forEach((_, i) => { emptyAnswers[`q${i}`] = '' })
              submitInfoMutation.mutate(emptyAnswers)
            }}
            isLoading={submitInfoMutation.isPending}
          />
        </div>
      )}

      {step === 'analyzing' && (
        <div className="space-y-4 animate-fade-in">
          <div className="bg-white dark:bg-slate-800 dark:border dark:border-slate-700 rounded-xl p-8 shadow-md text-center">
            <div className="text-6xl mb-4 animate-pulse">📊</div>
            <p className="text-lg font-medium mb-2 dark:text-white">正在为您深度分析</p>
            <p className="text-gray-500 dark:text-slate-400 text-sm mb-6">
              结合行业顶级知识与多情景推演，进行综合分析
            </p>
            <div className="flex justify-center gap-3 text-sm">
              <span className="text-gray-400 dark:text-slate-500">🔍 检索知识库</span>
              <span className="text-amber-500">→</span>
              <span className="text-gray-400 dark:text-slate-500">📈 情景推演</span>
              <span className="text-amber-500">→</span>
              <span className="text-gray-400 dark:text-slate-500">🎯 计算胜率</span>
            </div>
            <p className="text-xs text-gray-400 dark:text-slate-500 mt-6">
              您也可以稍后回来，在历史记录中查看完整分析结果
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SkeletonCard />
            <SkeletonCard />
          </div>
          <SkeletonCard />
        </div>
      )}

      {step === 'result' && result && (
        <div className="space-y-6 animate-fade-in">
          <div className="bg-white dark:bg-slate-800 dark:border dark:border-slate-700 rounded-xl p-6 shadow-md">
            <h2 className="text-xl font-bold mb-4 text-center dark:text-white">
              {result.industry_name || '综合'} 领域分析
            </h2>
            <div className="text-center">
              <p className="text-2xl font-bold dark:text-white">
                置信度：{Math.round(result.confidence * 100)}%
              </p>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-800 dark:border dark:border-slate-700 rounded-xl p-6 shadow-md">
            <h2 className="text-xl font-bold mb-4 dark:text-white">📊 形势评估</h2>
            <div className="space-y-4">
              {[
                { label: '当前形势', key: 'present_situation' as const },
                { label: '变化趋势', key: 'transformation' as const },
                { label: '未来可能', key: 'future_possibility' as const },
              ].map(({ label, key }) => (
                <div key={key}>
                  <h3 className="font-medium text-gray-700 dark:text-slate-200 mb-1">{label}</h3>
                  <p className="text-gray-600 dark:text-slate-300 bg-gray-50 dark:bg-slate-700 p-3 rounded-lg">{result[key]}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white dark:bg-slate-800 dark:border dark:border-slate-700 rounded-xl p-6 shadow-md">
            <h2 className="text-xl font-bold mb-4 dark:text-white">📈 胜率分析</h2>
            <ProbabilityChart distribution={result.probability_distribution} />
          </div>

          <div className="bg-gradient-to-r from-amber-500 to-amber-600 rounded-xl p-6 text-white shadow-lg">
            <h2 className="text-xl font-bold mb-2">🎯 推荐方案</h2>
            <p className="text-lg">{result.recommended_action}</p>
          </div>

          <div className="bg-white dark:bg-slate-800 dark:border dark:border-slate-700 rounded-xl p-6 shadow-md">
            <h2 className="text-xl font-bold mb-4 dark:text-white">👀 预警信号</h2>
            <div className="space-y-3">
              {result.leading_indicators.map((indicator, i) => (
                <div key={i} className="flex items-start gap-3 p-3 bg-gray-50 dark:bg-slate-700 rounded-lg">
                  <span className="text-amber-500 mt-1">▸</span>
                  <div>
                    <p className="font-medium dark:text-white">{indicator.name}</p>
                    <p className="text-sm text-gray-500 dark:text-slate-300">{indicator.description}</p>
                    {indicator.threshold && (
                      <p className="text-xs text-amber-600 dark:text-amber-400 mt-1">阈值: {indicator.threshold}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {result.knowledge_context && result.knowledge_context.length > 0 && (
            <div className="bg-white dark:bg-slate-800 dark:border dark:border-slate-700 rounded-xl p-6 shadow-md">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2 dark:text-white">
                <span>📚</span> 参考来源
              </h2>
              <div className="space-y-3">
                {result.knowledge_context.slice(0, 6).map((item, i) => (
                  <div key={item.id ?? i} className="border border-gray-100 dark:border-slate-600 rounded-lg p-3">
                    <p className="font-medium text-gray-800 dark:text-slate-200 text-sm">{item.title}</p>
                    {item.content && (
                      <p className="text-xs text-gray-500 dark:text-slate-400 mt-1 line-clamp-2">
                        {item.content.replace(/\n/g, ' ').slice(0, 150)}…
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex gap-4">
            <button
              onClick={reset}
              className="flex-1 bg-gray-200 dark:bg-slate-700 dark:text-slate-200 text-gray-700 py-3 rounded-lg font-medium hover:bg-gray-300 dark:hover:bg-slate-600 transition-colors"
            >
              新建咨询
            </button>
            <button
              onClick={handleShare}
              className="flex-1 bg-amber-500 text-white py-3 rounded-lg font-medium hover:bg-amber-600 transition-colors"
            >
              复制结果
            </button>
          </div>

          {shareUrl && (
            <div className="bg-green-50 dark:bg-green-950/40 dark:text-green-300 dark:border-green-800 border border-green-200 rounded-lg p-3 text-sm text-green-700">
              分享链接：<span className="font-mono break-all">{shareUrl}</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function generateMarkdown(result: AnalysisResult, conversationId: number | null): string {
  const probLines = Object.entries(result.probability_distribution)
    .map(([k, v]) => `- **${k}**: ${(Number(v) * 100).toFixed(0)}%`)
    .join('\n')

  const indicatorLines = result.leading_indicators
    .map(ind => `- **${ind.name}**: ${ind.description}`)
    .join('\n')

  return `# Agent YJ 战略决策分析

## 分析领域
- **行业**: ${result.industry_name || '综合'}
- **置信度**: ${Math.round(result.confidence * 100)}%

## 📊 形势评估

**当前形势**
${result.present_situation}

**变化趋势**
${result.transformation}

**未来可能**
${result.future_possibility}

## 📈 胜率分析
${probLines}

## 🎯 推荐方案
${result.recommended_action}

## 👀 预警信号
${indicatorLines}

---
*由 Agent YJ V2 生成 | ${conversationId ? `ID: ${conversationId}` : ''}*
`
}