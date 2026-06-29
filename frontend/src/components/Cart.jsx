import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import * as api from '../api'

const EVENT_ICONS = {
  'page_view': '📄',
  'add_to_cart': '🛒',
  'checkout': '💳',
  'purchase': '✅',
}

const CATEGORY_ICONS = {
  'Electronics': '⚡', 'Fashion': '👗', 'Beauty': '💄',
  'Books': '📚', 'Home & Kitchen': '🏠', 'Sports': '⚽', 'Toys': '🎮',
}

export default function Cart({ user, cartItems, updateCartQuantity, removeFromCart, clearCart }) {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState(null)
  const sessionId = useRef(localStorage.getItem('sessionId') || crypto.randomUUID())
  const navigate = useNavigate()

  useEffect(() => {
    localStorage.setItem('sessionId', sessionId.current)
    if (!user) navigate('/login')
  }, [user])

  const showToast = (msg, type = 'info') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 4500)
  }

  const handleRecordEvent = async (actionType) => {
    if (!user) return
    setLoading(true)
    try {
      const res = await api.recordEvent(actionType, null, sessionId.current)
      setEvents(prev => [{ actionType, time: new Date().toLocaleTimeString() }, ...prev].slice(0, 50))

      if (res.fraud_alert) {
        showToast(`⚠️ FRAUD ALERT: ${res.fraud_alert.reason}`, 'warning')
      } else {
        showToast(`Event "${actionType}" recorded successfully`, 'success')
      }
    } catch (err) {
      showToast(`Error: ${err.response?.data?.detail || err.message}`, 'error')
    }
    setLoading(false)
  }

  const handleCheckout = async () => {
    if (cartItems.length === 0) {
      showToast('Your cart is empty. Add some products first!', 'warning')
      return
    }
    setLoading(true)
    try {
      const items = cartItems.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
      }))

      await api.createOrder(items)
      await api.recordEvent('checkout', null, sessionId.current)
      await api.recordEvent('purchase', null, sessionId.current)

      showToast(`Order placed! ${cartItems.length} items purchased for $${subtotal.toFixed(2)}.`, 'success')
      clearCart()
      setEvents([])
    } catch (err) {
      showToast('Checkout failed: ' + (err.response?.data?.detail || err.message), 'error')
    }
    setLoading(false)
  }

  if (!user) return null

  const subtotal = cartItems.reduce((sum, item) => sum + item.unit_price * item.quantity, 0)
  const totalItems = cartItems.reduce((sum, item) => sum + item.quantity, 0)

  return (
    <div style={{ maxWidth: 750, margin: '2rem auto' }}>
      {toast && (
        <div className="toast-container">
          <div className={`toast toast-${toast.type}`}>{toast.msg}</div>
        </div>
      )}

      {/* ── Cart Contents ─────────────────────────────── */}
      <div className="page-header">
        <h2>🛒 Your Cart</h2>
      </div>

      {cartItems.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🛒</div>
          <p>Your cart is empty.</p>
          <button className="btn btn-primary mt-2" onClick={() => navigate('/')}>
            Browse Products
          </button>
        </div>
      ) : (
        <div className="card mb-3">
          <div className="flex-between mb-2">
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--gray-700)' }}>
              {totalItems} item{totalItems !== 1 ? 's' : ''} in cart
            </h3>
            <button className="btn btn-ghost btn-sm" onClick={clearCart}>
              🗑️ Clear Cart
            </button>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Category</th>
                  <th>Price</th>
                  <th>Qty</th>
                  <th>Total</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {cartItems.map(item => {
                  const icon = CATEGORY_ICONS[item.category] || '📦'
                  return (
                    <tr key={item.product_id}>
                      <td>
                        <span style={{ marginRight: '0.4rem' }}>{icon}</span>
                        <strong title={`#${item.product_id}`}>{item.name || `#${item.product_id}`}</strong>
                      </td>
                      <td className="text-sm text-muted">{item.category}</td>
                      <td className="font-bold">${item.unit_price?.toFixed(2)}</td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                          <button
                            className="btn btn-ghost btn-sm"
                            onClick={() => updateCartQuantity(item.product_id, item.quantity - 1)}
                            style={{ padding: '0.1rem 0.4rem', fontSize: '0.8rem' }}
                          >
                            −
                          </button>
                          <span style={{ minWidth: '1.5rem', textAlign: 'center', fontWeight: 600 }}>
                            {item.quantity}
                          </span>
                          <button
                            className="btn btn-ghost btn-sm"
                            onClick={() => updateCartQuantity(item.product_id, item.quantity + 1)}
                            disabled={item.quantity >= item.stock_quantity}
                            style={{ padding: '0.1rem 0.4rem', fontSize: '0.8rem' }}
                          >
                            +
                          </button>
                        </div>
                      </td>
                      <td className="font-bold" style={{ color: 'var(--success)' }}>
                        ${(item.unit_price * item.quantity).toFixed(2)}
                      </td>
                      <td>
                        <button
                          className="btn btn-ghost btn-sm"
                          onClick={() => removeFromCart(item.product_id)}
                          style={{ color: 'var(--danger)' }}
                        >
                          ✕
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
              <tfoot>
                <tr style={{ background: 'var(--gray-50)', borderTop: '2px solid var(--gray-200)' }}>
                  <td colSpan={4} className="text-right font-bold" style={{ fontSize: '1rem' }}>
                    Subtotal:
                  </td>
                  <td className="font-bold" style={{ color: 'var(--success)', fontSize: '1.1rem' }}>
                    ${subtotal.toFixed(2)}
                  </td>
                  <td></td>
                </tr>
              </tfoot>
            </table>
          </div>

          <div className="flex-between mt-3">
            <button className="btn btn-outline" onClick={() => navigate('/')}>
              ← Continue Shopping
            </button>
            <button
              className="btn btn-success btn-lg"
              onClick={handleCheckout}
              disabled={loading || cartItems.length === 0}
            >
              {loading ? 'Processing...' : `💳 Place Order — $${subtotal.toFixed(2)}`}
            </button>
          </div>
        </div>
      )}

      {/* ── Clickstream Events (collapsed section) ────── */}
      <details style={{ marginTop: '1.5rem' }}>
        <summary style={{
          cursor: 'pointer', padding: '0.5rem 0', fontSize: '0.9rem',
          fontWeight: 600, color: 'var(--gray-500)', userSelect: 'none'
        }}>
          🔬 Clickstream Debug Panel
        </summary>

        <div className="card mb-2" style={{ marginTop: '0.5rem' }}>
          <div className="flex-between mb-2">
            <span className="text-sm text-muted font-bold">Session ID</span>
            <code style={{
              background: 'var(--gray-100)', padding: '0.2rem 0.6rem',
              borderRadius: 'var(--radius-sm)', fontSize: '0.82rem', color: 'var(--gray-600)'
            }}>
              {sessionId.current.slice(0, 8)}...
            </code>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <button className="btn btn-primary btn-sm" onClick={() => handleRecordEvent('page_view')} disabled={loading}>
              📄 Page View
            </button>
            <button className="btn btn-success btn-sm" onClick={() => handleRecordEvent('add_to_cart')} disabled={loading}>
              🛒 Add to Cart
            </button>
            <button className="btn btn-outline btn-sm" onClick={() => handleRecordEvent('checkout')} disabled={loading}>
              💳 Checkout
            </button>
            <button className="btn btn-primary btn-sm" onClick={() => handleRecordEvent('purchase')} disabled={loading}>
              ✅ Purchase
            </button>
          </div>
        </div>

        {events.length > 0 && (
          <div className="card">
            <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--gray-700)' }}>
              Recent Events ({events.length})
            </h3>
            <div className="table-container">
              <table>
                <thead>
                  <tr><th>Action</th><th>Time</th></tr>
                </thead>
                <tbody>
                  {events.map((e, i) => (
                    <tr key={i}>
                      <td>
                        <span style={{ marginRight: '0.4rem' }}>{EVENT_ICONS[e.actionType] || '•'}</span>
                        <span className="badge badge-info">{e.actionType}</span>
                      </td>
                      <td className="text-muted text-sm">{e.time}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        <div className="card mt-2" style={{ background: 'var(--gray-50)', border: '1px dashed var(--gray-300)' }}>
          <p className="text-sm text-muted">
            <strong>💡 Tip:</strong> Click <strong>"Add to Cart"</strong> rapidly (10+ times within 60 seconds) to trigger the fraud detection system.
          </p>
        </div>
      </details>
    </div>
  )
}
