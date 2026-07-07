import React from 'react'
import Sidebar from '../components/Sidebar'
import MobileNav from '../components/MobileNav'

export const AppLayout = ({ title, subtitle, actions, children }) => {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <header className="topbar">
          <div>
            <p className="eyebrow">ARM CUENTAS</p>
            <h1>{title}</h1>
            {subtitle ? <p className="topbar-subtitle">{subtitle}</p> : null}
          </div>
          {actions ? <div className="topbar-actions">{actions}</div> : null}
        </header>
        <main className="page-content">{children}</main>
      </div>
      <MobileNav />
    </div>
  )
}

export default AppLayout