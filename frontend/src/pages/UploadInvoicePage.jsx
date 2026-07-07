import React, { useState } from 'react'
import AppLayout from '../layouts/AppLayout'
import { categoriesService, filesService, obrasService, providersService } from '../services/api'

const initialReview = {
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

export const UploadInvoicePage = () => {
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [savingReview, setSavingReview] = useState(false)
  const [uploadedFile, setUploadedFile] = useState(null)
  const [review, setReview] = useState(initialReview)
  const [obras, setObras] = useState([])
  const [categories, setCategories] = useState([])
  const [providers, setProviders] = useState([])
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  React.useEffect(() => {
    const loadCatalogs = async () => {
      try {
        const [obrasResponse, categoriesResponse, providersResponse] = await Promise.all([
          obrasService.list(),
          categoriesService.list(),
          providersService.list(),
        ])
        setObras(obrasResponse.data)
        setCategories(categoriesResponse.data)
        setProviders(providersResponse.data)
      } catch (err) {
        console.error(err)
      }
    }
    loadCatalogs()
  }, [])
  
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
    setMessage('')
    
    try {
      const response = await filesService.upload(files[0])
      setUploadedFile(response.data)
      const extracted = response.data.datos_extraidos || {}
      setReview({
        ...initialReview,
        fecha: extracted.fecha ? `${extracted.fecha.split('/').reverse().join('-')}T09:00` : initialReview.fecha,
        tipo: extracted.tipo_detectado || 'gasto',
        concepto: extracted.concepto || extracted.proveedor || files[0].name,
        numero_factura: extracted.numero_factura || '',
        nif_cif: extracted.nif_cif || '',
        base_imponible: extracted.base_imponible || 0,
        iva_porcentaje: extracted.iva_porcentaje || 21,
        iva_cantidad: extracted.iva_cantidad || 0,
        importe_total: extracted.importe_total || 0,
      })
      setMessage('Factura leída. Revisa los datos antes de guardar.')
    } catch (err) {
      setError('Error al subir el archivo')
      console.error(err)
    } finally {
      setUploading(false)
    }
  }

  const submitReview = async () => {
    if (!uploadedFile?.file_id) return
    setSavingReview(true)
    setError('')
    try {
      await filesService.review(uploadedFile.file_id, {
        ...review,
        fecha: new Date(review.fecha).toISOString(),
        obra_id: review.obra_id ? Number(review.obra_id) : null,
        categoria_id: review.categoria_id ? Number(review.categoria_id) : null,
        proveedor_id: review.proveedor_id ? Number(review.proveedor_id) : null,
        base_imponible: Number(review.base_imponible || 0),
        iva_porcentaje: Number(review.iva_porcentaje || 0),
        iva_cantidad: Number(review.iva_cantidad || 0),
        importe_total: Number(review.importe_total || 0),
      })
      setMessage('Factura revisada y movimiento guardado correctamente.')
      setFiles([])
      setUploadedFile(null)
      setReview(initialReview)
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo guardar la factura revisada')
    } finally {
      setSavingReview(false)
    }
  }
  
  return (
    <AppLayout title="Subir factura" subtitle="Arrastra un PDF o imagen, revisa y guarda el movimiento">
      {error ? <div className="message error">{error}</div> : null}
      {message ? <div className="message success">{message}</div> : null}

      <section className="card">
        <div
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          className="dropzone"
        >
          <div className="stack">
            <div>
              <h2 className="section-title">Carga de factura</h2>
              <p className="helper-text">PDF, JPG, PNG o WEBP. Se guarda el archivo original y se extraen datos básicos.</p>
            </div>
            <input
              type="file"
              multiple
              accept=".pdf,.jpg,.jpeg,.png,.webp"
              onChange={(e) => handleFiles(Array.from(e.target.files))}
              className="hidden"
              id="file-input"
            />
            <label htmlFor="file-input" className="btn-primary">Seleccionar archivo</label>
          </div>
        </div>
        {files.length > 0 ? (
          <div className="stack" style={{ marginTop: '16px' }}>
            {files.map((file, idx) => (
              <div key={idx} className="split card-hover">
                <span>{file.name}</span>
                <button onClick={() => setFiles(files.filter((_, i) => i !== idx))} className="btn-secondary">Quitar</button>
              </div>
            ))}
            <button onClick={handleUpload} disabled={uploading} className="btn-primary">
              {uploading ? 'Leyendo factura...' : 'Leer factura'}
            </button>
          </div>
        ) : null}
      </section>

      {uploadedFile ? (
        <section className="card">
          <div className="split">
            <div>
              <h2 className="section-title">Revisión antes de guardar</h2>
              <p className="helper-text">Corrige cualquier dato antes de crear el movimiento definitivo.</p>
            </div>
            <span className="status-pill">Confianza {uploadedFile.datos_extraidos?.confianza || 0}%</span>
          </div>
          <div className="form-grid">
            <input className="input-field" type="datetime-local" value={review.fecha} onChange={(e) => setReview({ ...review, fecha: e.target.value })} />
            <select className="input-field" value={review.tipo} onChange={(e) => setReview({ ...review, tipo: e.target.value })}>
              <option value="gasto">Gasto</option>
              <option value="ingreso">Ingreso</option>
            </select>
            <input className="input-field" placeholder="Concepto" value={review.concepto} onChange={(e) => setReview({ ...review, concepto: e.target.value })} />
            <input className="input-field" placeholder="Número de factura" value={review.numero_factura} onChange={(e) => setReview({ ...review, numero_factura: e.target.value })} />
            <input className="input-field" placeholder="NIF/CIF" value={review.nif_cif} onChange={(e) => setReview({ ...review, nif_cif: e.target.value })} />
            <select className="input-field" value={review.proveedor_id} onChange={(e) => setReview({ ...review, proveedor_id: e.target.value })}>
              <option value="">Selecciona proveedor o cliente</option>
              {providers.map((provider) => <option key={provider.id} value={provider.id}>{provider.nombre}</option>)}
            </select>
            <select className="input-field" value={review.obra_id} onChange={(e) => setReview({ ...review, obra_id: e.target.value })}>
              <option value="">Selecciona obra</option>
              {obras.map((obra) => <option key={obra.id} value={obra.id}>{obra.nombre}</option>)}
            </select>
            <select className="input-field" value={review.categoria_id} onChange={(e) => setReview({ ...review, categoria_id: e.target.value })}>
              <option value="">Selecciona categoría</option>
              {categories.map((category) => <option key={category.id} value={category.id}>{category.nombre}</option>)}
            </select>
            <input className="input-field" type="number" step="0.01" placeholder="Base imponible" value={review.base_imponible} onChange={(e) => setReview({ ...review, base_imponible: e.target.value })} />
            <input className="input-field" type="number" step="1" placeholder="IVA %" value={review.iva_porcentaje} onChange={(e) => setReview({ ...review, iva_porcentaje: e.target.value })} />
            <input className="input-field" type="number" step="0.01" placeholder="IVA" value={review.iva_cantidad} onChange={(e) => setReview({ ...review, iva_cantidad: e.target.value })} />
            <input className="input-field" type="number" step="0.01" placeholder="Importe total" value={review.importe_total} onChange={(e) => setReview({ ...review, importe_total: e.target.value })} />
          </div>
          <textarea className="input-field" placeholder="Observaciones" value={review.observaciones} onChange={(e) => setReview({ ...review, observaciones: e.target.value })} style={{ marginTop: '16px' }} />
          <div className="card" style={{ marginTop: '16px' }}>
            <h3 className="section-title">Texto extraído</h3>
            <pre style={{ whiteSpace: 'pre-wrap', color: 'var(--muted)', fontSize: '0.85rem' }}>{uploadedFile.texto_extraido || uploadedFile.datos_extraidos?.texto_extraido || 'Sin texto extraído'}</pre>
          </div>
          <div className="topbar-actions" style={{ marginTop: '16px' }}>
            <button className="btn-primary" disabled={savingReview} onClick={submitReview}>{savingReview ? 'Guardando...' : 'Guardar factura y movimiento'}</button>
          </div>
        </section>
      ) : null}
    </AppLayout>
  )
}

export default UploadInvoicePage
