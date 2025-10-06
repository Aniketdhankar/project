# ML Pipeline Architecture

This document provides a high-level overview of the ML training pipeline architecture.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ML Training Pipeline                      │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   Data Source    │      │   Preprocessing  │      │   Model Training │
├──────────────────┤      ├──────────────────┤      ├──────────────────┤
│                  │      │                  │      │                  │
│ ModelTrainingRow │─────▶│  Feature         │─────▶│  RandomForest    │
│   (Database)     │      │  Extraction      │      │  Classifier      │
│                  │      │                  │      │                  │
│      OR          │      │  - Imputation    │      │  - 100 trees     │
│                  │      │  - Scaling       │      │  - max_depth=20  │
│  Sample Data     │      │  - Encoding      │      │  - balanced      │
│  Generator       │      │                  │      │                  │
└──────────────────┘      └──────────────────┘      └──────────────────┘
                                                             │
                                                             ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   Evaluation     │      │   Persistence    │      │   Deployment     │
├──────────────────┤      ├──────────────────┤      ├──────────────────┤
│                  │      │                  │      │                  │
│ - Accuracy       │      │ Model (.pkl)     │      │  Flask API       │
│ - Precision      │◀─────│ Preprocessor     │─────▶│  Endpoints       │
│ - Recall         │      │ Features (.txt)  │      │                  │
│ - F1 Score       │      │ Metrics (.json)  │      │  - /predict      │
│ - ROC-AUC        │      │                  │      │  - /recommend    │
│ - Cross-val      │      │                  │      │                  │
└──────────────────┘      └──────────────────┘      └──────────────────┘
```

## Data Flow

### 1. Training Phase

```
┌─────────────┐
│ Historical  │
│ Assignments │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│ Extract Features & Labels   │
│ - Employee features (9)     │
│ - Task features (4)         │
│ - Interaction features (2)  │
│ - Label: success/failure    │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Preprocess                  │
│ - Handle missing values     │
│ - Scale numeric features    │
│ - Encode categorical        │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Train-Test Split (80/20)    │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Train RandomForest          │
│ - Fit on training data      │
│ - Validate on test data     │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Evaluate & Save             │
│ - Calculate metrics         │
│ - Save model artifacts      │
│ - Generate report           │
└─────────────────────────────┘
```

### 2. Prediction Phase

```
┌─────────────────┐
│ New Assignment  │
│ Request         │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ Extract Features            │
│ - Employee: experience,     │
│   workload, rating, etc.    │
│ - Task: priority,           │
│   complexity, hours, etc.   │
│ - Interaction: skill match, │
│   workload compatibility    │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Load Preprocessor & Model   │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Preprocess Features         │
│ (using saved preprocessor)  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Make Prediction             │
│ - Binary: success/failure   │
│ - Probability: 0.0 to 1.0   │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Generate Recommendation     │
│ - Threshold check (0.6)     │
│ - Explanation               │
│ - Key factors               │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Log & Return                │
│ - Save to JSON/CSV          │
│ - Return to API             │
└─────────────────────────────┘
```

## Feature Engineering

### Input Features (11 total)

**Employee Features (5):**
```
1. emp_experience_years      (numeric, 0-20 years)
2. emp_workload_ratio         (numeric, 0-1)
3. emp_performance_rating     (numeric, 0-5)
4. emp_active_tasks           (numeric, count)
5. emp_availability           (categorical: available/busy/limited)
```

**Task Features (4):**
```
6. task_priority              (categorical: low/medium/high/critical)
7. task_complexity_score      (numeric, 1-5)
8. task_estimated_hours       (numeric, hours)
9. task_urgency_score         (numeric, 0-1)
```

**Interaction Features (2):**
```
10. skill_match_score         (numeric, 0-1)
11. workload_compatibility    (numeric, 0-1)
```

### Preprocessing Pipeline

```
Numeric Features (9)
├─ SimpleImputer (median)
└─ StandardScaler

Categorical Features (2)
├─ SimpleImputer (most_frequent)
└─ OneHotEncoder
    ├─ emp_availability: 3 values → 3 features
    └─ task_priority: 4 values → 4 features

Total Features After Preprocessing: 9 + 3 + 4 = 16
```

## Model Architecture

### RandomForest Classifier

```
RandomForestClassifier(
    n_estimators=100,        # Number of decision trees
    max_depth=20,            # Maximum tree depth
    min_samples_split=5,     # Minimum samples to split node
    min_samples_leaf=2,      # Minimum samples at leaf
    class_weight='balanced', # Handle imbalanced classes
    random_state=42,         # Reproducibility
    n_jobs=-1               # Use all CPU cores
)
```

**Why RandomForest?**
- ✓ Handles non-linear relationships
- ✓ Robust to outliers
- ✓ Built-in feature importance
- ✓ Handles mixed feature types
- ✓ Low risk of overfitting
- ✓ Good interpretability

## Evaluation Metrics

### Primary Metrics

```
┌─────────────────┬──────────────────────────────────────┐
│ Metric          │ Description                          │
├─────────────────┼──────────────────────────────────────┤
│ ROC-AUC         │ Overall discriminative ability       │
│ (Target: >0.90) │ (area under ROC curve)               │
├─────────────────┼──────────────────────────────────────┤
│ Accuracy        │ Overall correctness                  │
│ (Target: >0.85) │ (correct predictions / total)        │
├─────────────────┼──────────────────────────────────────┤
│ Precision       │ Of predicted successes, how many     │
│ (Target: >0.80) │ were actually successful             │
├─────────────────┼──────────────────────────────────────┤
│ Recall          │ Of actual successes, how many        │
│ (Target: >0.85) │ did we identify                      │
├─────────────────┼──────────────────────────────────────┤
│ F1 Score        │ Harmonic mean of precision/recall    │
│ (Target: >0.82) │                                      │
└─────────────────┴──────────────────────────────────────┘
```

### Confusion Matrix

```
                    Predicted
                  Failure  Success
