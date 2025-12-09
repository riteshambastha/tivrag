import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { googleAPI } from '../api'
import './Configuration.css'

function Configuration({ onLogout }) {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    loadStatus()
  }, [])

  const loadStatus = async () => {
    try {
      const response = await googleAPI.getStatus()
      setStatus(response.data)
    } catch (err) {
      console.error('Failed to load status', err)
    } finally {
      setLoading(false)
    }
  }

  const handleConnect = async () => {
    try {
      const response = await googleAPI.getAuthUrl()
      window.location.href = response.data.auth_url
    } catch (err) {
      console.error('Failed to get auth URL', err)
      alert('Failed to connect. Please try again.')
    }
  }

  const handleDisconnect = async () => {
    if (!confirm('Are you sure you want to disconnect Google services?')) {
      return
    }

    try {
      await googleAPI.disconnect()
      setStatus({ connected: false })
      alert('Google services disconnected successfully!')
    } catch (err) {
      console.error('Failed to disconnect', err)
      alert('Failed to disconnect. Please try again.')
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
          <button className="nav-link" onClick={() => navigate('/dashboard')}>
            Dashboard
          </button>
          <button className="nav-link active" onClick={() => navigate('/configuration')}>
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
        <div className="config-card">
          <h1>Configuration</h1>
          <p className="config-subtitle">Connect your Google services to search emails and documents</p>

          {loading ? (
            <div className="loading">Loading...</div>
          ) : (
            <div className="service-section">
              <div className="service-card">
                <div className="service-header">
                  <div className="service-icon">🔗</div>
                  <div>
                    <h3>Google Services</h3>
                    <p>Gmail & Google Drive</p>
                  </div>
                </div>

                {status?.connected ? (
                  <div className="connected-info">
                    <div className="status-badge connected">
                      <span className="status-dot"></span>
                      Connected
                    </div>
                    <p className="connected-date">
                      Connected on {new Date(status.connected_at).toLocaleDateString()}
                    </p>
                    
                    <div className="scopes-section">
                      <h4>Permissions:</h4>
                      <ul className="scopes-list">
                        <li>✓ Read Gmail messages</li>
                        <li>✓ Read Google Drive files</li>
                      </ul>
                    </div>

                    <button className="disconnect-button" onClick={handleDisconnect}>
                      Disconnect
                    </button>
                  </div>
                ) : (
                  <div className="disconnected-info">
                    <div className="status-badge disconnected">
                      <span className="status-dot"></span>
                      Not Connected
                    </div>
                    <p className="info-text">
                      Connect your Google account to enable searching through your emails and documents.
                    </p>
                    <button className="connect-button" onClick={handleConnect}>
                      Connect Google Services
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="info-box">
            <h4>ℹ️ How it works</h4>
            <ul>
              <li>Click "Connect Google Services" to authorize Tivrag</li>
              <li>You'll be redirected to Google to grant permissions</li>
              <li>Once connected, go to Workplace to search your data</li>
              <li>Your credentials are stored securely and never shared</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Configuration

