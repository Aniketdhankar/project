# Frontend Guide - HTML/CSS/Bootstrap/JS Dashboard

This guide explains the HTML/CSS/Bootstrap/JS frontend implementation for the Time & Resource Allocation System.

## Overview

The frontend is built using **only HTML, CSS, Bootstrap 5.3, and vanilla JavaScript** - no React, Vue, or other frontend frameworks. It provides complete Manager and Employee dashboards with real-time updates.

## Features

### Authentication
- **Login Page** (`/login`)
  - Email and password authentication
  - Remember me functionality
  - Client-side validation
  - Auto-redirect based on user role

- **Registration Page** (`/register`)
  - User registration with role selection (Manager/Employee)
  - Department and skills input
  - Password confirmation validation
  - Terms acceptance checkbox

### Manager Views

#### Dashboard (`/manager/dashboard`)
- **Metrics Cards**: Total Tasks, Completed, In Progress, Overdue
- **Task Queue**: Sortable table with filtering
- **Charts** (Chart.js):
  - Resource Utilization (Bar Chart)
  - Team Velocity (Line Chart)
  - Burndown Chart (Line Chart)
- **Live Updates**: Server-Sent Events for real-time notifications
- **Quick Actions**:
  - Create New Task (modal form)
  - Auto-Assign Tasks (ML pipeline trigger)
  - Preview Assignments (shows recommended assignments)
- **Employee Summary**: Quick stats on team availability

#### Employee Management (`/manager/employees`)
- **Employee Table**: Complete list with all employee details
- **Search & Filter**: By name, email, skills, department, status
- **Workload Visualization**: Color-coded progress bars
- **Actions**:
  - Add Employee (modal form)
  - Edit Employee (modal form with pre-filled data)
  - View Workload (detailed modal with charts)
  - Delete Employee (with confirmation)

### Employee Views

#### Dashboard (`/employee/dashboard`)
- **Personal Metrics**: My Tasks, Completed, Hours This Week, Workload %
- **Task List**: Assigned tasks with progress bars
- **Recent Activity**: Timeline of recent actions
- **My Stats**: Performance metrics and ratings
- **Task Distribution**: Doughnut chart showing task breakdown
- **Quick Actions**:
  - Submit Timesheet (modal form)
  - Update Progress (modal with slider)
  - Refresh Tasks
- **Live Updates**: Real-time notifications for assignments and updates

## Technology Stack

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Custom styles with modern features
- **Bootstrap 5.3**: Responsive layout and components
- **Bootstrap Icons**: UI iconography
- **Chart.js 4.4**: Data visualizations
- **Vanilla JavaScript**: No frameworks, ES6+ features

### Backend Integration
- **Flask**: Serves HTML templates and API endpoints
- **Server-Sent Events**: Real-time updates from backend
- **REST API**: Fetch API for AJAX calls

## File Structure

```
backend/
├── templates/                    # HTML templates
│   ├── login.html               # Login page
│   ├── register.html            # Registration page
│   ├── manager_dashboard.html   # Manager main dashboard
│   ├── manager_employees.html   # Employee management
│   └── employee_dashboard.html  # Employee main dashboard
├── static/
│   ├── css/
│   │   └── style.css           # Global styles (~6.5KB)
│   └── js/
│       ├── auth.js             # Authentication logic (~6KB)
│       ├── manager_dashboard.js # Manager dashboard (~17KB)
│       ├── manager_employees.js # Employee management (~16KB)
│       └── employee_dashboard.js # Employee dashboard (~16KB)
└── app.py                       # Flask app with HTML routes
```

## Running the Application

### Prerequisites
```bash
pip install Flask Flask-CORS python-dotenv
```

### Start the Server
```bash
cd time_resource_allocation/backend
python3 app.py
```

The application will be available at `http://localhost:5000`

### Default Routes
- `/` - Redirects to login
- `/login` - Login page
- `/register` - Registration page
- `/manager/dashboard` - Manager dashboard (requires manager login)
- `/manager/employees` - Employee management (requires manager login)
- `/employee/dashboard` - Employee dashboard (requires employee login)

## Authentication

The frontend uses **localStorage** for client-side session management:

### Login Flow
1. User enters email and password
2. JavaScript validates and sends credentials
3. On success, stores user info and token in localStorage
4. Redirects to appropriate dashboard based on role

