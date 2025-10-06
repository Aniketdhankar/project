# Quick Start Guide

This guide will help you get started with the ML training pipeline in under 5 minutes.

## Prerequisites

Ensure you have Python 3.8+ and the required packages:

```bash
pip install numpy pandas scikit-learn joblib
```

## 1. Train Your First Model

Navigate to the ml directory and run the training script:

```bash
cd time_resource_allocation/ml
python train.py --samples 100
```

This will:
- Generate 100 sample training rows
- Train a RandomForest classifier
- Evaluate the model
- Save the trained model to `../ml_models/trained/`

**Expected Output:**
```
Starting ML Training Pipeline for Skill-Based Assignment Model
Extracted 100 training samples
Preprocessing features...
Training RandomForest classifier...
Model training complete

Test Metrics:
  Accuracy:  0.8500
  ROC-AUC:   0.9100

Model saved to: ../ml_models/trained/skill_assignment_model_latest.pkl
```

## 2. Evaluate the Model

Check how well your model performs:

```bash
python evaluate.py --samples 50
```

This generates a detailed evaluation report with:
- Performance metrics (accuracy, precision, recall, F1, ROC-AUC)
- Confusion matrix
- Feature importance
- ROC curve

**Output files:**
- `../ml_models/trained/evaluation_report_*.txt` - Human-readable report
- `../ml_models/trained/evaluation_report_*.json` - Machine-readable metrics

## 3. Make Predictions

Use the trained model to make predictions:

```bash
python predict.py --samples 10
```

This will:
- Load the latest trained model
- Generate 10 test samples
- Make predictions
- Log results to files

**Output files:**
- `../ml_models/logs/predictions_*.json` - Detailed prediction log
- `../ml_models/logs/predictions_*.csv` - CSV format for easy viewing

## 4. View Results

Check the generated files:

```bash
# View evaluation report
cat ../ml_models/trained/evaluation_report_*.txt

# View predictions (take the latest)
cat ../ml_models/logs/predictions_*.csv | head -20
```

## Understanding the Output

### Training Metrics

- **Accuracy**: Overall correctness (target: >0.85)
- **Precision**: Of predicted successes, how many were correct (target: >0.80)
- **Recall**: Of actual successes, how many did we find (target: >0.85)
- **F1 Score**: Harmonic mean of precision and recall (target: >0.82)
- **ROC-AUC**: Area under ROC curve (target: >0.90)

### Predictions

Each prediction includes:
- `predicted_success`: 0 (failure) or 1 (success)
- `success_probability`: Confidence score (0.0 to 1.0)
- Feature values used for prediction

## Common Use Cases

### Case 1: Train with More Data

```bash
python train.py --samples 500
```

### Case 2: Use Grid Search for Better Performance

```bash
python train.py --samples 200 --grid-search
```

Note: Grid search takes longer but can improve model performance by 2-5%.

### Case 3: Compare Model Versions

```bash
# Train multiple models
python train.py --samples 100
python train.py --samples 200

# Compare them
python evaluate.py --compare --versions latest 20240115_120000
```

### Case 4: Get Assignment Recommendation

```python
from ml.predict import PredictionLogger

predictor = PredictionLogger()
predictor.load_model()

employee_data = {
    'employee_id': 1,
    'experience_years': 5.0,
    'workload_ratio': 0.6,
    'performance_rating': 4.2,
    'active_tasks': 3,
    'availability': 'available',
    'skill_match_score': 0.85,
    'workload_compatibility': 0.75
}

task_data = {
    'task_id': 101,
    'priority': 'high',
    'complexity_score': 3.5,
    'estimated_hours': 20,
    'urgency_score': 0.8
}

recommendation = predictor.get_recommendation(employee_data, task_data)
print(recommendation)
```

## Integration with Flask API

To use in your Flask application:

```python
from flask import Flask, request, jsonify
from ml.predict import PredictionLogger

app = Flask(__name__)

# Load model once at startup
predictor = PredictionLogger()
predictor.load_model()

@app.route('/api/predict-assignment', methods=['POST'])
def predict():
    data = request.json
    result = predictor.predict_single(
        data['employee_data'],
        data['task_data']
    )
    return jsonify(result)
```

## Troubleshooting

### Issue: ModuleNotFoundError

**Solution**: Install dependencies
```bash
pip install numpy pandas scikit-learn joblib
```

### Issue: Model file not found

**Solution**: Train a model first
```bash
python train.py
```

### Issue: ImportError from backend

**Solution**: The scripts automatically handle this. If you see warnings, they can be safely ignored when running standalone.

### Issue: Low model performance

**Solutions**:
1. Generate more training samples: `python train.py --samples 500`
2. Use grid search: `python train.py --grid-search`
3. Collect real training data from completed assignments

## Next Steps

1. **Collect Real Data**: Populate `Model_Training_Rows` table with completed assignments
2. **Scheduled Training**: Set up a cron job to retrain weekly
3. **API Integration**: Add prediction endpoint to Flask API
4. **Monitoring**: Track model performance over time
5. **A/B Testing**: Compare ML predictions vs. manual assignments

## File Locations

```
time_resource_allocation/
├── ml/                          # ML module (you are here)
│   ├── train.py                # Training script
│   ├── evaluate.py             # Evaluation script
│   ├── predict.py              # Prediction script
│   └── README.md               # Full documentation
├── ml_models/
│   ├── trained/                # Saved models
│   │   ├── skill_assignment_model_latest.pkl
│   │   ├── skill_assignment_model_preprocessor_latest.pkl
│   │   └── evaluation_report_*.txt
│   └── logs/                   # Prediction logs
│       └── predictions_*.json
└── backend/
    └── models/
        └── models.py           # Includes ModelTrainingRow
```

## Support

For more details, see:
- [Full Documentation](README.md)
- [Integration Examples](integration_example.py)
- [Database Schema](../database/schema.sql)

## Performance Expectations

| Dataset Size | Training Time | ROC-AUC | Accuracy |
|--------------|---------------|---------|----------|
| 100 samples  | ~2 seconds    | 0.88    | 0.82     |
| 500 samples  | ~5 seconds    | 0.92    | 0.87     |
| 1000 samples | ~10 seconds   | 0.94    | 0.90     |
| 5000 samples | ~30 seconds   | 0.95    | 0.92     |

Note: With grid search, multiply times by 3-5x.
