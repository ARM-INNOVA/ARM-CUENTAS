import React, { useEffect, useState } from 'react'
import AppLayout from '../layouts/AppLayout'
import { obrasService } from '../services/api'

const initialForm = {
  nombre: '',
  cliente: '',
  direccion: '',
  estado: 'activa',
  fecha_inicio: '',
  fecha_fin_prevista: '',
  presupuesto_previsto: 0,
  observaciones: '',
}

export const ObrasPage = () => {
  const [obras, setObras] = useState([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState(initialForm)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  
  useEffect(() => {
    const fetchObras = async () => {
      try {
        const response = await obrasService.list()
        setObras(response.data)
      } catch (error) {
        console.error('Error fetching obras:', error)
        setError('No se pudieron cargar las obras')
      } finally {
        setLoading(false)
      }
    }
    
    fetchObras()
  }, [])

  const submitObra = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    setMessage('')
    try {
      const payload = {
        ...form,
        fecha_inicio: form.fecha_inicio ? new Date(form.fecha_inicio).toISOString() : null,
        fecha_fin_prevista: form.fecha_fin_prevista ? new Date(form.fecha_fin_prevista).toISOString() : null,
        presupuesto_previsto: Number(form.presupuesto_previsto || 0),
      }
      const response = await obrasService.create(payload)
      setObras((prev) => [response.data, ...prev])
      setForm(initialForm)
      setMessage('Obra creada correctamente')
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo crear la obra')
    } finally {
      setSaving(false)
    }
  }
  
  if (loading) {
    return <AppLayout title="Obras" subtitle="Seguimiento de proyectos"><div className="card">Cargando obras...</div></AppLayout>
  }
  
  return (
    <AppLayout title="Obras" subtitle="Controla el estado y presupuesto de cada proyecto">
      {error ? <div className="message error">{error}</div> : null}
      {message ? <div className="message success">{message}</div> : null}
      <div className="dashboard-grid">
        <section className="card">
          <h2 className="section-title">Nueva obra</h2>
          <form className="stack" onSubmit={submitObra}>
            <input className="input-field" placeholder="Nombre de la obra" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} required />
            <input className="input-field" placeholder="Cliente" value={form.cliente} onChange={(e) => setForm({ ...form, cliente: e.target.value })} required />
            <input className="input-field" placeholder="Dirección" value={form.direccion} onChange={(e) => setForm({ ...form, direccion: e.target.value })} />
            <div className="form-grid">
              <select className="input-field" value={form.estado} onChange={(e) => setForm({ ...form, estado: e.target.value })}>
                <option value="activa">Activa</option>
                <option value="pausada">Pausada</option>
                <option value="terminada">Terminada</option>
                <option value="archivada">Archivada</option>
              </select>
              <input className="input-field" type="number" step="0.01" placeholder="Presupuesto" value={form.presupuesto_previsto} onChange={(e) => setForm({ ...form, presupuesto_previsto: e.target.value })} />
            </div>
            <div className="form-grid">
              <input className="input-field" type="date" value={form.fecha_inicio} onChange={(e) => setForm({ ...form, fecha_inicio: e.target.value })} />
              <input className="input-field" type="date" value={form.fecha_fin_prevista} onChange={(e) => setForm({ ...form, fecha_fin_prevista: e.target.value })} />
            </div>
            <textarea className="input-field" placeholder="Observaciones" value={form.observaciones} onChange={(e) => setForm({ ...form, observaciones: e.target.value })} />
            <button className="btn-primary" disabled={saving} type="submit">{saving ? 'Guardando...' : 'Guardar obra'}</button>
          </form>
        </section>
        <section className="card">
          <div className="split">
            <div>
              <h2 className="section-title">Resumen</h2>
              <p className="helper-text">Tus obras visibles y su estado actual.</p>
            </div>
            <span className="status-pill">{obras.length} obras</span>
          </div>
          <div className="stack">
            {obras.map((obra) => (
              <div key={obra.id} className="card-hover">
                <div className="split">
                  <strong>{obra.nombre}</strong>
                  <span className="status-pill">{obra.estado}</span>
                </div>
                <p className="helper-text">{obra.cliente}</p>
                <div className="split">
                  <span className="helper-text">Presupuesto</span>
                  <strong>{Number(obra.presupuesto_previsto || 0).toFixed(2)}€</strong>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </AppLayout>
  )
}

export default ObrasPage
