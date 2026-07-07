import React, { useEffect, useState } from 'react'
import AppLayout from '../layouts/AppLayout'
import { exportsService, movementsService, obrasService } from '../services/api'

const downloadBlob = (blob, filename) => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  window.URL.revokeObjectURL(url)
}

export const DashboardPage = () => {
  const [data, setData] = useState(null)
  const [recentMovements, setRecentMovements] = useState([])
  const [obraCount, setObraCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dashboardResponse, movementsResponse, obrasResponse] = await Promise.all([
          movementsService.getDashboard(),
          movementsService.list({ limit: 6 }),
          obrasService.list(),
        ])
        setData(dashboardResponse.data)
        setRecentMovements(movementsResponse.data)
        setObraCount(obrasResponse.data.length)
      } catch (error) {
        console.error('Error fetching dashboard:', error)
        setError('No se pudieron cargar los datos del panel')
      } finally {
        setLoading(false)
      }
    }
    
    fetchData()
  }, [])

  const exportCurrentMonth = async (type) => {
    const now = new Date()
    const params = { year: now.getFullYear(), month: now.getMonth() + 1 }
    const response = type === 'excel' ? await exportsService.excel(params) : await exportsService.csv(params)
    downloadBlob(response.data, type === 'excel' ? 'movimientos-mes.xlsx' : 'movimientos-mes.csv')
  }
  
  if (loading) {
    return <AppLayout title="Dashboard" subtitle="Resumen financiero de la empresa"><div className="card">Cargando panel...</div></AppLayout>
  }
  
  return (
    <AppLayout
      title="Dashboard"
      subtitle="Control rápido de ingresos, gastos, obras y facturas pendientes"
      actions={
        <>
          <button className="btn-secondary" onClick={() => exportCurrentMonth('csv')}>Exportar CSV</button>
          <button className="btn-primary" onClick={() => exportCurrentMonth('excel')}>Exportar Excel</button>
        </>
      }
    >
      {error ? <div className="message error">{error}</div> : null}

      <section className="stats-grid">
        <div className="card"><p className="helper-text">Ingresos del mes</p><h2 className="tag-success">{data?.mes?.ingresos?.toFixed(2) || '0.00'}€</h2></div>
        <div className="card"><p className="helper-text">Gastos del mes</p><h2 className="tag-danger">{data?.mes?.gastos?.toFixed(2) || '0.00'}€</h2></div>
        <div className="card"><p className="helper-text">Beneficio del mes</p><h2>{data?.mes?.beneficio?.toFixed(2) || '0.00'}€</h2></div>
        <div className="card"><p className="helper-text">Obras activas</p><h2>{obraCount}</h2></div>
      </section>

      <section className="dashboard-grid">
        <div className="card">
          <div className="split">
            <div>
              <h2 className="section-title">Últimos movimientos</h2>
              <p className="helper-text">Movimientos recientes para revisión rápida.</p>
            </div>
            <span className="status-pill">{recentMovements.length} visibles</span>
          </div>
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Concepto</th>
                  <th>Tipo</th>
                  <th>Importe</th>
                </tr>
              </thead>
              <tbody>
                {recentMovements.map((movement) => (
                  <tr key={movement.id}>
                    <td>{new Date(movement.fecha).toLocaleDateString('es-ES')}</td>
                    <td>{movement.concepto}</td>
                    <td>{movement.tipo}</td>
                    <td>{Number(movement.importe_total).toFixed(2)}€</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="stack">
          <div className="card">
            <h2 className="section-title">Resumen anual</h2>
            <div className="stack">
              <div className="split"><span className="helper-text">Ingresos</span><strong>{data?.ano?.ingresos?.toFixed(2) || '0.00'}€</strong></div>
              <div className="split"><span className="helper-text">Gastos</span><strong>{data?.ano?.gastos?.toFixed(2) || '0.00'}€</strong></div>
              <div className="split"><span className="helper-text">Beneficio</span><strong>{data?.ano?.beneficio?.toFixed(2) || '0.00'}€</strong></div>
            </div>
          </div>
          <div className="card">
            <h2 className="section-title">IVA y revisión</h2>
            <div className="stack">
              <div className="split"><span className="helper-text">IVA soportado</span><strong>{data?.mes?.iva_soportado?.toFixed(2) || '0.00'}€</strong></div>
              <div className="split"><span className="helper-text">IVA repercutido</span><strong>{data?.mes?.iva_repercutido?.toFixed(2) || '0.00'}€</strong></div>
              <div className="split"><span className="helper-text">Diferencia</span><strong>{data?.mes?.diferencia_iva?.toFixed(2) || '0.00'}€</strong></div>
              <div className="split"><span className="helper-text">Pendientes</span><strong>{data?.movimientos_pendientes || 0}</strong></div>
              <div className="split"><span className="helper-text">Facturas a revisar</span><strong>{data?.facturas_pendiente_revision || 0}</strong></div>
            </div>
          </div>
        </div>
      </section>
    </AppLayout>
  )
}

export default DashboardPage
