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
        navigate(data.user.role === 'admin' ? '/admin' : '/')
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-card">
      <div className="card">
        <h2>{isRegister ? 'Create Account' : 'Welcome Back'}</h2>
        <p className="subtitle">
          {isRegister
            ? 'Sign up to start shopping and track your orders.'
            : 'Sign in to your account to continue.'}
        </p>

        {error && (
          <div className="card mb-2" style={{ borderLeft: '4px solid var(--danger)', background: 'var(--danger-light)', padding: '0.75rem 1rem' }}>
            <p style={{ color: '#991b1b', fontWeight: 500, fontSize: '0.9rem' }}>{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
            />
          </div>

          {isRegister && (
            <>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                />
              </div>
              <div className="form-group">
                <label>Display Name</label>
                <input
                  value={displayName}
                  onChange={e => setDisplayName(e.target.value)}
                  placeholder="How should we call you?"
                />
              </div>
            </>
          )}

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-block btn-lg"
            disabled={loading}
          >
            {loading ? (
              <>Processing...</>
            ) : isRegister ? (
              'Create Account'
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        <div className="auth-toggle">
          {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
          <a href="#" onClick={(e) => { e.preventDefault(); setIsRegister(!isRegister); setError('') }}>
            {isRegister ? 'Sign In' : 'Register'}
          </a>
        </div>
      </div>

      {!isRegister && (
        <div style={{ marginTop: '1rem', padding: '1rem', background: 'var(--gray-50)', borderRadius: 'var(--radius)', border: '1px dashed var(--gray-300)', textAlign: 'center' }}>
          <p className="text-sm text-muted">
            <strong>Demo:</strong> Register a new account or use one of the pre-loaded customer accounts.<br />
            Try username <code>user_1</code> with password <code>password123</code>
          </p>
        </div>
      )}
    </div>
  )
}

