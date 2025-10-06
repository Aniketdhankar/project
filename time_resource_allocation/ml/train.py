"""
ML Training Pipeline for Skill-Based Assignment Model

This module implements a scikit-learn-based training pipeline for the 
supervised skill assignment model. It handles:
- Data extraction from ModelTrainingRow
- Feature preprocessing (imputation, scaling, encoding)
- Model training (RandomForest classifier)
- Model evaluation (accuracy, ROC-AUC, etc.)
- Model persistence with joblib
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional

import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    mean_squared_error,
    r2_score,
    mean_absolute_error
)

# Add backend path to import models
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

try:
    from models.models import db, ModelTrainingRow, Employee, Task, TaskAssignment
    from flask import Flask
    from config.config import Config
except ImportError as e:
    logging.warning(f"Could not import Flask models: {e}. Using standalone mode.")
    db = None
    ModelTrainingRow = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SkillAssignmentTrainer:
    """Trainer for skill-based assignment model using scikit-learn"""
    
    def __init__(self, model_dir: str = None):
        """
        Initialize the trainer
        
        Args:
            model_dir: Directory to save trained models (default: ../ml_models/trained)
        """
        if model_dir is None:
            model_dir = Path(__file__).parent.parent / 'ml_models' / 'trained'
        
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.model = None
        self.preprocessor = None
        self.label_encoder = None
        self.feature_names = []
        self.metrics = {}
        
        logger.info(f"Initialized trainer. Models will be saved to: {self.model_dir}")
    
    def extract_training_data(
        self, 
        database_connection=None,
        min_samples: int = 50
    ) -> pd.DataFrame:
        """
        Extract and flatten training data from ModelTrainingRow table
        
        Args:
            database_connection: Database connection (Flask app context)
            min_samples: Minimum samples to generate if DB is empty
            
        Returns:
            DataFrame with features and labels
        """
        logger.info("Extracting training data from database...")
        
        # Try to fetch from database if available
        if database_connection and ModelTrainingRow:
            try:
                from flask import current_app
                with current_app.app_context():
                    rows = ModelTrainingRow.query.all()
                    
                    if rows:
                        logger.info(f"Found {len(rows)} training rows in database")
                        data = [row.to_dict() for row in rows]
                        df = pd.DataFrame(data)
                        return df
                    else:
                        logger.warning("No training data found in database. Generating sample data.")
            except Exception as e:
                logger.warning(f"Error fetching from database: {e}. Using sample data.")
        
        # Generate sample training data
        logger.info(f"Generating {min_samples} sample training rows...")
        sample_data = self._generate_sample_data(min_samples)
        
        return sample_data
    
    def _generate_sample_data(self, n_samples: int = 100) -> pd.DataFrame:
        """Generate sample training data for demonstration"""
        np.random.seed(42)
        
        data = {
            # Employee features
            'emp_experience_years': np.random.uniform(0.5, 15, n_samples),
            'emp_workload_ratio': np.random.uniform(0.1, 0.95, n_samples),
            'emp_performance_rating': np.random.uniform(2.0, 5.0, n_samples),
            'emp_active_tasks': np.random.randint(0, 10, n_samples),
            'emp_availability': np.random.choice(['available', 'busy', 'limited'], n_samples),
            
            # Task features
            'task_priority': np.random.choice(['low', 'medium', 'high', 'critical'], n_samples),
            'task_complexity_score': np.random.uniform(1.0, 5.0, n_samples),
            'task_estimated_hours': np.random.uniform(2, 80, n_samples),
            'task_urgency_score': np.random.uniform(0.1, 1.0, n_samples),
            
            # Interaction features
            'skill_match_score': np.random.uniform(0.3, 1.0, n_samples),
            'workload_compatibility': np.random.uniform(0.2, 1.0, n_samples),
        }
        
        df = pd.DataFrame(data)
        
        # Generate labels based on features (synthetic relationship)
        # Success score is influenced by skill match, workload, and experience
        df['success_score'] = (
            0.4 * df['skill_match_score'] +
            0.3 * (1 - df['emp_workload_ratio']) +
            0.2 * (df['emp_experience_years'] / 15) +
            0.1 * (df['emp_performance_rating'] / 5) +
            np.random.normal(0, 0.1, n_samples)  # Add noise
        ).clip(0, 1)
        
        # Binary success label (threshold at 0.6)
        df['completed_on_time'] = (df['success_score'] > 0.6).astype(int)
        
        logger.info(f"Generated {len(df)} sample training rows")
        logger.info(f"Success rate: {df['completed_on_time'].mean():.2%}")
        
        return df
    
    def preprocess_features(
        self, 
        df: pd.DataFrame, 
        fit: bool = True
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Preprocess features with imputation, scaling, and encoding
        
        Args:
            df: DataFrame with raw features
            fit: Whether to fit the preprocessor (True for training, False for inference)
            
        Returns:
            Tuple of (processed features, labels)
        """
        logger.info("Preprocessing features...")
        
        # Define feature columns
        numeric_features = [
            'emp_experience_years',
            'emp_workload_ratio', 
            'emp_performance_rating',
            'emp_active_tasks',
            'task_complexity_score',
            'task_estimated_hours',
            'task_urgency_score',
            'skill_match_score',
            'workload_compatibility'
        ]
        
        categorical_features = [
            'emp_availability',
            'task_priority'
        ]
        
        # Store feature names
        self.feature_names = numeric_features + categorical_features
        
        # Extract features and labels
        X = df[self.feature_names].copy()
        
        # Handle labels
        if 'completed_on_time' in df.columns:
            y = df['completed_on_time'].values
        elif 'success_score' in df.columns:
            # Convert continuous success score to binary
            y = (df['success_score'] > 0.6).astype(int).values
        else:
            raise ValueError("No label column found (completed_on_time or success_score)")
        
        # Create preprocessing pipeline
        if fit or self.preprocessor is None:
            numeric_transformer = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler())
            ])
            
            categorical_transformer = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
            ])
            
            self.preprocessor = ColumnTransformer(
                transformers=[
                    ('num', numeric_transformer, numeric_features),
                    ('cat', categorical_transformer, categorical_features)
                ],
                verbose_feature_names_out=False
            )
            
            X_processed = self.preprocessor.fit_transform(X)
            logger.info(f"Fitted preprocessor on {X.shape[0]} samples")
        else:
            X_processed = self.preprocessor.transform(X)
            logger.info(f"Transformed {X.shape[0]} samples")
        
        logger.info(f"Processed features shape: {X_processed.shape}")
        logger.info(f"Label distribution: {np.bincount(y)}")
        
        return X_processed, y
    
    def train_model(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        use_grid_search: bool = False
    ) -> Dict:
        """
        Train RandomForest classifier
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_test: Test features
            y_test: Test labels
            use_grid_search: Whether to use grid search for hyperparameter tuning
            
        Returns:
            Dictionary with model and training metrics
        """
        logger.info("Training RandomForest classifier...")
        
        if use_grid_search:
            logger.info("Using grid search for hyperparameter tuning...")
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
            
            base_model = RandomForestClassifier(random_state=42, n_jobs=-1)
            grid_search = GridSearchCV(
                base_model,
                param_grid,
                cv=3,
                scoring='roc_auc',
                n_jobs=-1,
                verbose=1
            )
            
            grid_search.fit(X_train, y_train)
            self.model = grid_search.best_estimator_
            logger.info(f"Best parameters: {grid_search.best_params_}")
        else:
            # Use default parameters with reasonable settings
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
                class_weight='balanced'  # Handle imbalanced classes
            )
            
            self.model.fit(X_train, y_train)
        
        logger.info("Model training complete")
        
        # Evaluate model
        metrics = self.evaluate_model(X_train, y_train, X_test, y_test)
        self.metrics = metrics
        
        return metrics
    
    def evaluate_model(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict:
        """
        Evaluate model with comprehensive metrics
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_test: Test features
            y_test: Test labels
            
        Returns:
            Dictionary with evaluation metrics
        """
        logger.info("Evaluating model...")
        
        # Predictions
        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)
        
        # Prediction probabilities for ROC-AUC
        y_train_proba = self.model.predict_proba(X_train)[:, 1]
        y_test_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        metrics = {
            'train': {
                'accuracy': accuracy_score(y_train, y_train_pred),
                'precision': precision_score(y_train, y_train_pred, zero_division=0),
                'recall': recall_score(y_train, y_train_pred, zero_division=0),
                'f1': f1_score(y_train, y_train_pred, zero_division=0),
                'roc_auc': roc_auc_score(y_train, y_train_proba)
            },
            'test': {
                'accuracy': accuracy_score(y_test, y_test_pred),
                'precision': precision_score(y_test, y_test_pred, zero_division=0),
                'recall': recall_score(y_test, y_test_pred, zero_division=0),
                'f1': f1_score(y_test, y_test_pred, zero_division=0),
                'roc_auc': roc_auc_score(y_test, y_test_proba)
            },
            'confusion_matrix': confusion_matrix(y_test, y_test_pred).tolist(),
            'feature_importance': self._get_feature_importance()
        }
        
        # Cross-validation score
        cv_scores = cross_val_score(
            self.model, X_train, y_train, cv=5, scoring='roc_auc'
        )
        metrics['cv_roc_auc_mean'] = cv_scores.mean()
        metrics['cv_roc_auc_std'] = cv_scores.std()
        
        # Log results
        logger.info("\nTraining Metrics:")
        logger.info(f"  Accuracy:  {metrics['train']['accuracy']:.4f}")
        logger.info(f"  Precision: {metrics['train']['precision']:.4f}")
        logger.info(f"  Recall:    {metrics['train']['recall']:.4f}")
        logger.info(f"  F1 Score:  {metrics['train']['f1']:.4f}")
        logger.info(f"  ROC-AUC:   {metrics['train']['roc_auc']:.4f}")
        
        logger.info("\nTest Metrics:")
        logger.info(f"  Accuracy:  {metrics['test']['accuracy']:.4f}")
        logger.info(f"  Precision: {metrics['test']['precision']:.4f}")
        logger.info(f"  Recall:    {metrics['test']['recall']:.4f}")
        logger.info(f"  F1 Score:  {metrics['test']['f1']:.4f}")
        logger.info(f"  ROC-AUC:   {metrics['test']['roc_auc']:.4f}")
        
        logger.info(f"\nCross-validation ROC-AUC: {metrics['cv_roc_auc_mean']:.4f} (+/- {metrics['cv_roc_auc_std']:.4f})")
        
        return metrics
    
    def _get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from the trained model"""
        if self.model is None:
            return {}
        
        # Get feature names after preprocessing
        feature_names_out = self.preprocessor.get_feature_names_out()
        
        # Get importances
        importances = self.model.feature_importances_
        
        # Create dictionary
        importance_dict = dict(zip(feature_names_out, importances))
        
        # Sort by importance
        importance_dict = dict(
            sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        )
        
        return importance_dict
    
    def save_model(self, model_name: str = 'skill_assignment_model') -> Dict[str, str]:
        """
        Save trained model and preprocessor with joblib
        
        Args:
            model_name: Name for the saved model files
            
        Returns:
            Dictionary with paths to saved files
        """
        logger.info(f"Saving model to {self.model_dir}...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save model
        model_path = self.model_dir / f'{model_name}_{timestamp}.pkl'
        joblib.dump(self.model, model_path)
        logger.info(f"  Model saved to: {model_path}")
        
        # Save preprocessor
        preprocessor_path = self.model_dir / f'{model_name}_preprocessor_{timestamp}.pkl'
        joblib.dump(self.preprocessor, preprocessor_path)
        logger.info(f"  Preprocessor saved to: {preprocessor_path}")
        
        # Save feature names
        feature_names_path = self.model_dir / f'{model_name}_features_{timestamp}.txt'
        with open(feature_names_path, 'w') as f:
            f.write('\n'.join(self.feature_names))
        logger.info(f"  Feature names saved to: {feature_names_path}")
        
        # Save metrics
        metrics_path = self.model_dir / f'{model_name}_metrics_{timestamp}.json'
        import json
        with open(metrics_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        logger.info(f"  Metrics saved to: {metrics_path}")
        
        # Save latest model (without timestamp) for easy loading
        latest_model_path = self.model_dir / f'{model_name}_latest.pkl'
        latest_preprocessor_path = self.model_dir / f'{model_name}_preprocessor_latest.pkl'
        
        joblib.dump(self.model, latest_model_path)
        joblib.dump(self.preprocessor, latest_preprocessor_path)
        logger.info(f"  Latest model symlinks created")
        
        return {
            'model_path': str(model_path),
            'preprocessor_path': str(preprocessor_path),
            'feature_names_path': str(feature_names_path),
            'metrics_path': str(metrics_path),
            'latest_model_path': str(latest_model_path),
            'latest_preprocessor_path': str(latest_preprocessor_path)
        }
    
    def load_model(self, model_name: str = 'skill_assignment_model', version: str = 'latest'):
        """
        Load a saved model and preprocessor
        
        Args:
            model_name: Name of the model to load
            version: Version to load ('latest' or timestamp)
        """
        logger.info(f"Loading model {model_name} (version: {version})...")
        
        if version == 'latest':
            model_path = self.model_dir / f'{model_name}_latest.pkl'
            preprocessor_path = self.model_dir / f'{model_name}_preprocessor_latest.pkl'
        else:
            model_path = self.model_dir / f'{model_name}_{version}.pkl'
            preprocessor_path = self.model_dir / f'{model_name}_preprocessor_{version}.pkl'
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        self.model = joblib.load(model_path)
        self.preprocessor = joblib.load(preprocessor_path)
        
        logger.info(f"  Model loaded from: {model_path}")
        logger.info(f"  Preprocessor loaded from: {preprocessor_path}")
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions on new data
        
        Args:
            X: DataFrame with features
            
        Returns:
            Array of predictions
        """
        if self.model is None or self.preprocessor is None:
            raise ValueError("Model not trained or loaded. Call train_model() or load_model() first.")
        
        X_processed = self.preprocessor.transform(X[self.feature_names])
        predictions = self.model.predict(X_processed)
        
        return predictions
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make probability predictions on new data
        
        Args:
            X: DataFrame with features
            
        Returns:
            Array of prediction probabilities
        """
        if self.model is None or self.preprocessor is None:
            raise ValueError("Model not trained or loaded. Call train_model() or load_model() first.")
        
        X_processed = self.preprocessor.transform(X[self.feature_names])
        probabilities = self.model.predict_proba(X_processed)
        
        return probabilities


def train_pipeline(
    database_connection=None,
    use_grid_search: bool = False,
    test_size: float = 0.2,
    random_state: int = 42
) -> SkillAssignmentTrainer:
    """
    Complete training pipeline
    
    Args:
        database_connection: Database connection for data extraction
        use_grid_search: Whether to use grid search for hyperparameter tuning
        test_size: Proportion of data to use for testing
        random_state: Random seed for reproducibility
        
    Returns:
        Trained SkillAssignmentTrainer instance
    """
    logger.info("=" * 80)
    logger.info("Starting ML Training Pipeline for Skill-Based Assignment Model")
    logger.info("=" * 80)
    
    # Initialize trainer
    trainer = SkillAssignmentTrainer()
    
    # Extract training data
    df = trainer.extract_training_data(database_connection)
    logger.info(f"Extracted {len(df)} training samples")
    
    # Preprocess features
    X, y = trainer.preprocess_features(df, fit=True)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    logger.info(f"Split data: {len(X_train)} train, {len(X_test)} test")
    
    # Train model
    metrics = trainer.train_model(X_train, y_train, X_test, y_test, use_grid_search)
    
    # Save model
    saved_paths = trainer.save_model()
    
    logger.info("\n" + "=" * 80)
    logger.info("Training Pipeline Complete!")
    logger.info("=" * 80)
    logger.info(f"Model saved to: {saved_paths['latest_model_path']}")
    logger.info(f"Test ROC-AUC: {metrics['test']['roc_auc']:.4f}")
    logger.info(f"Test Accuracy: {metrics['test']['accuracy']:.4f}")
    
    return trainer


def main():
    """Main entry point for training"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Train skill-based assignment model')
    parser.add_argument('--grid-search', action='store_true', 
                        help='Use grid search for hyperparameter tuning')
    parser.add_argument('--test-size', type=float, default=0.2,
                        help='Test set size (default: 0.2)')
    parser.add_argument('--samples', type=int, default=100,
                        help='Number of samples to generate if DB is empty (default: 100)')
    
    args = parser.parse_args()
    
    # Run training pipeline
    trainer = train_pipeline(
        database_connection=None,
        use_grid_search=args.grid_search,
        test_size=args.test_size
    )
    
    logger.info("\nTraining completed successfully!")


if __name__ == '__main__':
    main()
