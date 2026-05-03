import { describe, it, expect, vi } from 'vitest'
import { consultationApi, industryApi, knowledgeApi, conversationApi } from '../services/api'

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: () => ({
      get: vi.fn(),
      post: vi.fn(),
    }),
  },
}))

describe('API Services', () => {
  describe('consultationApi', () => {
    it('should have submitQuery method', () => {
      expect(typeof consultationApi.submitQuery).toBe('function')
    })

    it('should have submitInfo method', () => {
      expect(typeof consultationApi.submitInfo).toBe('function')
    })

    it('should have getResult method', () => {
      expect(typeof consultationApi.getResult).toBe('function')
    })
  })

  describe('industryApi', () => {
    it('should have list method', () => {
      expect(typeof industryApi.list).toBe('function')
    })
  })

  describe('knowledgeApi', () => {
    it('should have list method', () => {
      expect(typeof knowledgeApi.list).toBe('function')
    })
  })

  describe('conversationApi', () => {
    it('should have list method', () => {
      expect(typeof conversationApi.list).toBe('function')
    })
  })
})