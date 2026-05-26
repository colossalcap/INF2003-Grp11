import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || ''

const client = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
})

export function setAuthToken(token) {
  if (token) {
    client.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete client.defaults.headers.common['Authorization']
  }
}

// ============================================================
// Auth
// ============================================================
export async function login(username, password) {
  const formData = new URLSearchParams()
  formData.append('username', username)
  formData.append('password', password)

  const res = await client.post('/api/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return res.data
}

export async function register(username, email, password, displayName) {
  const res = await client.post('/api/auth/register', {
    username, email, password, display_name: displayName,
  })
  return res.data
}

export async function getMe() {
  const res = await client.get('/api/auth/me')
  return res.data
}

// ============================================================
// Products
// ============================================================
export async function getProducts(page = 1, category = '', search = '') {
  const params = { page, limit: 20 }
  if (category) params.category = category
  if (search) params.search = search
  const res = await client.get('/api/products/', { params })
  return res.data
}

export async function getCategories() {
  const res = await client.get('/api/products/categories/all')
  return res.data.categories
}

// ============================================================
// Cart / Clickstream
// ============================================================
export async function recordEvent(actionType, productId, sessionId) {
  const res = await client.post('/api/cart/event', {
    action_type: actionType,
    product_id: productId,
    session_id: sessionId,
  })
  return res.data
}

// ============================================================
// Orders
// ============================================================
export async function createOrder(items) {
  const res = await client.post('/api/orders/', { items })
  return res.data
}

// ============================================================
// Analytics
// ============================================================
export async function getRFM() {
  const res = await client.get('/api/analytics/rfm')
  return res.data
}

export async function getMarketBasket() {
  const res = await client.get('/api/analytics/market-basket')
  return res.data
}

export async function getFunnel() {
  const res = await client.get('/api/analytics/funnel')
  return res.data
}

export async function getAlerts() {
  const res = await client.get('/api/analytics/alerts')
  return res.data
}

export async function getTopProducts() {
  const res = await client.get('/api/analytics/top-products')
  return res.data
}

export async function getSalesByCategory() {
  const res = await client.get('/api/analytics/sales-by-category')
  return res.data
}
