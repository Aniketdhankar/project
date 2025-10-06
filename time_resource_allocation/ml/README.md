# ML Training Pipeline for Skill-Based Assignment Model

This directory contains the machine learning training pipeline for the skill-based task assignment system using scikit-learn.

## Overview

The ML pipeline predicts the success probability of employee-task assignments based on:
- **Employee features**: Experience, workload, performance rating, availability
- **Task features**: Priority, complexity, estimated hours, urgency
- **Interaction features**: Skill match score, workload compatibility

## Components

### 1. `train.py` - Model Training Pipeline

Main training script that:
- Extracts training data from `ModelTrainingRow` database table
- Preprocesses features with imputation, scaling, and encoding
- Trains a RandomForest classifier
- Evaluates model performance (accuracy, ROC-AUC, precision, recall)
- Saves model and pipeline artifacts with joblib

**Usage:**
```bash
# Basic training
python train.py

# With grid search for hyperparameter tuning
python train.py --grid-search

# Custom test size and sample count
python train.py --test-size 0.3 --samples 200
```

**Key Classes:**
- `SkillAssignmentTrainer`: Main trainer class handling the complete pipeline

**Output Files:**
- `skill_assignment_model_latest.pkl` - Latest trained model
- `skill_assignment_model_preprocessor_latest.pkl` - Preprocessing pipeline
- `skill_assignment_model_features_*.txt` - Feature names
- `skill_assignment_model_metrics_*.json` - Training metrics

### 2. `evaluate.py` - Model Evaluation

Script for evaluating trained models and generating reports.

**Usage:**
```bash
# Evaluate latest model
python evaluate.py

# Evaluate specific version
python evaluate.py --version 20240101_120000

# Compare multiple versions
python evaluate.py --compare --versions latest 20240101_120000 20240102_140000
```

**Key Classes:**
- `ModelEvaluator`: Loads models and generates evaluation reports

**Output Files:**
- `evaluation_report_*.txt` - Detailed text report
- `evaluation_report_*.json` - Metrics in JSON format
- `model_comparison_*.csv` - Version comparison results

### 3. `predict.py` - Prediction and Logging

Script for making predictions and logging results.

**Usage:**
```bash
# Make predictions on sample data
python predict.py --samples 20

# Use custom threshold
python predict.py --threshold 0.7

# Use specific model version
python predict.py --version 20240101_120000
```

**Key Classes:**
- `PredictionLogger`: Makes predictions and logs results

**Output Files:**
- `predictions_*.json` - Prediction log in JSON format
- `predictions_*.csv` - Prediction log in CSV format

## Model Architecture

### Preprocessing Pipeline

1. **Numeric Features** (9 features):
   - Imputation: Median strategy
   - Scaling: StandardScaler
   - Features: experience_years, workload_ratio, performance_rating, active_tasks, complexity_score, estimated_hours, urgency_score, skill_match_score, workload_compatibility

2. **Categorical Features** (2 features):
   - Imputation: Most frequent strategy
   - Encoding: One-hot encoding
   - Features: emp_availability, task_priority

### Model: RandomForest Classifier

**Default Hyperparameters:**
- n_estimators: 100
- max_depth: 20
- min_samples_split: 5
- min_samples_leaf: 2
- class_weight: balanced
- random_state: 42

**Optimization:**
- Grid search available for hyperparameter tuning
- Cross-validation with 5 folds
- Scoring metric: ROC-AUC

## Evaluation Metrics

The pipeline tracks the following metrics:

### Classification Metrics
- **Accuracy**: Overall correctness
- **Precision**: Proportion of positive predictions that are correct
- **Recall**: Proportion of actual positives correctly identified
- **F1 Score**: Harmonic mean of precision and recall
- **ROC-AUC**: Area under the ROC curve

### Additional Metrics
- **Confusion Matrix**: True/False positives and negatives
- **Cross-validation Scores**: 5-fold CV with ROC-AUC
- **Feature Importance**: Contribution of each feature

## Database Integration

### ModelTrainingRow Table

The `ModelTrainingRow` table stores historical assignment data for training:

**Columns:**
- `training_row_id`: Primary key
- `employee_id`, `task_id`, `assignment_id`: Foreign keys
- `emp_experience_years`, `emp_workload_ratio`, etc.: Employee features (snapshot)
- `task_priority`, `task_complexity_score`, etc.: Task features
- `skill_match_score`, `workload_compatibility`: Interaction features
- `success_score`, `completed_on_time`, `actual_hours`, `quality_rating`: Labels/outcomes
- `created_at`: Timestamp

**Population:**
When assignments are completed, populate this table with:
```sql
INSERT INTO model_training_rows (
    employee_id, task_id, assignment_id,
    emp_experience_years, emp_workload_ratio, ...,
    success_score, completed_on_time, actual_hours, quality_rating
)
VALUES (...);
```

