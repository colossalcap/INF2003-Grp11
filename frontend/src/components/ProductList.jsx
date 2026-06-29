import { useState, useEffect, useRef } from 'react'
import * as api from '../api'

const CATEGORY_ICONS = {
  'Electronics': '⚡',
  'Fashion': '👗',
  'Beauty': '💄',
  'Books': '📚',
  'Home & Kitchen': '🏠',
  'Sports': '⚽',
  'Toys': '🎮',
}

const DEFAULT_ICON = '📦'

function getStockClass(qty) {
  if (qty >= 100) return 'stock-high'
  if (qty >= 20) return 'stock-medium'
  return 'stock-low'
}

export default function ProductList({ user, cartItems, addToCart }) {
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [selectedCategory, setSelectedCategory] = useState('')
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [toast, setToast] = useState(null)
  const sessionId = useRef(crypto.randomUUID())

  useEffect(() => {
    api.getCategories().then(setCategories).catch(() => {})
  }, [])

  useEffect(() => {
    loadProducts()
  }, [page, selectedCategory])

  const showToast = (msg, type = 'info') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3500)
  }

  const loadProducts = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await api.getProducts(page, selectedCategory, search)
      setProducts(data.products || [])
      setTotal(data.total || 0)
    } catch (err) {
      console.error('Product load error:', err)
      setError('Failed to load products. Is the backend running?')
    }
    setLoading(false)
  }

  const handleSearch = (e) => {
    e.preventDefault()
    setPage(1)
    loadProducts()
  }

  const cartMap = {}
  cartItems.forEach(item => { cartMap[item.product_id] = item.quantity })

  const handleAddToCart = async (product) => {
    if (!user) { showToast('Please login to add items to cart.', 'warning'); return }
    try {
      const res = await api.recordEvent('add_to_cart', product.product_id, sessionId.current)
      addToCart(product, 1)
      if (res.fraud_alert) {
        showToast(`⚠️ Fraud alert: ${res.fraud_alert.reason}`, 'warning')
      } else {
        showToast(`Added Product #${product.product_id} to cart!`, 'success')
      }
    } catch (err) {
      showToast('Failed to record event.', 'error')
    }
  }

  const totalPages = Math.ceil(total / 20)

  return (
    <div>
      {toast && (
        <div className="toast-container">
          <div className={`toast toast-${toast.type}`}>
            {toast.msg}
          </div>
        </div>
      )}

      <div className="page-header">
        <h2>Product Catalog</h2>
      </div>

      <form onSubmit={handleSearch} className="search-bar mb-2">
        <input
          type="text"
          placeholder="Search products by ID or name..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <select
          value={selectedCategory}
          onChange={e => { setSelectedCategory(e.target.value); setPage(1) }}
        >
          <option value="">All Categories</option>
          {categories.map(c => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
        <button type="submit" className="btn btn-primary">🔍 Search</button>
      </form>

      {error && (
        <div className="card mb-2" style={{ borderLeft: '4px solid var(--danger)', background: 'var(--danger-light)' }}>
          <p style={{ color: '#991b1b', fontWeight: 500 }}>{error}</p>
        </div>
      )}

      {loading ? (
        <div className="loading">
          <div className="loading-spinner"></div>
          <p className="loading-text">Loading products...</p>
        </div>
      ) : (
        <>
          <div className="grid grid-4">
            {products.map(p => {
              const icon = CATEGORY_ICONS[p.category] || DEFAULT_ICON
              const stockClass = getStockClass(p.stock_quantity)
              const inCartQty = cartMap[p.product_id] || 0
              return (
                <div key={p.product_id} className="product-card">
                  {inCartQty > 0 && (
                    <span style={{
                      position: 'absolute', top: '0.4rem', right: '0.4rem',
                      background: 'var(--success)', color: 'white', borderRadius: '50%',
                      width: '22px', height: '22px', display: 'flex', alignItems: 'center',
                      justifyContent: 'center', fontSize: '0.7rem', fontWeight: 700,
                      boxShadow: 'var(--shadow-sm)', zIndex: 1
                    }}>
                      {inCartQty}
                    </span>
                  )}
                  <div className="product-icon">{icon}</div>
                  <h4>Product #{p.product_id}</h4>
                  <p className="category">{p.category}</p>
                  <p className="price">${p.unit_price?.toFixed(2)}</p>
                  <p className={`stock ${stockClass}`}>
                    {p.stock_quantity < 20 ? '⚠️ ' : ''}Stock: {p.stock_quantity}
                  </p>
                  {user && (
                    <button
                      className="btn btn-primary btn-sm btn-block mt-1"
                      onClick={() => handleAddToCart(p)}
                    >
                      {inCartQty > 0 ? `🛒 Add More (${inCartQty})` : '🛒 Add to Cart'}
                    </button>
                  )}
                </div>
              )
            })}
          </div>

          {products.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">🔍</div>
              <p>No products found. Try a different search or category.</p>
            </div>
          )}

          {totalPages > 1 && (
            <div className="flex-center mt-3 gap-sm">
              <button
                className="btn btn-outline btn-sm"
                disabled={page <= 1}
                onClick={() => setPage(p => p - 1)}
              >
                ← Previous
              </button>
              <span className="text-sm text-muted font-bold">
                Page {page} of {totalPages}
              </span>
              <button
                className="btn btn-outline btn-sm"
                disabled={page >= totalPages}
                onClick={() => setPage(p => p + 1)}
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
