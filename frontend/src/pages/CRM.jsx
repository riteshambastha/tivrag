import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import './CRM.css'

const API_BASE_URL = 'http://localhost:8002'

function CRM({ onLogout }) {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  // Dashboard data
  const [analytics, setAnalytics] = useState(null)
  
  // Contacts data
  const [contacts, setContacts] = useState([])
  const [selectedContact, setSelectedContact] = useState(null)
  const [showContactModal, setShowContactModal] = useState(false)
  const [contactForm, setContactForm] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    status: 'lead',
    tags: '',
    notes: ''
  })
  const [contactSearch, setContactSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  
  // Deals data
  const [deals, setDeals] = useState([])
  const [showDealModal, setShowDealModal] = useState(false)
  const [dealForm, setDealForm] = useState({
    contact_id: '',
    title: '',
    value: 0,
    stage: 'lead',
    probability: 0,
    expected_close_date: ''
  })
  
  // Tasks data
  const [tasks, setTasks] = useState([])
  const [showTaskModal, setShowTaskModal] = useState(false)
  const [taskForm, setTaskForm] = useState({
    title: '',
    description: '',
    assigned_to_contact_id: '',
    due_date: '',
    priority: 'medium',
    status: 'pending'
  })
  
  // Notes data
  const [notes, setNotes] = useState([])
  const [showNoteModal, setShowNoteModal] = useState(false)
  const [noteForm, setNoteForm] = useState({
    content: '',
    related_to_contact_id: '',
    related_to_deal_id: '',
    note_type: 'general'
  })
  
  const navigate = useNavigate()

  useEffect(() => {
    loadDashboardData()
  }, [])

  useEffect(() => {
    if (activeTab === 'contacts') {
      loadContacts()
    } else if (activeTab === 'deals') {
      loadDeals()
    } else if (activeTab === 'tasks') {
      loadTasks()
    } else if (activeTab === 'notes') {
      loadNotes()
    }
  }, [activeTab, contactSearch, statusFilter])

  const loadDashboardData = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get(`${API_BASE_URL}/api/crm/analytics/dashboard`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setAnalytics(response.data)
    } catch (err) {
      console.error('Failed to load analytics', err)
      setError('Failed to load dashboard data')
    }
  }

  const loadContacts = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('token')
      const params = {}
      if (statusFilter) params.status = statusFilter
      if (contactSearch) params.search = contactSearch
      
      const response = await axios.get(`${API_BASE_URL}/api/crm/contacts`, {
        headers: { Authorization: `Bearer ${token}` },
        params
      })
      setContacts(response.data)
    } catch (err) {
      console.error('Failed to load contacts', err)
      setError('Failed to load contacts')
    } finally {
      setLoading(false)
    }
  }

  const loadDeals = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('token')
      const response = await axios.get(`${API_BASE_URL}/api/crm/deals`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setDeals(response.data)
    } catch (err) {
      console.error('Failed to load deals', err)
      setError('Failed to load deals')
    } finally {
      setLoading(false)
    }
  }

  const loadTasks = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('token')
      const response = await axios.get(`${API_BASE_URL}/api/crm/tasks`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setTasks(response.data)
    } catch (err) {
      console.error('Failed to load tasks', err)
      setError('Failed to load tasks')
    } finally {
      setLoading(false)
    }
  }

  const loadNotes = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('token')
      const response = await axios.get(`${API_BASE_URL}/api/crm/notes`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setNotes(response.data)
    } catch (err) {
      console.error('Failed to load notes', err)
      setError('Failed to load notes')
    } finally {
      setLoading(false)
    }
  }

  const createContact = async () => {
    try {
      const token = localStorage.getItem('token')
      await axios.post(`${API_BASE_URL}/api/crm/contacts`, contactForm, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setShowContactModal(false)
      resetContactForm()
      loadContacts()
      loadDashboardData()
    } catch (err) {
      console.error('Failed to create contact', err)
      setError('Failed to create contact')
    }
  }

  const updateContact = async () => {
    try {
      const token = localStorage.getItem('token')
      await axios.put(`${API_BASE_URL}/api/crm/contacts/${selectedContact.id}`, contactForm, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setShowContactModal(false)
      resetContactForm()
      setSelectedContact(null)
      loadContacts()
      loadDashboardData()
    } catch (err) {
      console.error('Failed to update contact', err)
      setError('Failed to update contact')
    }
  }

  const deleteContact = async (id) => {
    if (!window.confirm('Are you sure you want to delete this contact?')) return
    
    try {
      const token = localStorage.getItem('token')
      await axios.delete(`${API_BASE_URL}/api/crm/contacts/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      loadContacts()
      loadDashboardData()
    } catch (err) {
      console.error('Failed to delete contact', err)
      setError('Failed to delete contact')
    }
  }

  const createDeal = async () => {
    try {
      const token = localStorage.getItem('token')
      await axios.post(`${API_BASE_URL}/api/crm/deals`, dealForm, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setShowDealModal(false)
      resetDealForm()
      loadDeals()
      loadDashboardData()
    } catch (err) {
      console.error('Failed to create deal', err)
      setError('Failed to create deal')
    }
  }

  const updateDealStage = async (dealId, newStage) => {
    try {
      const token = localStorage.getItem('token')
      await axios.put(`${API_BASE_URL}/api/crm/deals/${dealId}`, { stage: newStage }, {
        headers: { Authorization: `Bearer ${token}` }
      })
      loadDeals()
      loadDashboardData()
    } catch (err) {
      console.error('Failed to update deal', err)
      setError('Failed to update deal')
    }
  }

  const deleteDeal = async (id) => {
    if (!window.confirm('Are you sure you want to delete this deal?')) return
    
    try {
      const token = localStorage.getItem('token')
      await axios.delete(`${API_BASE_URL}/api/crm/deals/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      loadDeals()
      loadDashboardData()
    } catch (err) {
      console.error('Failed to delete deal', err)
      setError('Failed to delete deal')
    }
  }

  const createTask = async () => {
    try {
      const token = localStorage.getItem('token')
      await axios.post(`${API_BASE_URL}/api/crm/tasks`, taskForm, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setShowTaskModal(false)
      resetTaskForm()
      loadTasks()
      loadDashboardData()
    } catch (err) {
      console.error('Failed to create task', err)
      setError('Failed to create task')
    }
  }

  const toggleTaskComplete = async (taskId, completed) => {
    try {
      const token = localStorage.getItem('token')
      await axios.put(`${API_BASE_URL}/api/crm/tasks/${taskId}`, { 
        completed: !completed,
        status: !completed ? 'completed' : 'pending'
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })
      loadTasks()
      loadDashboardData()
    } catch (err) {
      console.error('Failed to update task', err)
      setError('Failed to update task')
    }
  }

  const deleteTask = async (id) => {
    if (!window.confirm('Are you sure you want to delete this task?')) return
    
    try {
      const token = localStorage.getItem('token')
      await axios.delete(`${API_BASE_URL}/api/crm/tasks/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      loadTasks()
      loadDashboardData()
    } catch (err) {
      console.error('Failed to delete task', err)
      setError('Failed to delete task')
    }
  }

  const createNote = async () => {
    try {
      const token = localStorage.getItem('token')
      await axios.post(`${API_BASE_URL}/api/crm/notes`, noteForm, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setShowNoteModal(false)
      resetNoteForm()
      loadNotes()
      loadDashboardData()
    } catch (err) {
      console.error('Failed to create note', err)
      setError('Failed to create note')
    }
  }

  const resetContactForm = () => {
    setContactForm({
      name: '',
      email: '',
      phone: '',
      company: '',
      status: 'lead',
      tags: '',
      notes: ''
    })
  }

  const resetDealForm = () => {
    setDealForm({
      contact_id: '',
      title: '',
      value: 0,
      stage: 'lead',
      probability: 0,
      expected_close_date: ''
    })
  }

  const resetTaskForm = () => {
    setTaskForm({
      title: '',
      description: '',
      assigned_to_contact_id: '',
      due_date: '',
      priority: 'medium',
      status: 'pending'
    })
  }

  const resetNoteForm = () => {
    setNoteForm({
      content: '',
      related_to_contact_id: '',
      related_to_deal_id: '',
      note_type: 'general'
    })
  }

  const openEditContact = (contact) => {
    setSelectedContact(contact)
    setContactForm({
      name: contact.name,
      email: contact.email || '',
      phone: contact.phone || '',
      company: contact.company || '',
      status: contact.status,
      tags: contact.tags || '',
      notes: contact.notes || ''
    })
    setShowContactModal(true)
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value)
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString()
  }

  const getContactName = (contactId) => {
    const contact = contacts.find(c => c.id === parseInt(contactId))
    return contact ? contact.name : 'Unknown'
  }

  const renderDashboard = () => (
    <div className="crm-dashboard">
      <h2>CRM Dashboard</h2>
      
      {analytics && (
        <>
          <div className="metrics-grid">
            <div className="metric-card">
              <h3>Total Contacts</h3>
              <div className="metric-value">{analytics.total_contacts}</div>
            </div>
            
            <div className="metric-card">
              <h3>Total Deal Value</h3>
              <div className="metric-value">{formatCurrency(analytics.total_deal_value)}</div>
            </div>
            
            <div className="metric-card">
              <h3>Active Tasks</h3>
              <div className="metric-value">{analytics.tasks_summary.total}</div>
              <div className="metric-detail">
                {analytics.tasks_summary.overdue > 0 && (
                  <span className="overdue">{analytics.tasks_summary.overdue} overdue</span>
                )}
              </div>
            </div>
          </div>

          <div className="dashboard-sections">
            <div className="dashboard-section">
              <h3>Contacts by Status</h3>
              <div className="chart-placeholder">
                {Object.entries(analytics.contacts_by_status).map(([status, count]) => (
                  <div key={status} className="chart-bar">
                    <span className="chart-label">{status}</span>
                    <div className="chart-bar-fill" style={{ width: `${(count / analytics.total_contacts) * 100}%` }}>
                      <span className="chart-value">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="dashboard-section">
              <h3>Deals Pipeline</h3>
              <div className="chart-placeholder">
                {Object.entries(analytics.deals_by_stage).map(([stage, count]) => (
                  <div key={stage} className="chart-bar">
                    <span className="chart-label">{stage}</span>
                    <div className="chart-bar-fill deals" style={{ width: `${count * 20}%` }}>
                      <span className="chart-value">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="dashboard-section">
              <h3>Recent Activity</h3>
              <div className="activity-feed">
                {analytics.recent_activities.map((activity) => (
                  <div key={activity.id} className="activity-item">
                    <div className="activity-type">{activity.type}</div>
                    <div className="activity-content">{activity.content}</div>
                    <div className="activity-meta">
                      {activity.contact_name && <span>Contact: {activity.contact_name}</span>}
                      {activity.deal_title && <span>Deal: {activity.deal_title}</span>}
                      <span>{formatDate(activity.created_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )

  const renderContacts = () => (
    <div className="crm-contacts">
      <div className="crm-header">
        <h2>Contacts</h2>
        <button className="btn-primary" onClick={() => {
          resetContactForm()
          setSelectedContact(null)
          setShowContactModal(true)
        }}>
          + New Contact
        </button>
      </div>

      <div className="crm-filters">
        <input
          type="text"
          placeholder="Search contacts..."
          value={contactSearch}
          onChange={(e) => setContactSearch(e.target.value)}
          className="search-input"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="filter-select"
        >
          <option value="">All Statuses</option>
          <option value="lead">Lead</option>
          <option value="prospect">Prospect</option>
          <option value="customer">Customer</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>

      <div className="contacts-table">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Company</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {contacts.map(contact => (
              <tr key={contact.id}>
                <td>{contact.name}</td>
                <td>{contact.email || 'N/A'}</td>
                <td>{contact.phone || 'N/A'}</td>
                <td>{contact.company || 'N/A'}</td>
                <td>
                  <span className={`status-badge ${contact.status}`}>
                    {contact.status}
                  </span>
                </td>
                <td>
                  <button className="btn-small" onClick={() => openEditContact(contact)}>Edit</button>
                  <button className="btn-small btn-danger" onClick={() => deleteContact(contact.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )

  const renderDeals = () => {
    const stages = ['lead', 'qualified', 'proposal', 'negotiation', 'closed_won', 'closed_lost']
    
    const dealsByStage = {}
    stages.forEach(stage => {
      dealsByStage[stage] = deals.filter(d => d.stage === stage)
    })

    return (
      <div className="crm-deals">
        <div className="crm-header">
          <h2>Deals Pipeline</h2>
          <button className="btn-primary" onClick={() => {
            resetDealForm()
            setShowDealModal(true)
          }}>
            + New Deal
          </button>
        </div>

        <div className="kanban-board">
          {stages.map(stage => (
            <div key={stage} className="kanban-column">
              <h3>{stage.replace('_', ' ').toUpperCase()}</h3>
              <div className="kanban-cards">
                {dealsByStage[stage].map(deal => (
                  <div key={deal.id} className="deal-card">
                    <h4>{deal.title}</h4>
                    <div className="deal-value">{formatCurrency(deal.value)}</div>
                    <div className="deal-meta">
                      <span>Contact: {getContactName(deal.contact_id)}</span>
                      <span>Probability: {deal.probability}%</span>
                    </div>
                    <div className="deal-actions">
                      {stage !== 'closed_won' && stage !== 'closed_lost' && (
                        <select
                          value={deal.stage}
                          onChange={(e) => updateDealStage(deal.id, e.target.value)}
                          className="stage-select"
                        >
                          {stages.map(s => (
                            <option key={s} value={s}>{s.replace('_', ' ')}</option>
                          ))}
                        </select>
                      )}
                      <button className="btn-small btn-danger" onClick={() => deleteDeal(deal.id)}>Delete</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const renderTasks = () => (
    <div className="crm-tasks">
      <div className="crm-header">
        <h2>Tasks</h2>
        <button className="btn-primary" onClick={() => {
          resetTaskForm()
          setShowTaskModal(true)
        }}>
          + New Task
        </button>
      </div>

      <div className="tasks-list">
        {tasks.map(task => (
          <div key={task.id} className={`task-item ${task.completed ? 'completed' : ''} priority-${task.priority}`}>
            <input
              type="checkbox"
              checked={task.completed}
              onChange={() => toggleTaskComplete(task.id, task.completed)}
            />
            <div className="task-content">
              <h4>{task.title}</h4>
              <p>{task.description}</p>
              <div className="task-meta">
                <span className={`priority-badge ${task.priority}`}>{task.priority}</span>
                <span>Due: {formatDate(task.due_date)}</span>
                {task.assigned_to_contact_id && (
                  <span>Assigned to: {getContactName(task.assigned_to_contact_id)}</span>
                )}
              </div>
            </div>
            <button className="btn-small btn-danger" onClick={() => deleteTask(task.id)}>Delete</button>
          </div>
        ))}
      </div>
    </div>
  )

  const renderNotes = () => (
    <div className="crm-notes">
      <div className="crm-header">
        <h2>Notes & Activities</h2>
        <button className="btn-primary" onClick={() => {
          resetNoteForm()
          setShowNoteModal(true)
        }}>
          + New Note
        </button>
      </div>

      <div className="notes-timeline">
        {notes.map(note => (
          <div key={note.id} className="note-item">
            <div className="note-type">{note.note_type}</div>
            <div className="note-content">{note.content}</div>
            <div className="note-meta">
              {note.related_to_contact_id && (
                <span>Contact: {getContactName(note.related_to_contact_id)}</span>
              )}
              <span>{formatDate(note.created_at)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )

  return (
    <div className="crm-container">
      <div className="crm-nav">
        <h1>CRM</h1>
        <div className="crm-tabs">
          <button
            className={activeTab === 'dashboard' ? 'active' : ''}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={activeTab === 'contacts' ? 'active' : ''}
            onClick={() => setActiveTab('contacts')}
          >
            Contacts
          </button>
          <button
            className={activeTab === 'deals' ? 'active' : ''}
            onClick={() => setActiveTab('deals')}
          >
            Deals
          </button>
          <button
            className={activeTab === 'tasks' ? 'active' : ''}
            onClick={() => setActiveTab('tasks')}
          >
            Tasks
          </button>
          <button
            className={activeTab === 'notes' ? 'active' : ''}
            onClick={() => setActiveTab('notes')}
          >
            Notes
          </button>
        </div>
        <button className="btn-logout" onClick={onLogout}>Logout</button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="crm-content">
        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'contacts' && renderContacts()}
        {activeTab === 'deals' && renderDeals()}
        {activeTab === 'tasks' && renderTasks()}
        {activeTab === 'notes' && renderNotes()}
      </div>

      {/* Contact Modal */}
      {showContactModal && (
        <div className="modal-overlay" onClick={() => setShowContactModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>{selectedContact ? 'Edit Contact' : 'New Contact'}</h3>
            <input
              type="text"
              placeholder="Name *"
              value={contactForm.name}
              onChange={(e) => setContactForm({ ...contactForm, name: e.target.value })}
            />
            <input
              type="email"
              placeholder="Email"
              value={contactForm.email}
              onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
            />
            <input
              type="tel"
              placeholder="Phone"
              value={contactForm.phone}
              onChange={(e) => setContactForm({ ...contactForm, phone: e.target.value })}
            />
            <input
              type="text"
              placeholder="Company"
              value={contactForm.company}
              onChange={(e) => setContactForm({ ...contactForm, company: e.target.value })}
            />
            <select
              value={contactForm.status}
              onChange={(e) => setContactForm({ ...contactForm, status: e.target.value })}
            >
              <option value="lead">Lead</option>
              <option value="prospect">Prospect</option>
              <option value="customer">Customer</option>
              <option value="inactive">Inactive</option>
            </select>
            <textarea
              placeholder="Notes"
              value={contactForm.notes}
              onChange={(e) => setContactForm({ ...contactForm, notes: e.target.value })}
            />
            <div className="modal-actions">
              <button className="btn-primary" onClick={selectedContact ? updateContact : createContact}>
                {selectedContact ? 'Update' : 'Create'}
              </button>
              <button className="btn-secondary" onClick={() => setShowContactModal(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}

      {/* Deal Modal */}
      {showDealModal && (
        <div className="modal-overlay" onClick={() => setShowDealModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>New Deal</h3>
            <select
              value={dealForm.contact_id}
              onChange={(e) => setDealForm({ ...dealForm, contact_id: e.target.value })}
            >
              <option value="">Select Contact *</option>
              {contacts.map(c => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
            <input
              type="text"
              placeholder="Deal Title *"
              value={dealForm.title}
              onChange={(e) => setDealForm({ ...dealForm, title: e.target.value })}
            />
            <input
              type="number"
              placeholder="Value"
              value={dealForm.value}
              onChange={(e) => setDealForm({ ...dealForm, value: parseFloat(e.target.value) })}
            />
            <select
              value={dealForm.stage}
              onChange={(e) => setDealForm({ ...dealForm, stage: e.target.value })}
            >
              <option value="lead">Lead</option>
              <option value="qualified">Qualified</option>
              <option value="proposal">Proposal</option>
              <option value="negotiation">Negotiation</option>
              <option value="closed_won">Closed Won</option>
              <option value="closed_lost">Closed Lost</option>
            </select>
            <input
              type="number"
              placeholder="Probability (%)"
              value={dealForm.probability}
              onChange={(e) => setDealForm({ ...dealForm, probability: parseInt(e.target.value) })}
              min="0"
              max="100"
            />
            <input
              type="date"
              placeholder="Expected Close Date"
              value={dealForm.expected_close_date}
              onChange={(e) => setDealForm({ ...dealForm, expected_close_date: e.target.value })}
            />
            <div className="modal-actions">
              <button className="btn-primary" onClick={createDeal}>Create</button>
              <button className="btn-secondary" onClick={() => setShowDealModal(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}

      {/* Task Modal */}
      {showTaskModal && (
        <div className="modal-overlay" onClick={() => setShowTaskModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>New Task</h3>
            <input
              type="text"
              placeholder="Task Title *"
              value={taskForm.title}
              onChange={(e) => setTaskForm({ ...taskForm, title: e.target.value })}
            />
            <textarea
              placeholder="Description"
              value={taskForm.description}
              onChange={(e) => setTaskForm({ ...taskForm, description: e.target.value })}
            />
            <select
              value={taskForm.assigned_to_contact_id}
              onChange={(e) => setTaskForm({ ...taskForm, assigned_to_contact_id: e.target.value })}
            >
              <option value="">Assign to Contact (optional)</option>
              {contacts.map(c => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
            <input
              type="date"
              value={taskForm.due_date}
              onChange={(e) => setTaskForm({ ...taskForm, due_date: e.target.value })}
            />
            <select
              value={taskForm.priority}
              onChange={(e) => setTaskForm({ ...taskForm, priority: e.target.value })}
            >
              <option value="low">Low Priority</option>
              <option value="medium">Medium Priority</option>
              <option value="high">High Priority</option>
            </select>
            <div className="modal-actions">
              <button className="btn-primary" onClick={createTask}>Create</button>
              <button className="btn-secondary" onClick={() => setShowTaskModal(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}

      {/* Note Modal */}
      {showNoteModal && (
        <div className="modal-overlay" onClick={() => setShowNoteModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>New Note</h3>
            <textarea
              placeholder="Note Content *"
              value={noteForm.content}
              onChange={(e) => setNoteForm({ ...noteForm, content: e.target.value })}
              rows="4"
            />
            <select
              value={noteForm.note_type}
              onChange={(e) => setNoteForm({ ...noteForm, note_type: e.target.value })}
            >
              <option value="general">General</option>
              <option value="call">Call</option>
              <option value="meeting">Meeting</option>
              <option value="email">Email</option>
              <option value="task">Task</option>
            </select>
            <select
              value={noteForm.related_to_contact_id}
              onChange={(e) => setNoteForm({ ...noteForm, related_to_contact_id: e.target.value })}
            >
              <option value="">Related to Contact (optional)</option>
              {contacts.map(c => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
            <div className="modal-actions">
              <button className="btn-primary" onClick={createNote}>Create</button>
              <button className="btn-secondary" onClick={() => setShowNoteModal(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default CRM