## Integration with Existing System

### With LightGBM Models (backend/scripts/train_score_model.py)

The scikit-learn pipeline complements the existing LightGBM models:
- **LightGBM**: Used for regression scoring and ETA prediction
- **RandomForest (this module)**: Used for binary classification and feature preprocessing

Both can coexist and be used for different purposes:
```python
# Use LightGBM for scoring
from backend.scripts.train_score_model import ModelTrainer
lightgbm_trainer = ModelTrainer()

# Use RandomForest for classification
from ml.train import SkillAssignmentTrainer
rf_trainer = SkillAssignmentTrainer()
```

### API Integration

To use the trained model in the Flask API:

```python
from ml.predict import PredictionLogger

# In your API route
predictor = PredictionLogger()
predictor.load_model()

# Make prediction
result = predictor.predict_single(employee_data, task_data)

# Get recommendation
recommendation = predictor.get_recommendation(
    employee_data, 
    task_data, 
    threshold=0.6
)
```

## Example Workflow

### 1. Train a New Model

```bash
cd time_resource_allocation/ml
python train.py --grid-search --samples 500
```

**Output:**
```
Starting ML Training Pipeline for Skill-Based Assignment Model
Extracted 500 training samples
Split data: 400 train, 100 test
Training RandomForest classifier...
Model training complete

Test Metrics:
  Accuracy:  0.8700
  Precision: 0.8621
  Recall:    0.8929
  F1 Score:  0.8772
  ROC-AUC:   0.9234

Cross-validation ROC-AUC: 0.9156 (+/- 0.0234)

Model saved to: ../ml_models/trained/skill_assignment_model_latest.pkl
```

### 2. Evaluate the Model

```bash
python evaluate.py --samples 200
```

**Output:**
```
Loading model: skill_assignment_model (version: latest)
Evaluating on 200 samples

EVALUATION SUMMARY
Accuracy:  0.8650
Precision: 0.8571
Recall:    0.8824
F1 Score:  0.8696
ROC-AUC:   0.9187

Full report: ../ml_models/trained/evaluation_report_20240115_143022.txt
```

### 3. Make Predictions

```bash
python predict.py --samples 10 --threshold 0.7
```

**Output:**
```
Making predictions on 10 samples...
Predictions complete. Success rate: 70.00%

PREDICTION SUMMARY
Total predictions: 10
Predicted successes: 7
Success rate: 70.00%
Average probability: 0.7234

Top 5 predictions:
employee_id  task_id  predicted_success  success_probability
          1      100                  1               0.8542
          2      101                  1               0.7823
          3      102                  0               0.4321
          4      103                  1               0.8901
          5      104                  1               0.7234
```

## Performance Benchmarks

Based on sample data (may vary with real data):

| Metric | Value |
|--------|-------|
| Training Time | ~2-5 seconds (100 samples) |
| Prediction Time | <1ms per sample |
| Model Size | ~1-5 MB |
| ROC-AUC | 0.90-0.95 |
| Accuracy | 0.85-0.90 |

## Continuous Improvement

### Retraining Schedule

1. **Initial Training**: When system is first deployed
2. **Regular Retraining**: Weekly or monthly with new data
3. **Triggered Retraining**: When model performance degrades

### Model Versioning

Models are automatically timestamped and versioned:
- Latest version always available as `*_latest.pkl`
- Historical versions preserved with timestamps
- Compare versions using `evaluate.py --compare`

### Feature Engineering

To add new features:
1. Update `ModelTrainingRow` table schema
2. Modify `feature_names` in `train.py`
3. Update preprocessing pipeline
4. Retrain model

## Troubleshooting

### Issue: ImportError when running scripts

**Solution:** Make sure you're in the correct directory:
```bash
cd time_resource_allocation/ml
python train.py
```

### Issue: No training data in database

**Solution:** Scripts automatically generate sample data. To use real data:
1. Populate `model_training_rows` table
2. Pass database connection to `extract_training_data()`

### Issue: Model performance is poor

**Solutions:**
- Use `--grid-search` for hyperparameter tuning
- Collect more training data
- Check feature quality and preprocessing
- Review feature importance to identify weak features

## Future Enhancements

- [ ] Add support for multi-class classification (success levels)
- [ ] Implement online learning for real-time updates
- [ ] Add SHAP values for explainability
- [ ] Support for ensemble models (voting classifier)
- [ ] Automated A/B testing framework
- [ ] Integration with MLflow for experiment tracking

## References

- scikit-learn Documentation: https://scikit-learn.org/
- RandomForest Classifier: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
- Model Persistence: https://scikit-learn.org/stable/model_persistence.html
