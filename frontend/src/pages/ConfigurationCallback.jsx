import React, { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { googleAPI } from '../api'
import './ConfigurationCallback.css'

function ConfigurationCallback({ onLogout }) {
  const [searchParams] = useSearchParams()
  const [status, setStatus] = useState('processing')
  const navigate = useNavigate()

  useEffect(() => {
    handleCallback()
  }, [])

  const handleCallback = async () => {
    const code = searchParams.get('code')
    const error = searchParams.get('error')

    if (error) {
      setStatus('error')
      setTimeout(() => navigate('/configuration'), 3000)
      return
    }

    if (!code) {
      setStatus('error')
      setTimeout(() => navigate('/configuration'), 3000)
      return
    }

    try {
      await googleAPI.handleCallback(code)
      setStatus('success')
      setTimeout(() => navigate('/configuration'), 2000)
    } catch (err) {
      console.error('Failed to complete authorization', err)
      setStatus('error')
      setTimeout(() => navigate('/configuration'), 3000)
    }
  }

  return (
    <div className="callback-container">
      <div className="callback-card">
        {status === 'processing' && (
          <>
            <div className="spinner"></div>
            <h2>Connecting to Google...</h2>
            <p>Please wait while we complete the authorization.</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="success-icon">✓</div>
            <h2>Successfully Connected!</h2>
            <p>Redirecting you back to Configuration...</p>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="error-icon">✗</div>
            <h2>Connection Failed</h2>
            <p>Something went wrong. Redirecting you back...</p>
          </>
        )}
      </div>
    </div>
  )
}

export default ConfigurationCallback

