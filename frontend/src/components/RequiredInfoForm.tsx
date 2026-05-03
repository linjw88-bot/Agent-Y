import { useState } from 'react'

interface RequiredInfoFormProps {
  questions: string[]
  onSubmit: (answers: Record<string, string>) => void
  onSkip?: () => void
  isLoading: boolean
}

export default function RequiredInfoForm({ questions, onSubmit, onSkip, isLoading }: RequiredInfoFormProps) {
  const [answers, setAnswers] = useState<Record<string, string>>({})

  const handleChange = (index: number, value: string) => {
    setAnswers(prev => ({ ...prev, [`q${index}`]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(answers)
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-md">
      <div className="space-y-4">
        {questions.map((question, index) => (
          <div key={index}>
            <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">
              {question}
            </label>
            <input
              type="text"
              value={answers[`q${index}`] || ''}
              onChange={(e) => handleChange(index, e.target.value)}
              className="w-full p-3 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              placeholder="请输入您的回答"
            />
          </div>
        ))}
      </div>

      <div className="flex gap-4 mt-6">
        <button
          type="submit"
          disabled={isLoading}
          className="flex-1 bg-amber-500 text-white py-3 rounded-lg font-medium hover:bg-amber-600 disabled:opacity-50 transition-colors"
        >
          {isLoading ? '提交中...' : '提交'}
        </button>
        {onSkip && (
          <button
            type="button"
            onClick={onSkip}
            className="px-6 py-3 border border-gray-300 dark:border-slate-600 text-gray-700 dark:text-slate-300 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-slate-700 transition-colors"
          >
            跳过
          </button>
        )}
      </div>
    </form>
  )
}