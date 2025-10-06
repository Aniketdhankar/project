# Scheduler Service Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLIENT / FRONTEND                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK API LAYER                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  POST /api/trigger_pipeline                              │   │
│  │  POST /api/assignments/preview                           │   │
│  │  POST /api/assignments/finalize/<id>                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SCHEDULER SERVICE LAYER                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              SchedulerService                            │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  • assign_tasks()                                  │  │   │
│  │  │  • preview_assignments()                           │  │   │
│  │  │  • finalize_assignments()                          │  │   │
│  │  │  • _greedy_ml_assignment()                         │  │   │
│  │  │  • _balanced_ml_assignment()                       │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └────────────────────────┬─────────────────────────────────┘   │
└───────────────────────────┼─────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────────────┐            ┌──────────────────────┐
│   ML SERVICE LAYER   │            │  DATABASE LAYER      │
│  ┌────────────────┐  │            │  ┌────────────────┐  │
│  │   MLService    │  │            │  │  Tasks         │  │
│  │  • predict_    │  │            │  │  Employees     │  │
│  │    proba()     │  │            │  │  Task_         │  │
│  │  • score_      │  │            │  │    Assignments │  │
│  │    candidates()│  │            │  │  ML_Training_  │  │
│  │  • extract_    │  │            │  │    Data        │  │
│  │    features()  │  │            │  └────────────────┘  │
│  └────────┬───────┘  │            └──────────────────────┘
└───────────┼──────────┘
            │
    ┌───────┴────────┐
    │                │
    ▼                ▼
┌─────────┐    ┌─────────────┐
│  ML     │    │  Feature    │
│  Models │    │  Builder    │
│ (LGBM)  │    │  Service    │
└─────────┘    └──────┬──────┘
                      │
              ┌───────┴────────┐
              │                │
              ▼                ▼
       ┌──────────┐    ┌──────────────┐
       │  Skill   │    │   Gemini     │
       │ Matching │    │   Client     │
       └──────────┘    └──────────────┘
```

## Component Architecture

### 1. API Layer (routes/api.py)

```
┌─────────────────────────────────────────────┐
│         API Endpoints                        │
├─────────────────────────────────────────────┤
│                                              │
│  trigger_pipeline()                          │
│    ├─→ Fetch tasks & employees              │
│    ├─→ Call scheduler service                │
│    ├─→ Preview or finalize                   │
│    └─→ Return results                        │
│                                              │
│  preview_assignments()                       │
│    ├─→ Validate input                        │
│    ├─→ Call scheduler.preview_assignments()  │
│    └─→ Return preview                        │
│                                              │
│  finalize_assignments(preview_id)            │
│    ├─→ Call scheduler.finalize_assignments() │
│    ├─→ Store in database                     │
│    └─→ Return result                         │
│                                              │
└─────────────────────────────────────────────┘
```

### 2. Scheduler Service (scheduler_service.py)

```
┌─────────────────────────────────────────────────────┐
│              SchedulerService                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  __init__()                                          │
│    ├─→ Initialize ML service                        │
│    └─→ Setup preview storage                        │
│                                                      │
│  assign_tasks(tasks, employees, constraints, method)│
│    ├─→ Select algorithm                             │
│    ├─→ Sort tasks by priority                       │
│    ├─→ For each task:                               │
│    │   ├─→ Filter available employees               │
│    │   ├─→ Score candidates (ML)                    │
│    │   ├─→ Check constraints                        │
│    │   └─→ Create assignment                        │
│    └─→ Return assignments                           │
│                                                      │
│  _greedy_ml_assignment()                            │
│    ├─→ Priority-based ordering                      │
│    ├─→ Best match per task                          │
│    └─→ Fast execution                               │
│                                                      │
│  _balanced_ml_assignment()                          │
│    ├─→ Workload-adjusted scoring                    │
│    ├─→ Fair distribution                            │
│    └─→ Capacity checking                            │
│                                                      │
│  preview_assignments()                              │
│    ├─→ Generate assignments                         │
│    ├─→ Create preview ID                            │
│    ├─→ Store preview                                │
│    └─→ Return preview data                          │
│                                                      │
│  finalize_assignments(preview_id)                   │
│    ├─→ Get preview                                  │
│    ├─→ Store in database                            │
│    ├─→ Log training data                            │
│    ├─→ Cleanup preview                              │
│    └─→ Return result                                │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### 3. ML Service (ml_service.py)

