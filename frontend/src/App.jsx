import { useEffect, useRef, useState } from 'react'
import {
  AlertTriangle, ArrowRight, CheckCircle2, HelpCircle, Eye,
  EyeOff, FileSpreadsheet, FileText, KeyRound, Loader2, LogOut,
  Mail, ShieldCheck, Sparkles, UploadCloud, X
} from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_URL || ''
const acceptedTypes = [
  'application/pdf',
  'text/csv',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
]
const progressSteps = [
  'Parsing uploaded documents',
  'Building source-aware financial records',
  'Checking required financial signals',
  'Reviewing gaps and trajectory patterns',
  'Assembling cited analysis',
]

function api(path, options = {}, token = '') {
  return fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { ...(options.headers || {}), ...(token ? { Authorization: `Bearer ${token}` } : {}) },
  })
}

async function readResponse(response) {
  const contentType = response.headers.get('content-type') || ''
  const payload = contentType.includes('application/json')
    ? await response.json()
    : { detail: await response.text() }
  if (!response.ok) throw new Error(payload.detail || 'The request could not be completed.')
  return payload
}

function Brand({ compact = false }) {
  return <div className="brand">
    <div className="brand-mark" aria-hidden="true">C</div>
    {!compact && <div><strong>Clarafin</strong><span>Financial clarity, grounded in your documents</span></div>}
  </div>
}

function PasswordField({ value, onChange, label = 'Password', autoComplete = 'current-password' }) {
  const [visible, setVisible] = useState(false)
  return <label className="field-label">{label}
    <div className="password-wrap">
      <input type={visible ? 'text' : 'password'} value={value} onChange={onChange} autoComplete={autoComplete} minLength="8" required />
      <button type="button" className="icon-button password-button" onClick={() => setVisible(!visible)} aria-label={visible ? 'Hide password' : 'Show password'}>
        {visible ? <EyeOff size={18} /> : <Eye size={18} />}
      </button>
    </div>
  </label>
}

function AuthScreen({ onAuthenticated }) {
  const [mode, setMode] = useState('signin')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (event) => {
    event.preventDefault()
    setBusy(true); setMessage('')
    try {
      if (mode === 'forgot') {
        setMessage('Password reset email delivery will be enabled after the email service is configured. For the prototype, contact the administrator.')
        return
      }
      const path = mode === 'signup' ? '/auth/signup' : '/auth/login'
      const response = await api(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) })
      const data = await readResponse(response)
      if (mode === 'signup') { setMode('signin'); setMessage('Account created. Sign in to continue.'); return }
      onAuthenticated(data.access_token, email)
    } catch (error) { setMessage(error.message || 'Connection error. Please check that the backend is running.') }
    finally { setBusy(false) }
  }

  const demoLogin = async () => {
    setBusy(true); setMessage('')
    try {
      const response = await api('/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email: 'demo@sme-agent.com', password: 'demo1234' }) })
      const data = await readResponse(response)
      onAuthenticated(data.access_token, 'demo@sme-agent.com')
    } catch (error) { setMessage(error.message) }
    finally { setBusy(false) }
  }

  const isForgot = mode === 'forgot'
  return <main className="auth-page">
    <div className="ambient ambient-one" /><div className="ambient ambient-two" />
    <section className="auth-copy">
      <Brand />
      <p className="eyebrow">FINANCIAL DOCUMENT INTELLIGENCE</p>
      <h1>Know what your numbers are telling you.</h1>
      <p className="lead">Clarafin reads the financial documents your business already has, explains the current state, identifies gaps, and highlights reasoned forward-looking flags.</p>
      <div className="promise-list">
        <span><ShieldCheck size={18} /> Every claim is traceable to a source</span>
        <span><Sparkles size={18} /> Analysis starts when documents are uploaded</span>
        <span><HelpCircle size={18} /> No tax or investment recommendations</span>
      </div>
    </section>

    <section className="auth-card" aria-label="Clarafin account access">
      <div className="auth-card-heading"><Brand compact /><div><p className="eyebrow">WELCOME TO CLARAFIN</p><h2>{isForgot ? 'Reset your password' : mode === 'signup' ? 'Create your account' : 'Sign in to your workspace'}</h2></div></div>
      {isForgot && <p className="helper-copy">Enter your email address. In the production version, we will send a secure password-reset link.</p>}
      <form onSubmit={submit} className="auth-form">
        <label className="field-label">Email address
          <div className="input-with-icon"><Mail size={17} /><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" autoComplete="email" required /></div>
        </label>
        {!isForgot && <PasswordField value={password} onChange={(e) => setPassword(e.target.value)} autoComplete={mode === 'signup' ? 'new-password' : 'current-password'} />}
        {message && <p className="form-message">{message}</p>}
        <button className="primary-button" disabled={busy}>{busy ? <Loader2 className="spin" size={18} /> : <>{isForgot ? 'Request reset link' : mode === 'signup' ? 'Create account' : 'Sign in'} <ArrowRight size={18} /></>}</button>
      </form>
      {!isForgot && <><button className="text-button align-right" onClick={() => { setMode('forgot'); setMessage('') }}>Forgot password?</button><div className="divider"><span>or</span></div>
        <button type="button" className="google-button" onClick={() => setMessage('Google sign-in is planned. It needs a Google OAuth client ID before it can be enabled securely.')}><span className="google-g">G</span> Continue with Google</button>
        <button type="button" className="demo-button" onClick={demoLogin} disabled={busy}><Sparkles size={16} /> Try the demo account</button>
      </>}
      <p className="auth-switch">{isForgot ? <button className="text-button" onClick={() => { setMode('signin'); setMessage('') }}>Back to sign in</button> : mode === 'signup' ? <>Already have an account? <button className="text-button" onClick={() => setMode('signin')}>Sign in</button></> : <>New to Clarafin? <button className="text-button" onClick={() => setMode('signup')}>Create an account</button></>}</p>
    </section>
  </main>
}

