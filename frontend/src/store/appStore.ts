import { create } from 'zustand'

interface AppState {
  sessionId: string
  generateSessionId: () => string
}

export const useAppStore = create<AppState>((set, get) => ({
  sessionId: '',
  generateSessionId: () => {
    const newId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    set({ sessionId: newId })
    return newId
  },
}))