```
┌──────────────────────────────────────────────────┐
│                MLService                          │
├──────────────────────────────────────────────────┤
│                                                   │
│  __init__(model_dir)                              │
│    ├─→ Initialize feature builder                │
│    └─→ Load ML models                             │
│                                                   │
│  predict_proba(employee, task, include_gemini)    │
│    ├─→ Build features                             │
│    ├─→ Run ML model OR fallback                   │
│    └─→ Return (score, confidence)                 │
│                                                   │
│  score_candidates(task, employees, top_k)         │
│    ├─→ Score each employee                        │
│    ├─→ Sort by score                              │
│    └─→ Return top_k candidates                    │
│                                                   │
│  extract_features(employee, task)                 │
│    └─→ Return feature vector                      │
│                                                   │
│  _fallback_score(employee, task)                  │
│    ├─→ Skill match (40%)                          │
│    ├─→ Experience match (30%)                     │
│    ├─→ Workload availability (30%)                │
│    └─→ Return (score, confidence)                 │
│                                                   │
└──────────────────────────────────────────────────┘
```

### 4. Feature Engineering Flow

```
Employee Data          Task Data
     │                    │
     ▼                    ▼
┌─────────┐         ┌─────────┐
│Employee │         │  Task   │
│Features │         │Features │
└────┬────┘         └────┬────┘
     │                   │
     │    ┌──────────────┘
     │    │
     ▼    ▼
┌──────────────┐
│ Interaction  │
│  Features    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Combined    │
│   Features   │
│   (17+)      │
└──────┬───────┘
       │
       ▼
   ML Model
       │
       ▼
  Score (0-1)
```

## Data Flow

### Assignment Creation Flow

```
1. API Request
   │
   ▼
2. Fetch Data
   ├─→ Get pending tasks from DB
   └─→ Get available employees from DB
   │
   ▼
3. Scheduler Service
   ├─→ Sort tasks by priority/deadline
   │
   ▼
4. For Each Task
   ├─→ Filter available employees
   │   ├─→ Check availability_status
   │   ├─→ Check workload capacity
   │   └─→ Check max_assignments
   │
   ▼
5. ML Scoring
   ├─→ Build features for each pair
   ├─→ Run ML model
   ├─→ Get score + confidence
   │
   ▼
6. Assignment Decision
   ├─→ Select best employee
   ├─→ Create assignment record
   ├─→ Update counters
   │
   ▼
7. Return Results
   └─→ List of assignments

8. Finalization (if not preview)
   ├─→ Store assignments in DB
   ├─→ Log training data
   ├─→ Update task statuses
   └─→ Return confirmation
```

### ML Scoring Flow

```
Employee + Task
     │
     ▼
Feature Builder
     │
     ├─→ Employee Features (6)
     │   ├─ Experience
     │   ├─ Workload ratio
     │   ├─ Availability
     │   ├─ Performance
     │   ├─ Active tasks
     │   └─ Avg completion
     │
     ├─→ Task Features (6)
     │   ├─ Priority
     │   ├─ Complexity
     │   ├─ Estimated hours
     │   ├─ Time pressure
     │   ├─ Dependencies
     │   └─ Task age
     │
     └─→ Interaction Features (5)
         ├─ Skill match
         ├─ Experience-complexity ratio
         ├─ Capacity fit
         ├─ Department match
         └─ Success rate
     │
     ▼
Combined Feature Vector (17)
     │
     ▼
ML Model (LightGBM)
     │
     ├─→ If model exists: predict
     │   └─→ Score (0-1), Confidence (0.85)
     │
     └─→ If no model: fallback
         ├─ 0.4 × skill_match
         ├─ 0.3 × experience_match
         └─ 0.3 × workload_score
         └─→ Score (0-1), Confidence (0.6)
```

## Algorithm Comparison

### Greedy ML Algorithm

```
┌─────────────────────────────────┐
│  1. Sort by Priority/Deadline   │
│     (Critical → High → Medium)  │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  2. For Each Task (in order):   │
│     ┌─────────────────────────┐ │
│     │ Filter Available Emps   │ │
│     └───────────┬─────────────┘ │
│                 │                │
│                 ▼                │
│     ┌─────────────────────────┐ │
│     │ Score All (ML)          │ │
│     └───────────┬─────────────┘ │
│                 │                │
│                 ▼                │
│     ┌─────────────────────────┐ │
│     │ Select Best Score       │ │
│     └───────────┬─────────────┘ │
│                 │                │
│                 ▼                │
│     ┌─────────────────────────┐ │
│     │ Create Assignment       │ │
│     └───────────┬─────────────┘ │
│                 │                │
│                 ▼                │
│     ┌─────────────────────────┐ │
│     │ Update Counters         │ │
│     └─────────────────────────┘ │
└─────────────────────────────────┘

Pros:
✓ Fast execution
✓ Prioritizes important tasks
✓ Simple logic

Cons:
✗ May overload some employees
✗ Less fair distribution
```

### Balanced ML Algorithm

