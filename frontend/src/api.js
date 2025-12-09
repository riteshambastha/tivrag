import axios from 'axios'

const API_BASE_URL = 'http://localhost:8002'

const api = axios.create({
  baseURL: API_BASE_URL,
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authAPI = {
  signup: (username, password) => api.post('/api/signup', { username, password }),
  login: (username, password) => api.post('/api/login', { username, password }),
  getMe: () => api.get('/api/me'),
}

export const googleAPI = {
  getAuthUrl: () => api.get('/api/google/auth-url'),
  handleCallback: (code) => api.post('/api/google/callback', { authorization_code: code }),
  getStatus: () => api.get('/api/google/status'),
  disconnect: () => api.delete('/api/google/disconnect'),
}

export const searchAPI = {
  search: (query, person) => api.post('/api/search', { query, person }),
}

export default api

