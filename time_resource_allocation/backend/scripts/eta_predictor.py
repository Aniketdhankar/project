"""
ETA Predictor Module
Predicts task completion time using ML models and Gemini API
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

from score_inference import get_score_inference
from gemini_client import get_gemini_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ETAPredictor:
    """Predicts task completion ETAs"""
    
    def __init__(self):
        """Initialize ETA predictor"""
        self.score_inference = get_score_inference()
        self.gemini_client = get_gemini_client()
    
    def predict_task_eta(
        self,
        task: Dict,
        employee: Dict,
        use_gemini: bool = False
    ) -> Dict:
        """
        Predict ETA for a task assignment
        
        Args:
            task: Task data dictionary
            employee: Employee data dictionary
            use_gemini: Whether to use Gemini for prediction
        
        Returns:
            Dictionary with ETA prediction and explanation
        """
        logger.info(f"Predicting ETA for task {task.get('task_id')}")
        
        # Use ML model or Gemini
        if use_gemini:
            result = self._predict_with_gemini(task, employee)
        else:
            result = self.score_inference.predict_eta(
                employee,
                task,
                use_gemini_fallback=True
            )
        
        # Calculate estimated completion date
        if result['predicted_hours']:
            # Assuming 8 hours per working day
            days_needed = result['predicted_hours'] / 8
            estimated_completion = datetime.now() + timedelta(days=days_needed)
            result['estimated_completion_date'] = estimated_completion.isoformat()
        
        # Add explanation
        if use_gemini and not result.get('explanation'):
            result['explanation'] = self._generate_explanation(task, employee, result)
        
        return result
    
    def batch_predict_etas(
        self,
        assignments: List[Dict],
        tasks_dict: Dict[int, Dict],
        employees_dict: Dict[int, Dict],
        database_connection=None
    ) -> List[Dict]:
        """
        Predict ETAs for multiple assignments
        
        Args:
            assignments: List of assignment dictionaries
            tasks_dict: Dictionary mapping task_id to task data
            employees_dict: Dictionary mapping employee_id to employee data
            database_connection: Database connection
        
        Returns:
            List of ETA predictions
        """
        logger.info(f"Batch predicting ETAs for {len(assignments)} assignments")
        
        predictions = []
        
        for assignment in assignments:
            task_id = assignment['task_id']
            employee_id = assignment['employee_id']
            
            task = tasks_dict.get(task_id)
            employee = employees_dict.get(employee_id)
            
            if task and employee:
                eta_result = self.predict_task_eta(task, employee)
                
                prediction = {
                    'task_id': task_id,
                    'employee_id': employee_id,
                    'predicted_hours': eta_result['predicted_hours'],
                    'estimated_completion': eta_result.get('estimated_completion_date'),
                    'confidence': eta_result['confidence'],
                    'source': eta_result['source'],
                    'generated_at': datetime.now().isoformat()
                }
                
                predictions.append(prediction)
        
        # Store in database
        if database_connection and predictions:
            self._store_eta_predictions(predictions, database_connection)
        
        logger.info(f"Generated {len(predictions)} ETA predictions")
        return predictions
    
    def update_eta_with_progress(
        self,
        task: Dict,
        employee: Dict,
        progress: Dict,
        original_eta: Dict
    ) -> Dict:
        """
        Update ETA based on actual progress
        
        Args:
            task: Task data dictionary
            employee: Employee data dictionary
            progress: Current progress data
            original_eta: Original ETA prediction
        
        Returns:
            Updated ETA dictionary
        """
        logger.info(f"Updating ETA for task {task.get('task_id')} based on progress")
        
        progress_pct = progress.get('progress_percentage', 0)
        hours_spent = progress.get('hours_spent', 0)
        original_hours = original_eta.get('predicted_hours', 40)
        
        # Calculate velocity
        if progress_pct > 0 and hours_spent > 0:
            velocity = progress_pct / hours_spent  # % per hour
            
            # Estimate remaining hours
            remaining_pct = 100 - progress_pct
            remaining_hours = remaining_pct / velocity if velocity > 0 else original_hours
            
            # Adjust based on original estimate
            adjusted_hours = (remaining_hours + original_hours * 0.2) / 1.2  # Weighted average
        else:
            adjusted_hours = original_hours
        
        # Calculate new completion date
        days_needed = adjusted_hours / 8
        new_completion = datetime.now() + timedelta(days=days_needed)
        
        # Determine if ETA changed significantly
        original_completion = original_eta.get('estimated_completion_date')
        if original_completion:
            original_date = datetime.fromisoformat(original_completion.replace('Z', '+00:00'))
            date_diff = (new_completion - original_date).days
            
            if abs(date_diff) > 1:
                confidence_adjustment = -0.1
            else:
                confidence_adjustment = 0.05
        else:
            confidence_adjustment = 0
        
        updated_confidence = min(1.0, max(0.0, 
            original_eta.get('confidence', 0.7) + confidence_adjustment
        ))
        
        return {
            'task_id': task['task_id'],
            'employee_id': employee['employee_id'],
            'predicted_hours': adjusted_hours,
            'estimated_completion_date': new_completion.isoformat(),
            'confidence': updated_confidence,
            'source': 'progress_adjusted',
            'original_hours': original_hours,
            'adjustment_reason': 'Updated based on actual progress',
            'progress_percentage': progress_pct,
            'hours_spent': hours_spent,
            'generated_at': datetime.now().isoformat()
        }
    
    def _predict_with_gemini(
        self,
        task: Dict,
        employee: Dict
    ) -> Dict:
        """Use Gemini API for ETA prediction"""
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
        
        result = self.gemini_client.predict_eta(task_data)
        result['source'] = 'gemini_api'
        
        return result
    
    def _generate_explanation(
        self,
        task: Dict,
        employee: Dict,
        eta_result: Dict
    ) -> str:
        """Generate human-readable explanation for ETA"""
        predicted_hours = eta_result['predicted_hours']
        confidence = eta_result['confidence']
        
        explanation = f"""
        ETA Analysis for {task.get('title')}:
        
        Predicted Time: {predicted_hours:.1f} hours ({predicted_hours/8:.1f} days)
        Confidence: {confidence*100:.0f}%
        
        Key Factors:
        - Task complexity: {task.get('complexity_score', 'N/A')}
        - Estimated hours: {task.get('estimated_hours', 'N/A')}
        - Employee experience: {employee.get('experience_years', 'N/A')} years
        - Current workload: {employee.get('current_workload', 'N/A')} hours
        
        The prediction is based on historical performance data and task characteristics.
        """
        
        return explanation.strip()
    
    def _store_eta_predictions(self, predictions: List[Dict], database_connection):
        """Store ETA predictions in database"""
        # TODO: Implement actual database insertion
        logger.info(f"Storing {len(predictions)} ETA predictions in database (placeholder)")
        pass


# Singleton instance
_eta_predictor = None

def get_eta_predictor() -> ETAPredictor:
    """Get or create singleton ETAPredictor instance"""
    global _eta_predictor
    if _eta_predictor is None:
        _eta_predictor = ETAPredictor()
    return _eta_predictor
