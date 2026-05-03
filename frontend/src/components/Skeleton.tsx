export function SkeletonCard() {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-md animate-pulse">
      <div className="h-6 bg-gray-200 dark:bg-slate-700 rounded w-1/3 mb-4" />
      <div className="space-y-2">
        <div className="h-4 bg-gray-200 dark:bg-slate-700 rounded w-full" />
        <div className="h-4 bg-gray-200 dark:bg-slate-700 rounded w-5/6" />
        <div className="h-4 bg-gray-200 dark:bg-slate-700 rounded w-4/6" />
      </div>
    </div>
  )
}