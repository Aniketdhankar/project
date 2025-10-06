"""
Unit tests for API endpoints
"""

import json
import pytest


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_login_success(self, client):
        """Test successful login"""
        response = client.post('/api/auth/login',
                              data=json.dumps({
                                  'username': 'alice@example.com',
                                  'password': 'password123'
                              }),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data
        assert 'user' in data
        assert data['user']['email'] == 'alice@example.com'
    
    def test_login_missing_credentials(self, client):
        """Test login with missing credentials"""
        response = client.post('/api/auth/login',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_login_no_body(self, client):
        """Test login without request body"""
        response = client.post('/api/auth/login',
                              content_type='application/json')
        
        assert response.status_code == 400


class TestEmployeeEndpoints:
    """Test employee endpoints"""
    
    def test_list_employees(self, client):
        """Test listing all employees"""
        response = client.get('/api/employees/')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'employees' in data
        assert 'page' in data
        assert 'total' in data
        assert isinstance(data['employees'], list)
    
    def test_list_employees_with_filters(self, client):
        """Test listing employees with filters"""
        response = client.get('/api/employees/?department=Engineering&availability_status=available')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'employees' in data
    
    def test_get_employee_detail(self, client):
        """Test getting employee details"""
        response = client.get('/api/employees/1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'employee_id' in data
        assert data['employee_id'] == 1
        assert 'name' in data
        assert 'active_assignments' in data


class TestTaskEndpoints:
    """Test task endpoints"""
    
    def test_create_task(self, client):
        """Test creating a new task"""
        response = client.post('/api/tasks/',
                              data=json.dumps({
                                  'title': 'Test Task',
                                  'priority': 'high',
                                  'estimated_hours': 16
                              }),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'task_id' in data
        assert data['title'] == 'Test Task'
        assert data['priority'] == 'high'
        assert 'message' in data
    
    def test_create_task_missing_title(self, client):
        """Test creating task without title"""
        response = client.post('/api/tasks/',
                              data=json.dumps({
                                  'priority': 'high'
                              }),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_update_task(self, client):
        """Test updating a task"""
        response = client.put('/api/tasks/1',
                             data=json.dumps({
                                 'title': 'Updated Task',
                                 'status': 'in_progress'
                             }),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['task_id'] == 1
        assert 'message' in data


class TestSchedulerEndpoints:
    """Test scheduler endpoints"""
    
    def test_run_scheduler(self, client):
        """Test running the scheduler"""
        response = client.post('/api/scheduler/run',
                              data=json.dumps({
                                  'project_id': 1,
                                  'method': 'balanced'
                              }),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'assignments_created' in data
        assert 'method' in data
        assert data['method'] == 'balanced'
    
    def test_run_scheduler_invalid_method(self, client):
        """Test scheduler with invalid method"""
        response = client.post('/api/scheduler/run',
                              data=json.dumps({
                                  'project_id': 1,
                                  'method': 'invalid_method'
                              }),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestAssignmentEndpoints:
    """Test assignment endpoints"""
    
    def test_finalize_assignments(self, client):
        """Test finalizing assignments"""
        response = client.post('/api/assignments/finalize',
                              data=json.dumps({
                                  'assignment_ids': [1, 2, 3],
                                  'notify_employees': True
                              }),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'finalized_count' in data
        assert 'assignments' in data
    
    def test_finalize_assignments_missing_params(self, client):
        """Test finalizing without required params"""
        response = client.post('/api/assignments/finalize',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_get_employee_assignments(self, client):
        """Test getting employee assignments"""
        response = client.get('/api/assignments/employee/1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'employee_id' in data
        assert data['employee_id'] == 1
        assert 'assignments' in data
        assert isinstance(data['assignments'], list)
    
    def test_get_employee_assignments_with_filters(self, client):
        """Test getting employee assignments with filters"""
        response = client.get('/api/assignments/employee/1?status=in_progress')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'assignments' in data


class TestTimesheetEndpoints:
    """Test timesheet endpoints"""
    
    def test_log_timesheet(self, client):
        """Test logging timesheet"""
        response = client.post('/api/timesheets/',
                              data=json.dumps({
                                  'task_id': 1,
                                  'employee_id': 1,
                                  'hours_spent': 4.5,
                                  'progress_percentage': 65
                              }),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'log_id' in data
        assert data['task_id'] == 1
        assert data['employee_id'] == 1
        assert data['hours_spent'] == 4.5
        assert 'message' in data
    
    def test_log_timesheet_missing_required(self, client):
        """Test logging timesheet without required fields"""
        response = client.post('/api/timesheets/',
                              data=json.dumps({
                                  'hours_spent': 4.5
                              }),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_log_timesheet_invalid_progress(self, client):
        """Test logging timesheet with invalid progress percentage"""
        response = client.post('/api/timesheets/',
                              data=json.dumps({
                                  'task_id': 1,
                                  'employee_id': 1,
                                  'progress_percentage': 150
                              }),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestDashboardEndpoints:
    """Test dashboard endpoints"""
    
    def test_get_dashboard_metrics(self, client):
        """Test getting dashboard metrics"""
        response = client.get('/api/dashboard/1/metrics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'project_id' in data
        assert data['project_id'] == 1
        assert 'total_tasks' in data
        assert 'completed_tasks' in data
        assert 'avg_utilization' in data
        assert 'recent_activity' in data
    
    def test_export_csv(self, client):
        """Test exporting CSV report"""
        response = client.get('/api/dashboard/1/export?format=csv')
        
        assert response.status_code == 200
        assert response.content_type == 'text/csv; charset=utf-8'
        assert b'task_id' in response.data  # Check for CSV header
    
    def test_export_json(self, client):
        """Test exporting JSON report"""
        response = client.get('/api/dashboard/1/export?format=json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'project_id' in data
        assert 'tasks' in data
        assert isinstance(data['tasks'], list)
    
    def test_export_invalid_format(self, client):
        """Test export with invalid format"""
        response = client.get('/api/dashboard/1/export?format=xml')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test API health check"""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_index(self, client):
        """Test index endpoint"""
        response = client.get('/')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'name' in data
        assert 'status' in data
        assert data['status'] == 'running'
