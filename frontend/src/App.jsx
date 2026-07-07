import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './hooks/useStore'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import UploadInvoicePage from './pages/UploadInvoicePage'
import './styles/globals.css'

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuthStore()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />
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
        <Route path="/login" element={<LoginPage />} />
        
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
        
        <Route path="/" element={<Navigate to="/dashboard" />} />
      </Routes>
    </Router>
  )
}