function UploadBox({ onFiles, uploading }) {
  const picker = useRef(null)
  const [over, setOver] = useState(false)
  const select = (files) => { const valid = [...files].filter((file) => acceptedTypes.includes(file.type) || /\.(pdf|csv|xlsx|xls)$/i.test(file.name)); if (valid.length) onFiles(valid) }
  return <div className={`upload-box ${over ? 'over' : ''}`} onDragOver={(e) => { e.preventDefault(); setOver(true) }} onDragLeave={() => setOver(false)} onDrop={(e) => { e.preventDefault(); setOver(false); select(e.dataTransfer.files) }}>
    <input ref={picker} type="file" accept=".pdf,.csv,.xlsx,.xls" multiple onChange={(e) => select(e.target.files)} hidden />
    <div className="upload-icon"><UploadCloud size={25} /></div><h3>{uploading ? 'Uploading documents...' : 'Drop files here'}</h3><p>or <button type="button" className="inline-link" onClick={() => picker.current?.click()}>browse your computer</button></p><span>PDF, CSV, XLSX - Native or scanned PDF</span>
  </div>
}

function Citation({ citation, onSelect }) { return <button className="citation" onClick={() => onSelect?.(citation)}><FileText size={13} /> {citation.doc || citation.filename} · {citation.loc || citation.location}</button> }

