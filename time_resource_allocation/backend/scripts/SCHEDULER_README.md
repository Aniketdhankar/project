# Scheduler Service Documentation

## Overview

The Scheduler Service provides intelligent task assignment capabilities using a hybrid approach combining greedy heuristics and ML-based scoring. It integrates scikit-learn and LightGBM models to score (task, employee) pairs for optimal assignment.

## Architecture

### Components

1. **MLService** (`ml_service.py`)
   - Loads and manages ML models
   - Provides `predict_proba` for scoring employee-task pairs
   - Feature engineering utilities
   - Fallback heuristic scoring when ML model unavailable

2. **SchedulerService** (`scheduler_service.py`)
   - Core scheduler logic
   - Multiple assignment algorithms (greedy_ml, balanced_ml)
   - Assignment preview/finalization workflow
   - Training data logging for continuous improvement

## Usage

### Basic Task Assignment

```python
from scheduler_service import get_scheduler_service

# Initialize scheduler
scheduler = get_scheduler_service()

# Prepare data
tasks = [
    {
        'task_id': 1,
        'title': 'Implement Authentication',
        'required_skills': 'Python,Flask,JWT',
        'priority': 'high',
        'estimated_hours': 20,
        'deadline': '2024-02-15',
        'complexity_score': 4.0
    }
]

employees = [
    {
        'employee_id': 1,
        'name': 'Alice Johnson',
        'skills': 'Python,React,PostgreSQL,ML',
        'experience_years': 5.5,
        'current_workload': 20,
        'max_workload': 40,
        'availability_status': 'available',
        'performance_rating': 4.5
    }
]

# Create assignments
assignments = scheduler.assign_tasks(
    tasks=tasks,
    employees=employees,
    constraints={'max_assignments_per_employee': 5},
    method='greedy_ml'
)
```

### Assignment Methods

#### 1. Greedy ML (`greedy_ml`)
Assigns tasks one at a time, selecting the best available employee based on ML scores.

**Characteristics:**
- Fast execution
- Considers priority and deadline ordering
- Respects employee capacity constraints
- Uses ML model for scoring when available

**Best for:**
- Quick assignments
- High-priority tasks need immediate assignment
- Clear skill-match scenarios

#### 2. Balanced ML (`balanced_ml`)
Considers both ML scores and workload distribution to balance assignments.

**Characteristics:**
- Balances workload across team
- Adjusts ML scores based on current workload
- Prevents overloading specific employees
- Configurable workload weight

**Best for:**
- Fair workload distribution
- Long-term project planning
- Preventing burnout

### Preview and Finalization Workflow

```python
# Generate preview
preview = scheduler.preview_assignments(
    tasks=tasks,
    employees=employees,
    constraints={'max_assignments_per_employee': 5},
    method='greedy_ml'
)

# Review preview
print(f"Preview ID: {preview['preview_id']}")
print(f"Assignments: {len(preview['assignments'])}")
print(f"Unassigned: {preview['summary']['unassigned_tasks']}")

# Finalize if acceptable
result = scheduler.finalize_assignments(
    preview_id=preview['preview_id'],
    database_connection=db_conn  # Optional
)
```

### Constraints

Configure assignment behavior with constraints dictionary:

```python
constraints = {
    'max_assignments_per_employee': 5,  # Max tasks per employee
    'include_gemini': False,  # Use Gemini API for features
}
```

## API Endpoints

### 1. Trigger Pipeline

**Endpoint:** `POST /api/trigger_pipeline`

**Request:**
```json
{
    "method": "greedy_ml",
    "include_gemini": false,
    "max_assignments_per_employee": 5,
    "preview_only": false
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Pipeline completed successfully",
    "finalized": {
        "preview_id": "preview_20240202_143022",
        "finalized_at": "2024-02-02T14:30:25.123456",
        "assignments_stored": 10,
        "summary": {
            "total_tasks": 15,
            "total_employees": 5,
            "assignments_created": 10,
            "unassigned_tasks": 5
        }
    },
    "timestamp": "2024-02-02T14:30:25.123456"
}
```

### 2. Preview Assignments

**Endpoint:** `POST /api/assignments/preview`

**Request:**
```json
{
    "tasks": [...],
    "employees": [...],
    "method": "balanced_ml",
    "constraints": {
        "max_assignments_per_employee": 5
    }
}
```

**Response:**
```json
{
    "preview_id": "preview_20240202_143022",
    "created_at": "2024-02-02T14:30:22.123456",
    "method": "balanced_ml",
    "constraints": {...},
    "assignments": [
        {
            "task_id": 1,
            "employee_id": 1,
            "assignment_method": "balanced_ml",
            "assignment_score": 0.87,
            "ml_score": 0.85,
            "confidence": 0.85,
            "task_title": "Implement Authentication",
            "employee_name": "Alice Johnson",
            "estimated_hours": 20,
            "features": [...]
        }
    ],
    "summary": {
        "total_tasks": 15,
        "total_employees": 5,
        "assignments_created": 10,
        "unassigned_tasks": 5
    }
}
```

### 3. Finalize Assignments

**Endpoint:** `POST /api/assignments/finalize/<preview_id>`