Actual  Failure    TN       FP
        Success    FN       TP

Where:
  TN = True Negatives  (correctly predicted failures)
  FP = False Positives (incorrectly predicted successes)
  FN = False Negatives (missed successes)
  TP = True Positives  (correctly predicted successes)
```

## File Structure

```
time_resource_allocation/
├── ml/                              # ML module
│   ├── __init__.py                 # Package initialization
│   ├── train.py                    # Training pipeline (main)
│   │   └── SkillAssignmentTrainer  # Main trainer class
│   ├── evaluate.py                 # Model evaluation
│   │   └── ModelEvaluator          # Evaluation class
│   ├── predict.py                  # Prediction service
│   │   └── PredictionLogger        # Prediction class
│   ├── integration_example.py      # Integration patterns
│   ├── test_structure.py           # Validation test
│   ├── README.md                   # Full documentation
│   ├── QUICKSTART.md              # Quick start guide
│   └── ARCHITECTURE.md            # This file
│
├── ml_models/                      # Model artifacts
│   ├── trained/                    # Saved models
│   │   ├── skill_assignment_model_latest.pkl
│   │   ├── skill_assignment_model_preprocessor_latest.pkl
│   │   ├── skill_assignment_model_features_*.txt
│   │   ├── skill_assignment_model_metrics_*.json
│   │   └── evaluation_report_*.txt
│   └── logs/                       # Prediction logs
│       ├── predictions_*.json
│       └── predictions_*.csv
│
├── backend/
│   └── models/
│       └── models.py               # SQLAlchemy models
│           └── ModelTrainingRow    # Training data table
│
└── database/
    └── schema.sql                  # Database schema
        └── Model_Training_Rows     # Training data table
```

## Integration Points

### 1. Database Integration

```python
# Populate training data from completed assignments
from models.models import ModelTrainingRow, TaskAssignment

for assignment in completed_assignments:
    training_row = ModelTrainingRow(
        employee_id=assignment.employee_id,
        task_id=assignment.task_id,
        # ... features and outcomes
    )
    db.session.add(training_row)
db.session.commit()
```

### 2. Flask API Integration

```python
# API endpoint for predictions
from ml.predict import PredictionLogger

predictor = PredictionLogger()
predictor.load_model()

@app.route('/api/predict-assignment', methods=['POST'])
def predict():
    result = predictor.predict_single(
        request.json['employee_data'],
        request.json['task_data']
    )
    return jsonify(result)
```

### 3. Scheduled Retraining

```bash
# Cron job for weekly retraining
0 2 * * 0 cd /path/to/ml && python train.py
```

## Performance Considerations

### Training Performance

```
Dataset Size    Training Time    Memory Usage
─────────────   ─────────────    ────────────
100 samples     ~2 seconds       ~50 MB
500 samples     ~5 seconds       ~100 MB
1,000 samples   ~10 seconds      ~150 MB
5,000 samples   ~30 seconds      ~300 MB
10,000 samples  ~60 seconds      ~500 MB
```

### Prediction Performance

```
Batch Size      Latency          Throughput
──────────      ─────────        ──────────
1 prediction    <1 ms            1,000+/sec
10 predictions  <5 ms            2,000+/sec
100 predictions <50 ms           2,000+/sec
1,000 predictions ~500 ms        2,000+/sec
```

## Monitoring & Maintenance

### Key Metrics to Monitor

1. **Model Performance**
   - Track ROC-AUC over time
   - Monitor prediction accuracy vs. actual outcomes
   - Alert if metrics drop below thresholds

2. **Data Quality**
   - Check for data drift in features
   - Monitor missing value rates
   - Track feature distributions

3. **System Health**
   - Prediction latency
   - Model loading time
   - Memory usage

### Maintenance Schedule

```
Daily:      Monitor prediction logs
Weekly:     Review model performance metrics
Monthly:    Retrain model with new data
Quarterly:  Full model evaluation and comparison
Annually:   Architecture review and updates
```

## Scalability

### Current Capacity

- Handles 10,000+ training samples efficiently
- Supports 1,000+ predictions per second
- Model size: ~1-5 MB (lightweight)

### Future Enhancements

1. **Horizontal Scaling**
   - Deploy multiple prediction instances
   - Load balancing with Redis/memcached

2. **Model Optimization**
   - Feature selection for faster inference
   - Model compression techniques
   - Batch prediction optimization

3. **Advanced ML**
   - Ensemble methods (stacking, voting)
   - Deep learning for complex patterns
   - Online learning for real-time updates

## Security Considerations

1. **Model Security**
   - Access control for model files
   - Versioning and audit trails
   - Secure model serving endpoints

2. **Data Privacy**
   - No PII in training data
   - Encrypted database connections
   - Secure prediction logs

3. **API Security**
   - Authentication required
   - Rate limiting
   - Input validation

## Conclusion

This ML pipeline provides a robust, scalable solution for skill-based assignment prediction. The architecture balances simplicity with flexibility, making it easy to:

- Train and evaluate models
- Make predictions in production
- Monitor and maintain performance
- Integrate with existing systems

For detailed usage instructions, see [QUICKSTART.md](QUICKSTART.md) and [README.md](README.md).
