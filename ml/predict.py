"""
Prediction and Logging Script

This script loads a trained model and makes predictions on new data,
logging predictions for monitoring and analysis.
"""

import os
import sys
import logging
import joblib
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Union

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PredictionLogger:
    """
    Handles predictions and logging for skill-based assignment model
    """
    
    def __init__(
        self,
        model_path: str,
        log_dir: str = None
    ):
        """
        Initialize prediction logger
        
        Args:
            model_path: Path to the trained model
            log_dir: Directory to save prediction logs
        """
        self.model_path = Path(model_path)
        self.model = None
        
        if log_dir is None:
            log_dir = os.path.join(os.path.dirname(__file__), 'predictions')
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.load_model()
        
        # Initialize prediction log
        self.prediction_log = []
    
    def load_model(self):
        """Load the trained model"""
        logger.info(f"Loading model from: {self.model_path}")
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        self.model = joblib.load(self.model_path)
        logger.info("Model loaded successfully")
    
    def predict(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        return_proba: bool = True
    ) -> Dict:
        """
        Make predictions on input data
        
        Args:
            X: Input features
            return_proba: Whether to return probability scores
        
        Returns:
            Dictionary with predictions and optional probabilities
        """
        logger.info(f"Making predictions for {len(X)} samples")
        
        # Make predictions
        predictions = self.model.predict(X)
        
        result = {
            'predictions': predictions.tolist(),
            'n_samples': len(X)
        }
        
        if return_proba:
            probabilities = self.model.predict_proba(X)
            result['probabilities'] = probabilities.tolist()
            result['confidence'] = np.max(probabilities, axis=1).tolist()
        
        logger.info("Predictions completed")
        return result
    
    def predict_and_log(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        metadata: Dict = None,
        feature_names: List[str] = None
    ) -> Dict:
        """
        Make predictions and log them for monitoring
        
        Args:
            X: Input features
            metadata: Optional metadata about the predictions
            feature_names: Names of features
        
        Returns:
            Dictionary with predictions and log information
        """
        timestamp = datetime.now()
        
        # Make predictions
        result = self.predict(X, return_proba=True)
        
        # Create log entry
        log_entry = {
            'timestamp': timestamp.isoformat(),
            'n_samples': result['n_samples'],
            'predictions': result['predictions'],
            'probabilities': result['probabilities'],
            'confidence': result['confidence'],
            'metadata': metadata or {}
        }
        
        # Add to prediction log
        self.prediction_log.append(log_entry)
        
        # Save to file
        log_file = self.log_dir / f"predictions_{timestamp.strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        logger.info(f"Predictions logged to: {log_file}")
        
        return result
    
    def predict_assignment_scores(
        self,
        employee_task_pairs: List[Dict],
        feature_names: List[str] = None
    ) -> pd.DataFrame:
        """
        Predict assignment scores for employee-task pairs
        
        Args:
            employee_task_pairs: List of dicts with employee and task features
            feature_names: Expected feature names in order
        
        Returns:
            DataFrame with predictions and confidence scores
        """
        logger.info(f"Scoring {len(employee_task_pairs)} employee-task pairs")
        
        # Extract features from pairs
        if feature_names:
            X = np.array([[pair.get(fname, 0) for fname in feature_names] 
                         for pair in employee_task_pairs])
        else:
            # Assume pairs are already feature vectors
            X = np.array([list(pair.values()) for pair in employee_task_pairs])
        
        # Make predictions
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        confidence = np.max(probabilities, axis=1)
        
        # Create results DataFrame
        results = pd.DataFrame({
            'pair_index': range(len(employee_task_pairs)),
            'prediction': predictions,
            'success_probability': probabilities[:, 1] if probabilities.shape[1] == 2 else confidence,
            'confidence': confidence
        })
        
        # Sort by success probability
        results = results.sort_values('success_probability', ascending=False)
        
        logger.info("Assignment scoring completed")
        return results
    
    def get_top_k_assignments(
        self,
        employee_task_pairs: List[Dict],
        k: int = 5,
        feature_names: List[str] = None
    ) -> List[Dict]:
        """
        Get top K recommended assignments
        
        Args:
            employee_task_pairs: List of employee-task pair features
            k: Number of top recommendations to return
            feature_names: Feature names
        
        Returns:
            List of top K assignments with scores
        """
        logger.info(f"Getting top {k} assignment recommendations")
        
        # Get all predictions
        results = self.predict_assignment_scores(
            employee_task_pairs,
            feature_names
        )
        
        # Get top K
        top_k = results.head(k)
        
        recommendations = []
        for idx, row in top_k.iterrows():
            pair_idx = int(row['pair_index'])
            recommendations.append({
                'pair_index': pair_idx,
                'employee_task_data': employee_task_pairs[pair_idx],
                'predicted_success': int(row['prediction']),
                'success_probability': float(row['success_probability']),
                'confidence': float(row['confidence'])
            })
        
        return recommendations
    
    def analyze_prediction_log(self) -> Dict:
        """
        Analyze the prediction log for insights
        
        Returns:
            Dictionary with log analysis
        """
        if not self.prediction_log:
            logger.warning("No predictions in log")
            return {}
        
        # Calculate statistics
        total_predictions = sum(entry['n_samples'] for entry in self.prediction_log)
        
        all_predictions = []
        all_confidences = []
        for entry in self.prediction_log:
            all_predictions.extend(entry['predictions'])
            all_confidences.extend(entry['confidence'])
        
        analysis = {
            'total_prediction_calls': len(self.prediction_log),
            'total_predictions': total_predictions,
            'prediction_distribution': {
                str(k): all_predictions.count(k) 
                for k in set(all_predictions)
            },
            'average_confidence': np.mean(all_confidences),
            'min_confidence': np.min(all_confidences),
            'max_confidence': np.max(all_confidences),
            'low_confidence_predictions': sum(1 for c in all_confidences if c < 0.6),
        }
        
        logger.info(f"Analyzed {total_predictions} predictions from {len(self.prediction_log)} calls")
        
        return analysis
    
    def save_log_summary(self, output_file: str = None):
        """
        Save a summary of prediction logs
        
        Args:
            output_file: Path to save summary (optional)
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.log_dir / f'log_summary_{timestamp}.json'
        
        analysis = self.analyze_prediction_log()
        
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        logger.info(f"Saved log summary to: {output_file}")
        return analysis


def main():
    """Main function for making predictions"""
    parser = argparse.ArgumentParser(
        description='Make predictions with trained skill-based assignment model'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='ml/models/skill_assignment_model_latest.pkl',
        help='Path to trained model'
    )
    parser.add_argument(
        '--log-dir',
        type=str,
        default='ml/predictions',
        help='Directory to save prediction logs'
    )
    parser.add_argument(
        '--n-samples',
        type=int,
        default=10,
        help='Number of sample predictions to make'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize predictor
        predictor = PredictionLogger(args.model, args.log_dir)
        
        # Generate sample data for prediction
        logger.info(f"Generating {args.n_samples} sample predictions")
        np.random.seed(42)
        n_features = 17
        X_sample = np.random.rand(args.n_samples, n_features)
        
        # Make predictions and log
        metadata = {
            'source': 'command_line_test',
            'model_version': 'latest'
        }
        
        result = predictor.predict_and_log(X_sample, metadata=metadata)
        
        # Print results
        print("\n" + "=" * 60)
        print("Prediction Results")
        print("=" * 60)
        print(f"\nNumber of samples: {result['n_samples']}")
        print(f"\nPredictions: {result['predictions']}")
        print(f"\nConfidence scores:")
        for i, conf in enumerate(result['confidence']):
            print(f"  Sample {i+1}: {conf:.4f}")
        
        # Analyze log
        analysis = predictor.analyze_prediction_log()
        print(f"\nPrediction Log Analysis:")
        print(f"  Total predictions: {analysis['total_predictions']}")
        print(f"  Average confidence: {analysis['average_confidence']:.4f}")
        print(f"  Low confidence predictions: {analysis['low_confidence_predictions']}")
        
        # Save summary
        predictor.save_log_summary()
        
        print("\n" + "=" * 60 + "\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    exit(main())
