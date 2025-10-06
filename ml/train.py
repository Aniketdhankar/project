"""
ML Training Pipeline for Skill-Based Assignment Model

This module implements a supervised learning training pipeline using scikit-learn
for the skill-based task assignment model. It extracts data from the database,
processes features, trains a classifier, evaluates performance, and saves artifacts.
"""

import os
import sys
import logging
import joblib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)

# Add parent directory to path to import from time_resource_allocation
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'time_resource_allocation', 'backend'))

try:
    from models.models import db, Employee, Task, TaskAssignment
    from scripts.feature_builder import get_feature_builder
except ImportError:
    # Fallback if imports fail
    db = None
    Employee = None
    Task = None
    TaskAssignment = None
    get_feature_builder = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SkillAssignmentTrainer:
    """
    Trainer for skill-based task assignment model using scikit-learn
    """
    
    def __init__(
        self,
        model_dir: str = None,
        random_state: int = 42
    ):
        """
        Initialize the trainer
        
        Args:
            model_dir: Directory to save trained models (defaults to ml/models/)
            random_state: Random state for reproducibility
        """
        if model_dir is None:
            model_dir = os.path.join(os.path.dirname(__file__), 'models')
        
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.random_state = random_state
        
        # Initialize feature builder if available
        self.feature_builder = get_feature_builder() if get_feature_builder else None
        
        # Model and preprocessing components
        self.imputer = SimpleImputer(strategy='mean')
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.model = None
        self.pipeline = None
        
        logger.info(f"Initialized SkillAssignmentTrainer with model_dir: {self.model_dir}")
    
    def extract_training_data(
        self,
        database_connection=None,
        use_sample_data: bool = True
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Extract and flatten feature/label data from the database
        
        Args:
            database_connection: Database connection object (if available)
            use_sample_data: Whether to use sample data if DB not available
        
        Returns:
            Tuple of (features DataFrame, labels Series)
        """
        logger.info("Extracting training data from database")
        
        if database_connection and not use_sample_data:
            # Extract from actual database
            try:
                return self._extract_from_db(database_connection)
            except Exception as e:
                logger.warning(f"Failed to extract from DB: {e}. Using sample data.")
                use_sample_data = True
        
        if use_sample_data:
            return self._generate_sample_data()
        
        raise ValueError("No data source available")
    
    def _extract_from_db(self, db_connection) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Extract training data from actual database
        
        Args:
            db_connection: Database connection
        
        Returns:
            Tuple of (features DataFrame, labels Series)
        """
        logger.info("Extracting from database using TaskAssignment records")
        
        # Query completed assignments with employee and task details
        if self.feature_builder:
            # Use feature builder to create dataset
            df = self.feature_builder.create_training_dataset(
                db_connection,
                include_gemini=False
            )
            
            # Split features and labels
            feature_cols = self.feature_builder.get_feature_names(include_gemini=False)
            X = df[feature_cols]
            y = df['label']
            
            logger.info(f"Extracted {len(X)} samples from database")
            return X, y
        else:
            # Fallback: create simple features from raw data
            logger.warning("Feature builder not available, using simple features")
            # This is a placeholder - would need actual DB query implementation
            return self._generate_sample_data()
    
    def _generate_sample_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Generate sample training data for testing/demonstration
        
        Returns:
            Tuple of (features DataFrame, labels Series)
        """
        logger.info("Generating sample training data")
        
        n_samples = 200
        n_features = 17  # Matching feature builder output
        
        # Generate synthetic features
        np.random.seed(self.random_state)
        
        # Create realistic feature distributions
        data = {
            'employee_experience': np.random.uniform(0, 1, n_samples),
            'employee_workload_ratio': np.random.uniform(0, 1, n_samples),
            'employee_availability': np.random.choice([0, 1], n_samples, p=[0.2, 0.8]),
            'employee_performance': np.random.uniform(0.5, 1.0, n_samples),
            'employee_active_tasks': np.random.uniform(0, 1, n_samples),
            'employee_avg_completion': np.random.uniform(0.3, 1.0, n_samples),
            'task_priority': np.random.uniform(0.25, 1.0, n_samples),
            'task_complexity': np.random.uniform(0.2, 1.0, n_samples),
            'task_estimated_hours': np.random.uniform(0, 1, n_samples),
            'task_time_pressure': np.random.uniform(0, 1, n_samples),
            'task_dependencies': np.random.uniform(0, 0.6, n_samples),
            'task_age': np.random.uniform(0, 0.8, n_samples),
            'skill_match_score': np.random.uniform(0.3, 1.0, n_samples),
            'experience_complexity_ratio': np.random.uniform(0.3, 1.0, n_samples),
            'workload_capacity_fit': np.random.uniform(0, 1, n_samples),
            'department_match': np.random.choice([0.5, 1.0], n_samples, p=[0.3, 0.7]),
            'historical_success_rate': np.random.uniform(0.5, 0.95, n_samples),
        }
        
        X = pd.DataFrame(data)
        
        # Generate labels based on feature combinations (simulating assignment success)
        # Success is more likely with:
        # - High skill match
        # - Good workload fit
        # - High experience
        # - Low complexity or high experience-complexity ratio
        success_score = (
            0.3 * X['skill_match_score'] +
            0.2 * X['experience_complexity_ratio'] +
            0.15 * X['workload_capacity_fit'] +
            0.15 * X['employee_performance'] +
            0.1 * X['historical_success_rate'] +
            0.1 * (1 - X['task_complexity'])
        )
        
        # Convert to binary labels (successful/unsuccessful assignment)
        threshold = success_score.median()
        y = (success_score > threshold).astype(int)
        
        # Add some noise
        noise_idx = np.random.choice(n_samples, size=int(0.1 * n_samples), replace=False)
        y.iloc[noise_idx] = 1 - y.iloc[noise_idx]
        
        logger.info(f"Generated {n_samples} samples with {n_features} features")
        logger.info(f"Label distribution: {y.value_counts().to_dict()}")
        
        return X, y
    
    def preprocess_features(
        self,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Preprocess features: impute missing values and scale
        
        Args:
            X_train: Training features
            X_test: Test features
        
        Returns:
            Tuple of (preprocessed X_train, preprocessed X_test)
        """
        logger.info("Preprocessing features (imputation and scaling)")
        
        # Impute missing values
        X_train_imputed = self.imputer.fit_transform(X_train)
        X_test_imputed = self.imputer.transform(X_test)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train_imputed)
        X_test_scaled = self.scaler.transform(X_test_imputed)
        
        logger.info(f"Preprocessed training shape: {X_train_scaled.shape}")
        logger.info(f"Preprocessed test shape: {X_test_scaled.shape}")
        
        return X_train_scaled, X_test_scaled
    
    def train_model(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        n_estimators: int = 100,
        max_depth: int = 10,
        min_samples_split: int = 5,
        **kwargs
    ) -> RandomForestClassifier:
        """
        Train RandomForest classifier
        
        Args:
            X_train: Training features
            y_train: Training labels
            n_estimators: Number of trees in the forest
            max_depth: Maximum depth of trees
            min_samples_split: Minimum samples required to split
            **kwargs: Additional RandomForest parameters
        
        Returns:
            Trained RandomForestClassifier
        """
        logger.info("Training RandomForest classifier")
        logger.info(f"Parameters: n_estimators={n_estimators}, max_depth={max_depth}, "
                   f"min_samples_split={min_samples_split}")
        
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=self.random_state,
            n_jobs=-1,
            **kwargs
        )
        
        self.model.fit(X_train, y_train)
        
        logger.info("Model training completed")
        return self.model
    
    def evaluate_model(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray,
        feature_names: list = None
    ) -> Dict:
        """
        Evaluate model performance with multiple metrics
        
        Args:
            X_test: Test features
            y_test: Test labels
            feature_names: Names of features for importance ranking
        
        Returns:
            Dictionary with evaluation metrics
        """
        logger.info("Evaluating model performance")
        
        if self.model is None:
            raise ValueError("Model not trained yet")
        
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
        
        # ROC-AUC (for binary classification)
        if len(np.unique(y_test)) == 2:
            metrics['roc_auc'] = roc_auc_score(y_test, y_pred_proba[:, 1])
        else:
            metrics['roc_auc'] = roc_auc_score(
                y_test, y_pred_proba, 
                multi_class='ovr', average='weighted'
            )
        
        # Classification report
        metrics['classification_report'] = classification_report(
            y_test, y_pred, output_dict=True
        )
        
        # Confusion matrix
        metrics['confusion_matrix'] = confusion_matrix(y_test, y_pred).tolist()
        
        # Feature importance
        if feature_names is not None:
            importances = self.model.feature_importances_
            feature_importance = dict(zip(feature_names, importances))
            # Sort by importance
            feature_importance = dict(
                sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            )
            metrics['feature_importance'] = feature_importance
        
        # Log key metrics
        logger.info(f"Accuracy: {metrics['accuracy']:.4f}")
        logger.info(f"Precision: {metrics['precision']:.4f}")
        logger.info(f"Recall: {metrics['recall']:.4f}")
        logger.info(f"F1 Score: {metrics['f1_score']:.4f}")
        logger.info(f"ROC-AUC: {metrics['roc_auc']:.4f}")
        
        return metrics
    
    def perform_cross_validation(
        self,
        X: np.ndarray,
        y: np.ndarray,
        cv: int = 5
    ) -> Dict:
        """
        Perform cross-validation to assess model stability
        
        Args:
            X: Features
            y: Labels
            cv: Number of cross-validation folds
        
        Returns:
            Dictionary with cross-validation results
        """
        logger.info(f"Performing {cv}-fold cross-validation")
        
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        cv_scores = cross_val_score(
            self.model, X, y, 
            cv=cv, 
            scoring='accuracy',
            n_jobs=-1
        )
        
        results = {
            'cv_scores': cv_scores.tolist(),
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }
        
        logger.info(f"CV Accuracy: {results['cv_mean']:.4f} (+/- {results['cv_std']:.4f})")
        
        return results
    
    def save_model(
        self,
        metrics: Dict,
        feature_names: list = None
    ) -> Dict[str, str]:
        """
        Save model, preprocessing pipeline, and metadata
        
        Args:
            metrics: Evaluation metrics to save
            feature_names: Feature names for reference
        
        Returns:
            Dictionary with paths to saved artifacts
        """
        logger.info("Saving model and artifacts")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save the complete preprocessing + model pipeline
        pipeline = Pipeline([
            ('imputer', self.imputer),
            ('scaler', self.scaler),
            ('classifier', self.model)
        ])
        
        model_path = self.model_dir / f'skill_assignment_model_{timestamp}.pkl'
        joblib.dump(pipeline, model_path)
        logger.info(f"Saved model pipeline to: {model_path}")
        
        # Also save as latest for easy access
        latest_model_path = self.model_dir / 'skill_assignment_model_latest.pkl'
        joblib.dump(pipeline, latest_model_path)
        logger.info(f"Saved model as latest: {latest_model_path}")
        
        # Save metadata
        metadata = {
            'timestamp': timestamp,
            'model_type': 'RandomForestClassifier',
            'sklearn_version': joblib.__version__,
            'metrics': metrics,
            'feature_names': feature_names,
            'model_params': self.model.get_params()
        }
        
        metadata_path = self.model_dir / f'model_metadata_{timestamp}.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved metadata to: {metadata_path}")
        
        # Save feature names separately for reference
        if feature_names:
            feature_path = self.model_dir / 'feature_names.txt'
            with open(feature_path, 'w') as f:
                f.write('\n'.join(feature_names))
            logger.info(f"Saved feature names to: {feature_path}")
        
        # Save evaluation report
        report_path = self.model_dir / f'evaluation_report_{timestamp}.txt'
        self._save_evaluation_report(report_path, metrics)
        logger.info(f"Saved evaluation report to: {report_path}")
        
        return {
            'model_path': str(model_path),
            'latest_model_path': str(latest_model_path),
            'metadata_path': str(metadata_path),
            'report_path': str(report_path)
        }
    
    def _save_evaluation_report(self, path: Path, metrics: Dict):
        """Save a human-readable evaluation report"""
        with open(path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("Skill-Based Assignment Model - Evaluation Report\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("Model Performance Metrics:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Accuracy:  {metrics['accuracy']:.4f}\n")
            f.write(f"Precision: {metrics['precision']:.4f}\n")
            f.write(f"Recall:    {metrics['recall']:.4f}\n")
            f.write(f"F1 Score:  {metrics['f1_score']:.4f}\n")
            f.write(f"ROC-AUC:   {metrics['roc_auc']:.4f}\n\n")
            
            if 'cv_mean' in metrics:
                f.write("Cross-Validation Results:\n")
                f.write("-" * 40 + "\n")
                f.write(f"CV Mean Accuracy: {metrics['cv_mean']:.4f}\n")
                f.write(f"CV Std Dev:       {metrics['cv_std']:.4f}\n\n")
            
            if 'feature_importance' in metrics:
                f.write("Top 10 Feature Importances:\n")
                f.write("-" * 40 + "\n")
                for i, (feat, imp) in enumerate(list(metrics['feature_importance'].items())[:10], 1):
                    f.write(f"{i:2d}. {feat:30s} {imp:.4f}\n")
                f.write("\n")
            
            f.write("Confusion Matrix:\n")
            f.write("-" * 40 + "\n")
            f.write(str(metrics['confusion_matrix']) + "\n\n")
            
            f.write("=" * 60 + "\n")
    
    def train_pipeline(
        self,
        database_connection=None,
        use_sample_data: bool = True,
        test_size: float = 0.2,
        perform_cv: bool = True
    ) -> Dict:
        """
        Run the complete training pipeline
        
        Args:
            database_connection: Database connection (optional)
            use_sample_data: Whether to use sample data
            test_size: Fraction of data to use for testing
            perform_cv: Whether to perform cross-validation
        
        Returns:
            Dictionary with training results and artifact paths
        """
        logger.info("Starting ML training pipeline")
        logger.info("=" * 60)
        
        # Step 1: Extract data
        X, y = self.extract_training_data(database_connection, use_sample_data)
        feature_names = list(X.columns) if isinstance(X, pd.DataFrame) else None
        
        # Step 2: Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state, stratify=y
        )
        logger.info(f"Split data: {len(X_train)} train, {len(X_test)} test samples")
        
        # Step 3: Preprocess
        X_train_processed, X_test_processed = self.preprocess_features(X_train, X_test)
        
        # Step 4: Train model
        self.train_model(X_train_processed, y_train)
        
        # Step 5: Evaluate
        metrics = self.evaluate_model(X_test_processed, y_test, feature_names)
        
        # Step 6: Cross-validation (optional)
        if perform_cv:
            cv_results = self.perform_cross_validation(X_train_processed, y_train)
            metrics.update(cv_results)
        
        # Step 7: Save artifacts
        artifact_paths = self.save_model(metrics, feature_names)
        
        logger.info("=" * 60)
        logger.info("Training pipeline completed successfully!")
        
        return {
            'metrics': metrics,
            'artifact_paths': artifact_paths,
            'n_train_samples': len(X_train),
            'n_test_samples': len(X_test),
            'n_features': X_train.shape[1]
        }


def main():
    """Main function to run the training pipeline"""
    logger.info("Starting Skill-Based Assignment Model Training")
    
    # Initialize trainer
    trainer = SkillAssignmentTrainer()
    
    # Run training pipeline
    try:
        results = trainer.train_pipeline(
            database_connection=None,
            use_sample_data=True,
            test_size=0.2,
            perform_cv=True
        )
        
        print("\n" + "=" * 60)
        print("Training Complete!")
        print("=" * 60)
        print(f"\nModel Performance:")
        print(f"  Accuracy:  {results['metrics']['accuracy']:.4f}")
        print(f"  Precision: {results['metrics']['precision']:.4f}")
        print(f"  Recall:    {results['metrics']['recall']:.4f}")
        print(f"  F1 Score:  {results['metrics']['f1_score']:.4f}")
        print(f"  ROC-AUC:   {results['metrics']['roc_auc']:.4f}")
        
        if 'cv_mean' in results['metrics']:
            print(f"\nCross-Validation:")
            print(f"  Mean Accuracy: {results['metrics']['cv_mean']:.4f} "
                  f"(+/- {results['metrics']['cv_std']:.4f})")
        
        print(f"\nArtifacts saved to:")
        for key, path in results['artifact_paths'].items():
            print(f"  {key}: {path}")
        
        print("\n" + "=" * 60 + "\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    exit(main())
