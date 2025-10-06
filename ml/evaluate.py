"""
Model Evaluation Script

This script loads a trained model and evaluates it on test data,
providing detailed metrics and visualizations.
"""

import os
import sys
import logging
import joblib
import json
import argparse
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    classification_report,
    confusion_matrix
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Evaluator for trained skill-based assignment models
    """
    
    def __init__(self, model_path: str):
        """
        Initialize evaluator with a trained model
        
        Args:
            model_path: Path to the saved model pipeline
        """
        self.model_path = Path(model_path)
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model pipeline"""
        logger.info(f"Loading model from: {self.model_path}")
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        self.model = joblib.load(self.model_path)
        logger.info("Model loaded successfully")
    
    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray,
        feature_names: list = None
    ) -> dict:
        """
        Evaluate model on test data
        
        Args:
            X_test: Test features
            y_test: Test labels
            feature_names: Optional feature names
        
        Returns:
            Dictionary with evaluation metrics
        """
        logger.info("Evaluating model on test data")
        
        # Make predictions
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
            'f1_score': f1_score(y_test, y_pred, average='weighted', zero_division=0),
        }
        
        # ROC-AUC
        if len(np.unique(y_test)) == 2:
            metrics['roc_auc'] = roc_auc_score(y_test, y_pred_proba[:, 1])
            fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba[:, 1])
            metrics['roc_curve'] = {
                'fpr': fpr.tolist(),
                'tpr': tpr.tolist(),
                'thresholds': thresholds.tolist()
            }
        else:
            metrics['roc_auc'] = roc_auc_score(
                y_test, y_pred_proba,
                multi_class='ovr',
                average='weighted'
            )
        
        # Classification report
        metrics['classification_report'] = classification_report(
            y_test, y_pred, output_dict=True
        )
        
        # Confusion matrix
        metrics['confusion_matrix'] = confusion_matrix(y_test, y_pred).tolist()
        
        # Per-class metrics
        for i, class_metrics in enumerate(metrics['classification_report'].items()):
            if isinstance(class_metrics[1], dict):
                logger.info(f"Class {class_metrics[0]}: "
                           f"Precision={class_metrics[1].get('precision', 0):.4f}, "
                           f"Recall={class_metrics[1].get('recall', 0):.4f}, "
                           f"F1={class_metrics[1].get('f1-score', 0):.4f}")
        
        logger.info(f"Overall Accuracy: {metrics['accuracy']:.4f}")
        logger.info(f"Overall ROC-AUC: {metrics['roc_auc']:.4f}")
        
        return metrics
    
    def print_evaluation_summary(self, metrics: dict):
        """Print a formatted evaluation summary"""
        print("\n" + "=" * 60)
        print("Model Evaluation Summary")
        print("=" * 60)
        
        print(f"\nOverall Metrics:")
        print(f"  Accuracy:  {metrics['accuracy']:.4f}")
        print(f"  Precision: {metrics['precision']:.4f}")
        print(f"  Recall:    {metrics['recall']:.4f}")
        print(f"  F1 Score:  {metrics['f1_score']:.4f}")
        print(f"  ROC-AUC:   {metrics['roc_auc']:.4f}")
        
        print(f"\nConfusion Matrix:")
        cm = np.array(metrics['confusion_matrix'])
        print(cm)
        
        print(f"\nPer-Class Performance:")
        report = metrics['classification_report']
        for key, value in report.items():
            if isinstance(value, dict) and 'precision' in value:
                print(f"  Class {key}:")
                print(f"    Precision: {value['precision']:.4f}")
                print(f"    Recall:    {value['recall']:.4f}")
                print(f"    F1-Score:  {value['f1-score']:.4f}")
                print(f"    Support:   {value['support']}")
        
        print("\n" + "=" * 60 + "\n")
    
    def save_evaluation_results(
        self,
        metrics: dict,
        output_dir: str = None
    ):
        """
        Save evaluation results to files
        
        Args:
            metrics: Evaluation metrics dictionary
            output_dir: Directory to save results (defaults to ml/evaluations/)
        """
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(__file__), 'evaluations')
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save metrics as JSON
        metrics_path = output_dir / f'evaluation_metrics_{timestamp}.json'
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"Saved evaluation metrics to: {metrics_path}")
        
        # Save summary report
        report_path = output_dir / f'evaluation_summary_{timestamp}.txt'
        with open(report_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("Model Evaluation Report\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model: {self.model_path}\n\n")
            
            f.write("Overall Metrics:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Accuracy:  {metrics['accuracy']:.4f}\n")
            f.write(f"Precision: {metrics['precision']:.4f}\n")
            f.write(f"Recall:    {metrics['recall']:.4f}\n")
            f.write(f"F1 Score:  {metrics['f1_score']:.4f}\n")
            f.write(f"ROC-AUC:   {metrics['roc_auc']:.4f}\n\n")
            
            f.write("Confusion Matrix:\n")
            f.write("-" * 40 + "\n")
            f.write(str(metrics['confusion_matrix']) + "\n\n")
            
            f.write("Classification Report:\n")
            f.write("-" * 40 + "\n")
            report = metrics['classification_report']
            for key, value in report.items():
                if isinstance(value, dict):
                    f.write(f"\nClass {key}:\n")
                    for metric, score in value.items():
                        f.write(f"  {metric}: {score}\n")
        
        logger.info(f"Saved evaluation report to: {report_path}")
        
        return {
            'metrics_path': str(metrics_path),
            'report_path': str(report_path)
        }


def main():
    """Main function to run model evaluation"""
    parser = argparse.ArgumentParser(
        description='Evaluate a trained skill-based assignment model'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='ml/models/skill_assignment_model_latest.pkl',
        help='Path to trained model'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='ml/evaluations',
        help='Directory to save evaluation results'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize evaluator
        evaluator = ModelEvaluator(args.model)
        
        # Generate test data (in production, this would come from actual data)
        logger.info("Generating test data for evaluation")
        np.random.seed(42)
        n_samples = 100
        n_features = 17
        X_test = np.random.rand(n_samples, n_features)
        y_test = np.random.randint(0, 2, n_samples)
        
        # Evaluate
        metrics = evaluator.evaluate(X_test, y_test)
        
        # Print summary
        evaluator.print_evaluation_summary(metrics)
        
        # Save results
        paths = evaluator.save_evaluation_results(metrics, args.output_dir)
        
        print(f"Evaluation results saved to:")
        for key, path in paths.items():
            print(f"  {key}: {path}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    exit(main())
