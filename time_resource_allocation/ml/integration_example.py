"""
Integration Example

This file demonstrates how to integrate the ML training pipeline 
with the existing Flask application and database models.
"""

import sys
from pathlib import Path

# Add paths for imports
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

# Example 1: Training with Flask app context
def train_with_flask_app():
    """Train model using Flask app and database"""
    from flask import Flask
    from models.models import db, ModelTrainingRow
    from config.config import Config
    from ml.train import train_pipeline
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    # Train within app context
    with app.app_context():
        trainer = train_pipeline(
            database_connection=app,
            use_grid_search=False
        )
    
    print("Training complete!")
    return trainer


# Example 2: Populate ModelTrainingRow from completed assignments
def populate_training_data_from_assignments():
    """
    Populate ModelTrainingRow from completed task assignments.
    This should be called periodically to build training dataset.
    """
    from flask import Flask, current_app
    from models.models import db, ModelTrainingRow, TaskAssignment, Employee, Task
    from datetime import datetime
    
    # Pseudocode for populating training data
    """
    completed_assignments = TaskAssignment.query.filter_by(
        status='completed'
    ).all()
    
    for assignment in completed_assignments:
        # Skip if already in training data
        existing = ModelTrainingRow.query.filter_by(
            assignment_id=assignment.assignment_id
        ).first()
        
        if existing:
            continue
        
        # Get employee and task details
        employee = Employee.query.get(assignment.employee_id)
        task = Task.query.get(assignment.task_id)
        
        # Calculate success score based on outcomes
        success_score = calculate_success_score(assignment, task)
        
        # Create training row
        training_row = ModelTrainingRow(
            employee_id=assignment.employee_id,
            task_id=assignment.task_id,
            assignment_id=assignment.assignment_id,
            
            # Employee features (snapshot at assignment time)
            emp_experience_years=employee.experience_years,
            emp_workload_ratio=employee.current_workload / employee.max_workload,
            emp_performance_rating=employee.performance_rating,
            emp_active_tasks=len(employee.assignments),
            emp_availability=employee.availability_status,
            
            # Task features
            task_priority=task.priority,
            task_complexity_score=task.complexity_score,
            task_estimated_hours=task.estimated_hours,
            task_urgency_score=calculate_urgency(task),
            
            # Interaction features
            skill_match_score=calculate_skill_match(employee, task),
            workload_compatibility=calculate_workload_compat(employee, task),
            
            # Labels/outcomes
            success_score=success_score,
            completed_on_time=(assignment.completed_at <= assignment.estimated_completion),
            actual_hours=assignment.actual_hours,
            quality_rating=calculate_quality_rating(assignment)
        )
        
        db.session.add(training_row)
    
    db.session.commit()
    print(f"Added {len(completed_assignments)} training rows")
    """
    pass


# Example 3: Use trained model in API endpoint
def example_api_endpoint():
    """
    Example Flask API endpoint using the trained model for predictions
    """
    """
    from flask import Blueprint, request, jsonify
    from ml.predict import PredictionLogger
    
    ml_bp = Blueprint('ml', __name__, url_prefix='/api/ml')
    
    # Initialize predictor (load once at startup)
    predictor = PredictionLogger()
    predictor.load_model()
    
    @ml_bp.route('/predict-assignment', methods=['POST'])
    def predict_assignment():
        data = request.json
        
        employee_data = {
            'employee_id': data['employee_id'],
            'experience_years': data['emp_experience_years'],
            'workload_ratio': data['emp_workload_ratio'],
            'performance_rating': data['emp_performance_rating'],
            'active_tasks': data['emp_active_tasks'],
            'availability': data['emp_availability'],
            'skill_match_score': data['skill_match_score'],
            'workload_compatibility': data['workload_compatibility']
        }
        
        task_data = {
            'task_id': data['task_id'],
            'priority': data['task_priority'],
            'complexity_score': data['task_complexity_score'],
            'estimated_hours': data['task_estimated_hours'],
            'urgency_score': data['task_urgency_score']
        }
        
        # Make prediction
        result = predictor.predict_single(employee_data, task_data)
        
        # Get recommendation
        recommendation = predictor.get_recommendation(
            employee_data,
            task_data,
            threshold=0.6
        )
        
        return jsonify({
            'success': True,
            'prediction': result,
            'recommendation': recommendation
        })
    
    @ml_bp.route('/predict-batch', methods=['POST'])
    def predict_batch():
        import pandas as pd
        
        data = request.json
        df = pd.DataFrame(data['assignments'])
        
        # Make predictions
        results = predictor.predict_batch(df, log_predictions=True)
        
        return jsonify({
            'success': True,
            'predictions': results.to_dict('records'),
            'summary': {
                'total': len(results),
                'predicted_successes': int(results['predicted_success'].sum()),
                'success_rate': float(results['predicted_success'].mean())
            }
        })
    """
    pass


