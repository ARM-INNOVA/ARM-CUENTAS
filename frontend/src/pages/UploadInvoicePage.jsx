import React, { useMemo, useState } from 'react'
import AppLayout from '../layouts/AppLayout'
import { categoriesService, filesService, obrasService, providersService } from '../services/api'

const initialReview = {
  fecha: new Date().toISOString().slice(0, 16),
  fecha_factura: '',
  fecha_venta: '',
  supplier_name: '',
  supplier_tax_id: '',
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

const fieldMetaLabel = {
  supplier_name: 'Proveedor',
  supplier_tax_id: 'CIF/NIF proveedor',
  numero_factura: 'Nº factura',
  fecha_factura: 'Fecha factura',
  fecha_venta: 'Fecha venta/operación',
  base_imponible: 'Base imponible',
  iva_porcentaje: 'Tipo IVA',
  iva_cantidad: 'Cuota IVA',
  importe_total: 'Total factura',
  forma_pago: 'Forma de pago',
  obra_id: 'Obra',
  categoria_id: 'Categoría',
  tipo: 'Tipo de movimiento',
  estado: 'Estado',
  observaciones: 'Observaciones',
}

const fmtMoney = (v) => Number(v || 0).toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €'

const reviewStateText = (source, touched, hasValue) => {
  if (touched) return 'Introducido manualmente'
  if (!hasValue) return 'Pendiente de revisar'
  if ((source || '').toLowerCase().includes('calcul')) return source
  if (source) return source
  return 'Detectado automáticamente'
}

export const UploadInvoicePage = () => {
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [savingReview, setSavingReview] = useState(false)
  const [uploadedFile, setUploadedFile] = useState(null)
  const [review, setReview] = useState(initialReview)
  const [manualFields, setManualFields] = useState({})
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

  const parserData = uploadedFile?.datos_extraidos || {}
  const fieldSources = parserData.field_sources || {}

  const confidencePct = useMemo(() => {
    const c = uploadedFile?.confidence ?? parserData?.confidence ?? 0
    return Math.round(Number(c) * 100)
  }, [uploadedFile, parserData])

  const markManual = (name, value) => {
    setReview((prev) => ({ ...prev, [name]: value }))
    setManualFields((prev) => ({ ...prev, [name]: true }))
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    handleFiles(Array.from(e.dataTransfer.files))
  }

  const handleFiles = (fileList) => {
    setFiles((prev) => [...prev, ...fileList])
  }

  const normalizeDateToDatetimeLocal = (dateStr) => {
    if (!dateStr) return ''
    return `${dateStr}T09:00`
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

      const accountingDate = extracted.sale_date || extracted.invoice_date || ''
      setReview({
        ...initialReview,
        fecha: normalizeDateToDatetimeLocal(accountingDate) || initialReview.fecha,
        fecha_factura: extracted.invoice_date || '',
        fecha_venta: extracted.sale_date || '',
        supplier_name: extracted.supplier_name || extracted.proveedor || '',
        supplier_tax_id: extracted.supplier_tax_id || extracted.nif_cif || '',
        tipo: extracted.tipo_detectado || 'gasto',
        concepto: extracted.supplier_name || files[0].name,
        numero_factura: extracted.invoice_number || extracted.numero_factura || '',
        nif_cif: extracted.supplier_tax_id || extracted.nif_cif || '',
        base_imponible: extracted.tax_base ?? extracted.base_imponible ?? 0,
        iva_porcentaje: extracted.vat_rate ?? extracted.iva_porcentaje ?? 21,
        iva_cantidad: extracted.vat_amount ?? extracted.iva_cantidad ?? 0,
        importe_total: extracted.total_amount ?? extracted.importe_total ?? 0,
        forma_pago: extracted.payment_method || 'transferencia',
      })
      setManualFields({})
      setMessage('Factura leída. Revisa y confirma antes de guardar.')
    } catch (err) {
      setError('Error al subir el archivo')
      console.error(err)
    } finally {
      setUploading(false)
    }
  }

  const submitReview = async (needsReview = false) => {
    if (!uploadedFile?.file_id) return
    setSavingReview(true)
    setError('')
    try {
      await filesService.review(uploadedFile.file_id, {
        ...review,
        fecha: new Date(review.fecha || new Date().toISOString()).toISOString(),
        obra_id: review.obra_id ? Number(review.obra_id) : null,
        categoria_id: review.categoria_id ? Number(review.categoria_id) : null,
        proveedor_id: review.proveedor_id ? Number(review.proveedor_id) : null,
        base_imponible: Number(review.base_imponible || 0),
        iva_porcentaje: Number(review.iva_porcentaje || 0),
        iva_cantidad: Number(review.iva_cantidad || 0),
        importe_total: Number(review.importe_total || 0),
        needs_review: !!needsReview,
      })
      setMessage(needsReview ? 'Guardado como pendiente de revisión.' : 'Factura revisada y movimiento guardado correctamente.')
      setFiles([])
      setUploadedFile(null)
      setReview(initialReview)
      setManualFields({})
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo guardar la factura revisada')
    } finally {
      setSavingReview(false)
    }
  }

  const cancelReview = () => {
    setUploadedFile(null)
    setReview(initialReview)
    setManualFields({})
    setMessage('Revisión cancelada. Puedes subir otro archivo.')
  }

  const openPdf = async () => {
    if (!uploadedFile?.file_id) return
    try {
      const response = await filesService.download(uploadedFile.file_id)
      const blobUrl = URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
      window.open(blobUrl, '_blank', 'noopener,noreferrer')
      setTimeout(() => URL.revokeObjectURL(blobUrl), 30000)
    } catch (err) {
      setError('No se pudo abrir el PDF')
    }
  }

  const helper = (field) => reviewStateText(fieldSources[field], manualFields[field], !!review[field])

  return (
    <AppLayout title="Subir factura" subtitle="Carga PDF, revisa datos detectados y guarda con control contable">
      {error ? <div className="message error">{error}</div> : null}
      {message ? <div className="message success">{message}</div> : null}

      <section className="card">
        <div onDrop={handleDrop} onDragOver={(e) => e.preventDefault()} className="dropzone">
          <div className="stack">
            <div>
              <h2 className="section-title">Carga de factura</h2>
              <p className="helper-text">PDF, JPG, PNG o WEBP. Se procesa automáticamente y se muestra revisión editable.</p>
            </div>
            <input type="file" multiple accept=".pdf,.jpg,.jpeg,.png,.webp" onChange={(e) => handleFiles(Array.from(e.target.files))} className="hidden" id="file-input" />
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
            <button onClick={handleUpload} disabled={uploading} className="btn-primary">{uploading ? 'Leyendo factura...' : 'Leer factura'}</button>
          </div>
        ) : null}
      </section>

      {uploadedFile ? (
        <section className="card review-card">
          <div className="split">
            <div>
              <h2 className="section-title">Revisión de factura</h2>
              <p className="helper-text">Archivo: <strong>{uploadedFile.nombre_original}</strong></p>
              <p className="helper-text">Proveedor detectado: <strong>{review.supplier_name || 'Pendiente'}</strong></p>
            </div>
            <div className="stack" style={{ gap: '8px' }}>
              <span className="status-pill">Confianza {confidencePct}%</span>
              <button className="btn-secondary btn-sm" onClick={openPdf}>Abrir PDF</button>
            </div>
          </div>

          {(uploadedFile.warnings?.length || parserData.warnings?.length) ? (
            <div className="message warning">
              <strong>Avisos del parser:</strong>
              <ul className="inline-list">
                {(uploadedFile.warnings || parserData.warnings || []).map((warning, idx) => <li key={idx}>{warning}</li>)}
              </ul>
            </div>
          ) : null}

          <div className="review-grid">
            <div className="field-block"><label>Proveedor</label><input className="input-field" value={review.supplier_name} onChange={(e) => markManual('supplier_name', e.target.value)} /><small>{helper('supplier_name')}</small></div>
            <div className="field-block"><label>CIF/NIF proveedor</label><input className="input-field" value={review.supplier_tax_id} onChange={(e) => { markManual('supplier_tax_id', e.target.value); markManual('nif_cif', e.target.value) }} /><small>{helper('supplier_tax_id')}</small></div>
            <div className="field-block"><label>Nº factura</label><input className="input-field" value={review.numero_factura} onChange={(e) => markManual('numero_factura', e.target.value)} /><small>{helper('numero_factura')}</small></div>
            <div className="field-block"><label>Fecha factura</label><input className="input-field" type="date" value={review.fecha_factura} onChange={(e) => markManual('fecha_factura', e.target.value)} /><small>{helper('fecha_factura')}</small></div>
            <div className="field-block"><label>Fecha venta/operación</label><input className="input-field" type="date" value={review.fecha_venta} onChange={(e) => { const value = e.target.value; markManual('fecha_venta', value); markManual('fecha', value ? `${value}T09:00` : review.fecha) }} /><small>{helper('fecha_venta')}</small></div>
            <div className="field-block"><label>Fecha movimiento contable</label><input className="input-field" type="datetime-local" value={review.fecha} onChange={(e) => markManual('fecha', e.target.value)} /><small>{helper('fecha')}</small></div>
            <div className="field-block"><label>Base imponible</label><input className="input-field" type="number" step="0.01" value={review.base_imponible} onChange={(e) => markManual('base_imponible', e.target.value)} /><small>{helper('base_imponible')}</small></div>
            <div className="field-block"><label>Tipo IVA</label><input className="input-field" type="number" step="1" value={review.iva_porcentaje} onChange={(e) => markManual('iva_porcentaje', e.target.value)} /><small>{helper('iva_porcentaje')}</small></div>
            <div className="field-block"><label>Cuota IVA</label><input className="input-field" type="number" step="0.01" value={review.iva_cantidad} onChange={(e) => markManual('iva_cantidad', e.target.value)} /><small>{helper('iva_cantidad')}</small></div>
            <div className="field-block"><label>Total factura</label><input className="input-field" type="number" step="0.01" value={review.importe_total} onChange={(e) => markManual('importe_total', e.target.value)} /><small>{helper('importe_total')} · {fmtMoney(review.importe_total)}</small></div>
            <div className="field-block"><label>Forma de pago</label><select className="input-field" value={review.forma_pago} onChange={(e) => markManual('forma_pago', e.target.value)}><option value="transferencia">Transferencia</option><option value="banco">Banco</option><option value="tarjeta">Tarjeta</option><option value="bizum">Bizum</option><option value="efectivo">Efectivo</option><option value="otro">Otro</option></select><small>{helper('forma_pago')}</small></div>
            <div className="field-block"><label>Obra</label><select className="input-field" value={review.obra_id} onChange={(e) => markManual('obra_id', e.target.value)}><option value="">Sin asignar</option>{obras.map((obra) => <option key={obra.id} value={obra.id}>{obra.nombre}</option>)}</select><small>{helper('obra_id')}</small></div>
            <div className="field-block"><label>Categoría</label><select className="input-field" value={review.categoria_id} onChange={(e) => markManual('categoria_id', e.target.value)}><option value="">Sin asignar</option>{categories.map((category) => <option key={category.id} value={category.id}>{category.nombre}</option>)}</select><small>{helper('categoria_id')}</small></div>
            <div className="field-block"><label>Proveedor/cliente (catálogo)</label><select className="input-field" value={review.proveedor_id} onChange={(e) => markManual('proveedor_id', e.target.value)}><option value="">Sin asignar</option>{providers.map((provider) => <option key={provider.id} value={provider.id}>{provider.nombre}</option>)}</select><small>{helper('proveedor_id')}</small></div>
            <div className="field-block"><label>Tipo de movimiento</label><select className="input-field" value={review.tipo} onChange={(e) => markManual('tipo', e.target.value)}><option value="gasto">Gasto</option><option value="ingreso">Ingreso</option></select><small>{helper('tipo')}</small></div>
            <div className="field-block"><label>Estado</label><select className="input-field" value={review.estado} onChange={(e) => markManual('estado', e.target.value)}><option value="pendiente">Pendiente</option><option value="pagado">Pagado</option><option value="cobrado">Cobrado</option></select><small>{helper('estado')}</small></div>
          </div>

          <div className="field-block" style={{ marginTop: '12px' }}>
            <label>Observaciones</label>
            <textarea className="input-field" value={review.observaciones} onChange={(e) => markManual('observaciones', e.target.value)} />
            <small>{helper('observaciones')}</small>
          </div>

          <details className="extracted-text" style={{ marginTop: '16px' }}>
            <summary>Texto extraído (plegable)</summary>
            <pre>{uploadedFile.texto_extraido || parserData.extracted_text || parserData.texto_extraido || 'Sin texto extraído'}</pre>
          </details>

          <div className="topbar-actions" style={{ marginTop: '16px' }}>
            <button className="btn-primary" disabled={savingReview} onClick={() => submitReview(false)}>{savingReview ? 'Guardando...' : 'Confirmar y guardar'}</button>
            <button className="btn-secondary" disabled={savingReview} onClick={() => submitReview(true)}>Guardar como pendiente</button>
            <button className="btn-secondary" disabled={savingReview} onClick={cancelReview}>Cancelar</button>
          </div>
        </section>
      ) : null}
    </AppLayout>
  )
}

export default UploadInvoicePage
