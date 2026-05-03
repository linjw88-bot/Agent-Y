import axios from 'axios'
import type { AnalysisResult, ConsultationResponse } from '../types'

const api = axios.create({
  baseURL: '/api/v1',
})

export const consultationApi = {
  submitQuery: async (query: string, sessionId: string): Promise<ConsultationResponse> => {
    const response = await api.post('/consultation', {
      query,
      session_id: sessionId,
    })
    return response.data
  },

  submitInfo: async (conversationId: number, answers: Record<string, string>) => {
    const response = await api.post('/consultation/info', {
      conversation_id: conversationId,
      answers,
    })
    return response.data
  },

  getResult: async (conversationId: number): Promise<AnalysisResult> => {
    const response = await api.get(`/consultation/${conversationId}/result`)
    return response.data
  },
}

export const industryApi = {
  list: async () => {
    const response = await api.get('/industries')
    return response.data
  },
}

export const knowledgeApi = {
  list: async (industryId?: number) => {
    const params = industryId ? { industry_id: industryId } : {}
    const response = await api.get('/knowledge', { params })
    return response.data
  },
}

export const conversationApi = {
  list: async (sessionId?: string) => {
    const params = sessionId ? { session_id: sessionId } : {}
    const response = await api.get('/conversations', { params })
    return response.data
  },
}