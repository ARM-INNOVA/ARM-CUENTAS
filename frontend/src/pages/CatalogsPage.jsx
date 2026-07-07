import React, { useEffect, useState } from 'react'
import AppLayout from '../layouts/AppLayout'
import { categoriesService, providersService } from '../services/api'

const emptyCategory = { nombre: '', descripcion: '', color: '#dc2626' }
const emptyProvider = { nombre: '', nif_cif: '', email: '', telefono: '', direccion: '', tipo: 'proveedor' }

export const CatalogsPage = () => {
  const [categories, setCategories] = useState([])
  const [providers, setProviders] = useState([])
  const [categoryForm, setCategoryForm] = useState(emptyCategory)
  const [providerForm, setProviderForm] = useState(emptyProvider)
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const loadData = async () => {
    setLoading(true)
    try {
      const [categoriesResponse, providersResponse] = await Promise.all([
        categoriesService.list(),
        providersService.list(),
      ])
      setCategories(categoriesResponse.data)
      setProviders(providersResponse.data)
    } catch (err) {
      setError('No se pudieron cargar categorías y proveedores')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const createCategory = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    try {
      await categoriesService.create(categoryForm)
      setCategoryForm(emptyCategory)
      setMessage('Categoría creada correctamente')
      await loadData()
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo crear la categoría')
    }
  }

  const createProvider = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    try {
      await providersService.create(providerForm)
      setProviderForm(emptyProvider)
      setMessage('Proveedor o cliente creado correctamente')
      await loadData()
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo crear el proveedor')
    }
  }

  return (
    <AppLayout
      title="Catálogos"
      subtitle="Gestiona categorías y proveedores desde una sola pantalla"
    >
      {error ? <div className="message error">{error}</div> : null}
      {message ? <div className="message success">{message}</div> : null}
      <div className="catalog-grid">
        <section className="card">
          <div className="split">
            <div>
              <h2 className="section-title">Categorías</h2>
              <p className="helper-text">Materiales, subcontratas, herramientas y más.</p>
            </div>
            <span className="status-pill">{categories.length} activas</span>
          </div>
          <form className="stack" onSubmit={createCategory}>
            <input className="input-field" placeholder="Nombre" value={categoryForm.nombre} onChange={(e) => setCategoryForm({ ...categoryForm, nombre: e.target.value })} required />
            <input className="input-field" placeholder="Descripción" value={categoryForm.descripcion} onChange={(e) => setCategoryForm({ ...categoryForm, descripcion: e.target.value })} />
            <input className="input-field" type="color" value={categoryForm.color} onChange={(e) => setCategoryForm({ ...categoryForm, color: e.target.value })} />
            <button className="btn-primary" type="submit">Guardar categoría</button>
          </form>
          <div className="stack">
            {loading ? <p className="helper-text">Cargando categorías...</p> : categories.map((category) => (
              <div className="card-hover" key={category.id}>
                <div className="split">
                  <strong>{category.nombre}</strong>
                  <span className="status-pill" style={{ background: `${category.color}33` }}>{category.color}</span>
                </div>
                <p className="helper-text">{category.descripcion || 'Sin descripción'}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="card">
          <div className="split">
            <div>
              <h2 className="section-title">Proveedores y clientes</h2>
              <p className="helper-text">Normaliza nombres y deja listos los autocompletados.</p>
            </div>
            <span className="status-pill">{providers.length} registros</span>
          </div>
          <form className="stack" onSubmit={createProvider}>
            <input className="input-field" placeholder="Nombre" value={providerForm.nombre} onChange={(e) => setProviderForm({ ...providerForm, nombre: e.target.value })} required />
            <div className="form-grid">
              <input className="input-field" placeholder="NIF/CIF" value={providerForm.nif_cif} onChange={(e) => setProviderForm({ ...providerForm, nif_cif: e.target.value })} />
              <select className="input-field" value={providerForm.tipo} onChange={(e) => setProviderForm({ ...providerForm, tipo: e.target.value })}>
                <option value="proveedor">Proveedor</option>
                <option value="cliente">Cliente</option>
              </select>
            </div>
            <input className="input-field" placeholder="Email" value={providerForm.email} onChange={(e) => setProviderForm({ ...providerForm, email: e.target.value })} />
            <input className="input-field" placeholder="Teléfono" value={providerForm.telefono} onChange={(e) => setProviderForm({ ...providerForm, telefono: e.target.value })} />
            <input className="input-field" placeholder="Dirección" value={providerForm.direccion} onChange={(e) => setProviderForm({ ...providerForm, direccion: e.target.value })} />
            <button className="btn-primary" type="submit">Guardar proveedor</button>
          </form>
          <div className="stack">
            {loading ? <p className="helper-text">Cargando proveedores...</p> : providers.map((provider) => (
              <div className="card-hover" key={provider.id}>
                <div className="split">
                  <strong>{provider.nombre}</strong>
                  <span className="status-pill">{provider.tipo}</span>
                </div>
                <p className="helper-text">{provider.nif_cif || 'Sin NIF/CIF'} · {provider.email || 'Sin email'}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </AppLayout>
  )
}

export default CatalogsPage