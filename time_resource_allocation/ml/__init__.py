"""
ML Module for Skill-Based Assignment

This module provides machine learning capabilities for predicting 
assignment success using scikit-learn.
"""

from .train import SkillAssignmentTrainer, train_pipeline
from .evaluate import ModelEvaluator
from .predict import PredictionLogger

__all__ = [
    'SkillAssignmentTrainer',
    'train_pipeline',
    'ModelEvaluator',
    'PredictionLogger'
]