function AnalysisResults({ result, citation }) {
  const [tab, setTab] = useState('current')
  if (result?.error) return <div className="empty-analysis"><AlertTriangle size={28} /><h3>Analysis could not be completed</h3><p>{result.error}</p></div>
  const current = result?.current_state || {}
  const cards = [current.liquidity, current.margins, current.concentration].filter(Boolean)
  return <section className="analysis-card"><div className="tabs"><button className={tab === 'current' ? 'active' : ''} onClick={() => setTab('current')}>Current state</button><button className={tab === 'gaps' ? 'active' : ''} onClick={() => setTab('gaps')}>Gaps detected</button><button className={tab === 'flags' ? 'active' : ''} onClick={() => setTab('flags')}>Forward flags</button></div>
    <div className="analysis-content">
      {tab === 'current' && <><div className="metric-grid">{cards.map((item, index) => <article className="metric-card" key={item.metric || index}><span>{item.metric}</span><strong>{item.value}</strong><p>{item.interpretation}</p>{item.citations?.map((itemCitation, i) => <Citation key={i} citation={itemCitation} onSelect={citation} />)}</article>)}</div><section className="anomaly-section"><h3>Expense and transaction patterns</h3>{current.anomalies?.length ? current.anomalies.map((anomaly, index) => <article className="anomaly" key={index}><AlertTriangle size={18} /><div><strong>{anomaly.title}</strong><p>{anomaly.description}</p>{anomaly.citations?.map((itemCitation, i) => <Citation key={i} citation={itemCitation} />)}</div></article>) : <p className="muted">No anomalous patterns were returned from the uploaded set.</p>}</section></>}
      {tab === 'gaps' && <><p className="notice">Gaps are not errors. They show which decisions cannot yet be supported by the uploaded documents.</p>{result?.gap_detection?.map((gap, index) => <article className="gap-card" key={index}><span>Missing</span><h3>{gap.missing_item}</h3><div><p><b>Decision currently blocked</b>{gap.blocked_decision}</p><p><b>Why it matters</b>{gap.explanation}</p></div></article>)}</>}
      {tab === 'flags' && <><p className="notice amber">Forward-looking flags are reasoned patterns from the available trajectory—not forecasts or recommendations.</p>{result?.forward_flags?.map((flag, index) => <article className={`flag-card ${flag.severity?.toLowerCase() || 'low'}`} key={index}><div><h3>{flag.flag_type}</h3><p>{flag.trajectory_observation}</p></div><span>{flag.severity} risk</span></article>)}</>}
    </div>
  </section>
}

