import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Signup from './pages/Signup'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Configuration from './pages/Configuration'
import Workplace from './pages/Workplace'
import ConfigurationCallback from './pages/ConfigurationCallback'
import CRM from './pages/CRM'

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'))

  const handleLogin = (newToken) => {
    localStorage.setItem('token', newToken)
    setToken(newToken)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setToken(null)
  }

  return (
    <Router>
      <Routes>
        <Route path="/signup" element={!token ? <Signup onLogin={handleLogin} /> : <Navigate to="/dashboard" />} />
        <Route path="/login" element={!token ? <Login onLogin={handleLogin} /> : <Navigate to="/dashboard" />} />
        <Route path="/dashboard" element={token ? <Dashboard onLogout={handleLogout} /> : <Navigate to="/login" />} />
        <Route path="/configuration" element={token ? <Configuration onLogout={handleLogout} /> : <Navigate to="/login" />} />
        <Route path="/configuration/callback" element={token ? <ConfigurationCallback onLogout={handleLogout} /> : <Navigate to="/login" />} />
        <Route path="/workplace" element={token ? <Workplace onLogout={handleLogout} /> : <Navigate to="/login" />} />
        <Route path="/crm" element={token ? <CRM onLogout={handleLogout} /> : <Navigate to="/login" />} />
        <Route path="/" element={<Navigate to={token ? "/dashboard" : "/login"} />} />
      </Routes>
    </Router>
  )
}

export default App

