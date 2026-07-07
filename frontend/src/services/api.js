import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const authDisabled = import.meta.env.VITE_AUTH_DISABLED === 'true'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Interceptor para agregar token a las solicitudes
apiClient.interceptors.request.use((config) => {
  if (authDisabled) {
    return config
  }

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
    if (!authDisabled && error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authService = {
  login: (username, password) => 
    apiClient.post('/auth/login', { username, password }),
  register: (data) => 
    apiClient.post('/auth/register', data),
  me: () =>
    apiClient.get('/auth/me'),
}

export const movementsService = {
  list: (params = {}) =>
    apiClient.get('/movements/', { params: { skip: 0, limit: 100, ...params } }),
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

export const categoriesService = {
  list: () => apiClient.get('/categories/'),
  create: (data) => apiClient.post('/categories/', data),
  update: (id, data) => apiClient.put(`/categories/${id}`, data),
  delete: (id) => apiClient.delete(`/categories/${id}`),
}

export const providersService = {
  list: (params = {}) => apiClient.get('/providers/', { params }),
  create: (data) => apiClient.post('/providers/', data),
  update: (id, data) => apiClient.put(`/providers/${id}`, data),
  delete: (id) => apiClient.delete(`/providers/${id}`),
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
  attach: (id, movementId) =>
    apiClient.post(`/files/${id}/attach`, { movement_id: movementId }),
  review: (id, data) =>
    apiClient.post(`/files/${id}/review`, data),
}

export const exportsService = {
  csv: (params = {}) => apiClient.get('/exports/movements.csv', { params, responseType: 'blob' }),
  excel: (params = {}) => apiClient.get('/exports/movements.xlsx', { params, responseType: 'blob' }),
  invoicesZip: (params) => apiClient.get('/exports/invoices.zip', { params, responseType: 'blob' }),
}

export default apiClient
