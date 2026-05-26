import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import * as api from '../api'

export default function Login({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isRegister) {
        await api.register(username, email, password, displayName)
        setIsRegister(false)
        setError('')
        alert('Registration successful! Please login.')
      } else {
        const data = await api.login(username, password)
        onLogin(data.access_token, data.user)
        navigate('/')
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 420, margin: '3rem auto' }}>
      <div className="card">
        <h2 style={{ marginBottom: '1rem' }}>
          {isRegister ? 'Register' : 'Login'}
        </h2>

        {error && <div className="alert alert-danger">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input value={username} onChange={e => setUsername(e.target.value)} required />
          </div>

          {isRegister && (
            <>
              <div className="form-group">
                <label>Email</label>
                <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
              </div>
              <div className="form-group">
                <label>Display Name</label>
                <input value={displayName} onChange={e => setDisplayName(e.target.value)} />
              </div>
            </>
          )}

          <div className="form-group">
            <label>Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
            {loading ? 'Processing...' : isRegister ? 'Register' : 'Login'}
          </button>
        </form>

        <p style={{ marginTop: '1rem', textAlign: 'center', fontSize: '0.9rem' }}>
          {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
          <a href="#" onClick={() => { setIsRegister(!isRegister); setError('') }}>
            {isRegister ? 'Login' : 'Register'}
          </a>
        </p>
      </div>

      <div className="card" style={{ marginTop: '1rem', fontSize: '0.8rem', color: '#666' }}>
        <strong>Demo:</strong> Use any existing username/password or register a new account.
      </div>
    </div>
  )
}
