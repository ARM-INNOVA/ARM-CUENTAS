import { create } from 'zustand'

export const useAuthStore = create((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  
  login: (user, token) => set({
    user,
    token,
    isAuthenticated: true
  }),
  
  logout: () => set({
    user: null,
    token: null,
    isAuthenticated: false
  }),
  
  loadFromStorage: () => {
    const token = localStorage.getItem('token')
    const user = localStorage.getItem('user')
    
    if (token && user) {
      set({
        token,
        user: JSON.parse(user),
        isAuthenticated: true
      })
    }
  }
}))

export const useMovementsStore = create((set, get) => ({
  movements: [],
  loading: false,
  
  setMovements: (movements) => set({ movements }),
  setLoading: (loading) => set({ loading }),
  
  addMovement: (movement) => set(state => ({
    movements: [movement, ...state.movements]
  })),
  
  updateMovement: (id, data) => set(state => ({
    movements: state.movements.map(m => m.id === id ? { ...m, ...data } : m)
  })),
  
  deleteMovement: (id) => set(state => ({
    movements: state.movements.filter(m => m.id !== id)
  }))
}))

export const useDashboardStore = create((set) => ({
  summary: null,
  loading: false,
  
  setSummary: (summary) => set({ summary }),
  setLoading: (loading) => set({ loading })
}))
