import { create } from 'zustand'

const guestUser = {
  id: 0,
  username: 'invitado',
  full_name: 'Acceso temporal',
  role: 'admin',
}

export const useAuthStore = create((set) => ({
  user: guestUser,
  token: null,
  isAuthenticated: true,
  
  login: (user, token) => set({
    user,
    token,
    isAuthenticated: true
  }),
  
  logout: () => set({
    user: guestUser,
    token: null,
    isAuthenticated: true
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
      return
    }

    set({
      token: null,
      user: guestUser,
      isAuthenticated: true
    })
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
