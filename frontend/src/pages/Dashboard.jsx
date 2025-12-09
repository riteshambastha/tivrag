import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { authAPI } from '../api'
import './Dashboard.css'

function Dashboard({ onLogout }) {
  const [user, setUser] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    loadUser()
  }, [])

  const loadUser = async () => {
    try {
      const response = await authAPI.getMe()
      setUser(response.data)
    } catch (err) {
      console.error('Failed to load user', err)
      onLogout()
    }
  }

  const handleLogout = () => {
    onLogout()
    navigate('/login')
  }

  return (
    <div className="dashboard-container">
      <nav className="navbar">
        <div className="navbar-brand">Tivrag</div>
        <div className="navbar-menu">
          <button className="nav-link active" onClick={() => navigate('/dashboard')}>
            Dashboard
          </button>
          <button className="nav-link" onClick={() => navigate('/configuration')}>
            Configuration
          </button>
          <button className="nav-link" onClick={() => navigate('/workplace')}>
            Workplace
          </button>
          <button className="nav-link" onClick={() => navigate('/crm')}>
            CRM
          </button>
          <button className="logout-button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </nav>

      <div className="dashboard-content">
        <div className="welcome-card">
          <h1>Welcome{user ? `, ${user.username}` : ''}! 👋</h1>
          <p className="welcome-text">
            Get started by connecting your Google services in the Configuration page, 
            then head to Workplace to search through your emails and documents.
          </p>
          
          <div className="action-cards">
            <div className="action-card" onClick={() => navigate('/configuration')}>
              <div className="action-icon">🔧</div>
              <h3>Configuration</h3>
              <p>Connect your Gmail and Google Drive accounts</p>
            </div>
            
            <div className="action-card" onClick={() => navigate('/workplace')}>
              <div className="action-icon">🔍</div>
              <h3>Workplace</h3>
              <p>Search emails and documents from specific people</p>
            </div>

            <div className="action-card" onClick={() => navigate('/crm')}>
              <div className="action-icon">📊</div>
              <h3>CRM</h3>
              <p>Manage contacts, deals, tasks, and customer relationships</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

