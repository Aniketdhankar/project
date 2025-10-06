# Database Integration Guide

## Overview

This guide explains how to integrate the Scheduler Service with the PostgreSQL database for production use.

## Database Schema

The scheduler uses the following tables:

### Task_Assignments

Stores finalized task assignments:

```sql
CREATE TABLE Task_Assignments (
    assignment_id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES Tasks(task_id),
    employee_id INTEGER REFERENCES Employees(employee_id),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_completion TIMESTAMP,
    actual_hours DECIMAL(6,2),
    assignment_method VARCHAR(50),  -- 'greedy_ml', 'balanced_ml'
    assignment_score DECIMAL(5,4),
    status VARCHAR(50) DEFAULT 'assigned',
    notes TEXT
);
```

### ML_Training_Data (Recommended)

Store training data for continuous model improvement:

```sql
CREATE TABLE ML_Training_Data (
    log_id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES Tasks(task_id),
    employee_id INTEGER REFERENCES Employees(employee_id),
    features JSONB,  -- Feature vector
    feature_names JSONB,  -- Feature name mapping
    assignment_score DECIMAL(5,4),
    confidence DECIMAL(5,4),
    method VARCHAR(50),
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    outcome VARCHAR(50),  -- 'success', 'failure', 'pending'
    actual_completion_time DECIMAL(6,2)
);
```

## Implementation

### 1. Update scheduler_service.py

Replace the placeholder `_store_assignments` method:

```python
def _store_assignments(
    self,
    assignments: List[Dict],
    database_connection
) -> int:
    """Store assignments in database"""
    from models.models import db, TaskAssignment
    
    stored_count = 0
    
    try:
        for assignment in assignments:
            # Create TaskAssignment record
            ta = TaskAssignment(
                task_id=assignment['task_id'],
                employee_id=assignment['employee_id'],
                assignment_method=assignment['assignment_method'],
                assignment_score=assignment['assignment_score'],
                status='assigned',
                notes=f"Confidence: {assignment.get('confidence', 0):.3f}"
            )
            
            db.session.add(ta)
            stored_count += 1
        
        # Commit all assignments
        db.session.commit()
        logger.info(f"Stored {stored_count} assignments in database")
        
        return stored_count
        
    except Exception as e:
        logger.error(f"Error storing assignments: {e}")
        db.session.rollback()
        return 0
```

### 2. Update training data logging

Replace the placeholder `_log_training_data` method:

```python
def _log_training_data(
    self,
    assignments: List[Dict],
    database_connection
) -> None:
    """Log assignment and feature data for ML training"""
    from models.models import db
    import json
    
    try:
        for assignment in assignments:
            features = assignment.get('features', [])
            feature_names = self.ml_service.get_feature_names()
            
            # Using raw SQL for JSONB
            query = """
            INSERT INTO ML_Training_Data 
            (task_id, employee_id, features, feature_names, 
             assignment_score, confidence, method, logged_at, outcome)
            VALUES (:task_id, :employee_id, :features, :feature_names,
                    :score, :confidence, :method, NOW(), 'pending')
            """
            
            db.session.execute(
                query,
                {
                    'task_id': assignment['task_id'],
                    'employee_id': assignment['employee_id'],
                    'features': json.dumps(features),
                    'feature_names': json.dumps(feature_names),
                    'score': assignment['assignment_score'],
                    'confidence': assignment.get('confidence', 0.0),
                    'method': assignment['assignment_method']
                }
            )
        
        db.session.commit()
        logger.info(f"Logged training data for {len(assignments)} assignments")
        
    except Exception as e:
        logger.error(f"Error logging training data: {e}")
        db.session.rollback()
```

### 3. Fetch tasks and employees from database

In `routes/api.py`, replace sample data with database queries:

```python
@api.route('/trigger_pipeline', methods=['POST'])
def trigger_pipeline():
    try:
        from scheduler_service import get_scheduler_service
        from models.models import Task, Employee, db
        
        data = request.get_json() or {}
        method = data.get('method', 'greedy_ml')
        include_gemini = data.get('include_gemini', False)
        max_assignments = data.get('max_assignments_per_employee', 5)
        preview_only = data.get('preview_only', False)
        
        # Fetch pending tasks from database
        tasks = [
            t.to_dict() 
            for t in Task.query.filter_by(status='pending').all()
        ]
        
        # Fetch available employees from database
        employees = [
            e.to_dict() 
            for e in Employee.query.filter_by(availability_status='available').all()
        ]
        
        if not tasks:
            return jsonify({
                'status': 'success',
                'message': 'No pending tasks to assign'
            }), 200
        
        if not employees:
            return jsonify({
                'status': 'error',
                'message': 'No available employees'
            }), 400
        
        # Get scheduler service
        scheduler = get_scheduler_service()
        
        # Prepare constraints
        constraints = {
            'max_assignments_per_employee': max_assignments,
            'include_gemini': include_gemini
        }
        
        if preview_only:
            # Generate preview only
            preview = scheduler.preview_assignments(
                tasks, employees, constraints, method
            )
            
            result = {
                'status': 'success',
                'message': 'Assignment preview generated',
                'preview': preview,
                'timestamp': datetime.now().isoformat()
            }
        else:
            # Generate and finalize assignments
            preview = scheduler.preview_assignments(
                tasks, employees, constraints, method
            )
            
            # Pass database connection
            finalized = scheduler.finalize_assignments(
                preview['preview_id'],
                database_connection=db
            )
            
            # Update task statuses
            for assignment in preview['assignments']:
                task = Task.query.get(assignment['task_id'])
                if task:
                    task.status = 'assigned'
            
            db.session.commit()
            
            result = {
                'status': 'success',
                'message': 'Pipeline completed successfully',
                'finalized': finalized,
                'timestamp': datetime.now().isoformat()
            }
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error triggering pipeline: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
```

