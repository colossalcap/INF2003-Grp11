import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import * as api from '../api'

const EVENT_ICONS = {
  'page_view': '📄',
  'add_to_cart': '🛒',
  'checkout': '💳',
  'purchase': '✅',
}

export default function Cart({ user }) {
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

  if (!user) return null

  return (
    <div style={{ maxWidth: 650, margin: '2rem auto' }}>
      {toast && (
        <div className="toast-container">
          <div className={`toast toast-${toast.type}`}>{toast.msg}</div>
        </div>
      )}

      <div className="page-header">
        <h2>🛒 Cart & Clickstream</h2>
      </div>

      <div className="card mb-2">
        <div className="flex-between mb-2">
          <span className="text-sm text-muted font-bold">
            Session ID
          </span>
          <code style={{
            background: 'var(--gray-100)',
            padding: '0.2rem 0.6rem',
            borderRadius: 'var(--radius-sm)',
            fontSize: '0.82rem',
            color: 'var(--gray-600)'
          }}>
            {sessionId.current.slice(0, 8)}...
          </code>
        </div>

        <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--gray-700)' }}>
          Record Clickstream Events
        </h3>
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
                <tr>
                  <th>Action</th>
                  <th>Time</th>
                </tr>
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
          <strong>💡 Tip:</strong> Click <strong>"Add to Cart"</strong> rapidly (10+ times within 60 seconds) to trigger the fraud detection system. The alert will appear in the Admin Dashboard.
        </p>
      </div>
    </div>
  )
}
