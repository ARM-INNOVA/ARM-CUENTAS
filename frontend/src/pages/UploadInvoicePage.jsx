import React, { useState } from 'react'
import { filesService } from '../services/api'

export const UploadInvoicePage = () => {
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [extracted, setExtracted] = useState(null)
  const [error, setError] = useState('')
  
  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    
    const droppedFiles = Array.from(e.dataTransfer.files)
    handleFiles(droppedFiles)
  }
  
  const handleFiles = (fileList) => {
    setFiles(prev => [...prev, ...fileList])
  }
  
  const handleUpload = async () => {
    if (files.length === 0) return
    
    setUploading(true)
    setError('')
    
    try {
      for (const file of files) {
        const response = await filesService.upload(file)
        setExtracted(response.data)
      }
      setFiles([])
    } catch (err) {
      setError('Error al subir el archivo')
      console.error(err)
    } finally {
      setUploading(false)
    }
  }
  
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Subir Factura</h1>
      
      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center bg-gray-50 hover:bg-gray-100 transition cursor-pointer"
      >
        <p className="text-gray-600 mb-2">Arrastra facturas aquí o haz clic para seleccionar</p>
        <p className="text-sm text-gray-500">PDF, JPG, PNG o WEBP</p>
        
        <input
          type="file"
          multiple
          accept=".pdf,.jpg,.jpeg,.png,.webp"
          onChange={(e) => handleFiles(Array.from(e.target.files))}
          className="hidden"
          id="file-input"
        />
        <label htmlFor="file-input" className="btn-primary inline-block mt-4">
          Seleccionar Archivos
        </label>
      </div>
      
      {files.length > 0 && (
        <div className="mt-6">
          <h2 className="font-semibold mb-4">Archivos seleccionados ({files.length})</h2>
          <div className="space-y-2">
            {files.map((file, idx) => (
              <div key={idx} className="bg-gray-100 p-3 rounded flex justify-between items-center">
                <span>{file.name}</span>
                <button
                  onClick={() => setFiles(files.filter((_, i) => i !== idx))}
                  className="text-red-600 hover:text-red-800"
                >
                  Eliminar
                </button>
              </div>
            ))}
          </div>
          
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="btn-primary mt-6 disabled:opacity-50"
          >
            {uploading ? 'Subiendo...' : 'Subir Archivos'}
          </button>
        </div>
      )}
      
      {error && (
        <div className="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}
      
      {extracted && (
        <div className="mt-8 card">
          <h2 className="text-xl font-bold mb-4">Datos Extraídos</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-600">Número de Factura</label>
              <input type="text" value={extracted.numero_factura || ''} className="input-field" />
            </div>
            <div>
              <label className="block text-sm text-gray-600">Fecha</label>
              <input type="text" value={extracted.fecha || ''} className="input-field" />
            </div>
            <div>
              <label className="block text-sm text-gray-600">Proveedor</label>
              <input type="text" value={extracted.proveedor || ''} className="input-field" />
            </div>
            <div>
              <label className="block text-sm text-gray-600">Base Imponible</label>
              <input type="number" value={extracted.base_imponible || 0} className="input-field" />
            </div>
            <div>
              <label className="block text-sm text-gray-600">IVA %</label>
              <input type="number" value={extracted.iva_porcentaje || 21} className="input-field" />
            </div>
            <div>
              <label className="block text-sm text-gray-600">Total</label>
              <input type="number" value={extracted.importe_total || 0} className="input-field" />
            </div>
          </div>
          <button className="btn-primary mt-4">Guardar Movimiento</button>
        </div>
      )}
    </div>
  )
}

export default UploadInvoicePage
