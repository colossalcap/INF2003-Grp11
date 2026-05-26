import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import * as api from '../api'

export default function Cart({ user }) {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const sessionId = useRef(localStorage.getItem('sessionId') || crypto.randomUUID())
  const navigate = useNavigate()

  useEffect(() => {
    localStorage.setItem('sessionId', sessionId.current)
    if (!user) navigate('/login')
  }, [user])

  const handleRecordEvent = async (actionType) => {
    if (!user) return
    setLoading(true)
    try {
      const res = await api.recordEvent(actionType, null, sessionId.current)
      setEvents(prev => [...prev, { actionType, time: new Date().toLocaleTimeString() }])

      if (res.fraud_alert) {
        setMessage(`⚠️ FRAUD ALERT: ${res.fraud_alert.reason}`)
      } else {
        setMessage(`✅ Event "${actionType}" recorded.`)
      }
    } catch (err) {
      setMessage(`❌ Error: ${err.response?.data?.detail || err.message}`)
    }
    setLoading(false)
    setTimeout(() => setMessage(''), 4000)
  }

  if (!user) return null

  return (
    <div style={{ maxWidth: 600, margin: '2rem auto' }}>
      <h2>🛒 Cart & Clickstream</h2>
      <p style={{ color: '#666', marginBottom: '1rem' }}>
        Session: <code>{sessionId.current.slice(0, 8)}...</code>
      </p>

      {message && (
        <div className={`alert ${message.includes('❌') || message.includes('⚠️') ? 'alert-danger' : 'alert-success'}`}>
          {message}
        </div>
      )}

      <div className="card">
        <h3 style={{ marginBottom: '1rem' }}>Record Clickstream Events</h3>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button
            className="btn btn-primary btn-sm"
            onClick={() => handleRecordEvent('page_view')}
            disabled={loading}
          >
            📄 Page View
          </button>
          <button
            className="btn btn-success btn-sm"
            onClick={() => handleRecordEvent('add_to_cart')}
            disabled={loading}
          >
            🛒 Add to Cart
          </button>
          <button
            className="btn btn-outline btn-sm"
            onClick={() => handleRecordEvent('checkout')}
            disabled={loading}
          >
            💳 Checkout
          </button>
          <button
            className="btn btn-primary btn-sm"
            onClick={() => handleRecordEvent('purchase')}
            disabled={loading}
          >
            ✅ Purchase
          </button>
        </div>
      </div>

      {events.length > 0 && (
        <div className="card mt-2">
          <h3 style={{ marginBottom: '0.5rem' }}>Recent Events</h3>
          <table>
            <thead>
              <tr><th>Action</th><th>Time</th></tr>
            </thead>
            <tbody>
              {events.slice(-10).reverse().map((e, i) => (
                <tr key={i}>
                  <td>{e.actionType}</td>
                  <td>{e.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="card mt-2" style={{ fontSize: '0.85rem', color: '#666' }}>
        <strong>💡 Tip:</strong> Click "Add to Cart" rapidly (10+ times within 60 seconds) to trigger
        the fraud detection system. The alert will appear in the Admin Dashboard.
      </div>
    </div>
  )
}
