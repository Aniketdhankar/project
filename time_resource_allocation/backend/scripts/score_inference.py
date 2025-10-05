"""
Score Inference Module
Performs inference using trained models to score employee-task pairs
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import joblib
import logging
from pathlib import Path

import lightgbm as lgb

from feature_builder import get_feature_builder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScoreInference:
    """Handles inference using trained models"""
    
    def __init__(self, model_dir: str = '../ml_models/trained'):
        """
        Initialize score inference
        
        Args:
            model_dir: Directory containing trained models
        """
        self.model_dir = Path(model_dir)
        self.feature_builder = get_feature_builder()
        
        # Load models
        self.scoring_model = None
        self.priority_classifier = None
        self.eta_predictor = None
        
        self._load_models()
    
    def _load_models(self):
        """Load trained models from disk"""
        try:
            scoring_path = self.model_dir / 'scoring_model.txt'
            if scoring_path.exists():
                self.scoring_model = lgb.Booster(model_file=str(scoring_path))
                logger.info("Loaded scoring model")
            
            classifier_path = self.model_dir / 'priority_classifier.txt'
            if classifier_path.exists():
                self.priority_classifier = lgb.Booster(model_file=str(classifier_path))
                logger.info("Loaded priority classifier")
            
            eta_path = self.model_dir / 'eta_predictor.txt'
            if eta_path.exists():
                self.eta_predictor = lgb.Booster(model_file=str(eta_path))
                logger.info("Loaded ETA predictor")
                
        except Exception as e:
            logger.warning(f"Error loading models: {e}")
    
    def score_employee_task_pair(
        self,
        employee: Dict,
        task: Dict,
        include_gemini: bool = False
    ) -> Dict:
        """
        Score a single employee-task pair
        
        Args:
            employee: Employee data dictionary
            task: Task data dictionary
            include_gemini: Whether to use Gemini features
        
        Returns:
            Dictionary with scores and predictions
        """
        # Build features
        features = self.feature_builder.build_combined_features(
            employee,
            task,
            include_gemini
        )
        
        result = {
            'employee_id': employee.get('employee_id'),
            'task_id': task.get('task_id'),
            'employee_name': employee.get('name'),
            'task_title': task.get('title')
        }
        
        # Score using scoring model
        if self.scoring_model:
            score = self.scoring_model.predict([features])[0]
            result['match_score'] = float(score)
            result['confidence'] = min(abs(score) / 1.0, 1.0)  # Normalize confidence
        else:
            # Fallback to skill matching only
            from skill_matching import get_skill_matcher
            matcher = get_skill_matcher()
            score = matcher.calculate_similarity(
                employee.get('skills', ''),
                task.get('required_skills', '')
            )
            result['match_score'] = float(score)
            result['confidence'] = 0.6
        
        return result
    
    def score_candidates_for_task(
        self,
        task: Dict,
        employees: List[Dict],
        top_k: int = 5,
        include_gemini: bool = False
    ) -> List[Dict]:
        """
        Score multiple employees for a single task
        
        Args:
            task: Task data dictionary
            employees: List of employee dictionaries
            top_k: Number of top candidates to return
            include_gemini: Whether to use Gemini features
        
        Returns:
            List of scored candidates, sorted by score
        """
        logger.info(f"Scoring {len(employees)} candidates for task {task.get('task_id')}")
        
        candidates = []
        
        for employee in employees:
            score_result = self.score_employee_task_pair(
                employee,
                task,
                include_gemini
            )
            
            # Add additional scoring factors
            score_result['skill_match'] = self.feature_builder.skill_matcher.calculate_similarity(
                employee.get('skills', ''),
                task.get('required_skills', '')
            )
            
            score_result['workload_score'] = self._calculate_workload_score(employee)
            score_result['experience_score'] = self._calculate_experience_score(
                employee,
                task
            )
            
            candidates.append(score_result)
        
        # Sort by match score
        candidates.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Add ranking
        for rank, candidate in enumerate(candidates[:top_k], 1):
            candidate['ranking'] = rank
        
        return candidates[:top_k]
    
    def predict_priority(self, task: Dict) -> Dict:
        """
        Predict task priority
        
        Args:
            task: Task data dictionary
        
        Returns:
            Dictionary with priority prediction
        """
        if not self.priority_classifier:
            logger.warning("Priority classifier not loaded")
            return {
                'predicted_priority': task.get('priority', 'medium'),
                'confidence': 0.5
            }
        
        # Build task features
        features = self.feature_builder.build_task_features(task)
        
        # Predict
        predictions = self.priority_classifier.predict([features])[0]
        predicted_class = int(np.argmax(predictions))
        confidence = float(predictions[predicted_class])
        
        priority_map = {0: 'low', 1: 'medium', 2: 'high'}
        
        return {
            'predicted_priority': priority_map.get(predicted_class, 'medium'),
            'confidence': confidence,
            'probabilities': {
                'low': float(predictions[0]),
                'medium': float(predictions[1]),
                'high': float(predictions[2])
            }
        }
    
    def predict_eta(
        self,
        employee: Dict,
        task: Dict,
        use_gemini_fallback: bool = True
    ) -> Dict:
        """
        Predict task completion ETA
        
        Args:
            employee: Employee data dictionary
            task: Task data dictionary
            use_gemini_fallback: Whether to use Gemini as fallback
        
        Returns:
            Dictionary with ETA prediction
        """
        # Build features
        features = self.feature_builder.build_combined_features(employee, task)
        
        if self.eta_predictor:
            # Use trained model
            predicted_hours = float(self.eta_predictor.predict([features])[0])
            confidence = 0.8
            source = 'lightgbm'
        elif use_gemini_fallback:
            # Fallback to Gemini
            from gemini_client import get_gemini_client
            client = get_gemini_client()
            
            task_data = {
                'title': task.get('title'),
                'description': task.get('description'),
                'required_skills': task.get('required_skills'),
                'complexity': task.get('complexity_score'),
                'estimated_hours': task.get('estimated_hours'),
                'employee_name': employee.get('name'),
                'experience_years': employee.get('experience_years'),
                'current_workload': employee.get('current_workload')
            }
            
            result = client.predict_eta(task_data)
            predicted_hours = result['predicted_hours']
            confidence = result['confidence']
            source = 'gemini_api'
        else:
            # Simple fallback
            predicted_hours = task.get('estimated_hours', 20.0)
            confidence = 0.5
            source = 'fallback'
        
        return {
            'predicted_hours': predicted_hours,
            'confidence': confidence,
            'source': source,
            'employee_id': employee.get('employee_id'),
            'task_id': task.get('task_id')
        }
    
    def batch_score_tasks(
        self,
        tasks: List[Dict],
        employees: List[Dict],
        database_connection=None
    ) -> pd.DataFrame:
        """
        Score all task-employee combinations and store in database
        
        Args:
            tasks: List of task dictionaries
            employees: List of employee dictionaries
            database_connection: Database connection for storing results
        
        Returns:
            DataFrame with all scores
        """
        logger.info(f"Batch scoring {len(tasks)} tasks with {len(employees)} employees")
        
        results = []
        
        for task in tasks:
            candidates = self.score_candidates_for_task(
                task,
                employees,
                top_k=len(employees)
            )
            results.extend(candidates)
        
        # Convert to DataFrame
        df = pd.DataFrame(results)
        
        # Store in database
        if database_connection:
            self._store_scores(df, database_connection)
        
        logger.info(f"Batch scoring complete: {len(results)} scores generated")
        return df
    
    def _calculate_workload_score(self, employee: Dict) -> float:
        """Calculate workload-based score (higher = more available)"""
        current = employee.get('current_workload', 0)
        maximum = employee.get('max_workload', 40)
        
        if maximum == 0:
            return 0.0
        
        utilization = current / maximum
        # Invert so lower workload = higher score
        return max(0.0, 1.0 - utilization)
    
    def _calculate_experience_score(self, employee: Dict, task: Dict) -> float:
        """Calculate experience match score"""
        experience = employee.get('experience_years', 0)
        complexity = task.get('complexity_score', 3.0)
        
        # Ideal: experience >= complexity
        if experience >= complexity:
            return min(1.0, experience / (complexity * 1.5))
        else:
            return experience / complexity * 0.8
    
    def _store_scores(self, df: pd.DataFrame, database_connection):
        """Store scores in database"""
        # TODO: Implement actual database insertion
        logger.info("Storing scores in database (placeholder)")
        pass


# Singleton instance
_score_inference = None

def get_score_inference() -> ScoreInference:
    """Get or create singleton ScoreInference instance"""
    global _score_inference
    if _score_inference is None:
        _score_inference = ScoreInference()
    return _score_inference
