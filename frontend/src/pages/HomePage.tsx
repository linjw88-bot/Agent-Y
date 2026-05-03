import { Link } from 'react-router-dom'

export default function HomePage() {
  return (
    <div className="text-center">
      <h1 className="text-4xl font-bold mb-6 dark:text-white">
        AI 战略决策系统
      </h1>
      <p className="text-xl text-gray-600 dark:text-slate-300 mb-8 max-w-2xl mx-auto">
        像 AI 围棋一样思考，通过搜集顶级知识、分析未来情景，输出胜率最高的一步。
      </p>

      <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto mb-12">
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-md">
          <div className="text-4xl mb-4">🏭</div>
          <h3 className="text-lg font-bold mb-2 dark:text-white">行业智能识别</h3>
          <p className="text-gray-600 dark:text-slate-400 text-sm">
            自动识别问询所属行业领域
          </p>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-md">
          <div className="text-4xl mb-4">📚</div>
          <h3 className="text-lg font-bold mb-2 dark:text-white">顶级知识库</h3>
          <p className="text-gray-600 dark:text-slate-400 text-sm">
            3个初始行业的权威知识支撑
          </p>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-md">
          <div className="text-4xl mb-4">📊</div>
          <h3 className="text-lg font-bold mb-2 dark:text-white">多情景推演</h3>
          <p className="text-gray-600 dark:text-slate-400 text-sm">
            生成高/中/低概率情景进行分析
          </p>
        </div>
      </div>

      <Link
        to="/consultation"
        className="inline-block bg-amber-500 text-white px-8 py-4 rounded-lg font-medium text-lg hover:bg-amber-600 transition-colors"
      >
        开始咨询
      </Link>
    </div>
  )
}