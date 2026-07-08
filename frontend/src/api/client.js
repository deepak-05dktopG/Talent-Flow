import axios from 'axios'

// In development, Vite proxies /api to the backend.
// In production builds, VITE_API_URL provides the full backend URL.
const baseURL = import.meta.env.PROD
    ? `${import.meta.env.VITE_API_URL || ''}/api`
    : '/api'

const api = axios.create({
    baseURL,
    timeout: 30000,
})

// Attach JWT token to every request
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('talentflow_token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// Handle 401 globally
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('talentflow_token')
            localStorage.removeItem('talentflow_user')
            window.location.href = '/login'
        }
        return Promise.reject(error)
    }
)

export default api
