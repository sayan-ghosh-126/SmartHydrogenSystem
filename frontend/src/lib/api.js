const envBase = import.meta.env.VITE_API_BASE_URL
let API_BASE = envBase
if (!API_BASE && typeof window !== 'undefined') {
  const origin = window.location.origin
  if (origin.includes('localhost')) {
    API_BASE = 'http://localhost:8000/api'
  } else {
    API_BASE = `${origin}/api`
  }
}
API_BASE = API_BASE || 'http://localhost:8000/api'

export const api = {
  get: async (url) => {
    const r = await fetch(`${API_BASE}${url}`)
    return r.json()
  },
  post: async (url, data) => {
    const r = await fetch(`${API_BASE}${url}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    return r.json()
  }
}

export const API_BASE_URL = API_BASE