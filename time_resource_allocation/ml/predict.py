"""
Prediction and Logging Script

Makes predictions using trained models and logs results.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
import argparse

import numpy as np
import pandas as pd
import json

# Import trainer
from train import SkillAssignmentTrainer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PredictionLogger:
    """Makes predictions and logs results"""
    
    def __init__(self, model_dir: str = None):
        """
        Initialize prediction logger
        
        Args:
            model_dir: Directory containing trained models
        """
        if model_dir is None:
            model_dir = Path(__file__).parent.parent / 'ml_models' / 'trained'
        
        self.model_dir = Path(model_dir)
        self.logs_dir = self.model_dir.parent / 'logs'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.trainer = SkillAssignmentTrainer(model_dir=str(self.model_dir))
        self.prediction_log = []
    
    def load_model(
        self,
        model_name: str = 'skill_assignment_model',
        version: str = 'latest'
    ):
        """
        Load trained model
        
        Args:
            model_name: Name of the model
            version: Version to load
        """
        logger.info(f"Loading model: {model_name} (version: {version})")
        self.trainer.load_model(model_name, version)
        logger.info("Model loaded successfully")
    
    def predict_batch(
        self,
        data: pd.DataFrame,
        log_predictions: bool = True
    ) -> pd.DataFrame:
        """
        Make predictions on a batch of data
        
        Args:
            data: DataFrame with features
            log_predictions: Whether to log predictions
            
        Returns:
            DataFrame with predictions
        """
        logger.info(f"Making predictions on {len(data)} samples...")
        
        # Make predictions
        predictions = self.trainer.predict(data)
        probabilities = self.trainer.predict_proba(data)
        
        # Add to dataframe
        results = data.copy()
        results['predicted_success'] = predictions
        results['success_probability'] = probabilities[:, 1]
        results['prediction_timestamp'] = datetime.now()
        
        # Log predictions
        if log_predictions:
            for i, row in results.iterrows():
                log_entry = {
                    'timestamp': str(row['prediction_timestamp']),
                    'employee_id': row.get('employee_id', None),
                    'task_id': row.get('task_id', None),
                    'predicted_success': int(row['predicted_success']),
                    'success_probability': float(row['success_probability']),
                    'features': row[self.trainer.feature_names].to_dict()
                }
                self.prediction_log.append(log_entry)
        
        logger.info(f"Predictions complete. Success rate: {predictions.mean():.2%}")
        
        return results
    
    def predict_single(
        self,
        employee_data: dict,
        task_data: dict,
        log_prediction: bool = True
    ) -> dict:
        """
        Make prediction for a single employee-task pair
        
        Args:
            employee_data: Dictionary with employee features
            task_data: Dictionary with task features
            log_prediction: Whether to log prediction
            
        Returns:
            Dictionary with prediction results
        """
        # Combine features
        features = {
            'emp_experience_years': employee_data.get('experience_years', 0),
            'emp_workload_ratio': employee_data.get('workload_ratio', 0),
            'emp_performance_rating': employee_data.get('performance_rating', 3.0),
            'emp_active_tasks': employee_data.get('active_tasks', 0),
            'emp_availability': employee_data.get('availability', 'available'),
            'task_priority': task_data.get('priority', 'medium'),
            'task_complexity_score': task_data.get('complexity_score', 2.5),
            'task_estimated_hours': task_data.get('estimated_hours', 10),
            'task_urgency_score': task_data.get('urgency_score', 0.5),
            'skill_match_score': employee_data.get('skill_match_score', 0.5),
            'workload_compatibility': employee_data.get('workload_compatibility', 0.5)
        }
        
        # Create DataFrame
        df = pd.DataFrame([features])
        
        # Make prediction
        prediction = self.trainer.predict(df)[0]
        probability = self.trainer.predict_proba(df)[0, 1]
        
        result = {
            'employee_id': employee_data.get('employee_id'),
            'task_id': task_data.get('task_id'),
            'predicted_success': int(prediction),
            'success_probability': float(probability),
            'timestamp': datetime.now().isoformat(),
            'features': features
        }
        
        # Log prediction
        if log_prediction:
            self.prediction_log.append(result)
        
        logger.info(f"Prediction: {'Success' if prediction else 'Failure'} "
                   f"(probability: {probability:.4f})")
        
        return result
    
    def save_prediction_log(self, output_path: str = None) -> str:
        """
        Save prediction log to file
        
        Args:
            output_path: Path to save log (default: auto-generated)
            
        Returns:
            Path to saved log
        """
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.logs_dir / f'predictions_{timestamp}.json'
        
        logger.info(f"Saving {len(self.prediction_log)} predictions to {output_path}")
        
        with open(output_path, 'w') as f:
            json.dump(self.prediction_log, f, indent=2, default=str)
        
        logger.info(f"Prediction log saved to: {output_path}")
        
        # Also save as CSV for easy viewing
        csv_path = str(output_path).replace('.json', '.csv')
        df = pd.DataFrame(self.prediction_log)
        
        # Flatten features for CSV
        if 'features' in df.columns and len(df) > 0:
            features_df = pd.json_normalize(df['features'])
            df = pd.concat([df.drop('features', axis=1), features_df], axis=1)
        
        df.to_csv(csv_path, index=False)
        logger.info(f"CSV log saved to: {csv_path}")
        
        return str(output_path)
    
    def get_recommendation(
        self,
        employee_data: dict,
        task_data: dict,
        threshold: float = 0.6
    ) -> dict:
        """
        Get assignment recommendation with explanation
        
        Args:
            employee_data: Dictionary with employee features
            task_data: Dictionary with task features
            threshold: Success probability threshold for recommendation
            
        Returns:
            Dictionary with recommendation and explanation
        """
        # Make prediction
        result = self.predict_single(employee_data, task_data, log_prediction=False)
        
        probability = result['success_probability']
        recommended = probability >= threshold
        
        # Generate explanation
        if recommended:
            confidence = "high" if probability >= 0.8 else "moderate"
            explanation = (
                f"RECOMMENDED: This assignment has a {probability:.1%} probability of success. "
                f"Confidence level: {confidence}."
            )
        else:
            explanation = (
                f"NOT RECOMMENDED: This assignment has a {probability:.1%} probability of success, "
                f"which is below the {threshold:.1%} threshold."
            )
        
        # Add key factors
        features = result['features']
        key_factors = []
        
        if features['skill_match_score'] < 0.5:
            key_factors.append("Low skill match")
        if features['emp_workload_ratio'] > 0.8:
            key_factors.append("High employee workload")
        if features['task_complexity_score'] > 4:
            key_factors.append("High task complexity")
        if features['emp_experience_years'] < 1:
            key_factors.append("Low employee experience")
        
        if key_factors:
            explanation += f" Key concerns: {', '.join(key_factors)}."
        
        recommendation = {
            'recommended': recommended,
            'success_probability': probability,
            'confidence': confidence if recommended else "low",
            'explanation': explanation,
            'employee_id': result['employee_id'],
            'task_id': result['task_id'],
            'timestamp': result['timestamp']
        }
        
        return recommendation


def main():
    """Main entry point for predictions"""
    parser = argparse.ArgumentParser(description='Make predictions with trained model')
    parser.add_argument('--model-name', type=str, default='skill_assignment_model',
                        help='Name of the model to use')
    parser.add_argument('--version', type=str, default='latest',
                        help='Version to load (latest or timestamp)')
    parser.add_argument('--samples', type=int, default=10,
                        help='Number of samples to predict on (default: 10)')
    parser.add_argument('--threshold', type=float, default=0.6,
                        help='Success probability threshold for recommendations (default: 0.6)')
    
    args = parser.parse_args()
    
    # Initialize predictor
    predictor = PredictionLogger()
    
    # Load model
    predictor.load_model(args.model_name, args.version)
    
    # Generate sample data for predictions
    logger.info(f"Generating {args.samples} samples for prediction...")
    sample_data = predictor.trainer._generate_sample_data(n_samples=args.samples)
    
    # Add sample IDs
    sample_data['employee_id'] = range(1, len(sample_data) + 1)
    sample_data['task_id'] = range(100, 100 + len(sample_data))
    
    # Make predictions
    results = predictor.predict_batch(sample_data, log_predictions=True)
    
    # Save prediction log
    log_path = predictor.save_prediction_log()
    
    # Print summary
    print("\n" + "=" * 80)
    print("PREDICTION SUMMARY")
    print("=" * 80)
    print(f"Total predictions: {len(results)}")
    print(f"Predicted successes: {results['predicted_success'].sum()}")
    print(f"Success rate: {results['predicted_success'].mean():.2%}")
    print(f"Average probability: {results['success_probability'].mean():.4f}")
    print(f"\nTop 5 predictions:")
    print(results[['employee_id', 'task_id', 'predicted_success', 'success_probability']]
          .head().to_string(index=False))
    print(f"\nPrediction log saved to: {log_path}")
    
    # Example recommendation
    print("\n" + "=" * 80)
    print("EXAMPLE RECOMMENDATION")
    print("=" * 80)
    
    example_employee = {
        'employee_id': 1,
        'experience_years': 5.0,
        'workload_ratio': 0.6,
        'performance_rating': 4.2,
        'active_tasks': 3,
        'availability': 'available',
        'skill_match_score': 0.85,
        'workload_compatibility': 0.75
    }
    
    example_task = {
        'task_id': 101,
        'priority': 'high',
        'complexity_score': 3.5,
        'estimated_hours': 20,
        'urgency_score': 0.8
    }
    
    recommendation = predictor.get_recommendation(
        example_employee,
        example_task,
        threshold=args.threshold
    )
    
    print(f"Recommended: {recommendation['recommended']}")
    print(f"Probability: {recommendation['success_probability']:.2%}")
    print(f"Confidence: {recommendation['confidence']}")
    print(f"\n{recommendation['explanation']}")


if __name__ == '__main__':
    main()