# Example 4: Scheduled model retraining
def scheduled_retraining():
    """
    Example scheduled job for periodic model retraining.
    Can be run via cron or task scheduler.
    """
    """
    from ml.train import train_pipeline
    from ml.evaluate import ModelEvaluator
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting scheduled model retraining...")
        
        # Train new model
        trainer = train_pipeline(
            database_connection=app,
            use_grid_search=False
        )
        
        # Evaluate new model
        evaluator = ModelEvaluator()
        metrics = evaluator.load_and_evaluate(version='latest')
        
        # Check if new model is better than previous
        if metrics['roc_auc'] > 0.85:  # Threshold
            logger.info(f"New model deployed with ROC-AUC: {metrics['roc_auc']:.4f}")
            
            # Generate report
            evaluator.generate_report(metrics)
            
            # Reload predictor with new model
            global predictor
            predictor = PredictionLogger()
            predictor.load_model()
        else:
            logger.warning(f"New model not deployed. ROC-AUC: {metrics['roc_auc']:.4f}")
        
    except Exception as e:
        logger.error(f"Error in scheduled retraining: {e}")
    """
    pass


# Example 5: Integration with existing ML pipeline
def integrate_with_existing_pipeline():
    """
    Show how to use both LightGBM and RandomForest models together
    """
    """
    from backend.scripts.train_score_model import ModelTrainer as LGBMTrainer
    from ml.train import SkillAssignmentTrainer as RFTrainer
    
    # Use LightGBM for regression scoring
    lgbm_trainer = LGBMTrainer()
    scoring_results = lgbm_trainer.train_scoring_model(db_connection)
    
    # Use RandomForest for classification
    rf_trainer = RFTrainer()
    classification_results = rf_trainer.train_model(X_train, y_train, X_test, y_test)
    
    # Combine predictions
    def predict_assignment(employee, task):
        # Get regression score from LightGBM
        lgbm_score = lgbm_model.predict(features)
        
        # Get classification from RandomForest
        rf_prediction = rf_model.predict(features)
        rf_probability = rf_model.predict_proba(features)
        
        # Combine for final decision
        final_recommendation = {
            'lgbm_score': lgbm_score,
            'rf_prediction': rf_prediction,
            'rf_probability': rf_probability,
            'recommended': (rf_probability > 0.6) and (lgbm_score > 0.7)
        }
        
        return final_recommendation
    """
    pass


if __name__ == '__main__':
    print("ML Training Pipeline Integration Examples")
    print("=" * 80)
    print("\nThis file contains example code for integrating the ML pipeline")
    print("with the Flask application and database.")
    print("\nKey integration points:")
    print("1. Training with Flask app context")
    print("2. Populating ModelTrainingRow from completed assignments")
    print("3. Using trained model in API endpoints")
    print("4. Scheduled model retraining")
    print("5. Integration with existing LightGBM models")
    print("\nRefer to the code comments for implementation details.")
