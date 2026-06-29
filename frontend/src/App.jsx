import { useState, useEffect, useCallback } from 'react'
import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom'
import Login from './components/Login'
import ProductList from './components/ProductList'
import Cart from './components/Cart'
import AdminDashboard from './components/AdminDashboard'
import * as api from './api'

function loadCart() {
  try {
    const saved = localStorage.getItem('cart')
    return saved ? JSON.parse(saved) : []
  } catch { return [] }
}

function App() {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [cartItems, setCartItems] = useState(loadCart)

  // Persist cart to localStorage on every change
  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cartItems))
  }, [cartItems])

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
    localStorage.removeItem('cart')
    api.setAuthToken(null)
    setToken(null)
    setUser(null)
    setCartItems([])
  }

  // Cart management functions
  const addToCart = useCallback((product, quantity = 1) => {
    setCartItems(prev => {
      const existing = prev.find(item => item.product_id === product.product_id)
      if (existing) {
        return prev.map(item =>
          item.product_id === product.product_id
            ? { ...item, quantity: Math.min(item.quantity + quantity, item.stock_quantity) }
            : item
        )
      }
      return [...prev, {
        product_id: product.product_id,
        name: product.name || `Product #${product.product_id}`,
        category: product.category,
        unit_price: product.unit_price,
        stock_quantity: product.stock_quantity,
        quantity: Math.min(quantity, product.stock_quantity),
      }]
    })
  }, [])

  const removeFromCart = useCallback((productId) => {
    setCartItems(prev => prev.filter(item => item.product_id !== productId))
  }, [])

  const updateCartQuantity = useCallback((productId, quantity) => {
    if (quantity <= 0) {
      removeFromCart(productId)
      return
    }
    setCartItems(prev => prev.map(item =>
      item.product_id === productId
        ? { ...item, quantity: Math.min(quantity, item.stock_quantity) }
        : item
    ))
  }, [removeFromCart])

  const clearCart = useCallback(() => {
    setCartItems([])
  }, [])

  const cartCount = cartItems.reduce((sum, item) => sum + item.quantity, 0)

  return (
    <BrowserRouter>
      <nav className="navbar">
        <Link to="/" style={{ color: 'white', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '1.4rem' }}>🛒</span>
          <h1>E-Commerce Analytics</h1>
        </Link>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Link to="/">Products</Link>

          {user ? (
            <>
              <Link to="/cart">
                Cart{cartCount > 0 && (
                  <span style={{
                    background: '#ef4444', color: 'white', borderRadius: '50%',
                    padding: '0.1rem 0.4rem', fontSize: '0.7rem', marginLeft: '0.25rem',
                    fontWeight: 700, verticalAlign: 'middle'
                  }}>
                    {cartCount}
                  </span>
                )}
              </Link>
              {user.role === 'admin' && <Link to="/admin">Admin</Link>}

              <span style={{ color: '#475569', margin: '0 0.2rem', fontSize: '1.2rem' }}>|</span>

              <span className="nav-user-badge">
                {user.display_name || user.username}
              </span>

              <button onClick={handleLogout} className="nav-logout-btn">
                Logout
              </button>
            </>
          ) : (
            <>
              <span style={{ color: '#475569', margin: '0 0.2rem', fontSize: '1.2rem' }}>|</span>
              <Link to="/login">Login</Link>
              <Link to="/login?register=true" className="nav-register-btn">
                Register
              </Link>
            </>
          )}
        </div>
      </nav>

      <div className="container">
        <Routes>
          <Route path="/" element={
            <ProductList user={user} cartItems={cartItems} addToCart={addToCart} />
          } />
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="/cart" element={
            <Cart
              user={user}
              cartItems={cartItems}
              updateCartQuantity={updateCartQuantity}
              removeFromCart={removeFromCart}
              clearCart={clearCart}
            />
          } />
          <Route path="/admin" element={<AdminDashboard user={user} />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
