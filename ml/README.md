# ML Training Pipeline for Skill-Based Assignment Model

This directory contains the machine learning training pipeline for the skill-based task assignment model. The pipeline uses scikit-learn for supervised learning to predict assignment success based on employee-task features.

## Overview

The ML pipeline implements:
- **Feature extraction** from database (Employee, Task, TaskAssignment models)
- **Preprocessing** (imputation, scaling, encoding)
- **Model training** using RandomForest classifier
- **Evaluation** with multiple metrics (accuracy, precision, recall, F1, ROC-AUC)
- **Artifact export** (model, pipeline, metadata)

## Directory Structure

```
ml/
├── train.py              # Main training pipeline
├── evaluate.py           # Model evaluation script
├── predict.py            # Prediction and logging script
├── README.md             # This file
├── models/               # Saved model artifacts
│   ├── skill_assignment_model_latest.pkl
│   ├── skill_assignment_model_YYYYMMDD_HHMMSS.pkl
│   ├── model_metadata_YYYYMMDD_HHMMSS.json
│   ├── feature_names.txt
│   └── evaluation_report_YYYYMMDD_HHMMSS.txt
├── evaluations/          # Evaluation results
│   ├── evaluation_metrics_YYYYMMDD_HHMMSS.json
│   └── evaluation_summary_YYYYMMDD_HHMMSS.txt
└── predictions/          # Prediction logs
    ├── predictions_YYYYMMDD.jsonl
    └── log_summary_YYYYMMDD_HHMMSS.json
```

## Installation

Ensure you have the required dependencies installed:

```bash
pip install -r ../time_resource_allocation/requirements.txt
```

Key dependencies:
- scikit-learn==1.3.0
- numpy==1.24.3
- pandas==2.0.3
- joblib==1.3.2

## Usage

### 1. Train a Model

Run the training pipeline:

```bash
python ml/train.py
```

This will:
1. Extract training data from the database (or use sample data)
2. Preprocess features (imputation, scaling)
3. Train a RandomForest classifier
4. Evaluate on test set with cross-validation
5. Save model, pipeline, and metadata

**Output:**
- `models/skill_assignment_model_latest.pkl` - Latest trained model pipeline
- `models/model_metadata_YYYYMMDD_HHMMSS.json` - Training metadata and metrics
- `models/evaluation_report_YYYYMMDD_HHMMSS.txt` - Human-readable evaluation report
- `models/feature_names.txt` - List of feature names

### 2. Evaluate a Model

Evaluate a trained model on test data:

```bash
python ml/evaluate.py --model ml/models/skill_assignment_model_latest.pkl
```

**Options:**
- `--model`: Path to trained model (default: `ml/models/skill_assignment_model_latest.pkl`)
- `--output-dir`: Directory to save evaluation results (default: `ml/evaluations`)

**Output:**
- Evaluation metrics (JSON)
- Evaluation summary report (TXT)
- Console output with detailed metrics

### 3. Make Predictions

Use the trained model to make predictions:

```bash
python ml/predict.py --model ml/models/skill_assignment_model_latest.pkl --n-samples 10
```

**Options:**
- `--model`: Path to trained model
- `--log-dir`: Directory to save prediction logs (default: `ml/predictions`)
- `--n-samples`: Number of sample predictions to make

**Output:**
- Prediction logs (JSONL format)
- Log analysis summary (JSON)

## Model Architecture

### Features (17 dimensions)

The model uses the following feature groups:

**Employee Features (6):**
1. `employee_experience` - Years of experience (normalized 0-1)
2. `employee_workload_ratio` - Current workload / max workload
3. `employee_availability` - Binary availability status
4. `employee_performance` - Performance rating (normalized 0-1)
5. `employee_active_tasks` - Number of active tasks (normalized)
6. `employee_avg_completion` - Average completion time (normalized)

**Task Features (6):**
7. `task_priority` - Priority level (0.25-1.0)
8. `task_complexity` - Complexity score (normalized 0-1)
9. `task_estimated_hours` - Estimated hours (normalized)
10. `task_time_pressure` - Urgency based on deadline
11. `task_dependencies` - Number of dependencies (normalized)
12. `task_age` - Days since task creation (normalized)