```
┌─────────────────────────────────┐
│  1. Sort by Priority Only       │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  2. For Each Task:               │
│     ┌─────────────────────────┐ │
│     │ Score All Employees     │ │
│     └───────────┬─────────────┘ │
│                 │                │
│                 ▼                │
│     ┌─────────────────────────┐ │
│     │ Adjust by Workload      │ │
│     │ score' = (1-w)×score +  │ │
│     │          w×(1-load)     │ │
│     └───────────┬─────────────┘ │
│                 │                │
│                 ▼                │
│     ┌─────────────────────────┐ │
│     │ Sort by Adjusted Score  │ │
│     └───────────┬─────────────┘ │
│                 │                │
│                 ▼                │
│     ┌─────────────────────────┐ │
│     │ Find First with Capacity│ │
│     └───────────┬─────────────┘ │
│                 │                │
│                 ▼                │
│     ┌─────────────────────────┐ │
│     │ Create Assignment       │ │
│     └─────────────────────────┘ │
└─────────────────────────────────┘

Pros:
✓ Fair workload distribution
✓ Prevents overloading
✓ Better team balance

Cons:
✗ Slightly slower
✗ May not pick "best" match
```

## Database Schema

```
┌──────────────────────────────────────────────┐
│              Tasks                            │
├──────────────────────────────────────────────┤
│ task_id (PK)                                 │
│ title                                        │
│ required_skills                              │
│ priority                                     │
│ estimated_hours                              │
│ deadline                                     │
│ complexity_score                             │
│ status                                       │
└──────────────┬───────────────────────────────┘
               │
               │ references
               │
┌──────────────▼───────────────────────────────┐
│         Task_Assignments                     │
├──────────────────────────────────────────────┤
│ assignment_id (PK)                           │
│ task_id (FK)                                 │
│ employee_id (FK)                             │
│ assignment_method                            │
│ assignment_score                             │
│ confidence                                   │
│ assigned_at                                  │
│ status                                       │
└──────────────┬───────────────────────────────┘
               │
               │ references
               │
┌──────────────▼───────────────────────────────┐
│            Employees                         │
├──────────────────────────────────────────────┤
│ employee_id (PK)                             │
│ name                                         │
│ skills                                       │
│ experience_years                             │
│ current_workload                             │
│ max_workload                                 │
│ availability_status                          │
│ performance_rating                           │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│         ML_Training_Data                     │
├──────────────────────────────────────────────┤
│ log_id (PK)                                  │
│ task_id (FK)                                 │
│ employee_id (FK)                             │
│ features (JSONB)                             │
│ assignment_score                             │
│ confidence                                   │
│ method                                       │
│ logged_at                                    │
│ outcome                                      │
└──────────────────────────────────────────────┘
```

## Singleton Pattern

```
┌─────────────────────────────────────┐
│  get_scheduler_service()            │
│    │                                 │
│    ▼                                 │
│  if _scheduler_service is None:     │
│    _scheduler_service =             │
│       SchedulerService()            │
│    │                                 │
│    ▼                                 │
│  return _scheduler_service          │
└─────────────────────────────────────┘
              │
              │ Same instance
              │ shared across
              │ all calls
              ▼
    ┌──────────────────┐
    │  Single Instance │
    │  in Memory       │
    └──────────────────┘
```

## Error Handling Flow

```
Try Assignment
     │
     ├─→ Success
     │   └─→ Return assignments
     │
     ├─→ No Available Employees
     │   ├─→ Log warning
     │   └─→ Skip task
     │
     ├─→ Capacity Exceeded
     │   ├─→ Try next candidate
     │   └─→ Skip if none fit
     │
     ├─→ Model Loading Failed
     │   ├─→ Log warning
     │   └─→ Use fallback scoring
     │
     └─→ Database Error
         ├─→ Rollback transaction
         ├─→ Log error
         └─→ Return error response
```

## Integration Points

```
Scheduler Service
     │
     ├─→ Uses: feature_builder
     │         skill_matching
     │         ml_service
     │
     ├─→ Stores: Task_Assignments
     │           ML_Training_Data
     │
     └─→ Triggers: eta_predictor
                   realtime_detector
```

## Performance Characteristics

```
Operation              | Time Complexity | Space
─────────────────────────────────────────────────
ML Scoring (per pair)  | O(1)           | O(1)
Greedy Assignment      | O(n × m)       | O(n + m)
Balanced Assignment    | O(n × m)       | O(n + m)
Preview Storage        | O(1)           | O(n)
Database Insert        | O(n)           | O(n)

Where:
  n = number of tasks
  m = number of employees
```

## Deployment Architecture

```
┌───────────────────────────────────────────────┐
│            Load Balancer                       │
└─────────────────┬─────────────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
         ▼                 ▼
┌─────────────┐   ┌─────────────┐
│  Flask App  │   │  Flask App  │
│  Instance 1 │   │  Instance 2 │
└──────┬──────┘   └──────┬──────┘
       │                 │
       └────────┬────────┘
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
┌──────────────┐  ┌─────────────┐
│  PostgreSQL  │  │  ML Models  │
│   Database   │  │   (LightGBM)│
└──────────────┘  └─────────────┘
```

This architecture provides a scalable, maintainable, and production-ready solution for intelligent task assignment with ML integration.
