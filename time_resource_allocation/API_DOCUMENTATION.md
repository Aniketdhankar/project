# API Documentation

## Overview
RESTful API endpoints for the Time & Resource Allocation System. Supports authentication, employee management, task management, scheduling, assignments, timesheet logging, and dashboard metrics.

**Base URL:** `http://localhost:5000/api`

---

## Authentication

### POST /api/auth/login
User login endpoint with JWT/session management.

**Request Body:**
```json
{
  "username": "alice@example.com",
  "password": "password123"
}
```

**Response:** `200 OK`
```json
{
  "token": "jwt_token_string",
  "user": {
    "employee_id": 1,
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "role": "manager"
  },
  "expires_at": "2024-01-21T18:00:00"
}
```

**Error Responses:**
- `400 Bad Request` - Missing username or password
- `401 Unauthorized` - Invalid credentials
- `500 Internal Server Error` - Authentication failed

---

## Employees

### GET /api/employees
List all employees with optional filtering.

**Query Parameters:**
- `department` (string, optional) - Filter by department
- `availability_status` (string, optional) - Filter by status: `available`, `busy`, `on_leave`
- `skill` (string, optional) - Filter by skill keyword
- `page` (int, optional, default=1) - Page number
- `per_page` (int, optional, default=20) - Results per page

**Response:** `200 OK`
```json
{
  "employees": [
    {
      "employee_id": 1,
      "name": "Alice Johnson",
      "email": "alice@example.com",
      "role": "Senior Developer",
      "department": "Engineering",
      "skills": "Python,Flask,React,ML",
      "experience_years": 5.5,
      "current_workload": 32,
      "max_workload": 40,
      "availability_status": "available",
      "performance_rating": 4.5
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 10
}
```

### GET /api/employees/{id}
Get detailed information about a specific employee.

**Path Parameters:**
- `id` (int, required) - Employee ID

**Response:** `200 OK`
```json
{
  "employee_id": 1,
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "role": "Senior Developer",
  "department": "Engineering",
  "skills": "Python,Flask,React,ML",
  "experience_years": 5.5,
  "current_workload": 32,
  "max_workload": 40,
  "availability_status": "available",
  "performance_rating": 4.5,
  "active_assignments": [
    {
      "assignment_id": 1,
      "task_id": 1,
      "task_title": "Implement User Authentication",
      "status": "in_progress",
      "progress": 45,
      "assigned_at": "2024-01-15T10:00:00",
      "estimated_completion": "2024-01-22T17:00:00"
    }
  ],
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2024-01-15T12:00:00"
}
```

**Error Responses:**
- `404 Not Found` - Employee not found
- `500 Internal Server Error` - Server error

---

## Tasks

### POST /api/tasks
Create a new task.

**Request Body:**
```json
{
  "title": "Implement Feature X",
  "description": "Detailed description of the task",
  "required_skills": "Python,Flask,SQL",
  "priority": "high",
  "estimated_hours": 16.0,
  "deadline": "2024-01-30T17:00:00",
  "project_id": 1,
  "dependencies": "task_1,task_2"
}
```

**Response:** `201 Created`
```json
{
  "task_id": 100,
  "title": "Implement Feature X",
  "description": "Detailed description of the task",
  "required_skills": "Python,Flask,SQL",
  "priority": "high",
  "estimated_hours": 16.0,
  "deadline": "2024-01-30T17:00:00",
  "project_id": 1,
  "status": "pending",
  "created_at": "2024-01-20T10:00:00",
  "message": "Task created successfully"
}
```

**Priority Values:** `low`, `medium`, `high`, `critical`

**Error Responses:**
- `400 Bad Request` - Missing required fields
- `500 Internal Server Error` - Server error

### PUT /api/tasks/{id}
Update an existing task.

**Path Parameters:**
- `id` (int, required) - Task ID

**Request Body:**
```json
{
  "title": "Updated Task Title",
  "description": "Updated description",
  "status": "in_progress",
  "priority": "critical",
  "estimated_hours": 20.0,
  "deadline": "2024-01-25T17:00:00"
}
```

**Response:** `200 OK`
```json
{
  "task_id": 100,
  "title": "Updated Task Title",
  "description": "Updated description",
  "status": "in_progress",
  "priority": "critical",
  "estimated_hours": 20.0,
  "deadline": "2024-01-25T17:00:00",
  "updated_at": "2024-01-20T11:00:00",
  "message": "Task updated successfully"
}
```

**Status Values:** `pending`, `assigned`, `in_progress`, `completed`

