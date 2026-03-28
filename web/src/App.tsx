import './App.css'

const navItems = [
  { id: 'monitors', label: 'Monitors' },
  { id: 'runs', label: 'Runs' },
  { id: 'settings', label: 'Settings' },
] as const

function App() {
  return (
    <div className="app">
      <aside className="sidebar" aria-label="Main">
        <div className="sidebar-brand">Watchtower</div>
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <button key={item.id} type="button" className="nav-item">
              {item.label}
            </button>
          ))}
        </nav>
      </aside>
      <main className="main">
        <header className="main-header">
          <h1 className="main-title">Monitors</h1>
          <p className="main-subtitle">
            Add a product URL and a natural-language schedule — email alerts when
            the price moves.
          </p>
        </header>
        <section className="main-empty" aria-live="polite">
          <p>No monitors yet. Implementation follows the v1 eng plan.</p>
        </section>
      </main>
    </div>
  )
}

export default App
