import React, { useEffect, useState } from 'react'
import { obrasService } from '../services/api'

export const ObrasPage = () => {
  const [obras, setObras] = useState([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    const fetchObras = async () => {
      try {
        const response = await obrasService.list()
        setObras(response.data)
      } catch (error) {
        console.error('Error fetching obras:', error)
      } finally {
        setLoading(false)
      }
    }
    
    fetchObras()
  }, [])
  
  if (loading) {
    return <div className="p-8 text-center">Cargando obras...</div>
  }
  
  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Obras</h1>
        <button className="btn-primary">Nueva Obra</button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {obras.map((obra) => (
          <div key={obra.id} className="card-hover">
            <h3 className="text-lg font-bold mb-2">{obra.nombre}</h3>
            <p className="text-gray-600 text-sm mb-4">{obra.cliente}</p>
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Estado:</span>
                <span className={`px-2 py-1 rounded ${
                  obra.estado === 'activa' ? 'bg-green-100 text-green-800' :
                  obra.estado === 'pausada' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {obra.estado}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Presupuesto:</span>
                <span className="font-semibold">{obra.presupuesto_previsto || '0.00'}€</span>
              </div>
            </div>
            
            <button className="btn-sm btn-primary w-full mt-4">Ver Detalles</button>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ObrasPage
