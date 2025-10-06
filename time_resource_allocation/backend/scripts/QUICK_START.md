# Quick Start Guide - Scheduler Service

## 5-Minute Setup

### 1. Import and Initialize

```python
from scheduler_service import get_scheduler_service

scheduler = get_scheduler_service()
```

### 2. Prepare Your Data

```python
# Tasks to assign
tasks = [
    {
        'task_id': 1,
        'title': 'Implement Authentication',
        'required_skills': 'Python,Flask,JWT',
        'priority': 'high',  # low, medium, high, critical
        'estimated_hours': 20,
        'deadline': '2024-02-15',
        'complexity_score': 4.0  # 1-5 scale
    }
]

# Available employees
employees = [
    {
        'employee_id': 1,
        'name': 'Alice Johnson',
        'skills': 'Python,React,PostgreSQL',
        'experience_years': 5.5,
        'current_workload': 20,
        'max_workload': 40,
        'availability_status': 'available',
        'performance_rating': 4.5
    }
]
```

### 3. Run Assignment

```python
# Simple assignment
assignments = scheduler.assign_tasks(
    tasks=tasks,
    employees=employees,
    method='greedy_ml'  # or 'balanced_ml'
)

# View results
for a in assignments:
    print(f"{a['task_title']} → {a['employee_name']}")
    print(f"Score: {a['assignment_score']:.3f}")
```

### 4. Using Preview/Finalize (Recommended)

```python
# Generate preview
preview = scheduler.preview_assignments(
    tasks=tasks,
    employees=employees,
    method='greedy_ml'
)

# Review preview
print(f"Assignments: {len(preview['assignments'])}")
print(f"Unassigned: {preview['summary']['unassigned_tasks']}")

# Finalize if acceptable
result = scheduler.finalize_assignments(
    preview_id=preview['preview_id']
)
print(f"Stored: {result['assignments_stored']} assignments")
```

## Common Use Cases

### Case 1: Quick Assignment

When you need immediate assignments:

```python
assignments = scheduler.assign_tasks(tasks, employees, method='greedy_ml')
```

### Case 2: Balanced Workload

When fairness matters:

```python
assignments = scheduler.assign_tasks(tasks, employees, method='balanced_ml')
```

### Case 3: With Constraints

Limit tasks per employee:

```python
constraints = {'max_assignments_per_employee': 3}
assignments = scheduler.assign_tasks(
    tasks, employees, constraints, 'greedy_ml'
)
```

### Case 4: Preview Before Commit

Review before finalizing:

```python
preview = scheduler.preview_assignments(tasks, employees)
# Review and approve...
scheduler.finalize_assignments(preview['preview_id'])
```

## Via REST API

### Trigger Assignment

```bash
curl -X POST http://localhost:5000/api/trigger_pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "method": "greedy_ml",
    "max_assignments_per_employee": 5,
    "preview_only": false
  }'
```

### Preview Only

```bash
curl -X POST http://localhost:5000/api/trigger_pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "method": "balanced_ml",
    "preview_only": true
  }'
```

### Custom Preview

```bash
curl -X POST http://localhost:5000/api/assignments/preview \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [...],
    "employees": [...],
    "method": "greedy_ml"
  }'
```

### Finalize Preview

```bash
curl -X POST http://localhost:5000/api/assignments/finalize/preview_20240202_143022
```

## Assignment Methods Comparison

| Method | Speed | Fairness | Use Case |
|--------|-------|----------|----------|
| **greedy_ml** | Fast | Lower | Urgent tasks, clear priorities |
| **balanced_ml** | Medium | Higher | Regular planning, team balance |

## Key Parameters

### Required Task Fields
- `task_id`: Unique identifier
- `title`: Task name
- `required_skills`: Comma-separated skills
- `priority`: low, medium, high, or critical
- `estimated_hours`: Time estimate
- `complexity_score`: 1-5 difficulty rating

### Required Employee Fields
- `employee_id`: Unique identifier
- `name`: Employee name
- `skills`: Comma-separated skills
- `experience_years`: Years of experience
- `current_workload`: Current hours assigned
- `max_workload`: Maximum capacity
- `availability_status`: 'available' or 'on_leave'

### Optional Fields
- `deadline` (task): ISO date string
- `performance_rating` (employee): 0-5 rating
- `department` (both): For department matching
- `dependencies` (task): Task dependencies

## Scoring Explained

Each assignment gets:
- **Score** (0-1): Match quality (higher is better)
- **Confidence** (0-1): Prediction confidence

Score factors:
- Skill match (40%)
- Experience vs complexity (30%)
- Workload availability (30%)

## Common Issues

### No Assignments Created

**Cause:** No available employees or capacity
**Fix:** Check:
- Employee `availability_status` is 'available'
- `current_workload + estimated_hours <= max_workload`
- `max_assignments_per_employee` not exceeded

### Low Scores

**Cause:** Poor skill match
**Fix:**
- Verify skill definitions match
- Check employee experience levels
- Consider training or hiring

### Unbalanced Assignments

**Cause:** Using greedy_ml
**Fix:** Use `balanced_ml` method instead

## Best Practices

1. **Use preview mode** for important assignments
2. **Check unassigned tasks** in results
3. **Monitor assignment scores** (aim for >0.7)
4. **Adjust constraints** based on team capacity
5. **Review regularly** and retrain models

## Next Steps

- Read [SCHEDULER_README.md](SCHEDULER_README.md) for details
- Review [DATABASE_INTEGRATION.md](DATABASE_INTEGRATION.md) for production
- Run [example_scheduler_usage.py](example_scheduler_usage.py) for demos
- Check unit tests for more examples

## Support

- Check logs in `logs/` directory
- Review test cases for examples
- Verify ML models in `ml_models/trained/`
- Ensure database connection works

## Quick Troubleshooting

```python
# Test ML service
from ml_service import get_ml_service
ml = get_ml_service()
print("ML Service OK")

# Test scheduler
from scheduler_service import get_scheduler_service
scheduler = get_scheduler_service()
print("Scheduler OK")

# Test assignment
result = scheduler.assign_tasks(
    tasks=[{...}],
    employees=[{...}]
)
print(f"Assigned: {len(result)} tasks")
```

## Integration Checklist

- [ ] ML models in `ml_models/trained/`
- [ ] Database schema matches models
- [ ] Employee data has required fields
- [ ] Task data has required fields
- [ ] Constraints configured appropriately
- [ ] Preview workflow tested
- [ ] Error handling verified
- [ ] Logging configured
- [ ] Monitoring in place

---

**Ready to use!** Start with the basic example above and expand as needed.
