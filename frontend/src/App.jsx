import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './hooks/useStore'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import UploadInvoicePage from './pages/UploadInvoicePage'
import MovementsPage from './pages/MovementsPage'
import ObrasPage from './pages/ObrasPage'
import CatalogsPage from './pages/CatalogsPage'
import './styles/globals.css'

const authDisabled = import.meta.env.VITE_AUTH_DISABLED === 'true'

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuthStore()

  if (authDisabled) {
    return children
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}

export default function App() {
  const loadFromStorage = useAuthStore(state => state.loadFromStorage)
  
  useEffect(() => {
    loadFromStorage()
  }, [loadFromStorage])
  
  return (
    <Router>
      <Routes>
        <Route path="/login" element={authDisabled ? <Navigate to="/dashboard" replace /> : <LoginPage />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/upload"
          element={
            <ProtectedRoute>
              <UploadInvoicePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/movements"
          element={
            <ProtectedRoute>
              <MovementsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/obras"
          element={
            <ProtectedRoute>
              <ObrasPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/catalogs"
          element={
            <ProtectedRoute>
              <CatalogsPage />
            </ProtectedRoute>
          }
        />
        <Route path="/" element={<Navigate to="/dashboard" />} />
      </Routes>
    </Router>
  )
}
