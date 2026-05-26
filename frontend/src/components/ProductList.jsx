import { useState, useEffect, useRef } from 'react'
import * as api from '../api'

export default function ProductList({ user }) {
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [selectedCategory, setSelectedCategory] = useState('')
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const sessionId = useRef(crypto.randomUUID())

  useEffect(() => {
    api.getCategories().then(setCategories).catch(() => {})
  }, [])

  useEffect(() => {
    loadProducts()
  }, [page, selectedCategory])

  const loadProducts = async () => {
    setLoading(true)
    try {
      const data = await api.getProducts(page, selectedCategory, search)
      setProducts(data.products)
      setTotal(data.total)
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  const handleSearch = (e) => {
    e.preventDefault()
    setPage(1)
    loadProducts()
  }

  const handleAddToCart = async (productId) => {
    if (!user) return alert('Please login to add items to cart.')
    try {
      const res = await api.recordEvent('add_to_cart', productId, sessionId.current)
      if (res.fraud_alert) {
        setMessage(`⚠️ Fraud alert: ${res.fraud_alert.reason}`)
      } else {
        setMessage(`✅ Added product ${productId} to cart!`)
      }
      setTimeout(() => setMessage(''), 3000)
    } catch (err) {
      setMessage('❌ Failed to record event.')
      setTimeout(() => setMessage(''), 3000)
    }
  }

  const handleCheckout = async () => {
    if (!user) return alert('Please login to checkout.')
    if (products.length === 0) return

    try {
      const items = products.slice(0, 3).map(p => ({
        product_id: p.product_id,
        quantity: 1,
      }))

      await api.createOrder(items)
      setMessage('🎉 Order placed successfully!')

      // Record checkout + purchase events
      await api.recordEvent('checkout', null, sessionId.current)
      await api.recordEvent('purchase', null, sessionId.current)

      setTimeout(() => setMessage(''), 3000)
    } catch (err) {
      setMessage('❌ Checkout failed: ' + (err.response?.data?.detail || err.message))
      setTimeout(() => setMessage(''), 3000)
    }
  }

  const totalPages = Math.ceil(total / 20)

  return (
    <div>
      <div className="flex-between mb-2">
        <h2>Product Catalog</h2>
        {user && (
          <div>
            <button className="btn btn-success btn-sm" onClick={handleCheckout}>
              🛒 Checkout (Sample Order)
            </button>
          </div>
        )}
      </div>

      {message && (
        <div className={`alert ${message.includes('❌') || message.includes('⚠️') ? 'alert-danger' : 'alert-success'}`}>
          {message}
        </div>
      )}

      <form onSubmit={handleSearch} className="flex-between mb-2" style={{ gap: '0.5rem' }}>
        <input
          type="text"
          placeholder="Search products..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ flex: 1, padding: '0.5rem', border: '1px solid #ddd', borderRadius: 4 }}
        />
        <select
          value={selectedCategory}
          onChange={e => { setSelectedCategory(e.target.value); setPage(1) }}
          style={{ padding: '0.5rem', border: '1px solid #ddd', borderRadius: 4 }}
        >
          <option value="">All Categories</option>
          {categories.map(c => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
        <button type="submit" className="btn btn-primary">Search</button>
      </form>

      {loading ? (
        <div className="loading">Loading products...</div>
      ) : (
        <>
          <div className="grid grid-4">
            {products.map(p => (
              <div key={p.product_id} className="card" style={{ textAlign: 'center' }}>
                <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>📦</h3>
                <h4 style={{ fontSize: '0.95rem', marginBottom: '0.25rem' }}>{p.product_id}</h4>
                <p style={{ color: '#666', fontSize: '0.85rem' }}>{p.category}</p>
                <p style={{ fontSize: '1.1rem', fontWeight: 600, color: '#2e7d32' }}>
                  ${p.unit_price?.toFixed(2)}
                </p>
                <p style={{ fontSize: '0.8rem', color: '#999' }}>
                  Stock: {p.stock_quantity}
                </p>
                {user && (
                  <button
                    className="btn btn-primary btn-sm mt-1"
                    onClick={() => handleAddToCart(p.product_id)}
                    style={{ width: '100%' }}
                  >
                    Add to Cart
                  </button>
                )}
              </div>
            ))}
          </div>

          {products.length === 0 && (
            <div className="loading">No products found.</div>
          )}

          {totalPages > 1 && (
            <div className="flex-between mt-2" style={{ justifyContent: 'center', gap: '0.5rem' }}>
              <button
                className="btn btn-outline btn-sm"
                disabled={page <= 1}
                onClick={() => setPage(p => p - 1)}
              >
                Previous
              </button>
              <span>Page {page} of {totalPages}</span>
              <button
                className="btn btn-outline btn-sm"
                disabled={page >= totalPages}
                onClick={() => setPage(p => p + 1)}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
