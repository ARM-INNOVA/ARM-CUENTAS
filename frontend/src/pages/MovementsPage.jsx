import React, { useEffect, useState } from 'react'
import AppLayout from '../layouts/AppLayout'
import { categoriesService, exportsService, movementsService, obrasService, providersService } from '../services/api'

const initialForm = {
  fecha: new Date().toISOString().slice(0, 16),
  tipo: 'gasto',
  concepto: '',
  descripcion: '',
  obra_id: '',
  categoria_id: '',
  proveedor_id: '',
  numero_factura: '',
  nif_cif: '',
  base_imponible: 0,
  iva_porcentaje: 21,
  iva_cantidad: 0,
  importe_total: 0,
  forma_pago: 'transferencia',
  estado: 'pendiente',
  observaciones: '',
}

const fmtMoney = (v) => Number(v || 0).toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €'
const fmtDate = (d) => (d ? new Date(d).toLocaleDateString('es-ES') : 'Pendiente')

const downloadBlob = (blob, filename) => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  window.URL.revokeObjectURL(url)
}

export const MovementsPage = () => {
  const [movements, setMovements] = useState([])
  const [obras, setObras] = useState([])
  const [categories, setCategories] = useState([])
  const [providers, setProviders] = useState([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [form, setForm] = useState(initialForm)
  const [filters, setFilters] = useState({ tipo: '', estado: '' })

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [movementsResponse, obrasResponse, categoriesResponse, providersResponse] = await Promise.all([
          movementsService.list(),
          obrasService.list(),
          categoriesService.list(),
          providersService.list(),
        ])
        setMovements(movementsResponse.data)
        setObras(obrasResponse.data)
        setCategories(categoriesResponse.data)
        setProviders(providersResponse.data)
      } catch (err) {
        console.error(err)
        setError('No se pudieron cargar movimientos y catálogos')
      } finally {
        setLoading(false)
      }
    }

    fetchInitialData()
  }, [])

  const filteredMovements = movements.filter((movement) => {
    if (filters.tipo && movement.tipo !== filters.tipo) return false
    if (filters.estado && movement.estado !== filters.estado) return false
    return true
  })

  const submitMovement = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    setMessage('')
    try {
      const payload = {
        ...form,
        fecha: new Date(form.fecha).toISOString(),
        obra_id: form.obra_id ? Number(form.obra_id) : null,
        categoria_id: form.categoria_id ? Number(form.categoria_id) : null,
        proveedor_id: form.proveedor_id ? Number(form.proveedor_id) : null,
        base_imponible: Number(form.base_imponible),
        iva_porcentaje: Number(form.iva_porcentaje),
        iva_cantidad: Number(form.iva_cantidad),
        importe_total: Number(form.importe_total),
      }
      const response = await movementsService.create(payload)
      setMovements((prev) => [response.data, ...prev])
      setForm(initialForm)
      setMessage('Movimiento guardado correctamente')
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo guardar el movimiento')
    } finally {
      setSaving(false)
    }
  }

  const exportData = async (type) => {
    const response = type === 'excel' ? await exportsService.excel() : await exportsService.csv()
    downloadBlob(response.data, type === 'excel' ? 'movimientos.xlsx' : 'movimientos.csv')
  }

  if (loading) {
    return <AppLayout title="Movimientos" subtitle="Ingresos y gastos"><div className="card">Cargando movimientos...</div></AppLayout>
  }

  return (
    <AppLayout
      title="Movimientos"
      subtitle="Alta y control de facturas/movimientos"
      actions={
        <>
          <button className="btn-secondary" onClick={() => exportData('csv')}>CSV</button>
          <button className="btn-primary" onClick={() => exportData('excel')}>Excel</button>
        </>
      }
    >
      {error ? <div className="message error">{error}</div> : null}
      {message ? <div className="message success">{message}</div> : null}

      <div className="dashboard-grid">
        <section className="card">
          <h2 className="section-title">Nuevo movimiento</h2>
          <form className="stack" onSubmit={submitMovement}>
            <div className="form-grid">
              <input className="input-field" type="datetime-local" value={form.fecha} onChange={(e) => setForm({ ...form, fecha: e.target.value })} required />
              <select className="input-field" value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })}>
                <option value="gasto">Gasto</option>
                <option value="ingreso">Ingreso</option>
              </select>
            </div>
            <input className="input-field" placeholder="Concepto" value={form.concepto} onChange={(e) => setForm({ ...form, concepto: e.target.value })} required />
            <textarea className="input-field" placeholder="Descripción" value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} />
            <div className="form-grid">
              <select className="input-field" value={form.obra_id} onChange={(e) => setForm({ ...form, obra_id: e.target.value })}><option value="">Sin obra</option>{obras.map((obra) => <option key={obra.id} value={obra.id}>{obra.nombre}</option>)}</select>
              <select className="input-field" value={form.categoria_id} onChange={(e) => setForm({ ...form, categoria_id: e.target.value })}><option value="">Sin categoría</option>{categories.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}</select>
            </div>
            <div className="form-grid">
              <select className="input-field" value={form.proveedor_id} onChange={(e) => setForm({ ...form, proveedor_id: e.target.value })}><option value="">Sin proveedor</option>{providers.map((p) => <option key={p.id} value={p.id}>{p.nombre}</option>)}</select>
              <input className="input-field" placeholder="Número de factura" value={form.numero_factura} onChange={(e) => setForm({ ...form, numero_factura: e.target.value })} />
            </div>
            <div className="form-grid">
              <input className="input-field" type="number" step="0.01" placeholder="Base imponible" value={form.base_imponible} onChange={(e) => setForm({ ...form, base_imponible: e.target.value })} />
              <input className="input-field" type="number" step="1" placeholder="IVA %" value={form.iva_porcentaje} onChange={(e) => setForm({ ...form, iva_porcentaje: e.target.value })} />
            </div>
            <div className="form-grid">
              <input className="input-field" type="number" step="0.01" placeholder="Cuota IVA" value={form.iva_cantidad} onChange={(e) => setForm({ ...form, iva_cantidad: e.target.value })} />
              <input className="input-field" type="number" step="0.01" placeholder="Total" value={form.importe_total} onChange={(e) => setForm({ ...form, importe_total: e.target.value })} required />
            </div>
            <div className="form-grid">
              <select className="input-field" value={form.estado} onChange={(e) => setForm({ ...form, estado: e.target.value })}><option value="pendiente">Pendiente</option><option value="pagado">Pagado</option><option value="cobrado">Cobrado</option></select>
              <select className="input-field" value={form.forma_pago} onChange={(e) => setForm({ ...form, forma_pago: e.target.value })}><option value="transferencia">Transferencia</option><option value="banco">Banco</option><option value="tarjeta">Tarjeta</option><option value="bizum">Bizum</option><option value="efectivo">Efectivo</option><option value="otro">Otro</option></select>
            </div>
            <button className="btn-primary" disabled={saving} type="submit">{saving ? 'Guardando...' : 'Guardar movimiento'}</button>
          </form>
        </section>

        <section className="card">
          <h2 className="section-title">Filtros rápidos</h2>
          <div className="stack">
            <select className="input-field" value={filters.tipo} onChange={(e) => setFilters({ ...filters, tipo: e.target.value })}><option value="">Todos los tipos</option><option value="ingreso">Ingreso</option><option value="gasto">Gasto</option></select>
            <select className="input-field" value={filters.estado} onChange={(e) => setFilters({ ...filters, estado: e.target.value })}><option value="">Todos los estados</option><option value="pendiente">Pendiente</option><option value="pagado">Pagado</option><option value="cobrado">Cobrado</option></select>
            <div className="split"><span className="helper-text">Total visible</span><strong>{filteredMovements.length}</strong></div>
          </div>
        </section>
      </div>

      <section className="card">
        <h2 className="section-title">Listado de facturas y movimientos</h2>

        <div className="table-responsive desktop-only">
          <table className="data-table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Proveedor</th>
                <th>Nº factura</th>
                <th>Obra</th>
                <th>Categoría</th>
                <th>Base imponible</th>
                <th>IVA</th>
                <th>Total</th>
                <th>Estado</th>
                <th>Archivo</th>
                <th>Revisión</th>
              </tr>
            </thead>
            <tbody>
              {filteredMovements.map((m) => {
                const file = (m.files || [])[0]
                const needsReview = !!(m.files || []).find((f) => f.necesita_revision)
                return (
                  <tr key={m.id}>
                    <td>{fmtDate(m.fecha)}</td>
                    <td>{m.proveedor?.nombre || 'Sin asignar'}</td>
                    <td>{m.numero_factura || 'Pendiente'}</td>
                    <td>{m.obra?.nombre || 'Sin asignar'}</td>
                    <td>{m.categoria?.nombre || 'Sin asignar'}</td>
                    <td>{fmtMoney(m.base_imponible)}</td>
                    <td>{fmtMoney(m.iva_cantidad)} ({m.iva_porcentaje || '-'}%)</td>
                    <td>{fmtMoney(m.importe_total)}</td>
                    <td>{m.estado || 'Pendiente'}</td>
                    <td>{file?.nombre_original || 'Sin archivo'}</td>
                    <td>{needsReview ? 'Pendiente' : 'OK'}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        <div className="mobile-cards">
          {filteredMovements.map((m) => {
            const file = (m.files || [])[0]
            const needsReview = !!(m.files || []).find((f) => f.necesita_revision)
            return (
              <article key={m.id} className="card movement-item">
                <div className="split"><strong>{m.numero_factura || 'Pendiente'}</strong><span>{fmtDate(m.fecha)}</span></div>
                <p><strong>Proveedor:</strong> {m.proveedor?.nombre || 'Sin asignar'}</p>
                <p><strong>Obra:</strong> {m.obra?.nombre || 'Sin asignar'}</p>
                <p><strong>Categoría:</strong> {m.categoria?.nombre || 'Sin asignar'}</p>
                <p><strong>Base:</strong> {fmtMoney(m.base_imponible)}</p>
                <p><strong>IVA:</strong> {fmtMoney(m.iva_cantidad)} ({m.iva_porcentaje || '-'}%)</p>
                <p><strong>Total:</strong> {fmtMoney(m.importe_total)}</p>
                <p><strong>Estado:</strong> {m.estado || 'Pendiente'}</p>
                <p><strong>Archivo:</strong> {file?.nombre_original || 'Sin archivo'}</p>
                <p><strong>Revisión:</strong> {needsReview ? 'Pendiente' : 'OK'}</p>
              </article>
            )
          })}
        </div>
      </section>
    </AppLayout>
  )
}

export default MovementsPage
