import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './hooks/useStore'
import DashboardPage from './pages/DashboardPage'
import UploadInvoicePage from './pages/UploadInvoicePage'
import './styles/globals.css'

export default function App() {
  const loadFromStorage = useAuthStore(state => state.loadFromStorage)
  
  useEffect(() => {
    loadFromStorage()
  }, [loadFromStorage])
  
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/upload" element={<UploadInvoicePage />} />
        <Route path="/" element={<Navigate to="/dashboard" />} />
      </Routes>
    </Router>
  )
}
