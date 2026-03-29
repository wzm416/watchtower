import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { Navigate } from 'react-router-dom'
import {
  createMonitor,
  deleteMonitor,
  listMonitors,
  translateSchedule,
  type Monitor,
} from '../api'
import { useAuth } from '../auth'

function fmtMoney(minor: number | null, cur: string | null) {
  if (minor == null || !cur) return '—'
  const sym = cur === 'USD' ? '$' : cur === 'EUR' ? '€' : cur === 'GBP' ? '£' : `${cur} `
  return `${sym}${(minor / 100).toFixed(2)}`
}

export function MonitorsPage() {
  const { token, signOut } = useAuth()
  const [rows, setRows] = useState<Monitor[]>([])
  const [loadErr, setLoadErr] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const [label, setLabel] = useState('')
  const [url, setUrl] = useState('')
  const [selector, setSelector] = useState('')
  const [cron, setCron] = useState('0 * * * *')
  const [tz, setTz] = useState('UTC')
  const [targetDollars, setTargetDollars] = useState('')
  const [nlHint, setNlHint] = useState('')
  const [formErr, setFormErr] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    if (!token) return
    setLoadErr(null)
    try {
      setRows(await listMonitors(token))
    } catch (e) {
      setLoadErr(e instanceof Error ? e.message : 'Failed to load monitors')
    }
  }, [token])

  useEffect(() => {
    void refresh()
  }, [refresh])

  if (!token) return <Navigate to="/" replace />

  async function onSuggestNl() {
    if (!token || !nlHint.trim()) return
    setFormErr(null)
    setBusy(true)
    try {
      const r = await translateSchedule(token, nlHint.trim(), tz)
      setCron(r.cron)
    } catch (e) {
      setFormErr(e instanceof Error ? e.message : 'Could not translate schedule')
    } finally {
      setBusy(false)
    }
  }

  async function onCreate(e: FormEvent) {
    e.preventDefault()
    if (!token) return
    setFormErr(null)
    setBusy(true)
    try {
      const target_minor =
        targetDollars.trim() === ''
          ? null
          : Math.round(Number.parseFloat(targetDollars) * 100)
      if (targetDollars.trim() !== '' && Number.isNaN(target_minor!)) {
        setFormErr('Target price must be a number')
        setBusy(false)
        return
      }
      await createMonitor(token, {
        label: label.trim(),
        product_url: url.trim(),
        css_selector: selector.trim() || undefined,
        schedule_cron: cron.trim(),
        timezone: tz,
        target_price_minor: target_minor,
      })
      setLabel('')
      setUrl('')
      setSelector('')
      setTargetDollars('')
      setNlHint('')
      await refresh()
    } catch (err) {
      setFormErr(err instanceof Error ? err.message : 'Create failed')
    } finally {
      setBusy(false)
    }
  }

  async function onDelete(id: string) {
    if (!token) return
    if (!confirm('Delete this monitor?')) return
    setBusy(true)
    try {
      await deleteMonitor(token, id)
      await refresh()
    } catch (e) {
      setLoadErr(e instanceof Error ? e.message : 'Delete failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="app">
      <aside className="sidebar" aria-label="Main">
        <div className="sidebar-brand">Watchtower</div>
        <nav className="sidebar-nav">
          <span className="nav-item nav-item-active">Monitors</span>
        </nav>
        <button type="button" className="signout-btn" onClick={signOut}>
          Sign out
        </button>
      </aside>
      <main className="main">
        <header className="main-header">
          <h1 className="main-title">Monitors</h1>
          <p className="main-subtitle">
            HTTPS product URLs only. Cron runs in your timezone; use “Suggest” for simple English
            phrases.
          </p>
        </header>

        {loadErr ? <p className="banner-err">{loadErr}</p> : null}

        <section className="panel">
          <h2 className="panel-title">Add monitor</h2>
          <form className="form-grid" onSubmit={onCreate}>
            <label className="field">
              <span>Label</span>
              <input
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                placeholder="Running shoes"
              />
            </label>
            <label className="field field-span2">
              <span>Product URL (https)</span>
              <input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://…"
                required
              />
            </label>
            <label className="field field-span2">
              <span>CSS selector (optional)</span>
              <input
                value={selector}
                onChange={(e) => setSelector(e.target.value)}
                placeholder=".price, #product-price, …"
              />
            </label>
            <label className="field">
              <span>Timezone</span>
              <input value={tz} onChange={(e) => setTz(e.target.value)} placeholder="UTC" />
            </label>
            <label className="field">
              <span>Cron (5 fields)</span>
              <input value={cron} onChange={(e) => setCron(e.target.value)} required />
            </label>
            <label className="field field-span2">
              <span>Schedule hint (English)</span>
              <div className="inline-row">
                <input
                  value={nlHint}
                  onChange={(e) => setNlHint(e.target.value)}
                  placeholder="every hour, every day at 9am, …"
                />
                <button type="button" className="btn secondary" onClick={onSuggestNl} disabled={busy}>
                  Suggest cron
                </button>
              </div>
            </label>
            <label className="field">
              <span>Target price (USD, optional)</span>
              <input
                value={targetDollars}
                onChange={(e) => setTargetDollars(e.target.value)}
                placeholder="29.99"
              />
            </label>
            {formErr ? <p className="field-span2 form-err">{formErr}</p> : null}
            <div className="field-span2">
              <button type="submit" className="btn primary" disabled={busy}>
                {busy ? 'Saving…' : 'Add monitor'}
              </button>
            </div>
          </form>
        </section>

        <section className="panel">
          <h2 className="panel-title">Your monitors</h2>
          {rows.length === 0 ? (
            <p className="muted">Nothing here yet — add a URL you want to watch.</p>
          ) : (
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Label</th>
                    <th>URL</th>
                    <th>Last price</th>
                    <th>Next run</th>
                    <th>Status</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {rows.map((m) => (
                    <tr key={m.id}>
                      <td>{m.label || '—'}</td>
                      <td className="cell-url" title={m.product_url}>
                        {m.product_url}
                      </td>
                      <td>{fmtMoney(m.last_price_minor, m.last_currency)}</td>
                      <td className="muted">
                        {m.next_run_at ? new Date(m.next_run_at).toLocaleString() : '—'}
                      </td>
                      <td>
                        <span className={`pill pill-${m.status}`}>{m.status}</span>
                      </td>
                      <td>
                        <button
                          type="button"
                          className="btn link danger"
                          onClick={() => void onDelete(m.id)}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
