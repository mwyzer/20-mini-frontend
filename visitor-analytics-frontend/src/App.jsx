import { useEffect, useMemo, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const WINDOWS = [
  { value: 'day', label: '24 Jam Terakhir' },
  { value: 'week', label: '7 Hari Terakhir' }
]
const POLL_INTERVAL_MS = 4000

const formatDate = (value) => new Intl.DateTimeFormat('id-ID', {
  dateStyle: 'medium',
  timeStyle: 'medium'
}).format(new Date(value))

const formatUserAgent = (ua) => {
  if (!ua) return 'Tidak diketahui'
  if (ua.length < 80) return ua
  return `${ua.slice(0, 80)}…`
}

function App() {
  const [windowFilter, setWindowFilter] = useState('day')
  const [summary, setSummary] = useState(null)
  const [visitors, setVisitors] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const fetchData = async (activeWindow) => {
    setLoading(true)
    try {
      const [summaryRes, visitorsRes] = await Promise.all([
        fetch(`${API_BASE}/visitors/summary?window=${activeWindow}`),
        fetch(`${API_BASE}/visitors?window=${activeWindow}`)
      ])

      if (!summaryRes.ok || !visitorsRes.ok) {
        throw new Error('Gagal memuat data pengunjung')
      }

      const summaryBody = await summaryRes.json()
      const visitorBody = await visitorsRes.json()
      setSummary(summaryBody)
      setVisitors(visitorBody)
      setError('')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const pingVisitor = async () => {
    try {
      const res = await fetch(`${API_BASE}/visitors`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      })
      if (!res.ok) throw new Error('Gagal mencatat kunjungan manual')
      fetchData(windowFilter)
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    fetchData(windowFilter)
    const id = setInterval(() => fetchData(windowFilter), POLL_INTERVAL_MS)
    return () => clearInterval(id)
  }, [windowFilter])

  const latestVisitor = summary?.latest_visitor
  const totalHits = summary?.total_hits ?? 0
  const uniqueVisitors = summary?.unique_visitors ?? 0

  const topIp = useMemo(() => {
    if (!visitors.length) return null
    return visitors.reduce((prev, curr) => (curr.visit_count > prev.visit_count ? curr : prev), visitors[0])
  }, [visitors])

  return (
    <div className="app-shell">
      <header className="header">
        <div>
          <h1 style={{ margin: 0 }}>Visitor Analytics</h1>
          <p style={{ margin: 0, color: '#475569' }}>
            Dashboard realtime untuk memantau trafik pengunjung.
          </p>
        </div>
        <div className="controls">
          <select
            className="select"
            value={windowFilter}
            onChange={(e) => setWindowFilter(e.target.value)}
          >
            {WINDOWS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <button className="button" onClick={pingVisitor}>
            Tambah Kunjungan
          </button>
        </div>
      </header>

      {error && (
        <div className="table-card" style={{ borderColor: '#ef4444', background: '#fef2f2', color: '#b91c1c' }}>
          {error}
        </div>
      )}

      <section className="metrics">
        <article className="metric-card">
          <h2>Total Hit</h2>
          <p className="metric-value">{totalHits}</p>
          <p className="metric-subtext">Jumlah request unik dan duplikasi yang tercatat</p>
        </article>
        <article className="metric-card secondary">
          <h2>Pengunjung Unik</h2>
          <p className="metric-value">{uniqueVisitors}</p>
          <p className="metric-subtext">Dicatat dengan deduplikasi otomatis</p>
        </article>
        <article className="metric-card" style={{ background: 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)' }}>
          <h2>Aktivitas Terbaru</h2>
          <p className="metric-value" style={{ fontSize: '1.6rem' }}>
            {latestVisitor ? formatDate(latestVisitor.last_seen) : 'Belum ada data'}
          </p>
          <p className="metric-subtext">
            {latestVisitor
              ? `${latestVisitor.ip_address} · ${formatUserAgent(latestVisitor.user_agent)}`
              : 'Menunggu request pertama'}
          </p>
        </article>
      </section>

      <section className="table-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <h3 style={{ margin: 0 }}>Detail Pengunjung</h3>
          <span className="badge">Live refresh {POLL_INTERVAL_MS / 1000} detik</span>
        </div>
        <p style={{ margin: '0.2rem 0 0.8rem 0', color: '#475569' }}>
          Filter waktu: <strong>{WINDOWS.find((w) => w.value === windowFilter)?.label}</strong>
        </p>
        <div style={{ overflowX: 'auto' }}>
          <table className="table">
            <thead>
              <tr>
                <th>IP Address</th>
                <th>User Agent</th>
                <th>Terakhir Dilihat</th>
                <th>Hits</th>
              </tr>
            </thead>
            <tbody>
              {visitors.length === 0 && (
                <tr>
                  <td colSpan="4" style={{ textAlign: 'center', padding: '1rem', color: '#94a3b8' }}>
                    {loading ? 'Memuat data…' : 'Belum ada pengunjung pada rentang ini'}
                  </td>
                </tr>
              )}
              {visitors.map((visitor) => (
                <tr key={visitor.id}>
                  <td><span className="pill">{visitor.ip_address}</span></td>
                  <td>{formatUserAgent(visitor.user_agent)}</td>
                  <td>{formatDate(visitor.last_seen)}</td>
                  <td><strong>{visitor.visit_count}</strong></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {topIp && (
          <p className="footer-note">
            Paling sering: <strong>{topIp.ip_address}</strong> ({topIp.visit_count} hits)
          </p>
        )}
      </section>
    </div>
  )
}

export default App
