"""
Model Training Module
Trains LightGBM models for employee-task scoring, priority classification, and ETA prediction
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
import joblib
import logging
from datetime import datetime
from pathlib import Path

import lightgbm as lgb
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report

from feature_builder import get_feature_builder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """Handles training of ML models"""
    
    def __init__(self, model_dir: str = '../ml_models/trained'):
        """
        Initialize model trainer
        
        Args:
            model_dir: Directory to save trained models
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.feature_builder = get_feature_builder()
        
        # Model configurations
        self.scorer_params = {
            'objective': 'regression',
            'metric': 'rmse',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1
        }
        
        self.classifier_params = {
            'objective': 'multiclass',
            'num_class': 3,  # low, medium, high
            'metric': 'multi_logloss',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'verbose': -1
        }
        
        self.eta_params = {
            'objective': 'regression',
            'metric': 'rmse',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'verbose': -1
        }
    
    def train_scoring_model(
        self,
        database_connection,
        include_gemini: bool = False
    ) -> Dict:
        """
        Train employee-task scoring model
        
        Args:
            database_connection: Database connection object
            include_gemini: Whether to include Gemini features
        
        Returns:
            Dictionary with model and metrics
        """
        logger.info("Training employee-task scoring model")
        
        # Build training dataset
        df = self.feature_builder.create_training_dataset(
            database_connection,
            include_gemini
        )
        
        # Split features and labels
        feature_names = self.feature_builder.get_feature_names(include_gemini)
        X = df[feature_names].values
        y = df['label'].values
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Create LightGBM dataset
        train_data = lgb.Dataset(X_train, label=y_train)
        test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
        
        # Train model
        logger.info("Training LightGBM scoring model...")
        model = lgb.train(
            self.scorer_params,
            train_data,
            num_boost_round=100,
            valid_sets=[test_data],
            callbacks=[lgb.early_stopping(stopping_rounds=10)]
        )
        
        # Evaluate
        y_pred = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        logger.info(f"Scoring model RMSE: {rmse:.4f}")
        
        # Save model
        model_path = self.model_dir / 'scoring_model.txt'
        model.save_model(str(model_path))
        logger.info(f"Model saved to {model_path}")
        
        # Save feature names
        feature_path = self.model_dir / 'scoring_features.txt'
        with open(feature_path, 'w') as f:
            f.write('\n'.join(feature_names))
        
        return {
            'model': model,
            'rmse': rmse,
            'feature_importance': dict(zip(
                feature_names,
                model.feature_importance()
            )),
            'model_path': str(model_path)
        }
    
    def train_priority_classifier(
        self,
        database_connection
    ) -> Dict:
        """
        Train task priority classification model
        
        Args:
            database_connection: Database connection object
        
        Returns:
            Dictionary with model and metrics
        """
        logger.info("Training priority classification model")
        
        # TODO: Fetch actual data from database
        # For now, create sample data
        X_train, y_train = self._create_sample_classification_data(100)
        X_test, y_test = self._create_sample_classification_data(30)
        
        # Create LightGBM dataset
        train_data = lgb.Dataset(X_train, label=y_train)
        test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
        
        # Train model
        logger.info("Training LightGBM priority classifier...")
        model = lgb.train(
            self.classifier_params,
            train_data,
            num_boost_round=100,
            valid_sets=[test_data],
            callbacks=[lgb.early_stopping(stopping_rounds=10)]
        )
        
        # Evaluate
        y_pred = model.predict(X_test).argmax(axis=1)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Priority classifier accuracy: {accuracy:.4f}")
        
        # Save model
        model_path = self.model_dir / 'priority_classifier.txt'
        model.save_model(str(model_path))
        logger.info(f"Model saved to {model_path}")
        
        return {
            'model': model,
            'accuracy': accuracy,
            'model_path': str(model_path)
        }
    
    def train_eta_predictor(
        self,
        database_connection,
        include_gemini: bool = False
    ) -> Dict:
        """
        Train ETA prediction model
        
        Args:
            database_connection: Database connection object
            include_gemini: Whether to include Gemini features
        
        Returns:
            Dictionary with model and metrics
        """
        logger.info("Training ETA prediction model")
        
        # TODO: Fetch actual historical completion data
        # For now, create sample data
        X_train, y_train = self._create_sample_eta_data(100)
        X_test, y_test = self._create_sample_eta_data(30)
        
        # Create LightGBM dataset
        train_data = lgb.Dataset(X_train, label=y_train)
        test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
        
        # Train model
        logger.info("Training LightGBM ETA predictor...")
        model = lgb.train(
            self.eta_params,
            train_data,
            num_boost_round=100,
            valid_sets=[test_data],
            callbacks=[lgb.early_stopping(stopping_rounds=10)]
        )
        
        # Evaluate
        y_pred = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = np.mean(np.abs(y_test - y_pred))
        
        logger.info(f"ETA predictor RMSE: {rmse:.4f}, MAE: {mae:.4f}")
        
        # Save model
        model_path = self.model_dir / 'eta_predictor.txt'
        model.save_model(str(model_path))
        logger.info(f"Model saved to {model_path}")
        
        return {
            'model': model,
            'rmse': rmse,
            'mae': mae,
            'model_path': str(model_path)
        }
    
    def train_all_models(
        self,
        database_connection,
        include_gemini: bool = False
    ) -> Dict:
        """
        Train all models
        
        Args:
            database_connection: Database connection object
            include_gemini: Whether to include Gemini features
        
        Returns:
            Dictionary with all models and metrics
        """
        logger.info("Training all models...")
        
        results = {
            'scoring_model': self.train_scoring_model(
                database_connection,
                include_gemini
            ),
            'priority_classifier': self.train_priority_classifier(
                database_connection
            ),
            'eta_predictor': self.train_eta_predictor(
                database_connection,
                include_gemini
            ),
            'timestamp': datetime.now().isoformat()
        }
        
        # Save training summary
        summary_path = self.model_dir / 'training_summary.txt'
        with open(summary_path, 'w') as f:
            f.write(f"Training Summary - {results['timestamp']}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Scoring Model RMSE: {results['scoring_model']['rmse']:.4f}\n")
            f.write(f"Priority Classifier Accuracy: {results['priority_classifier']['accuracy']:.4f}\n")
            f.write(f"ETA Predictor RMSE: {results['eta_predictor']['rmse']:.4f}\n")
        
        logger.info(f"Training complete. Summary saved to {summary_path}")
        return results
    
    # Helper methods for sample data generation
    
    def _create_sample_classification_data(
        self,
        n_samples: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Create sample data for classification"""
        X = np.random.rand(n_samples, 10)
        y = np.random.randint(0, 3, n_samples)
        return X, y
    
    def _create_sample_eta_data(
        self,
        n_samples: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Create sample data for ETA prediction"""
        X = np.random.rand(n_samples, 15)
        y = 10 + 40 * np.random.rand(n_samples)  # Hours between 10-50
        return X, y


def main():
    """Main training function"""
    # TODO: Replace with actual database connection
    database_connection = None
    
    trainer = ModelTrainer()
    results = trainer.train_all_models(database_connection, include_gemini=False)
    
    print("\nTraining Results:")
    print("=" * 50)
    print(f"Scoring Model RMSE: {results['scoring_model']['rmse']:.4f}")
    print(f"Priority Classifier Accuracy: {results['priority_classifier']['accuracy']:.4f}")
    print(f"ETA Predictor RMSE: {results['eta_predictor']['rmse']:.4f}")
    print(f"\nModels saved to: {trainer.model_dir}")


if __name__ == '__main__':
    main()