### Demo Credentials
- **Manager**: 
  - Email: `manager@example.com`
  - Password: `password123`
- **Employee**: 
  - Email: `employee@example.com`
  - Password: `password123`

## Key Features

### 1. Real-Time Updates
All dashboards connect to Server-Sent Events endpoint:
```javascript
const eventSource = new EventSource('/api/stream/updates');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  handleUpdate(data);
};
```

### 2. Charts
Using Chart.js for visualizations:
- **Bar Chart**: Resource utilization across employees
- **Line Chart**: Team velocity over time
- **Burndown Chart**: Sprint progress tracking
- **Doughnut Chart**: Task distribution by status

### 3. Forms & Modals
- Bootstrap modals for all forms
- Client-side validation before API calls
- Toast notifications for user feedback
- Form reset after successful submission

### 4. Responsive Design
- Mobile-first approach
- Breakpoints: `xs` (< 576px), `sm`, `md`, `lg`, `xl`
- Collapsible navigation on mobile
- Responsive tables with horizontal scroll

### 5. Interactive Tables
- Sortable columns
- Filterable data
- Pagination support
- Action buttons (View, Edit, Delete)
- Status badges with color coding

## API Integration

The frontend expects these API endpoints (from `routes/api.py`):

### Manager APIs
- `GET /api/assignments` - Get all task assignments
- `POST /api/trigger_pipeline` - Trigger auto-assignment
- `GET /api/analytics/dashboard` - Dashboard metrics
- `GET /api/employees` - Get all employees
- `POST /api/employees` - Create employee
- `PUT /api/employees/{id}` - Update employee
- `DELETE /api/employees/{id}` - Delete employee
- `GET /api/employee/{id}/workload` - Employee workload details

### Employee APIs
- `GET /api/assignments?employee_id={id}` - Get my tasks
- `POST /api/timesheets` - Submit timesheet
- `PUT /api/assignments/{id}/progress` - Update task progress

### Real-Time
- `GET /api/stream/updates` - Server-Sent Events stream

## Customization

### Styling
Edit `/static/css/style.css` to customize:
- Colors (CSS variables at top)
- Card styles
- Table appearance
- Button styles
- Modal layouts

### Mock Data
Currently uses mock data in JavaScript files. To connect to real API:
1. Replace mock data with fetch calls
2. Update API endpoints in JavaScript
3. Handle API responses and errors

### Charts
Modify chart configurations in respective JavaScript files:
- `initializeResourceChart()` - Resource utilization
- `initializeVelocityChart()` - Team velocity
- `initializeBurndownChart()` - Burndown
- `initializeTaskDistributionChart()` - Task distribution

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- Lazy loading for charts
- Debounced search inputs
- Pagination for large tables
- Event source reconnection on failure
- Minimal external dependencies

## Security

- Client-side validation (not a replacement for server-side)
- CSRF tokens should be added for production
- XSS prevention via proper escaping
- Authentication tokens in localStorage (consider httpOnly cookies for production)

## Next Steps

To connect to real backend:
1. Implement actual authentication API endpoints
2. Connect task management APIs
3. Enable WebSocket/SSE for real-time updates
4. Add error handling and retry logic
5. Implement proper session management
6. Add loading states and skeleton screens
7. Add unit tests for JavaScript functions

## Troubleshooting

### Charts not loading
- Check if Chart.js CDN is accessible
- Verify canvas elements exist in HTML
- Check browser console for errors

### Login not working
- Check localStorage is enabled
- Verify API endpoint responses
- Check browser console for errors

### Real-time updates not working
- Verify SSE endpoint is running
- Check browser support for EventSource
- Monitor connection status indicator

## Screenshots

### Login Page
![Login](https://github.com/user-attachments/assets/f7314319-0121-4e7f-9a8f-ac16cdaa2ab1)

### Register Page
![Register](https://github.com/user-attachments/assets/f3c26622-30f5-40fc-a991-dd31a84d4753)

### Manager Dashboard
Complete dashboard with metrics, charts, and real-time updates.

### Employee Management
![Employees](https://github.com/user-attachments/assets/9948c79e-ee19-4a7c-aa50-b81ce5a1e2a9)

### Employee Dashboard
Personal task management with progress tracking and timesheet submission.

## License

Part of the Time & Resource Allocation System - Final Year Project

---

For backend API documentation, see `routes/api.py` and `routes/websocket.py`.
