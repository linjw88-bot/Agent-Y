interface ProbabilityChartProps {
  distribution: Record<string, number>
}

export default function ProbabilityChart({ distribution }: ProbabilityChartProps) {
  const entries = Object.entries(distribution)

  if (entries.length === 0) {
    return <div className="text-gray-500 dark:text-slate-400 text-center py-4">暂无数据</div>
  }

  const maxValue = Math.max(...entries.map(([, v]) => Number(v)))

  return (
    <div className="space-y-3">
      {entries.map(([name, value]) => {
        const pct = Number(value) * 100
        const width = (Number(value) / maxValue) * 100

        return (
          <div key={name} className="relative">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-gray-700 dark:text-slate-300">
                {name}
              </span>
              <span className="text-sm font-bold text-amber-600 dark:text-amber-400">
                {pct.toFixed(0)}%
              </span>
            </div>
            <div className="h-3 bg-gray-200 dark:bg-slate-600 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-amber-400 to-amber-500 rounded-full transition-all duration-500"
                style={{ width: `${width}%` }}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}