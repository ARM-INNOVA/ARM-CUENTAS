import React from 'react'
import Navbar from './Navbar'

export const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-7xl mx-auto">
        {children}
      </main>
    </div>
  )
}

export default Layout
