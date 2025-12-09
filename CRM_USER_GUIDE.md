# CRM User Guide

## Quick Start

### Accessing the CRM
1. Log in to Tivrag
2. Click the **"CRM"** button in the navigation bar (available from Dashboard, Workplace, or Configuration pages)
3. You'll land on the CRM Dashboard

## Features Overview

### 📊 Dashboard Tab
Your CRM command center showing:
- **Total Contacts**: Count of all your contacts
- **Total Deal Value**: Sum of all deal values in your pipeline
- **Active Tasks**: Number of tasks with overdue indicators
- **Contacts by Status**: Visual breakdown of leads, prospects, customers
- **Deals Pipeline**: Visual breakdown by stage
- **Recent Activity**: Latest 10 notes/activities

### 👥 Contacts Tab

#### Creating a Contact
1. Click **"+ New Contact"** button
2. Fill in the form:
   - **Name** (required)
   - Email
   - Phone
   - Company
   - **Status**: Choose from Lead, Prospect, Customer, or Inactive
   - Notes: Any additional information
3. Click **"Create"**

#### Managing Contacts
- **Search**: Type in the search box to filter by name, email, or company
- **Filter by Status**: Use the dropdown to show only specific statuses
- **Edit**: Click "Edit" button on any contact row
- **Delete**: Click "Delete" button (requires confirmation)

#### Contact Statuses
- **Lead**: Potential customer, initial contact
- **Prospect**: Qualified lead, actively pursuing
- **Customer**: Active paying customer
- **Inactive**: No longer active

### 💼 Deals Tab (Pipeline)

#### Understanding the Pipeline
The Kanban board shows deals in 6 stages:
1. **LEAD**: Initial opportunity identified
2. **QUALIFIED**: Prospect has budget, authority, need, timeline
3. **PROPOSAL**: Quote/proposal sent
4. **NEGOTIATION**: Terms being discussed
5. **CLOSED WON**: Deal successfully closed 🎉
6. **CLOSED LOST**: Deal didn't close

#### Creating a Deal
1. Click **"+ New Deal"** button
2. Fill in the form:
   - **Contact**: Select which contact this deal is for (required)
   - **Title**: Name of the deal (required)
   - **Value**: Deal amount in dollars
   - **Stage**: Starting stage (default: Lead)
   - **Probability**: Likelihood of closing (0-100%)
   - **Expected Close Date**: When you expect to close
3. Click **"Create"**

#### Moving Deals
- Use the **dropdown** on each deal card to change its stage
- Deals automatically update in real-time
- Track progress visually as deals move right across the board

#### Deal Cards Show
- Deal title
- Dollar value
- Contact name
- Probability percentage

### ✅ Tasks Tab

#### Creating a Task
1. Click **"+ New Task"** button
2. Fill in the form:
   - **Title**: What needs to be done (required)
   - Description: Details about the task
   - **Assign to Contact**: Optional, link to a specific contact
   - **Due Date**: When it's due
   - **Priority**: Low, Medium, or High
3. Click **"Create"**

#### Managing Tasks
- **Complete a Task**: Click the checkbox next to the task
- **Priority Colors**:
  - 🟢 **Green** = Low priority
  - 🟠 **Orange** = Medium priority
  - 🔴 **Red** = High priority
- **Overdue**: Tasks past their due date are highlighted
- **Delete**: Click "Delete" button to remove

#### Task Workflow
Tasks can be:
- **Pending**: Not started yet
- **In Progress**: Currently working on it
- **Completed**: Finished
- **Cancelled**: No longer needed

### 📝 Notes Tab

#### Creating a Note
1. Click **"+ New Note"** button
2. Fill in the form:
   - **Content**: The note text (required)
   - **Type**: General, Call, Meeting, Email, or Task
   - **Related to Contact**: Optional, link to a contact
3. Click **"Create"**

#### Note Types
- 📄 **General**: Regular notes
- 📞 **Call**: Phone call notes
- 🤝 **Meeting**: Meeting minutes
- ✉️ **Email**: Email correspondence
- ✅ **Task**: Task-related notes

#### Viewing Notes
- Notes appear in chronological order (newest first)
- Each note shows:
  - Type badge
  - Content
  - Related contact (if linked)
  - Creation date/time

## Common Workflows

### 1. New Lead Workflow
```
1. Add Contact (status: Lead)
   ↓
2. Create Deal (stage: Lead)
   ↓
3. Create Task: "Follow up with lead"
   ↓
4. Add Note: Document first conversation
   ↓
5. Update Contact status to Prospect when qualified
   ↓
6. Move Deal to Qualified stage
```

