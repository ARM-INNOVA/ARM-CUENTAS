import { useNavigate } from 'react-router-dom'
import { useAuthStore } from './useStore'
import { authService } from '../services/api'
import { useCallback } from 'react'

const authDisabled = import.meta.env.VITE_AUTH_DISABLED === 'true'
const guestUser = {
  id: 0,
  username: 'invitado',
  full_name: 'Acceso temporal',
  role: 'admin',
}

export const useAuth = () => {
  const navigate = useNavigate()
  const authStore = useAuthStore()
  
  const login = useCallback(async (username, password) => {
    if (authDisabled) {
      authStore.login(guestUser, 'guest-session')
      navigate('/dashboard')
      return
    }

    try {
      const response = await authService.login(username, password)
      const { access_token, user } = response.data
      
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify(user))
      
      authStore.login(user, access_token)
      navigate('/dashboard')
    } catch (error) {
      throw error.response?.data?.detail || 'Error al iniciar sesión'
    }
  }, [authStore, navigate])
  
  const logout = useCallback(() => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    authStore.logout()
    navigate(authDisabled ? '/dashboard' : '/login')
  }, [authStore, navigate])
  
  return { ...authStore, login, logout }
}
