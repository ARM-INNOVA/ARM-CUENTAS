import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Interceptor para agregar token a las solicitudes
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, (error) => {
  return Promise.reject(error)
})

// Interceptor para manejo de errores
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
    return Promise.reject(error)
  }
)

export const authService = {
  login: (username, password) => 
    apiClient.post('/auth/login', { username, password }),
  register: (data) => 
    apiClient.post('/auth/register', data),
}

export const movementsService = {
  list: (skip = 0, limit = 100) =>
    apiClient.get('/movements/', { params: { skip, limit } }),
  create: (data) =>
    apiClient.post('/movements/', data),
  get: (id) =>
    apiClient.get(`/movements/${id}`),
  update: (id, data) =>
    apiClient.put(`/movements/${id}`, data),
  delete: (id) =>
    apiClient.delete(`/movements/${id}`),
  getDashboard: () =>
    apiClient.get('/movements/dashboard/summary'),
}

export const obrasService = {
  list: (estado) =>
    apiClient.get('/obras/', { params: { estado } }),
  create: (data) =>
    apiClient.post('/obras/', data),
  get: (id) =>
    apiClient.get(`/obras/${id}`),
  update: (id, data) =>
    apiClient.put(`/obras/${id}`, data),
  delete: (id) =>
    apiClient.delete(`/obras/${id}`),
}

export const filesService = {
  upload: (file, movementId = null) => {
    const formData = new FormData()
    formData.append('file', file)
    if (movementId) {
      formData.append('movement_id', movementId)
    }
    return apiClient.post('/files/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  get: (id) =>
    apiClient.get(`/files/${id}`),
  download: (id) =>
    apiClient.get(`/files/${id}/download`, { responseType: 'blob' }),
  extract: (id) =>
    apiClient.post(`/files/${id}/extract`),
}

export default apiClient