**Error Responses:**
- `400 Bad Request` - Invalid request
- `404 Not Found` - Task not found
- `500 Internal Server Error` - Server error

---

## Scheduler

### POST /api/scheduler/run
Run the auto-assignment scheduler for a project.

**Request Body:**
```json
{
  "project_id": 1,
  "method": "balanced",
  "include_gemini": false,
  "force_reassign": false
}
```

**Method Values:** `greedy`, `hungarian`, `balanced`

**Response:** `200 OK`
```json
{
  "status": "success",
  "message": "Scheduler executed successfully",
  "project_id": 1,
  "assignments_created": 5,
  "assignments_updated": 2,
  "execution_time": 1.25,
  "method": "balanced",
  "gemini_enabled": false,
  "timestamp": "2024-01-20T12:00:00"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid method
- `500 Internal Server Error` - Scheduler execution failed

---

## Assignments

### POST /api/assignments/finalize
Persist and finalize pending assignments.

**Request Body:**
```json
{
  "assignment_ids": [1, 2, 3],
  "project_id": 1,
  "notify_employees": true
}
```

**Response:** `200 OK`
```json
{
  "status": "success",
  "message": "Assignments finalized successfully",
  "finalized_count": 3,
  "assignments": [
    {
      "assignment_id": 1,
      "status": "assigned",
      "assigned_at": "2024-01-20T12:30:00"
    }
  ],
  "notifications_sent": true
}
```

**Error Responses:**
- `400 Bad Request` - Missing required fields
- `500 Internal Server Error` - Server error

### GET /api/assignments/employee/{id}
Get all tasks assigned to a specific employee.

**Path Parameters:**
- `id` (int, required) - Employee ID

**Query Parameters:**
- `status` (string, optional) - Filter by status: `assigned`, `in_progress`, `completed`
- `project_id` (int, optional) - Filter by project

**Response:** `200 OK`
```json
{
  "employee_id": 1,
  "employee_name": "Alice Johnson",
  "assignments": [
    {
      "assignment_id": 1,
      "task_id": 1,
      "task_title": "Implement User Authentication",
      "task_description": "Build JWT-based authentication system",
      "status": "in_progress",
      "priority": "high",
      "assigned_at": "2024-01-15T10:00:00",
      "started_at": "2024-01-15T14:00:00",
      "estimated_completion": "2024-01-22T17:00:00",
      "estimated_hours": 16.0,
      "progress": 45,
      "project_id": 1
    }
  ],
  "total_assignments": 2,
  "total_hours": 28.0
}
```

**Error Responses:**
- `404 Not Found` - Employee not found
- `500 Internal Server Error` - Server error

---

## Timesheets

### POST /api/timesheets
Log timesheet/progress for a task.

**Request Body:**
```json
{
  "task_id": 1,
  "employee_id": 1,
  "hours_spent": 4.5,
  "progress_percentage": 65.0,
  "status_update": "in_progress",
  "blockers": "Waiting for API documentation",
  "notes": "Completed authentication module",
  "date": "2024-01-20"
}
```

**Response:** `201 Created`
```json
{
  "log_id": 150,
  "task_id": 1,
  "employee_id": 1,
  "hours_spent": 4.5,
  "progress_percentage": 65.0,
  "status_update": "in_progress",
  "blockers": "Waiting for API documentation",
  "notes": "Completed authentication module",
  "logged_at": "2024-01-20T14:30:00",
  "message": "Progress logged successfully"
}
```

**Validation:**
- `progress_percentage` must be between 0 and 100

**Error Responses:**
- `400 Bad Request` - Missing required fields or invalid values
- `404 Not Found` - Task or employee not found
- `500 Internal Server Error` - Server error

---

## Dashboard

### GET /api/dashboard/{project_id}/metrics
Fetch dashboard metrics for a specific project.

**Path Parameters:**
- `project_id` (int, required) - Project ID

**Response:** `200 OK`
```json
{
  "project_id": 1,
  "project_name": "Resource Allocation System",
  "total_tasks": 25,
  "completed_tasks": 12,
  "in_progress_tasks": 8,
  "pending_tasks": 5,
  "total_employees": 10,
  "active_employees": 5,
  "avg_utilization": 75.5,
  "completion_rate": 48.0,
  "on_time_rate": 83.3,
  "overdue_tasks": 2,
  "at_risk_tasks": 3,
  "total_hours_estimated": 450.0,
  "total_hours_spent": 285.5,
  "efficiency_rate": 92.5,
  "recent_activity": [
    {
      "activity_type": "task_completed",
      "task_title": "Implement User Authentication",
      "employee_name": "Alice Johnson",
      "timestamp": "2024-01-20T15:30:00"
    }
  ],
  "task_distribution": {
    "by_priority": {
      "critical": 3,
      "high": 7,
      "medium": 10,
      "low": 5
    },
    "by_status": {
      "completed": 12,
      "in_progress": 8,
      "pending": 5
    }
  }
}
```

**Error Responses:**
- `404 Not Found` - Project not found
- `500 Internal Server Error` - Server error

### GET /api/dashboard/{project_id}/export
Export project report in CSV or JSON format.

**Path Parameters:**
- `project_id` (int, required) - Project ID

**Query Parameters:**
- `format` (string, optional, default=csv) - Export format: `csv` or `json`

**Response (CSV):** `200 OK`
```
Content-Type: text/csv
Content-Disposition: attachment; filename=project_1_report_20240120.csv

