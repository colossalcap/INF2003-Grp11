import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom'
import Login from './components/Login'
import ProductList from './components/ProductList'
import Cart from './components/Cart'
import AdminDashboard from './components/AdminDashboard'
import * as api from './api'

function App() {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))

  useEffect(() => {
    if (token) {
      api.setAuthToken(token)
      api.getMe()
        .then(u => setUser(u))
        .catch(() => {
          localStorage.removeItem('token')
          setToken(null)
          setUser(null)
        })
    }
  }, [token])

  const handleLogin = (tok, userData) => {
    localStorage.setItem('token', tok)
    api.setAuthToken(tok)
    setToken(tok)
    setUser(userData)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    api.setAuthToken(null)
    setToken(null)
    setUser(null)
  }

  return (
    <BrowserRouter>
      <nav className="navbar">
        <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>
          <h1>📊 E-Commerce Analytics</h1>
        </Link>
        <nav>
          <Link to="/">Products</Link>
          {user ? (
            <>
              <Link to="/cart">Cart</Link>
              {user.role === 'admin' && <Link to="/admin">Admin</Link>}
              <span style={{ color: '#aaa', marginLeft: '1rem' }}>
                {user.display_name || user.username}
              </span>
              <a href="#" onClick={handleLogout} style={{ marginLeft: '0.5rem' }}>
                Logout
              </a>
            </>
          ) : (
            <Link to="/login">Login</Link>
          )}
        </nav>
      </nav>

      <div className="container">
        <Routes>
          <Route path="/" element={<ProductList user={user} />} />
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="/cart" element={<Cart user={user} />} />
          <Route path="/admin" element={<AdminDashboard user={user} />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
