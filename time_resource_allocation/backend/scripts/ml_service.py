"""
ML Service Module
Provides ML model loading and inference for task-employee scoring
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import joblib

import lightgbm as lgb

from feature_builder import get_feature_builder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLService:
    """Handles ML model operations for task assignment scoring"""
    
    def __init__(self, model_dir: str = '../ml_models/trained'):
        """
        Initialize ML Service
        
        Args:
            model_dir: Directory containing trained models
        """
        self.model_dir = Path(model_dir)
        self.feature_builder = get_feature_builder()
        
        # Models
        self.scoring_model = None
        
        # Load models on initialization
        self._load_models()
    
    def _load_models(self):
        """Load trained ML models from disk"""
        try:
            scoring_path = self.model_dir / 'scoring_model.txt'
            if scoring_path.exists():
                self.scoring_model = lgb.Booster(model_file=str(scoring_path))
                logger.info(f"Loaded scoring model from {scoring_path}")
            else:
                logger.warning(f"Scoring model not found at {scoring_path}")
                
        except Exception as e:
            logger.warning(f"Error loading models: {e}")
            logger.info("ML service will use fallback scoring methods")
    
    def predict_proba(
        self,
        employee: Dict,
        task: Dict,
        include_gemini: bool = False
    ) -> Tuple[float, float]:
        """
        Predict probability score for employee-task pair
        
        Args:
            employee: Employee data dictionary
            task: Task data dictionary
            include_gemini: Whether to use Gemini features
        
        Returns:
            Tuple of (score, confidence)
        """
        # Build features
        features = self.feature_builder.build_combined_features(
            employee,
            task,
            include_gemini
        )
        
        if self.scoring_model:
            # Use trained model
            try:
                score = float(self.scoring_model.predict([features])[0])
                # Normalize score to 0-1 range
                score = max(0.0, min(1.0, score))
                confidence = 0.85  # High confidence when using trained model
                
                logger.debug(
                    f"ML score for employee {employee.get('employee_id')} "
                    f"and task {task.get('task_id')}: {score:.3f}"
                )
                
                return score, confidence
                
            except Exception as e:
                logger.warning(f"Error during model prediction: {e}")
                # Fall through to fallback method
        
        # Fallback: use skill matching and heuristics
        return self._fallback_score(employee, task)
    
    def _fallback_score(self, employee: Dict, task: Dict) -> Tuple[float, float]:
        """
        Fallback scoring method using heuristics
        
        Args:
            employee: Employee data dictionary
            task: Task data dictionary
        
        Returns:
            Tuple of (score, confidence)
        """
        from skill_matching import get_skill_matcher
        
        # Skill match (40% weight)
        matcher = get_skill_matcher()
        skill_score = matcher.calculate_similarity(
            employee.get('skills', ''),
            task.get('required_skills', '')
        )
        
        # Experience match (30% weight)
        experience = employee.get('experience_years', 0)
        complexity = task.get('complexity_score', 3.0)
        if experience >= complexity:
            exp_score = min(1.0, experience / (complexity * 1.5))
        else:
            exp_score = experience / complexity * 0.8
        
        # Workload availability (30% weight)
        current = employee.get('current_workload', 0)
        maximum = employee.get('max_workload', 40)
        workload_score = max(0.0, 1.0 - (current / maximum)) if maximum > 0 else 0.0
        
        # Combined score
        score = (
            0.4 * skill_score +
            0.3 * exp_score +
            0.3 * workload_score
        )
        
        confidence = 0.6  # Lower confidence for fallback method
        
        logger.debug(
            f"Fallback score for employee {employee.get('employee_id')} "
            f"and task {task.get('task_id')}: {score:.3f} "
            f"(skill={skill_score:.2f}, exp={exp_score:.2f}, workload={workload_score:.2f})"
        )
        
        return score, confidence
    
    def score_candidates(
        self,
        task: Dict,
        employees: List[Dict],
        top_k: Optional[int] = None,
        include_gemini: bool = False
    ) -> List[Dict]:
        """
        Score multiple candidates for a task
        
        Args:
            task: Task data dictionary
            employees: List of employee dictionaries
            top_k: Number of top candidates to return (None = all)
            include_gemini: Whether to use Gemini features
        
        Returns:
            List of scored candidates with scores and confidence
        """
        logger.info(f"Scoring {len(employees)} candidates for task {task.get('task_id')}")
        
        candidates = []
        
        for employee in employees:
            score, confidence = self.predict_proba(employee, task, include_gemini)
            
            candidates.append({
                'employee_id': employee.get('employee_id'),
                'task_id': task.get('task_id'),
                'employee_name': employee.get('name'),
                'match_score': score,
                'confidence': confidence,
                'features': self.feature_builder.build_combined_features(
                    employee, task, include_gemini
                ).tolist()
            })
        
        # Sort by score
        candidates.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Return top_k or all
        if top_k:
            return candidates[:top_k]
        return candidates
    
    def extract_features(
        self,
        employee: Dict,
        task: Dict,
        include_gemini: bool = False
    ) -> np.ndarray:
        """
        Extract feature vector for logging/training
        
        Args:
            employee: Employee data dictionary
            task: Task data dictionary
            include_gemini: Whether to use Gemini features
        
        Returns:
            Feature vector as numpy array
        """
        return self.feature_builder.build_combined_features(
            employee,
            task,
            include_gemini
        )
    
    def get_feature_names(self, include_gemini: bool = False) -> List[str]:
        """
        Get feature names for interpretation
        
        Args:
            include_gemini: Whether to include Gemini feature names
        
        Returns:
            List of feature names
        """
        return self.feature_builder.get_feature_names(include_gemini)


# Singleton instance
_ml_service = None


def get_ml_service() -> MLService:
    """Get or create singleton MLService instance"""
    global _ml_service
    if _ml_service is None:
        _ml_service = MLService()
    return _ml_service