## Configuration

### Database Connection

Ensure your `config/config.py` has the database URL:

```python
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost:5432/time_allocation'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### Environment Variables

Create `.env` file:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/time_allocation
GEMINI_API_KEY=your_gemini_api_key  # Optional
```

## Testing with Database

### 1. Setup Test Database

```bash
# Create test database
createdb time_allocation_test

# Run schema
psql -d time_allocation_test -f database/schema.sql
```

### 2. Run Integration Tests

```python
import pytest
from models.models import db, Task, Employee, TaskAssignment

@pytest.fixture
def app():
    from app import create_app
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_scheduler_with_database(app):
    with app.app_context():
        # Create test data
        emp = Employee(
            name='Test Employee',
            email='test@example.com',
            skills='Python,Flask',
            experience_years=5.0,
            max_workload=40
        )
        db.session.add(emp)
        
        task = Task(
            title='Test Task',
            required_skills='Python',
            priority='high',
            estimated_hours=10
        )
        db.session.add(task)
        db.session.commit()
        
        # Run scheduler
        from scheduler_service import get_scheduler_service
        scheduler = get_scheduler_service()
        
        assignments = scheduler.assign_tasks(
            tasks=[task.to_dict()],
            employees=[emp.to_dict()],
            method='greedy_ml'
        )
        
        # Finalize with database
        preview = scheduler.preview_assignments(
            [task.to_dict()],
            [emp.to_dict()]
        )
        scheduler.finalize_assignments(preview['preview_id'], db)
        
        # Verify in database
        assignment = TaskAssignment.query.first()
        assert assignment is not None
        assert assignment.task_id == task.task_id
        assert assignment.employee_id == emp.employee_id
```

## Monitoring and Maintenance

### 1. Track Assignment Success

```sql
-- View assignment success rate
SELECT 
    assignment_method,
    COUNT(*) as total,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
    ROUND(AVG(assignment_score), 3) as avg_score
FROM Task_Assignments
GROUP BY assignment_method;
```

### 2. Analyze Training Data

```sql
-- Get recent training data for model retraining
SELECT 
    task_id,
    employee_id,
    features,
    assignment_score,
    outcome,
    actual_completion_time
FROM ML_Training_Data
WHERE outcome = 'success'
    AND logged_at > NOW() - INTERVAL '30 days'
ORDER BY logged_at DESC;
```

### 3. Monitor Workload

```sql
-- Check current employee workload
SELECT 
    e.name,
    e.current_workload,
    e.max_workload,
    COUNT(ta.assignment_id) as active_assignments
FROM Employees e
LEFT JOIN Task_Assignments ta 
    ON e.employee_id = ta.employee_id 
    AND ta.status IN ('assigned', 'in_progress')
GROUP BY e.employee_id, e.name, e.current_workload, e.max_workload
ORDER BY e.current_workload DESC;
```

## Performance Optimization

### 1. Add Indexes

```sql
-- Optimize assignment queries
CREATE INDEX idx_task_assignments_method 
    ON Task_Assignments(assignment_method);

CREATE INDEX idx_task_assignments_score 
    ON Task_Assignments(assignment_score DESC);

-- Optimize training data queries
CREATE INDEX idx_ml_training_outcome 
    ON ML_Training_Data(outcome);

CREATE INDEX idx_ml_training_date 
    ON ML_Training_Data(logged_at DESC);
```

### 2. Use Connection Pooling

In `config/config.py`:

```python
class Config:
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
```

### 3. Batch Operations

When storing many assignments:

```python
# Use bulk insert for better performance
db.session.bulk_insert_mappings(
    TaskAssignment,
    [
        {
            'task_id': a['task_id'],
            'employee_id': a['employee_id'],
            'assignment_method': a['assignment_method'],
            'assignment_score': a['assignment_score']
        }
        for a in assignments
    ]
)
db.session.commit()
```

## Troubleshooting

### Connection Issues

```python
# Test database connection
from sqlalchemy import create_engine

engine = create_engine(DATABASE_URL)
try:
    connection = engine.connect()
    print("✓ Database connection successful")
    connection.close()
except Exception as e:
    print(f"✗ Database connection failed: {e}")
```

### Transaction Deadlocks

Use proper isolation levels:

```python
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    isolation_level="READ_COMMITTED"
)
```

### Large Result Sets

Use pagination:

```python
# Fetch tasks in batches
page = 1
per_page = 100

while True:
    tasks = Task.query.filter_by(status='pending')\
        .offset((page - 1) * per_page)\
        .limit(per_page)\
        .all()
    
    if not tasks:
        break
    
    # Process batch
    # ...
    
    page += 1
```

## Migration from Sample Data

If you're migrating from sample data to database:

1. Export existing assignments
2. Create database schema
3. Import historical data
4. Update code to use database
5. Test with small batch
6. Deploy to production

## Best Practices

1. **Always use transactions** for assignment storage
2. **Log errors** for debugging
3. **Monitor database performance** 
4. **Regular backups** of assignment data
5. **Archive old training data** periodically
6. **Use prepared statements** to prevent SQL injection
7. **Validate data** before database insertion

## Support

For database-related issues:
- Check connection string in config
- Verify database schema matches models
- Review database logs
- Check permissions for database user
- Monitor connection pool usage
