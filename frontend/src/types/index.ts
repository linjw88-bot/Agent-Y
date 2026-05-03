export interface AnalysisResult {
  id?: number
  conversation_id: number
  status: string
  industry_name: string
  confidence: number
  present_situation: string
  transformation: string
  future_possibility: string
  probability_distribution: Record<string, number>
  recommended_action: string
  leading_indicators: LeadingIndicator[]
  contingency_triggers: ContingencyTrigger[]
  knowledge_context: KnowledgeItem[]
  llm_analysis: string
  llm_available: boolean
  depth_analysis: DepthAnalysis
  created_at?: string
}

export interface LeadingIndicator {
  name: string
  description: string
  threshold?: string
}

export interface ContingencyTrigger {
  condition: string
  action: string
  priority: string
}

export interface KnowledgeItem {
  id: number
  title: string
  content: string
  summary: string
  source?: string
  relevance_score: number
}

export interface DepthAnalysis {
  situation_analysis?: string
  transformation_analysis?: string
  future_analysis?: string
}

export interface Industry {
  id: number
  name: string
  description?: string
  keywords?: string[]
}

export interface ConsultationResponse {
  conversation_id: number
  session_id: string
  identified_industry?: Industry
  required_info: string[]
  confidence: number
  can_proceed: boolean
}