**Interaction Features (5):**
13. `skill_match_score` - Similarity between employee and task skills
14. `experience_complexity_ratio` - Employee experience vs task complexity
15. `workload_capacity_fit` - Can employee fit this task in workload?
16. `department_match` - Department alignment
17. `historical_success_rate` - Past success rate for employee

### Preprocessing Pipeline

1. **Imputation**: Missing values filled with mean (SimpleImputer)
2. **Scaling**: Features standardized with zero mean and unit variance (StandardScaler)

### Model

- **Algorithm**: RandomForestClassifier
- **Default Parameters**:
  - `n_estimators=100` - Number of trees
  - `max_depth=10` - Maximum tree depth
  - `min_samples_split=5` - Minimum samples to split
  - `random_state=42` - For reproducibility

### Output

- **Binary Classification**: Predicts assignment success (0/1)
- **Probability Scores**: Returns confidence for each prediction

## Evaluation Metrics

The model is evaluated using:

1. **Accuracy**: Overall correctness
2. **Precision**: True positives / (True positives + False positives)
3. **Recall**: True positives / (True positives + False negatives)
4. **F1 Score**: Harmonic mean of precision and recall
5. **ROC-AUC**: Area under ROC curve (discrimination ability)
6. **Confusion Matrix**: Classification breakdown
7. **Cross-Validation**: 5-fold CV for stability assessment

## Integration with ML Service

The trained model is compatible with ML service integration through:

1. **Saved Pipeline**: Complete preprocessing + model pipeline saved with joblib
2. **Metadata**: JSON metadata includes model parameters, metrics, and feature names
3. **Standardized Format**: Compatible with scikit-learn's joblib format
4. **Feature Names**: Saved separately for reference and validation

### Loading a Trained Model

```python
import joblib

# Load the complete pipeline
pipeline = joblib.load('ml/models/skill_assignment_model_latest.pkl')

# Make predictions
predictions = pipeline.predict(X_new)
probabilities = pipeline.predict_proba(X_new)
```

## Data Sources

### From Database

The training pipeline can extract data from:
- `TaskAssignment` table (completed assignments)
- `Employee` table (employee profiles and skills)
- `Task` table (task requirements and attributes)

Query example:
```sql
SELECT ta.*, e.*, t.*
FROM task_assignments ta
JOIN employees e ON ta.employee_id = e.employee_id
JOIN tasks t ON ta.task_id = t.task_id
WHERE ta.status = 'completed'
```

### Sample Data

When database is not available, the pipeline generates synthetic training data that mimics real feature distributions.

## Logging and Monitoring

### Prediction Logs

All predictions are logged in JSONL format:

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "n_samples": 10,
  "predictions": [1, 0, 1, ...],
  "probabilities": [[0.2, 0.8], [0.7, 0.3], ...],
  "confidence": [0.8, 0.7, ...],
  "metadata": {"source": "api", "model_version": "v1.0"}
}
```

### Log Analysis

Analyze prediction logs to monitor:
- Prediction distribution
- Average confidence scores
- Low-confidence predictions (< 0.6)
- Total prediction volume

## Model Retraining

Retrain the model periodically to incorporate new data:

```bash
# Train with latest data
python ml/train.py

# Evaluate the new model
python ml/evaluate.py --model ml/models/skill_assignment_model_latest.pkl

# Compare with previous version
diff ml/models/evaluation_report_*.txt
```

## Performance Benchmarks

Typical performance on sample data:
- **Accuracy**: ~0.75-0.85
- **ROC-AUC**: ~0.80-0.90
- **Training Time**: < 1 minute (200 samples)
- **Inference Time**: < 10ms per sample

## Troubleshooting

### Issue: Model not loading
**Solution**: Ensure joblib version matches training environment

### Issue: Feature dimension mismatch
**Solution**: Check feature_names.txt and ensure input has 17 features

### Issue: Low accuracy
**Solution**: 
- Increase training data
- Tune hyperparameters
- Check feature quality

## Future Enhancements

Planned improvements:
- [ ] Hyperparameter tuning with GridSearchCV
- [ ] Feature selection and importance analysis
- [ ] Support for additional algorithms (XGBoost, LightGBM)
- [ ] Online learning for continuous model updates
- [ ] A/B testing framework
- [ ] Model versioning and rollback

## Contact

For questions or issues, please refer to the main project documentation or create an issue in the repository.
