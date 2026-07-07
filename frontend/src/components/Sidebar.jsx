import React from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

const authDisabled = import.meta.env.VITE_AUTH_DISABLED === 'true'

const navItems = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/movements', label: 'Movimientos' },
  { to: '/upload', label: 'Facturas' },
  { to: '/obras', label: 'Obras' },
  { to: '/catalogs', label: 'Categorías y proveedores' },
]

export const Sidebar = () => {
  const { user, logout } = useAuth()

  return (
    <aside className="sidebar">
      <div className="brand-block">
        <div className="brand-mark">ARM</div>
        <div>
          <strong>ARM CUENTAS</strong>
          <p>Ingresos, gastos y facturas</p>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="user-card">
          <span className="user-pill">{user?.role || 'user'}</span>
          <strong>{user?.full_name || user?.username}</strong>
          <p>{authDisabled ? 'Acceso temporal' : 'Sesión iniciada'}</p>
        </div>
        {!authDisabled ? (
          <button className="btn-secondary w-full" onClick={logout}>
            Cerrar sesión
          </button>
        ) : null}
      </div>
    </aside>
  )
}

export default Sidebar