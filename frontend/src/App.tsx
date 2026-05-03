import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import ConsultationPage from './pages/ConsultationPage'
import KnowledgePage from './pages/KnowledgePage'
import HistoryPage from './pages/HistoryPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="consultation" element={<ConsultationPage />} />
        <Route path="knowledge" element={<KnowledgePage />} />
        <Route path="history" element={<HistoryPage />} />
      </Route>
    </Routes>
  )
}

export default App