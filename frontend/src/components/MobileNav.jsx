import React from 'react'
import { NavLink } from 'react-router-dom'

const items = [
  { to: '/dashboard', label: 'Inicio' },
  { to: '/movements', label: 'Movs' },
  { to: '/upload', label: 'Factura' },
  { to: '/obras', label: 'Obras' },
  { to: '/catalogs', label: 'Más' },
]

export const MobileNav = () => {
  return (
    <nav className="mobile-nav">
      {items.map((item) => (
        <NavLink key={item.to} to={item.to} className={({ isActive }) => `mobile-link ${isActive ? 'active' : ''}`}>
          {item.label}
        </NavLink>
      ))}
    </nav>
  )
}

export default MobileNav