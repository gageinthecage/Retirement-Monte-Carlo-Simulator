#All Frontend Code

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Retirement Simulator</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
package.json
{
  "name": "retirement-simulator-ui",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "d3": "^7.9.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.4.0"
  }
}
vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
src/index.css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #0f172a;       --surface: #1e293b;    --surface2: #263347;
  --border: #334155;   --text: #f1f5f9;       --text-muted: #94a3b8;
  --accent: #3b82f6;   --accent-glow: rgba(59,130,246,0.15);
  --green: #22c55e;    --amber: #f59e0b;      --red: #ef4444;
  --purple: #a78bfa;   --radius: 12px;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  line-height: 1.5;
}
src/main.jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode><App /></StrictMode>
)
src/App.jsx
import { useState } from 'react'
import './App.css'
import SimulationForm from './components/SimulationForm'
import SimulationChart from './components/SimulationChart'
import DistributionChart from './components/DistributionChart'

const API = 'http://127.0.0.1:8000'

export default function App() {
  const [result, setResult] = useState(null)
  const [params, setParams]  = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  async function handleSimulate(values) {
    setLoading(true); setError(null); setParams(values)
    try {
      const { starting, monthly, target } = values
      const res = await fetch(
        `${API}/simulate?starting=${starting}&monthly=${monthly}&target=${target}`,
        { method: 'POST' }
      )
      if (!res.ok) throw new Error((await res.json().catch(()=>({}))).detail || `Error ${res.status}`)
      setResult(await res.json())
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  const s = result?.stats ?? {}
  const fmt = (n, d=1) => n?.toFixed(d) ?? '—'

  return (
    <div className="app">
      <header className="app-header">
        <h1>Retirement Portfolio Simulator</h1>
        <p>Monte Carlo · Geometric Brownian Motion · S&amp;P 500 historical parameters</p>
      </header>

      <SimulationForm onSimulate={handleSimulate} loading={loading} />
      {error && <div className="error-banner">{error}</div>}

      {result && (<>
        <div className="stats-row">
          <div className="stat-card">
            <div className="stat-label">Success Rate</div>
            <div className={`stat-value ${result.success_rate>=80?'green':result.success_rate>=50?'amber':'red'}`}>
              {result.success_rate?.toFixed(1)}%
            </div>
            <div className="stat-sub">reach target within {result.parameters?.annual_return_pct}% avg return</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Median Retirement</div>
            <div className="stat-value blue">{fmt(s.median_years)} <span style={{fontSize:14,fontWeight:500}}>yrs</span></div>
            <div className="stat-sub">50% of simulations</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Best 10% (p10)</div>
            <div className="stat-value green">{fmt(s.p10_years)} <span style={{fontSize:14,fontWeight:500}}>yrs</span></div>
            <div className="stat-sub">fastest paths</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Worst 10% (p90)</div>
            <div className="stat-value amber">{fmt(s.p90_years)} <span style={{fontSize:14,fontWeight:500}}>yrs</span></div>
            <div className="stat-sub">slowest successful paths</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Simulations Run</div>
            <div className="stat-value purple">{result.n_simulations?.toLocaleString()}</div>
            <div className="stat-sub">independent paths</div>
          </div>
        </div>

        <SimulationChart paths={result.individual_paths} bands={result.bands}
          monthsAxis={result.months_axis} targetAmount={params?.target} yMax={result.y_max} />
        <DistributionChart histogram={result.histogram} stats={s} />
      </>)}
    </div>
  )
}
src/App.css — (full file shown above in the Read output — 275 lines of styles)
src/components/SimulationForm.jsx
import { useState } from 'react'

function NumericInput({ label, id, value, onChange, placeholder }) {
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <div className="input-wrap">
        <span className="dollar">$</span>
        <input id={id} type="number" min="0" step="any"
          value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder} />
      </div>
    </div>
  )
}

export default function SimulationForm({ onSimulate, loading }) {
  const [starting, setStarting] = useState('')
  const [monthly, setMonthly]   = useState('')
  const [target, setTarget]     = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    const s=parseFloat(starting), m=parseFloat(monthly), t=parseFloat(target)
    if (isNaN(s)||isNaN(m)||isNaN(t)||s<0||m<0||t<=0) return
    onSimulate({ starting: s, monthly: m, target: t })
  }

  return (
    <form className="form-card" onSubmit={handleSubmit}>
      <div className="form-grid">
        <NumericInput label="Starting Amount"       id="starting" value={starting} onChange={setStarting} placeholder="50,000" />
        <NumericInput label="Monthly Contribution"  id="monthly"  value={monthly}  onChange={setMonthly}  placeholder="1,000" />
        <NumericInput label="Target Amount"         id="target"   value={target}   onChange={setTarget}   placeholder="1,000,000" />
      </div>
      <button className="btn-simulate" type="submit" disabled={loading||!starting||!monthly||!target}>
        {loading && <span className="spinner" />}
        {loading ? 'Simulating…' : 'Run Simulation'}
      </button>
    </form>
  )
