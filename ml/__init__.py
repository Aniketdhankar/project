"""
ML Module for Skill-Based Assignment Model

This module provides training, evaluation, and prediction capabilities
for the skill-based task assignment model.
"""

from .train import SkillAssignmentTrainer
from .evaluate import ModelEvaluator
from .predict import PredictionLogger

__all__ = [
    'SkillAssignmentTrainer',
    'ModelEvaluator', 
    'PredictionLogger'
]

__version__ = '1.0.0'
