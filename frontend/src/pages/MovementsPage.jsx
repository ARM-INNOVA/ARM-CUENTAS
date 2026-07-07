import React, { useEffect, useState } from 'react'
import { movementsService } from '../services/api'

export const MovementsPage = () => {
  const [movements, setMovements] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    tipo: '',
    estado: ''
  })
  
  useEffect(() => {
    const fetchMovements = async () => {
      try {
        const response = await movementsService.list()
        setMovements(response.data)
      } catch (error) {
        console.error('Error fetching movements:', error)
      } finally {
        setLoading(false)
      }
    }
    
    fetchMovements()
  }, [])
  
  if (loading) {
    return <div className="p-8 text-center">Cargando movimientos...</div>
  }
  
  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Movimientos</h1>
        <button className="btn-primary">Nuevo Movimiento</button>
      </div>
      
      {/* Filtros */}
      <div className="card mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm text-gray-600 mb-2">Tipo</label>
            <select
              value={filters.tipo}
              onChange={(e) => setFilters({ ...filters, tipo: e.target.value })}
              className="input-field"
            >
              <option value="">Todos</option>
              <option value="ingreso">Ingreso</option>
              <option value="gasto">Gasto</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm text-gray-600 mb-2">Estado</label>
            <select
              value={filters.estado}
              onChange={(e) => setFilters({ ...filters, estado: e.target.value })}
              className="input-field"
            >
              <option value="">Todos</option>
              <option value="pendiente">Pendiente</option>
              <option value="pagado">Pagado</option>
              <option value="cobrado">Cobrado</option>
            </select>
          </div>
          
          <div className="flex items-end">
            <button className="btn-primary w-full">Filtrar</button>
          </div>
        </div>
      </div>
      
      {/* Tabla de movimientos */}
      <div className="table-responsive card">
        <table className="w-full">
          <thead className="border-b">
            <tr>
              <th className="text-left py-3 px-4 font-semibold">Fecha</th>
              <th className="text-left py-3 px-4 font-semibold">Concepto</th>
              <th className="text-left py-3 px-4 font-semibold">Tipo</th>
              <th className="text-left py-3 px-4 font-semibold">Importe</th>
              <th className="text-left py-3 px-4 font-semibold">Estado</th>
              <th className="text-left py-3 px-4 font-semibold">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {movements.map((m) => (
              <tr key={m.id} className="border-b hover:bg-gray-50">
                <td className="py-3 px-4">{new Date(m.fecha).toLocaleDateString('es-ES')}</td>
                <td className="py-3 px-4">{m.concepto}</td>
                <td className="py-3 px-4">
                  <span className={`px-2 py-1 rounded text-sm ${
                    m.tipo === 'ingreso' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {m.tipo}
                  </span>
                </td>
                <td className="py-3 px-4 font-semibold">{m.importe_total.toFixed(2)}€</td>
                <td className="py-3 px-4">
                  <span className={`px-2 py-1 rounded text-sm ${
                    m.estado === 'pendiente' ? 'bg-yellow-100 text-yellow-800' :
                    m.estado === 'pagado' ? 'bg-blue-100 text-blue-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {m.estado}
                  </span>
                </td>
                <td className="py-3 px-4">
                  <button className="text-blue-600 hover:text-blue-800 text-sm">Editar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default MovementsPage