### 2. Sales Process Workflow
```
Lead → Qualified → Proposal → Negotiation → Closed Won
(Update deal stage as you progress)
(Add notes at each stage documenting conversations)
(Create tasks for follow-ups)
```

### 3. Customer Management Workflow
```
1. Contact with status: Customer
   ↓
2. Create Tasks for check-ins
   ↓
3. Add Notes after each interaction
   ↓
4. Track upsell/renewal Deals
```

## Email Integration (Coming Soon)
When configured with Google OAuth:
- Send emails directly to contacts
- View email history
- Track email threads

To enable:
1. Go to Configuration page
2. Connect Google Services
3. Grant Gmail send permission
4. Return to CRM → Contacts
5. Edit a contact and look for "Send Email" option

## Tips & Best Practices

### Contact Management
- ✅ Always add an email address (required for email integration)
- ✅ Use consistent company names for better reporting
- ✅ Keep status updated as relationships progress
- ✅ Add notes after every significant interaction

### Deal Management
- ✅ Be realistic with probabilities (helps with forecasting)
- ✅ Keep expected close dates updated
- ✅ Move deals through stages consistently
- ✅ Archive closed deals (won or lost) instead of deleting

### Task Management
- ✅ Set due dates on all tasks
- ✅ Use high priority sparingly (only for urgent items)
- ✅ Assign tasks to contacts when relevant
- ✅ Complete tasks promptly to keep list clean

### Note Taking
- ✅ Add notes immediately after interactions
- ✅ Be specific and detailed
- ✅ Link notes to relevant contacts
- ✅ Use consistent note types for easier filtering

## Keyboard Shortcuts
- **Enter** in any modal = Submit form
- **Escape** = Close modal (when implemented)
- **Tab** = Navigate between form fields

## Data Management

### Searching
- Contact search looks in: name, email, company
- Search is case-insensitive
- Results update as you type

### Filtering
- Filter contacts by status
- Filter tasks by status or priority
- Filter notes by contact or deal

### Deleting Data
- ⚠️ **Warning**: Deletions are permanent!
- Deleting a contact does NOT delete associated:
  - Deals (orphaned deals remain)
  - Tasks (orphaned tasks remain)
  - Notes (notes remain for history)
- Always confirm before deleting

## Dashboard Metrics Explained

### Total Contacts
Simple count of all contacts in your database, regardless of status.

### Total Deal Value
Sum of the `value` field from all deals, regardless of stage.
- Use this to see your total pipeline value
- Filter by stage in Deals tab for more specific analysis

### Tasks Summary
- **Total**: All tasks
- **Pending**: Not started
- **In Progress**: Currently working
- **Completed**: Finished
- **Overdue**: Past due date and not completed (shown in warning color)

### Contacts by Status
Bar chart showing distribution of leads, prospects, customers, and inactive contacts.
- Wider bar = more contacts in that status
- Numbers show exact count

### Deals by Stage
Bar chart showing distribution across pipeline stages.
- Track where deals are clustering
- Identify bottlenecks in your process

### Recent Activity
Last 10 notes added to the system:
- Shows note type
- Truncated content (first 100 characters)
- Related contact/deal names
- Creation timestamp

## Troubleshooting

### Can't See CRM Button
- Make sure you're logged in
- Check you're on Dashboard, Workplace, or Configuration page
- Refresh the page

### No Contacts Showing
- Check your search/filter settings
- You may need to create your first contact
- Verify you're logged in as the correct user

### Can't Create Deal
- Ensure you have at least one contact
- Make sure you selected a contact in the form
- Contact must belong to your account

### Email Sending Not Working
- Verify Google Services are connected (Configuration page)
- Check contact has an email address
- Ensure Gmail send permissions were granted

### Dashboard Shows Zero
- This is normal for a new account
- Start by adding contacts, deals, and tasks
- Dashboard updates in real-time

## Mobile Usage

The CRM is fully responsive and works on mobile devices:
- Touch-friendly buttons and controls
- Optimized layout for small screens
- Scroll horizontally on pipeline for all stages
- Modals adapt to screen size

## Support & Feedback

For issues, questions, or feature requests:
1. Check this guide first
2. Review the CRM_IMPLEMENTATION_SUMMARY.md for technical details
3. Contact your system administrator

## What's Next?

Future enhancements being considered:
- CSV import/export
- Email templates
- Calendar integration
- Advanced reporting
- Custom fields
- Mobile app

---

**Happy CRM-ing! 🚀**

