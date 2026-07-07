import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

const authDisabled = import.meta.env.VITE_AUTH_DISABLED === 'true'

export const Navbar = () => {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  
  return (
    <nav className="bg-red-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center cursor-pointer" onClick={() => navigate('/dashboard')}>
            <h1 className="text-2xl font-bold">ARM CUENTAS</h1>
          </div>
          
          <div className="flex items-center space-x-4">
            <span className="text-sm">{user?.full_name || user?.username}</span>
            {authDisabled ? (
              <span className="px-4 py-2 bg-red-700 rounded text-sm">Acceso temporal</span>
            ) : (
              <button
                onClick={logout}
                className="px-4 py-2 bg-red-700 hover:bg-red-800 rounded text-sm transition"
              >
                Logout
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
