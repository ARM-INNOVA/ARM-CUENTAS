import React, { useEffect, useState } from 'react'
import { movementsService } from '../services/api'
import { useDashboardStore } from '../hooks/useStore'

export const DashboardPage = () => {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await movementsService.getDashboard()
        setData(response.data)
      } catch (error) {
        console.error('Error fetching dashboard:', error)
      } finally {
        setLoading(false)
      }
    }
    
    fetchData()
  }, [])
  
  if (loading) {
    return <div className="p-8 text-center">Cargando...</div>
  }
  
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      
      {/* Tarjetas de resumen */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <h3 className="text-gray-600 text-sm font-semibold">Ingresos (Mes)</h3>
          <p className="text-2xl font-bold text-green-600 mt-2">
            {data?.mes?.ingresos?.toFixed(2) || '0.00'}€
          </p>
        </div>
        
        <div className="card">
          <h3 className="text-gray-600 text-sm font-semibold">Gastos (Mes)</h3>
          <p className="text-2xl font-bold text-red-600 mt-2">
            {data?.mes?.gastos?.toFixed(2) || '0.00'}€
          </p>
        </div>
        
        <div className="card">
          <h3 className="text-gray-600 text-sm font-semibold">Beneficio (Mes)</h3>
          <p className="text-2xl font-bold text-blue-600 mt-2">
            {data?.mes?.beneficio?.toFixed(2) || '0.00'}€
          </p>
        </div>
        
        <div className="card">
          <h3 className="text-gray-600 text-sm font-semibold">IVA Soportado</h3>
          <p className="text-2xl font-bold mt-2">
            {data?.mes?.iva_soportado?.toFixed(2) || '0.00'}€
          </p>
        </div>
        
        <div className="card">
          <h3 className="text-gray-600 text-sm font-semibold">IVA Repercutido</h3>
          <p className="text-2xl font-bold mt-2">
            {data?.mes?.iva_repercutido?.toFixed(2) || '0.00'}€
          </p>
        </div>
        
        <div className="card">
          <h3 className="text-gray-600 text-sm font-semibold">Diferencia IVA</h3>
          <p className="text-2xl font-bold mt-2">
            {data?.mes?.diferencia_iva?.toFixed(2) || '0.00'}€
          </p>
        </div>
      </div>
      
      {/* Datos anuales */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Resumen Anual</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-gray-600">Ingresos Anuales</p>
            <p className="text-xl font-bold">{data?.ano?.ingresos?.toFixed(2) || '0.00'}€</p>
          </div>
          <div>
            <p className="text-gray-600">Gastos Anuales</p>
            <p className="text-xl font-bold">{data?.ano?.gastos?.toFixed(2) || '0.00'}€</p>
          </div>
          <div>
            <p className="text-gray-600">Beneficio Anual</p>
            <p className="text-xl font-bold">{data?.ano?.beneficio?.toFixed(2) || '0.00'}€</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
