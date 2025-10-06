# API Tests

This directory contains unit tests for the Flask API endpoints.

## Test Coverage

The test suite covers all major endpoints:

- **Authentication** (`test_api_endpoints.py::TestAuthEndpoints`)
  - Login with valid credentials
  - Login with missing credentials
  - Login without request body

- **Employees** (`test_api_endpoints.py::TestEmployeeEndpoints`)
  - List all employees
  - List employees with filters
  - Get employee details

- **Tasks** (`test_api_endpoints.py::TestTaskEndpoints`)
  - Create new task
  - Create task with missing title
  - Update existing task

- **Scheduler** (`test_api_endpoints.py::TestSchedulerEndpoints`)
  - Run scheduler with valid method
  - Run scheduler with invalid method

- **Assignments** (`test_api_endpoints.py::TestAssignmentEndpoints`)
  - Finalize assignments
  - Finalize without required parameters
  - Get employee assignments
  - Get employee assignments with filters

- **Timesheets** (`test_api_endpoints.py::TestTimesheetEndpoints`)
  - Log timesheet with valid data
  - Log timesheet with missing fields
  - Log timesheet with invalid progress percentage

- **Dashboard** (`test_api_endpoints.py::TestDashboardEndpoints`)
  - Get dashboard metrics
  - Export CSV report
  - Export JSON report
  - Export with invalid format

- **Health Check** (`test_api_endpoints.py::TestHealthCheck`)
  - API health check
  - Index endpoint

## Running Tests

### Run all tests
```bash
cd backend
python3 -m pytest tests/
```

### Run specific test file
```bash
python3 -m pytest tests/test_api_endpoints.py
```

### Run with verbose output
```bash
python3 -m pytest tests/ -v
```

### Run specific test class
```bash
python3 -m pytest tests/test_api_endpoints.py::TestAuthEndpoints
```

### Run specific test method
```bash
python3 -m pytest tests/test_api_endpoints.py::TestAuthEndpoints::test_login_success
```

### Run with coverage
```bash
pip install pytest-cov
python3 -m pytest tests/ --cov=routes --cov-report=html
```

## Test Results

All 24 tests pass successfully:

```
======================== 24 passed, 10 warnings in 0.27s ========================
```

## Adding New Tests

When adding new endpoints:

1. Add test class to `test_api_endpoints.py`
2. Follow naming convention: `TestXXXEndpoints`
3. Test both success and failure cases
4. Validate response structure and status codes

Example:
```python
class TestNewEndpoints:
    """Test new endpoints"""
    
    def test_success_case(self, client):
        """Test successful request"""
        response = client.get('/api/new/endpoint')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'expected_field' in data
    
    def test_error_case(self, client):
        """Test error handling"""
        response = client.get('/api/new/endpoint?invalid=param')
        assert response.status_code == 400
```

## Notes

- Tests use placeholder data (no actual database)
- Tests run in isolation using Flask's test client
- Database integration tests should be added separately
- Consider adding integration tests when database is connected