function Dashboard({ token, email, onLogout }) {
  const [documents, setDocuments] = useState([]); const [selected, setSelected] = useState([]); const [uploading, setUploading] = useState(false); const [error, setError] = useState('')
  const [analysis, setAnalysis] = useState(null); const [progress, setProgress] = useState(''); const [running, setRunning] = useState(false); const [citation, setCitation] = useState(null)
  const [apiKey, setApiKey] = useState(sessionStorage.getItem('clarafin-groq-key') || '')
  const loadDocuments = async () => { try { const response = await api('/documents', {}, token); if (response.status === 401) return onLogout(); setDocuments(await readResponse(response)) } catch { setError('Could not load documents. Check that the backend is running.') } }
  useEffect(() => { loadDocuments() }, [])
  useEffect(() => { if (!running || !analysis?.id) return; const timer = setInterval(async () => { try { const response = await api(`/analysis/${analysis.id}`, {}, token); const data = await response.json(); setProgress(data.progress_message || 'Analyzing documents...'); if (data.status === 'finished' || data.status === 'failed') { setAnalysis(data); setRunning(false) } } catch { setRunning(false); setError('Lost connection while checking analysis status.') } }, 1300); return () => clearInterval(timer) }, [running, analysis?.id])
  const startAnalysis = async (docIds) => { if (!docIds.length) return setError('Select at least one document before starting the analysis.'); setError(''); setAnalysis(null); setRunning(true); setProgress('Queuing your document analysis...'); try { const response = await api('/analysis/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ doc_ids: docIds, groq_api_key: apiKey || null }) }, token); if (response.status === 401) return onLogout(); setAnalysis(await readResponse(response)) } catch (runError) { setRunning(false); setError(runError.message) } }
  const upload = async (files) => { setUploading(true); setError(''); try { const uploadedDocuments = []; for (const file of files) { const form = new FormData(); form.append('file', file); const response = await api('/documents/upload', { method: 'POST', body: form }, token); if (response.status === 401) return onLogout(); uploadedDocuments.push(await readResponse(response)) } const uploadedIds = uploadedDocuments.map((document) => document.id); setSelected(uploadedIds); await loadDocuments(); await startAnalysis(uploadedIds) } catch (uploadError) { setError(uploadError.message) } finally { setUploading(false) } }
  const run = async () => startAnalysis(selected)
  return <div className="app-shell"><header className="topbar"><Brand /><div className="account"><span>{email}</span><button onClick={onLogout}><LogOut size={16} /> Sign out</button></div></header><main className="workspace"><aside className="sidebar"><div className="side-heading"><div><p className="eyebrow">YOUR DOCUMENTS</p><h2>Financial workspace</h2></div><span>{documents.length}</span></div><UploadBox onFiles={upload} uploading={uploading} />{error && <p className="error-message">{error}</p>}<div className="document-list">{documents.length === 0 ? <p className="muted documents-empty">No files uploaded yet.</p> : documents.map((doc) => <label className={`document-row ${selected.includes(doc.id) ? 'selected' : ''}`} key={doc.id}><input type="checkbox" checked={selected.includes(doc.id)} onChange={() => setSelected((items) => items.includes(doc.id) ? items.filter((id) => id !== doc.id) : [...items, doc.id])} /><FileSpreadsheet size={18} /><div><strong>{doc.filename}</strong><span>{doc.doc_type} · {new Date(doc.upload_date).toLocaleDateString()}</span></div></label>)}</div><button className="primary-button analyze-button" onClick={run} disabled={running || !selected.length}>{running ? <Loader2 size={18} className="spin" /> : <Sparkles size={18} />} Analyze {selected.length || ''} document{selected.length === 1 ? '' : 's'}</button></aside><section className="main-panel"><div className="panel-heading"><div><p className="eyebrow">AUTONOMOUS ANALYSIS</p><h1>Financial intelligence, with evidence.</h1><p>Upload a bank statement, P&amp;L, invoice ledger, balance sheet, or cash-flow report to begin.</p></div><label className="api-key"><KeyRound size={16} /><input type="password" value={apiKey} onChange={(e) => { setApiKey(e.target.value); sessionStorage.setItem('clarafin-groq-key', e.target.value) }} placeholder="Groq API key (optional)" /></label></div>{running && <section className="progress-card"><div className="progress-top"><Loader2 className="spin" size={18} /><strong>{progress || 'Preparing analysis…'}</strong></div><div className="progress-steps">{progressSteps.map((step) => <span key={step} className={progress?.toLowerCase().includes(step.split(' ')[0].toLowerCase()) ? 'now' : ''}><CheckCircle2 size={15} /> {step}</span>)}</div></section>}{analysis?.result ? <AnalysisResults result={analysis.result} citation={setCitation} /> : !running && <section className="empty-state"><div className="empty-icon"><Sparkles size={25} /></div><h2>Ready when your documents are.</h2><p>Select one or more documents in the workspace. Clarafin will begin analysis automatically when you choose <b>Analyze documents</b>.</p><div className="scope"><span>PDF</span><span>CSV</span><span>XLSX</span></div></section>}</section></main>{citation && <div className="citation-modal-backdrop" onClick={() => setCitation(null)}><section className="citation-modal" onClick={(event) => event.stopPropagation()}><button className="icon-button modal-close" onClick={() => setCitation(null)}><X size={18} /></button><p className="eyebrow">SOURCE TRACEABILITY</p><h2>{citation.doc || citation.filename}</h2><p className="source-location">{citation.loc || citation.location}</p><blockquote>{citation.text || citation.detail || 'No source excerpt was provided.'}</blockquote></section></div>}</div>
}

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('clarafin-token') || ''); const [email, setEmail] = useState(localStorage.getItem('clarafin-email') || '')
  const auth = (nextToken, nextEmail) => { localStorage.setItem('clarafin-token', nextToken); localStorage.setItem('clarafin-email', nextEmail); setToken(nextToken); setEmail(nextEmail) }
  const logout = () => { localStorage.removeItem('clarafin-token'); localStorage.removeItem('clarafin-email'); setToken(''); setEmail('') }
  return token ? <Dashboard token={token} email={email} onLogout={logout} /> : <AuthScreen onAuthenticated={auth} />
}
