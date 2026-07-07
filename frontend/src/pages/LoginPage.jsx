import React, { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import '../styles/globals.css'

export const LoginPage = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    
    try {
      await login(username, password)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="min-h-screen" style={{ display: 'grid', placeItems: 'center', padding: '20px' }}>
      <div className="card" style={{ width: '100%', maxWidth: '1120px', display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', overflow: 'hidden' }}>
        <div style={{ padding: '40px', background: 'linear-gradient(160deg, rgba(220,38,38,0.22), rgba(153,27,27,0.1))' }}>
          <p className="eyebrow">ARM CUENTAS</p>
          <h1 style={{ fontSize: 'clamp(2.4rem, 4vw, 4rem)', marginTop: '12px', marginBottom: '20px' }}>Control financiero claro para tu empresa de reformas</h1>
          <p className="helper-text" style={{ maxWidth: '540px', fontSize: '1rem', lineHeight: 1.7 }}>
            Registra ingresos y gastos, sube facturas, revisa datos extraídos y mantén cada obra bajo control desde un único panel.
          </p>
          <div className="stats-grid" style={{ marginTop: '28px', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))' }}>
            <div className="card"><strong>Facturas</strong><p className="helper-text">Subida, revisión y archivo original</p></div>
            <div className="card"><strong>Obras</strong><p className="helper-text">Presupuesto, estado y seguimiento</p></div>
          </div>
        </div>
        <div style={{ padding: '40px' }}>
          <div className="stack">
            <div>
              <h2 className="section-title">Iniciar sesión</h2>
              <p className="helper-text">Accede con tu usuario para ver dashboard, movimientos y facturas.</p>
            </div>

            {error && (
              <div className="message error">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="stack">
              <div>
                <label className="helper-text">Usuario</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="input-field"
                  placeholder="Tu usuario"
                  required
                />
              </div>
              
              <div>
                <label className="helper-text">Contraseña</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-field"
                  placeholder="Tu contraseña"
                  required
                />
              </div>
              
              <button
                type="submit"
                disabled={loading}
                className="btn-primary"
              >
                {loading ? 'Iniciando sesión...' : 'Entrar en ARM CUENTAS'}
              </button>
            </form>

            <div className="card">
              <p className="helper-text">Consejo</p>
              <strong>Usa el panel para subir una factura y revisarla antes de guardar el gasto o ingreso.</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
