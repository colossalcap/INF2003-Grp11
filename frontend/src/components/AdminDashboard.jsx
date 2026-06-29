import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import * as api from '../api'

const COLORS = ['#1976d2', '#2e7d32', '#e65100', '#c62828', '#7b1fa2', '#00838f']

export default function AdminDashboard({ user }) {
  const [rfm, setRfm] = useState([])
  const [funnel, setFunnel] = useState([])
  const [alerts, setAlerts] = useState([])
  const [topProducts, setTopProducts] = useState([])
  const [salesByCategory, setSalesByCategory] = useState([])
  const [marketBasket, setMarketBasket] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('rfm')
  const navigate = useNavigate()

  useEffect(() => {
    if (!user || user.role !== 'admin') {
      navigate('/')
      return
    }
    loadAll()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user])

  const loadAll = async () => {
    setLoading(true)
    try {
      const [rfmRes, funnelRes, alertsRes, topRes, salesRes, basketRes] = await Promise.all([
        api.getRFM(),
        api.getFunnel(),
        api.getAlerts(),
        api.getTopProducts(),
        api.getSalesByCategory(),
        api.getMarketBasket(),
      ])
      setRfm(rfmRes.segments || [])
      setFunnel(funnelRes.funnel || [])
      setAlerts(alertsRes.alerts || [])
      setTopProducts(topRes.products || [])
      setSalesByCategory(salesRes.categories || [])
      setMarketBasket(basketRes.pairs || [])
    } catch (err) {
      console.error('Failed to load analytics:', err)
    }
    setLoading(false)
  }

  if (!user || user.role !== 'admin') return null

  const segmentCounts = {}
  rfm.forEach(r => {
    segmentCounts[r.segment] = (segmentCounts[r.segment] || 0) + 1
  })
  const segmentData = Object.entries(segmentCounts).map(([name, value]) => ({ name, value }))

  return (
    <div>
      <div className="flex-between mb-2">
        <h2>📊 Admin Dashboard</h2>
        <button className="btn btn-outline btn-sm" onClick={loadAll}>🔄 Refresh</button>
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        {['rfm', 'funnel', 'alerts', 'products', 'basket'].map(tab => (
          <button
            key={tab}
            className={`btn btn-sm ${activeTab === tab ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab === 'rfm' && 'RFM Segmentation'}
            {tab === 'funnel' && 'Funnel Analytics'}
            {tab === 'alerts' && `Alerts (${alerts.length})`}
            {tab === 'products' && 'Top Products'}
            {tab === 'basket' && 'Market Basket'}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="loading">Loading analytics...</div>
      ) : (
        <>
          {/* RFM Segmentation */}
          {activeTab === 'rfm' && (
            <div>
              <div className="card">
                <h3>Customer Segmentation (RFM Analysis)</h3>
                <p style={{ color: '#666', fontSize: '0.85rem', marginBottom: '1rem' }}>
                  Recency, Frequency, Monetary scores using NTILE(4). Total customers analyzed: {rfm.length}
                </p>
                <ResponsiveContainer width="100%" height={350}>
                  <PieChart>
                    <Pie data={segmentData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={130} label>
                      {segmentData.map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="card mt-2">
                <h3>Top Customers</h3>
                <table>
                  <thead>
                    <tr>
                      <th>Customer ID</th><th>Days Since Last</th><th>Orders</th>
                      <th>Total Spent</th><th>R</th><th>F</th><th>M</th><th>Segment</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rfm.slice(0, 15).map(r => (
                      <tr key={r.customer_id}>
                        <td><code>{r.customer_id?.slice(0, 8)}...</code></td>
                        <td>{r.recency_days}</td>
                        <td>{r.frequency}</td>
                        <td>${r.monetary?.toFixed(2)}</td>
                        <td>{r.r_score}</td>
                        <td>{r.f_score}</td>
                        <td>{r.m_score}</td>
                        <td>
                          <span className={`badge ${
                            r.segment === 'Champions' ? 'badge-success' :
                            r.segment === 'Loyal Customers' ? 'badge-info' :
                            r.segment === 'At Risk' ? 'badge-warning' : 'badge-danger'
                          }`}>
                            {r.segment}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Funnel Analytics */}
          {activeTab === 'funnel' && (
            <div>
              <div className="card">
                <h3>Conversion Funnel (MongoDB $facet Aggregation)</h3>
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={funnel}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="stage" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="count" fill="#1976d2" name="Session Count" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="card mt-2">
                <table>
                  <thead>
                    <tr><th>Stage</th><th>Sessions</th><th>Conversion Rate</th></tr>
                  </thead>
                  <tbody>
                    {funnel.map(f => (
                      <tr key={f.stage}>
                        <td>{f.stage}</td>
                        <td>{f.count}</td>
                        <td>{f.conversion_rate}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Alerts */}
          {activeTab === 'alerts' && (
            <div className="card">
              <h3>🚨 Fraud & Security Alerts</h3>
              {alerts.length === 0 ? (
                <p style={{ color: '#999' }}>No alerts. Try triggering fraud detection from the Cart page.</p>
              ) : (
                <table>
                  <thead>
                    <tr><th>ID</th><th>Customer</th><th>Message</th><th>Time</th><th>Status</th></tr>
                  </thead>
                  <tbody>
                    {alerts.map(a => (
                      <tr key={a.alert_id}>
                        <td>{a.alert_id}</td>
                        <td><code>{a.customer_id?.slice(0, 8)}...</code></td>
                        <td>{a.message}</td>
                        <td>{new Date(a.created_at).toLocaleString()}</td>
                        <td>
                          <span className={`badge ${a.acknowledged ? 'badge-success' : 'badge-warning'}`}>
                            {a.acknowledged ? 'Acknowledged' : 'Pending'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}

          {/* Top Products */}
          {activeTab === 'products' && (
            <div>
              <div className="card">
                <h3>Top Selling Products</h3>
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={topProducts.slice(0, 10)} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="product_id" type="category" width={100} />
                    <Tooltip />
                    <Bar dataKey="total_sold" fill="#2e7d32" name="Units Sold" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {salesByCategory.length > 0 && (
                <div className="card mt-2">
                  <h3>Sales by Category</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={salesByCategory}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="category" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="total_revenue" fill="#e65100" name="Revenue ($)" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          )}

          {/* Market Basket */}
          {activeTab === 'basket' && (
            <div className="card">
              <h3>Market Basket Analysis (Product Pairs)</h3>
              <p style={{ color: '#666', fontSize: '0.85rem', marginBottom: '1rem' }}>
                Self-join on order_items to find products frequently purchased together.
              </p>
              {marketBasket.length === 0 ? (
                <p style={{ color: '#999' }}>No co-occurrence data yet. Place more orders to see patterns.</p>
              ) : (
                <table>
                  <thead>
                    <tr><th>Product A</th><th>Product B</th><th>Times Bought Together</th></tr>
                  </thead>
                  <tbody>
                    {marketBasket.map((pair, i) => (
                      <tr key={i}>
                        <td>{pair.product_a}</td>
                        <td>{pair.product_b}</td>
                        <td><strong>{pair.pair_count}</strong></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}