task_id,task_title,description,status,priority,assigned_to,employee_email,estimated_hours,actual_hours,progress,deadline,completed_at
1,Implement User Authentication,Build JWT-based auth,completed,high,Alice Johnson,alice@example.com,16.0,14.5,100,2024-01-22T17:00:00,2024-01-20T15:30:00
...
```

**Response (JSON):** `200 OK`
```json
{
  "project_id": 1,
  "exported_at": "2024-01-20T16:00:00",
  "total_tasks": 25,
  "tasks": [
    {
      "task_id": 1,
      "task_title": "Implement User Authentication",
      "description": "Build JWT-based auth",
      "status": "completed",
      "priority": "high",
      "assigned_to": "Alice Johnson",
      "employee_email": "alice@example.com",
      "estimated_hours": 16.0,
      "actual_hours": 14.5,
      "progress": 100,
      "deadline": "2024-01-22T17:00:00",
      "completed_at": "2024-01-20T15:30:00"
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request` - Invalid format parameter
- `404 Not Found` - Project not found
- `500 Internal Server Error` - Server error

---

## Error Handling

All endpoints follow a consistent error response format:

```json
{
  "error": "Error message description"
}
```

### HTTP Status Codes
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters or body
- `401 Unauthorized` - Authentication required or failed
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Data Types

### Date/Time Format
All timestamps use ISO 8601 format: `YYYY-MM-DDTHH:mm:ss`

Example: `2024-01-20T15:30:00`

### Numeric Types
- `int` - Integer numbers
- `float` - Decimal numbers (e.g., 16.5)

### Enums

**Priority:** `low`, `medium`, `high`, `critical`

**Task Status:** `pending`, `assigned`, `in_progress`, `completed`

**Employee Availability:** `available`, `busy`, `on_leave`

**Assignment Method:** `greedy`, `hungarian`, `balanced`

---

## Authentication

Most endpoints require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

Currently, authentication is implemented with placeholder responses. For production:
1. Use JWT tokens for stateless authentication
2. Implement token refresh mechanism
3. Add role-based access control (RBAC)

---

## Rate Limiting

Currently, no rate limiting is implemented. For production deployment, consider:
- API rate limiting per user/IP
- Request throttling for expensive operations
- Implement caching for frequently accessed data

---

## Next Steps

1. **Database Integration:** Replace placeholder responses with actual SQLAlchemy queries
2. **JWT Implementation:** Implement proper JWT token generation and validation
3. **Validation:** Add comprehensive input validation using libraries like marshmallow or pydantic
4. **Testing:** Implement unit and integration tests
5. **Documentation:** Consider adding Swagger/OpenAPI specification
6. **Error Handling:** Implement more detailed error messages and logging
7. **Pagination:** Standardize pagination across all list endpoints
8. **Search:** Add full-text search capabilities for tasks and employees

---

## Testing with cURL

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice@example.com","password":"password123"}'
```

### List Employees
```bash
curl http://localhost:5000/api/employees
```

### Create Task
```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"New Task","priority":"high","estimated_hours":16}'
```

### Run Scheduler
```bash
curl -X POST http://localhost:5000/api/scheduler/run \
  -H "Content-Type: application/json" \
  -d '{"project_id":1,"method":"balanced"}'
```

### Log Timesheet
```bash
curl -X POST http://localhost:5000/api/timesheets \
  -H "Content-Type: application/json" \
  -d '{"task_id":1,"employee_id":1,"hours_spent":4.5,"progress_percentage":65}'
```

### Get Dashboard Metrics
```bash
curl http://localhost:5000/api/dashboard/1/metrics
```

### Export CSV
```bash
curl http://localhost:5000/api/dashboard/1/export?format=csv -o report.csv
```
