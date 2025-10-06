"""
Model Evaluation Script

Evaluates saved models on test data and generates detailed reports.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
import argparse

import numpy as np
import pandas as pd
import joblib
import json

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    roc_auc_score,
    roc_curve,
    confusion_matrix,
    classification_report
)

# Import trainer
from train import SkillAssignmentTrainer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluates trained models and generates reports"""
    
    def __init__(self, model_dir: str = None):
        """
        Initialize evaluator
        
        Args:
            model_dir: Directory containing trained models
        """
        if model_dir is None:
            model_dir = Path(__file__).parent.parent / 'ml_models' / 'trained'
        
        self.model_dir = Path(model_dir)
        self.trainer = SkillAssignmentTrainer(model_dir=str(self.model_dir))
        
    def load_and_evaluate(
        self,
        model_name: str = 'skill_assignment_model',
        version: str = 'latest',
        test_data: pd.DataFrame = None
    ) -> dict:
        """
        Load model and evaluate on test data
        
        Args:
            model_name: Name of the model to evaluate
            version: Version to load ('latest' or timestamp)
            test_data: Test data (if None, generates sample data)
            
        Returns:
            Dictionary with evaluation metrics
        """
        logger.info(f"Loading model: {model_name} (version: {version})")
        
        # Load model
        self.trainer.load_model(model_name, version)
        
        # Get test data
        if test_data is None:
            logger.info("Generating sample test data...")
            test_data = self.trainer._generate_sample_data(n_samples=200)
        
        logger.info(f"Evaluating on {len(test_data)} samples")
        
        # Preprocess
        X, y = self.trainer.preprocess_features(test_data, fit=False)
        
        # Make predictions
        y_pred = self.trainer.model.predict(X)
        y_proba = self.trainer.model.predict_proba(X)[:, 1]
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y, y_pred),
            'precision': precision_recall_fscore_support(y, y_pred, average='binary')[0],
            'recall': precision_recall_fscore_support(y, y_pred, average='binary')[1],
            'f1': precision_recall_fscore_support(y, y_pred, average='binary')[2],
            'roc_auc': roc_auc_score(y, y_proba),
            'confusion_matrix': confusion_matrix(y, y_pred).tolist(),
            'classification_report': classification_report(y, y_pred, output_dict=True)
        }
        
        # ROC curve points
        fpr, tpr, thresholds = roc_curve(y, y_proba)
        metrics['roc_curve'] = {
            'fpr': fpr.tolist(),
            'tpr': tpr.tolist(),
            'thresholds': thresholds.tolist()
        }
        
        # Feature importance
        if hasattr(self.trainer.model, 'feature_importances_'):
            importance = self.trainer._get_feature_importance()
            metrics['feature_importance'] = importance
        
        return metrics
    
    def generate_report(
        self,
        metrics: dict,
        output_path: str = None
    ) -> str:
        """
        Generate evaluation report
        
        Args:
            metrics: Dictionary with evaluation metrics
            output_path: Path to save report (default: auto-generated)
            
        Returns:
            Path to saved report
        """
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.model_dir / f'evaluation_report_{timestamp}.txt'
        
        logger.info(f"Generating evaluation report: {output_path}")
        
        with open(output_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("MODEL EVALUATION REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model Directory: {self.model_dir}\n\n")
            
            f.write("-" * 80 + "\n")
            f.write("PERFORMANCE METRICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Accuracy:  {metrics['accuracy']:.4f}\n")
            f.write(f"Precision: {metrics['precision']:.4f}\n")
            f.write(f"Recall:    {metrics['recall']:.4f}\n")
            f.write(f"F1 Score:  {metrics['f1']:.4f}\n")
            f.write(f"ROC-AUC:   {metrics['roc_auc']:.4f}\n\n")
            
            f.write("-" * 80 + "\n")
            f.write("CONFUSION MATRIX\n")
            f.write("-" * 80 + "\n")
            cm = metrics['confusion_matrix']
            f.write(f"True Negatives:  {cm[0][0]:5d}  |  False Positives: {cm[0][1]:5d}\n")
            f.write(f"False Negatives: {cm[1][0]:5d}  |  True Positives:  {cm[1][1]:5d}\n\n")
            
            f.write("-" * 80 + "\n")
            f.write("CLASSIFICATION REPORT\n")
            f.write("-" * 80 + "\n")
            cr = metrics['classification_report']
            for label, scores in cr.items():
                if isinstance(scores, dict):
                    f.write(f"\nClass {label}:\n")
                    for metric, value in scores.items():
                        f.write(f"  {metric:12s}: {value:.4f}\n")
            
            if 'feature_importance' in metrics:
                f.write("\n" + "-" * 80 + "\n")
                f.write("TOP 10 IMPORTANT FEATURES\n")
                f.write("-" * 80 + "\n")
                for i, (feature, importance) in enumerate(
                    list(metrics['feature_importance'].items())[:10], 1
                ):
                    f.write(f"{i:2d}. {feature:40s}: {importance:.6f}\n")
            
            f.write("\n" + "=" * 80 + "\n")
        
        logger.info(f"Report saved to: {output_path}")
        
        # Also save JSON version
        json_path = str(output_path).replace('.txt', '.json')
        with open(json_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"JSON metrics saved to: {json_path}")
        
        return str(output_path)
    
    def compare_models(
        self,
        model_versions: list,
        model_name: str = 'skill_assignment_model',
        test_data: pd.DataFrame = None
    ) -> pd.DataFrame:
        """
        Compare multiple model versions
        
        Args:
            model_versions: List of version strings to compare
            model_name: Name of the model
            test_data: Test data for evaluation
            
        Returns:
            DataFrame with comparison results
        """
        logger.info(f"Comparing {len(model_versions)} model versions...")
        
        results = []
        
        for version in model_versions:
            try:
                logger.info(f"Evaluating version: {version}")
                metrics = self.load_and_evaluate(model_name, version, test_data)
                
                results.append({
                    'version': version,
                    'accuracy': metrics['accuracy'],
                    'precision': metrics['precision'],
                    'recall': metrics['recall'],
                    'f1': metrics['f1'],
                    'roc_auc': metrics['roc_auc']
                })
            except Exception as e:
                logger.error(f"Error evaluating version {version}: {e}")
        
        df = pd.DataFrame(results)
        
        # Save comparison
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        comparison_path = self.model_dir / f'model_comparison_{timestamp}.csv'
        df.to_csv(comparison_path, index=False)
        logger.info(f"Comparison saved to: {comparison_path}")
        
        return df


def main():
    """Main entry point for evaluation"""
    parser = argparse.ArgumentParser(description='Evaluate trained models')
    parser.add_argument('--model-name', type=str, default='skill_assignment_model',
                        help='Name of the model to evaluate')
    parser.add_argument('--version', type=str, default='latest',
                        help='Version to evaluate (latest or timestamp)')
    parser.add_argument('--samples', type=int, default=200,
                        help='Number of test samples to generate (default: 200)')
    parser.add_argument('--compare', action='store_true',
                        help='Compare multiple versions')
    parser.add_argument('--versions', nargs='+',
                        help='List of versions to compare')
    
    args = parser.parse_args()
    
    evaluator = ModelEvaluator()
    
    if args.compare and args.versions:
        # Compare multiple versions
        df = evaluator.compare_models(args.versions, args.model_name)
        print("\nModel Comparison:")
        print(df.to_string(index=False))
    else:
        # Evaluate single model
        metrics = evaluator.load_and_evaluate(
            args.model_name,
            args.version
        )
        
        # Generate report
        report_path = evaluator.generate_report(metrics)
        
        # Print summary
        print("\n" + "=" * 80)
        print("EVALUATION SUMMARY")
        print("=" * 80)
        print(f"Accuracy:  {metrics['accuracy']:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall:    {metrics['recall']:.4f}")
        print(f"F1 Score:  {metrics['f1']:.4f}")
        print(f"ROC-AUC:   {metrics['roc_auc']:.4f}")
        print(f"\nFull report: {report_path}")


if __name__ == '__main__':
    main()