**Response:**
```json
{
    "preview_id": "preview_20240202_143022",
    "finalized_at": "2024-02-02T14:30:25.123456",
    "assignments_stored": 10,
    "summary": {...}
}
```

## ML Model Integration

### Model Requirements

The scheduler expects ML models in LightGBM format:

- **Location:** `ml_models/trained/scoring_model.txt`
- **Input:** Feature vector from `feature_builder`
- **Output:** Score between 0 and 1 (higher = better match)

### Feature Engineering

Features are automatically extracted using `FeatureBuilder`:

**Employee Features:**
- Experience years (normalized)
- Workload ratio
- Availability status
- Performance rating
- Active task count

**Task Features:**
- Priority level
- Complexity score
- Estimated hours
- Time until deadline
- Dependency count

**Interaction Features:**
- Skill match score
- Experience-complexity ratio
- Workload capacity fit
- Department match
- Historical success rate

### Fallback Scoring

When ML model is unavailable, the system uses heuristic scoring:

```
Score = 0.4 × skill_match + 0.3 × experience_match + 0.3 × workload_availability
```

## Training Data Logging

The scheduler automatically logs assignment data for model retraining:

**Logged Data:**
- Task and employee IDs
- Feature vectors
- Assignment scores
- Confidence levels
- Method used
- Timestamp

This data can be used to continuously improve the ML model.

## Best Practices

### 1. Regular Model Updates
- Retrain models periodically with new assignment data
- Monitor assignment success rates
- Adjust feature weights based on outcomes

### 2. Constraint Configuration
- Set reasonable `max_assignments_per_employee`
- Consider team size and task volume
- Adjust based on workload patterns

### 3. Preview Before Finalize
- Always review previews for critical assignments
- Check for unassigned tasks
- Verify workload distribution

### 4. Method Selection
- Use `greedy_ml` for urgent, high-priority tasks
- Use `balanced_ml` for regular sprint planning
- Consider team dynamics and preferences

### 5. Monitor Performance
- Track assignment success rates
- Measure task completion times
- Gather team feedback

## Error Handling

The scheduler handles various error conditions:

**No Available Employees:**
- Logs warning
- Skips task assignment
- Returns in unassigned_tasks list

**Capacity Exceeded:**
- Respects max_workload limits
- Skips assignments that would exceed capacity
- Tries alternative employees

**Model Loading Failures:**
- Falls back to heuristic scoring
- Logs warnings
- Continues operation

## Performance Considerations

### Scalability
- ML inference: ~1-5ms per employee-task pair
- Greedy assignment: O(n×m) where n=tasks, m=employees
- Balanced assignment: O(n×m) with workload adjustments

### Optimization Tips
- Limit `top_k` in candidate scoring
- Batch similar tasks
- Cache employee availability
- Use database indexes for queries

## Integration with Existing Systems

### Database Integration

The scheduler integrates with SQLAlchemy models:

```python
from models.models import Task, Employee, TaskAssignment

# Fetch from database
tasks = [t.to_dict() for t in Task.query.filter_by(status='pending').all()]
employees = [e.to_dict() for e in Employee.query.filter_by(availability_status='available').all()]

# Run scheduler
assignments = scheduler.assign_tasks(tasks, employees)

# Store results
for assignment in assignments:
    ta = TaskAssignment(
        task_id=assignment['task_id'],
        employee_id=assignment['employee_id'],
        assignment_method=assignment['assignment_method'],
        assignment_score=assignment['assignment_score']
    )
    db.session.add(ta)
db.session.commit()
```

### Anomaly Detection

After assignment, trigger anomaly detection:

```python
from realtime_detector import get_detector

detector = get_detector()
detector.check_all_assignments()
```

### ETA Prediction

Update ETAs for new assignments:

```python
from eta_predictor import get_eta_predictor

predictor = get_eta_predictor()
for assignment in assignments:
    eta = predictor.predict_eta(
        employee=employees_dict[assignment['employee_id']],
        task=tasks_dict[assignment['task_id']]
    )
    # Update assignment with ETA
```

## Troubleshooting

### Common Issues

**1. No assignments created**
- Check employee availability status
- Verify workload capacity
- Review skill matching
- Check max_assignments constraint

**2. Low assignment scores**
- Retrain ML model with recent data
- Review feature engineering
- Check skill definitions
- Consider adjusting heuristic weights

**3. Unbalanced workload**
- Use `balanced_ml` method
- Adjust workload_weight parameter
- Review max_workload settings
- Check employee availability

**4. Preview not found**
- Previews expire after finalization
- Verify preview_id is correct
- Don't reuse preview IDs

## Future Enhancements

Planned improvements:

1. **Multi-objective optimization**
   - Balance quality, workload, and deadlines
   - Pareto-optimal solutions

2. **Team dynamics**
   - Consider collaboration history
   - Account for team preferences

3. **Learning from feedback**
   - Incorporate assignment outcomes
   - Online learning capabilities

4. **Advanced constraints**
   - Time-based availability
   - Skill development goals
   - Project dependencies

## Support

For issues or questions:
- Review logs in `logs/` directory
- Check model files in `ml_models/trained/`
- Verify database connectivity
- Consult unit tests for usage examples
