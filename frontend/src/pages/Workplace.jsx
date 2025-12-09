import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import './Workplace.css'

const API_BASE_URL = 'http://localhost:8002'

function Workplace({ onLogout }) {
  const [step, setStep] = useState(1) // 1: Create Project, 2: Search, 3: Results & Analysis
  const [projects, setProjects] = useState([])
  const [selectedProject, setSelectedProject] = useState(null)
  
  // Step 1: Project creation
  const [projectName, setProjectName] = useState('')
  const [searchEmail, setSearchEmail] = useState('')
  const [emailTags, setEmailTags] = useState([])
  const [includeGmail, setIncludeGmail] = useState(true)
  const [includeDrive, setIncludeDrive] = useState(true)
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  
  // Step 2 & 3: Results and Analysis
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  // AI Analysis
  const [promptText, setPromptText] = useState('')
  const [threads, setThreads] = useState([])
  const [currentThread, setCurrentThread] = useState(null)
  const [chatHistory, setChatHistory] = useState([])
  const [analyzing, setAnalyzing] = useState(false)
  const [parseDocuments, setParseDocuments] = useState(false)
  const [parseEmails, setParseEmails] = useState(false)
  const [showNewThreadModal, setShowNewThreadModal] = useState(false)
  const [newThreadTitle, setNewThreadTitle] = useState('')
  
  // Delete modal
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [projectToDelete, setProjectToDelete] = useState(null)
  const [deleting, setDeleting] = useState(false)
  
  const navigate = useNavigate()

  useEffect(() => {
    loadProjects()
    // Set default date range to last 1 month
    const today = new Date()
    const oneMonthAgo = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate())
    setDateFrom(oneMonthAgo.toISOString().split('T')[0])
    setDateTo(today.toISOString().split('T')[0])
  }, [])

  useEffect(() => {
    // Load threads when project is selected
    if (selectedProject && step === 3) {
      loadThreads(selectedProject.id)
    }
  }, [selectedProject, step])

  const loadThreads = async (projectId) => {
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get(`${API_BASE_URL}/api/projects/${projectId}/threads`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setThreads(response.data)
      
      // Auto-select first thread if available
      if (response.data.length > 0 && !currentThread) {
        selectThread(response.data[0])
      }
    } catch (err) {
      console.error('Failed to load threads', err)
    }
  }

  const selectThread = async (thread) => {
    setCurrentThread(thread)
    await loadThreadMessages(thread.id)
  }

  const loadThreadMessages = async (threadId) => {
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get(`${API_BASE_URL}/api/threads/${threadId}/messages`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setChatHistory(response.data)
    } catch (err) {
      console.error('Failed to load thread messages', err)
    }
  }

  const createThread = async () => {
    if (!newThreadTitle.trim()) {
      setError('Please enter a thread title')
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await axios.post(
        `${API_BASE_URL}/api/threads`,
        {
          project_id: selectedProject.id,
          title: newThreadTitle
        },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      
      setShowNewThreadModal(false)
      setNewThreadTitle('')
      await loadThreads(selectedProject.id)
      selectThread(response.data)
    } catch (err) {
      console.error('Failed to create thread', err)
      setError('Failed to create thread')
    }
  }

  const deleteThread = async (threadId) => {
    if (!confirm('Are you sure you want to delete this thread and all its messages?')) return
    
    try {
      const token = localStorage.getItem('token')
      await axios.delete(`${API_BASE_URL}/api/threads/${threadId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      await loadThreads(selectedProject.id)
      if (currentThread && currentThread.id === threadId) {
        setCurrentThread(null)
        setChatHistory([])
      }
    } catch (err) {
      console.error('Failed to delete thread', err)
      setError('Failed to delete thread')
    }
  }

  const loadProjects = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get(`${API_BASE_URL}/api/projects`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setProjects(response.data)
    } catch (err) {
      console.error('Failed to load projects', err)
    }
  }

  const addEmailTag = (e) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      const email = searchEmail.trim()
      if (email && !emailTags.includes(email)) {
        setEmailTags([...emailTags, email])
        setSearchEmail('')
      }
    }
  }

  const removeEmailTag = (emailToRemove) => {
    setEmailTags(emailTags.filter(email => email !== emailToRemove))
  }

  const handleCreateProject = async (e) => {
    e.preventDefault()
    setError('')
    
    // Add current input to tags if not empty
    if (searchEmail.trim() && !emailTags.includes(searchEmail.trim())) {
      setEmailTags([...emailTags, searchEmail.trim()])
      setSearchEmail('')
    }

    // Validate we have at least one email
    const finalEmails = searchEmail.trim() ? [...emailTags, searchEmail.trim()] : emailTags
    if (finalEmails.length === 0) {
      setError('Please enter at least one email address')
      return
    }

    setLoading(true)

    try {
      const token = localStorage.getItem('token')
      // Join multiple emails with comma
      const response = await axios.post(`${API_BASE_URL}/api/projects`, {
        name: projectName,
        search_email: finalEmails.join(', '),
        include_gmail: includeGmail,
        include_drive: includeDrive,
        date_from: dateFrom ? `${dateFrom}T00:00:00` : null,
        date_to: dateTo ? `${dateTo}T23:59:59` : null
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      setSelectedProject(response.data)
      await loadProjects()
      setStep(2)
      // Automatically run search
      await runSearch(response.data.id)
    } catch (err) {
      console.error('Failed to create project', err)
      setError(err.response?.data?.detail || 'Failed to create project')
    } finally {
      setLoading(false)
    }
  }

  const runSearch = async (projectId) => {
    setLoading(true)
    setError('')
    
    try {
      const token = localStorage.getItem('token')
      const response = await axios.post(
        `${API_BASE_URL}/api/projects/${projectId}/search`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      )
      
      console.log('Search response:', response.data)
      setResults(response.data)
      
      // Display any search errors/warnings
      if (response.data.errors && response.data.errors.length > 0) {
        setError(`Search completed with warnings: ${response.data.errors.join(', ')}`)
      }
      
      setStep(3)
    } catch (err) {
      console.error('Search failed', err)
      console.error('Error details:', err.response?.data)
      setError(err.response?.data?.detail || 'Search failed. Please make sure you have connected Google services.')
    } finally {
      setLoading(false)
    }
  }

  const handleSelectProject = async (project) => {
    setSelectedProject(project)
    setStep(2)
    
    // Load cached results if available
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get(`${API_BASE_URL}/api/projects/${project.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      if (response.data.search_results) {
        setResults(response.data.search_results)
        setStep(3)
      }
    } catch (err) {
      console.error('Failed to load project', err)
    }
  }

  const loadChatHistory = async (projectId) => {
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get(`${API_BASE_URL}/api/projects/${projectId}/chat`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setChatHistory(response.data)
    } catch (err) {
      console.error('Failed to load chat history', err)
    }
  }

  const clearChatHistory = async () => {
    if (!confirm('Are you sure you want to clear the chat history?')) return
    
    try {
      const token = localStorage.getItem('token')
      await axios.delete(`${API_BASE_URL}/api/projects/${selectedProject.id}/chat`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setChatHistory([])
    } catch (err) {
      console.error('Failed to clear chat history', err)
      setError('Failed to clear chat history')
    }
  }

  const handleAnalyze = async (e) => {
    e.preventDefault()
    if (!promptText.trim()) return
    
    //If no thread selected, prompt to create one
    if (!currentThread) {
      setError('Please create or select a thread first')
      setShowNewThreadModal(true)
      return
    }
    
    setAnalyzing(true)
    setError('')
    
    // Add user message to UI immediately
    const userMessage = {
      role: 'user',
      content: promptText,
      created_at: new Date().toISOString()
    }
    setChatHistory([...chatHistory, userMessage])
    const currentPrompt = promptText
    setPromptText('')
    
    try {
      const token = localStorage.getItem('token')
      const response = await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/analyze`,
        {
          prompt: currentPrompt,
          project_id: selectedProject.id,
          thread_id: currentThread.id,
          parse_documents: parseDocuments,
          parse_emails: parseEmails
        },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      
      // Add assistant response to chat
      const assistantMessage = {
        role: 'assistant',
        content: response.data.analysis,
        parsed_count: response.data.parsed_count,
        created_at: new Date().toISOString()
      }
      setChatHistory(prev => [...prev, assistantMessage])
      
      // Reload threads to update message count
      await loadThreads(selectedProject.id)
    } catch (err) {
      console.error('Analysis failed', err)
      setError(err.response?.data?.detail || 'Analysis failed')
      // Remove user message on error
      setChatHistory(chatHistory)
    } finally {
      setAnalyzing(false)
    }
  }

  const handleLogout = () => {
    onLogout()
    navigate('/login')
  }

  const handleNewProject = () => {
    setStep(1)
    setSelectedProject(null)
    setResults(null)
    setThreads([])
    setCurrentThread(null)
    setChatHistory([])
    setProjectName('')
    setSearchEmail('')
    setEmailTags([])
    setPromptText('')
  }

  const handleDeleteProject = async () => {
    if (!projectToDelete) return
    
    setDeleting(true)
    setError('')
    
    try {
      const token = localStorage.getItem('token')
      await axios.delete(`${API_BASE_URL}/api/projects/${projectToDelete.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      // Close modal
      setShowDeleteModal(false)
      setProjectToDelete(null)
      
      // Refresh project list
      await loadProjects()
      
      // If we deleted the selected project, go back to step 1
      if (selectedProject && selectedProject.id === projectToDelete.id) {
        handleNewProject()
      }
    } catch (err) {
      console.error('Failed to delete project', err)
      setError(err.response?.data?.detail || 'Failed to delete project')
    } finally {
      setDeleting(false)
    }
  }

  const openDeleteModal = (project, e) => {
    e.stopPropagation() // Prevent project selection
    setProjectToDelete(project)
    setShowDeleteModal(true)
  }

  return (
    <div className="dashboard-container">
      <nav className="navbar">
        <div className="navbar-brand">Tivrag</div>
        <div className="navbar-menu">
          <button className="nav-link" onClick={() => navigate('/dashboard')}>
            Dashboard
          </button>
          <button className="nav-link" onClick={() => navigate('/configuration')}>
            Configuration
          </button>
          <button className="nav-link active" onClick={() => navigate('/workplace')}>
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
        <div className="workplace-card">
          <div className="workplace-header">
            <h1>Workplace</h1>
            {selectedProject && (
              <button className="new-project-button" onClick={handleNewProject}>
                + New Project
              </button>
            )}
          </div>

          {/* Step Indicator */}
          <div className="step-indicator">
            <div className={`step ${step >= 1 ? 'active' : ''}`}>
              <span className="step-number">1</span>
              <span className="step-label">Create Project</span>
            </div>
            <div className={`step ${step >= 2 ? 'active' : ''}`}>
              <span className="step-number">2</span>
              <span className="step-label">Search</span>
            </div>
            <div className={`step ${step >= 3 ? 'active' : ''}`}>
              <span className="step-number">3</span>
              <span className="step-label">Analyze</span>
            </div>
          </div>

          {error && (
            <div className="error-box">
              <strong>Error:</strong> {error}
            </div>
          )}

          {/* Step 1: Create Project */}
          {step === 1 && (
            <div className="step-content">
              <h2>Step 1: Create a New Project</h2>
              <p className="step-description">Name your project and configure search parameters</p>

              {projects.length > 0 && (
                <div className="existing-projects">
                  <h3>Or select an existing project:</h3>
                  <div className="projects-grid">
                    {projects.map((project) => (
                      <div
                        key={project.id}
                        className="project-card"
                        onClick={() => handleSelectProject(project)}
                      >
                        <button 
                          className="delete-project-button"
                          onClick={(e) => openDeleteModal(project, e)}
                          title="Delete project"
                        >
                          🗑️
                        </button>
                        <h4>{project.name}</h4>
                        <p className="project-email">{project.search_email}</p>
                        <p className="project-meta">
                          {project.include_gmail && '📧 Gmail'} {project.include_drive && '📄 Drive'}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <form onSubmit={handleCreateProject} className="project-form">
                <div className="form-group">
                  <label htmlFor="project-name">Project Name</label>
                  <input
                    type="text"
                    id="project-name"
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    placeholder="e.g., John's Q4 Communications"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="search-email">
                    Email Addresses to Search
                    <span className="label-hint">Press Enter or comma to add multiple</span>
                  </label>
                  <div className="email-tags-container">
                    {emailTags.map((email, index) => (
                      <div key={index} className="email-tag">
                        <span>{email}</span>
                        <button
                          type="button"
                          className="remove-tag"
                          onClick={() => removeEmailTag(email)}
                        >
                          ×
                        </button>
                      </div>
                    ))}
                    <input
                      type="text"
                      id="search-email"
                      value={searchEmail}
                      onChange={(e) => setSearchEmail(e.target.value)}
                      onKeyDown={addEmailTag}
                      placeholder={emailTags.length === 0 ? "john@example.com" : "Add another..."}
                      className="email-input"
                    />
                  </div>
                  <p className="input-hint">
                    💡 You can search multiple people at once. Type an email and press Enter or comma.
                  </p>
                </div>

                <div className="form-group">
                  <label>Search In</label>
                  <div className="checkbox-group">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={includeGmail}
                        onChange={(e) => setIncludeGmail(e.target.checked)}
                      />
                      📧 Gmail
                    </label>
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={includeDrive}
                        onChange={(e) => setIncludeDrive(e.target.checked)}
                      />
                      📄 Google Drive
                    </label>
                  </div>
                </div>

                <div className="form-group">
                  <label>Date Range</label>
                  <div className="date-range">
                    <div className="date-input">
                      <label htmlFor="date-from">From</label>
                      <input
                        type="date"
                        id="date-from"
                        value={dateFrom}
                        onChange={(e) => setDateFrom(e.target.value)}
                      />
                    </div>
                    <div className="date-input">
                      <label htmlFor="date-to">To</label>
                      <input
                        type="date"
                        id="date-to"
                        value={dateTo}
                        onChange={(e) => setDateTo(e.target.value)}
                      />
                    </div>
                  </div>
                  <p className="date-hint">Default: Last 1 month</p>
                </div>

                <button type="submit" className="create-project-button" disabled={loading}>
                  {loading ? 'Creating & Searching...' : 'Create Project & Search'}
                </button>
              </form>
            </div>
          )}

          {/* Step 2: Searching */}
          {step === 2 && loading && (
            <div className="step-content">
              <div className="loading-state">
                <div className="spinner"></div>
                <h2>Searching...</h2>
                <p>Finding emails and documents from {selectedProject?.search_email}</p>
              </div>
            </div>
          )}

          {/* Step 3: Results & Analysis */}
          {step === 3 && results && (
            <div className="step-content">
              <div className="results-header">
                <h2>Results for: {selectedProject?.name}</h2>
                <div className="results-actions">
                  <button className="refresh-button" onClick={() => runSearch(selectedProject.id)}>
                    🔄 Refresh
                  </button>
                  <button 
                    className="delete-button-header" 
                    onClick={(e) => openDeleteModal(selectedProject, e)}
                    title="Delete project"
                  >
                    🗑️ Delete Project
                  </button>
                </div>
              </div>

              <div className="results-summary">
                <div className="summary-card">
                  <span className="summary-number">{results.emails?.length || 0}</span>
                  <span className="summary-label">Emails</span>
                </div>
                <div className="summary-card">
                  <span className="summary-number">{results.documents?.length || 0}</span>
                  <span className="summary-label">Documents</span>
                </div>
              </div>

              {results.errors && results.errors.length > 0 && (
                <div className="warning-box">
                  <h4>⚠️ Search Warnings</h4>
                  {results.errors.map((err, idx) => (
                    <p key={idx}>{err}</p>
                  ))}
                </div>
              )}

              {/* No Data Found */}
              {(results.emails?.length === 0 && results.documents?.length === 0) && (
                <div className="no-data-found">
                  <div className="no-data-icon">📭</div>
                  <h3>No Data Found</h3>
                  <p className="no-data-message">
                    We couldn't find any emails or documents from <strong>{selectedProject?.search_email}</strong>
                  </p>
                  
                  <div className="no-data-details">
                    <div className="detail-item">
                      <span className="detail-label">Searched in:</span>
                      <span className="detail-value">
                        {selectedProject?.include_gmail && '📧 Gmail'} 
                        {selectedProject?.include_gmail && selectedProject?.include_drive && ' • '}
                        {selectedProject?.include_drive && '📄 Drive'}
                      </span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Date range:</span>
                      <span className="detail-value">
                        {selectedProject?.date_from ? new Date(selectedProject.date_from).toLocaleDateString() : 'Any'} 
                        {' → '} 
                        {selectedProject?.date_to ? new Date(selectedProject.date_to).toLocaleDateString() : 'Any'}
                      </span>
                    </div>
                  </div>

                  <div className="no-data-suggestions">
                    <h4>💡 Try these suggestions:</h4>
                    <ul>
                      <li>✓ Double-check the email address spelling</li>
                      <li>✓ Expand the date range (try "All time")</li>
                      <li>✓ Verify this person has sent you emails or shared files</li>
                      <li>✓ Check if Google services are properly connected</li>
                      <li>✓ Try searching for a different person</li>
                    </ul>
                  </div>

                  <div className="no-data-actions">
                    <button className="secondary-button" onClick={() => runSearch(selectedProject.id)}>
                      🔄 Try Again
                    </button>
                    <button className="primary-button" onClick={handleNewProject}>
                      ➕ New Search
                    </button>
                  </div>
                </div>
              )}

              {/* AI Chat Interface - Only show if we have data */}
              <div className="chat-section">
                <div className="chat-header">
                  <h3>🤖 AI Assistant</h3>
                  <button className="new-thread-button" onClick={() => setShowNewThreadModal(true)}>
                    ➕ New Thread
                  </button>
                </div>

                {/* Thread Sidebar */}
                <div className="chat-container">
                  <div className="threads-sidebar">
                    <div className="threads-list">
                      {threads.length === 0 ? (
                        <div className="no-threads">
                          <p>No threads yet</p>
                          <button onClick={() => setShowNewThreadModal(true)}>Create First Thread</button>
                        </div>
                      ) : (
                        threads.map((thread) => (
                          <div
                            key={thread.id}
                            className={`thread-item ${currentThread?.id === thread.id ? 'active' : ''}`}
                            onClick={() => selectThread(thread)}
                          >
                            <div className="thread-title">{thread.title}</div>
                            <div className="thread-meta">
                              {thread.message_count} messages
                            </div>
                            <button
                              className="delete-thread-btn"
                              onClick={(e) => {
                                e.stopPropagation()
                                deleteThread(thread.id)
                              }}
                            >
                              🗑️
                            </button>
                          </div>
                        ))
                      )}
                    </div>
                  </div>

                  {/* Chat Messages Area */}
                  <div className="chat-main">
                    {!currentThread ? (
                      <div className="no-thread-selected">
                        <p>👈 Select a thread or create a new one to start chatting</p>
                      </div>
                    ) : (
                      <>
                        <div className="chat-messages">
                          {chatHistory.length === 0 ? (
                            <div className="chat-empty-state">
                              <p>👋 Start a conversation in "{currentThread.title}"</p>
                              <div className="chat-suggestions">
                                <p className="suggestions-title">Try asking:</p>
                                <button onClick={() => setPromptText("Summarize the main topics discussed in these emails")}>
                                  Summarize the main topics
                                </button>
                                <button onClick={() => setPromptText("What are the key documents shared?")}>
                                  What are the key documents?
                                </button>
                                <button onClick={() => setPromptText("Find all action items and deadlines mentioned")}>
                                  Find action items
                                </button>
                              </div>
                            </div>
                          ) : (
                            chatHistory.map((message, index) => (
                              <div key={index} className={`chat-message ${message.role}`}>
                                <div className="message-avatar">
                                  {message.role === 'user' ? '👤' : '🤖'}
                                </div>
                                <div className="message-content">
                                  <div className="message-text">{message.content}</div>
                                  {message.parsed_count && message.role === 'assistant' && (
                                    <div className="message-meta">
                                      Analyzed {message.parsed_count.emails} email(s) and {message.parsed_count.documents} document(s) in detail
                                    </div>
                                  )}
                                  <div className="message-time">
                                    {new Date(message.created_at).toLocaleTimeString()}
                                  </div>
                                </div>
                              </div>
                            ))
                          )}
                          {analyzing && (
                            <div className="chat-message assistant">
                              <div className="message-avatar">🤖</div>
                              <div className="message-content">
                                <div className="typing-indicator">
                                  <span></span>
                                  <span></span>
                                  <span></span>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>

                        <form onSubmit={handleAnalyze} className="chat-input-form">
                          <div className="chat-options">
                            <label className="checkbox-label-small">
                              <input
                                type="checkbox"
                                checked={parseEmails}
                                onChange={(e) => setParseEmails(e.target.checked)}
                              />
                              Parse emails
                            </label>
                            <label className="checkbox-label-small">
                              <input
                                type="checkbox"
                                checked={parseDocuments}
                                onChange={(e) => setParseDocuments(e.target.checked)}
                              />
                              Parse documents
                            </label>
                          </div>
                          <div className="chat-input-container">
                            <textarea
                              value={promptText}
                              onChange={(e) => setPromptText(e.target.value)}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                  e.preventDefault()
                                  handleAnalyze(e)
                                }
                              }}
                              placeholder="Ask me anything about your emails and documents..."
                              className="chat-input"
                              rows={1}
                              disabled={analyzing}
                            />
                            <button
                              type="submit"
                              className="chat-send-button"
                              disabled={analyzing || !promptText.trim()}
                            >
                              {analyzing ? '⏳' : '📤'}
                            </button>
                          </div>
                        </form>
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Results Display - Only show if we have data */}
              {(results.emails?.length > 0 || results.documents?.length > 0) && (
                <div className="results-container">
                <div className="results-section">
                  <h3>📧 Emails ({results.emails?.length || 0})</h3>
                  {!results.emails || results.emails.length === 0 ? (
                    <p className="no-results">No emails found</p>
                  ) : (
                    <div className="results-list">
                      {results.emails.map((email) => (
                        <div key={email.id} className="result-item email-item">
                          <h4>{email.subject}</h4>
                          <p className="result-meta">
                            From: {email.from_} • {email.date}
                          </p>
                          <p className="result-snippet">{email.snippet}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="results-section">
                  <h3>📄 Documents ({results.documents?.length || 0})</h3>
                  {!results.documents || results.documents.length === 0 ? (
                    <p className="no-results">No documents found</p>
                  ) : (
                    <div className="results-list">
                      {results.documents.map((doc) => (
                        <div key={doc.id} className="result-item document-item">
                          <h4>
                            {doc.name}
                            <span className="doc-type">{doc.type}</span>
                          </h4>
                          <p className="result-meta">
                            Modified: {new Date(doc.modified_time).toLocaleString()}
                          </p>
                          <a
                            href={doc.web_view_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="view-link"
                          >
                            View Document →
                          </a>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="modal-overlay" onClick={() => !deleting && setShowDeleteModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-icon-warning">
              ⚠️
            </div>
            <h2 className="modal-title">Delete Project?</h2>
            <p className="modal-message">
              Are you sure you want to delete <strong>"{projectToDelete?.name}"</strong>?
            </p>
            <p className="modal-warning">
              This will permanently delete:
            </p>
            <ul className="modal-delete-list">
              <li>📧 All search results</li>
              <li>💬 All chat conversations</li>
              <li>📊 All project data</li>
            </ul>
            <p className="modal-warning-text">
              <strong>This action cannot be undone.</strong>
            </p>
            <div className="modal-actions">
              <button 
                className="modal-button modal-button-cancel"
                onClick={() => setShowDeleteModal(false)}
                disabled={deleting}
              >
                Cancel
              </button>
              <button 
                className="modal-button modal-button-delete"
                onClick={handleDeleteProject}
                disabled={deleting}
              >
                {deleting ? 'Deleting...' : 'Yes, Delete Project'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* New Thread Modal */}
      {showNewThreadModal && (
        <div className="modal-overlay" onClick={() => setShowNewThreadModal(false)}>
          <div className="modal-content modal-content-small" onClick={(e) => e.stopPropagation()}>
            <h2 className="modal-title">Create New Thread</h2>
            <p className="modal-message">Give your conversation thread a descriptive title</p>
            <input
              type="text"
              className="thread-title-input"
              placeholder="e.g., Budget Discussion, Action Items, Document Review..."
              value={newThreadTitle}
              onChange={(e) => setNewThreadTitle(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault()
                  createThread()
                }
              }}
              autoFocus
            />
            <div className="modal-actions">
              <button 
                className="modal-button modal-button-cancel"
                onClick={() => {
                  setShowNewThreadModal(false)
                  setNewThreadTitle('')
                }}
              >
                Cancel
              </button>
              <button 
                className="modal-button modal-button-primary"
                onClick={createThread}
                disabled={!newThreadTitle.trim()}
              >
                Create Thread
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Workplace
