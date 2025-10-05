"""
Feature Builder Module
Builds feature matrices for ML models from employee and task data
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

from skill_matching import get_skill_matcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureBuilder:
    """Builds feature matrices for ML models"""
    
    def __init__(self):
        """Initialize feature builder"""
        self.skill_matcher = get_skill_matcher()
        
        # Feature names for tracking
        self.feature_names = []
    
    def build_employee_features(self, employee: Dict) -> np.ndarray:
        """
        Build feature vector for an employee
        
        Args:
            employee: Employee data dictionary
        
        Returns:
            Feature vector as numpy array
        """
        features = []
        
        # Experience (normalized to 0-1, assuming max 20 years)
        experience = employee.get('experience_years', 0)
        features.append(min(experience / 20.0, 1.0))
        
        # Workload ratio (current / max)
        current_workload = employee.get('current_workload', 0)
        max_workload = employee.get('max_workload', 40)
        workload_ratio = current_workload / max_workload if max_workload > 0 else 0
        features.append(workload_ratio)
        
        # Availability (binary: 0 = not available, 1 = available)
        availability = 1.0 if employee.get('availability_status') == 'available' else 0.0
        features.append(availability)
        
        # Performance rating (normalized to 0-1, assuming max 5)
        performance = employee.get('performance_rating', 3.0)
        features.append(min(performance / 5.0, 1.0))
        
        # Number of active tasks
        active_tasks = employee.get('active_tasks', 0)
        features.append(min(active_tasks / 10.0, 1.0))  # Normalize, assuming max 10
        
        # Average task completion time (if available)
        avg_completion = employee.get('avg_completion_time', 40.0)
        features.append(min(avg_completion / 100.0, 1.0))  # Normalize to 0-1
        
        return np.array(features)
    
    def build_task_features(self, task: Dict) -> np.ndarray:
        """
        Build feature vector for a task
        
        Args:
            task: Task data dictionary
        
        Returns:
            Feature vector as numpy array
        """
        features = []
        
        # Priority (encoded: low=0.25, medium=0.5, high=0.75, critical=1.0)
        priority_map = {'low': 0.25, 'medium': 0.5, 'high': 0.75, 'critical': 1.0}
        priority = priority_map.get(task.get('priority', 'medium'), 0.5)
        features.append(priority)
        
        # Complexity score (normalized to 0-1, assuming max 5)
        complexity = task.get('complexity_score', 3.0)
        features.append(min(complexity / 5.0, 1.0))
        
        # Estimated hours (normalized, assuming max 200 hours)
        estimated_hours = task.get('estimated_hours', 0)
        features.append(min(estimated_hours / 200.0, 1.0))
        
        # Time until deadline (in days, normalized to 0-1, assuming max 30 days)
        deadline = task.get('deadline')
        if deadline:
            if isinstance(deadline, str):
                deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            days_until = (deadline - datetime.now()).days
            time_pressure = max(0, min(1.0 - (days_until / 30.0), 1.0))
        else:
            time_pressure = 0.5  # Default medium pressure
        features.append(time_pressure)
        
        # Number of dependencies
        dependencies = task.get('dependencies', [])
        if isinstance(dependencies, str):
            dependencies = dependencies.split(',') if dependencies else []
        dep_count = len(dependencies)
        features.append(min(dep_count / 5.0, 1.0))  # Normalize, assuming max 5
        
        # Task age (days since creation)
        created_at = task.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age_days = (datetime.now() - created_at).days
            features.append(min(age_days / 30.0, 1.0))
        else:
            features.append(0.0)
        
        return np.array(features)
    
    def build_interaction_features(
        self,
        employee: Dict,
        task: Dict
    ) -> np.ndarray:
        """
        Build interaction features between employee and task
        
        Args:
            employee: Employee data dictionary
            task: Task data dictionary
        
        Returns:
            Feature vector as numpy array
        """
        features = []
        
        # Skill match score
        skill_score = self.skill_matcher.calculate_similarity(
            employee.get('skills', ''),
            task.get('required_skills', '')
        )
        features.append(skill_score)
        
        # Experience-complexity match
        experience = employee.get('experience_years', 0)
        complexity = task.get('complexity_score', 3.0)
        exp_complexity_ratio = min(experience / complexity, 2.0) / 2.0  # Normalize
        features.append(exp_complexity_ratio)
        
        # Workload capacity (can employee take this task?)
        current_workload = employee.get('current_workload', 0)
        max_workload = employee.get('max_workload', 40)
        estimated_hours = task.get('estimated_hours', 0)
        remaining_capacity = max_workload - current_workload
        capacity_fit = min(remaining_capacity / estimated_hours, 1.0) if estimated_hours > 0 else 0
        features.append(max(0, capacity_fit))
        
        # Department match (if applicable)
        emp_dept = employee.get('department', '')
        task_dept = task.get('department', '')
        dept_match = 1.0 if emp_dept == task_dept else 0.5
        features.append(dept_match)
        
        # Historical success rate (if available)
        success_rate = employee.get('success_rate', 0.8)
        features.append(success_rate)
        
        return np.array(features)
    
    def build_combined_features(
        self,
        employee: Dict,
        task: Dict,
        include_gemini: bool = False
    ) -> np.ndarray:
        """
        Build complete feature vector combining all feature types
        
        Args:
            employee: Employee data dictionary
            task: Task data dictionary
            include_gemini: Whether to include Gemini-augmented features
        
        Returns:
            Complete feature vector
        """
        # Build individual feature sets
        emp_features = self.build_employee_features(employee)
        task_features = self.build_task_features(task)
        interaction_features = self.build_interaction_features(employee, task)
        
        # Combine all features
        all_features = np.concatenate([
            emp_features,
            task_features,
            interaction_features
        ])
        
        # Optionally add Gemini-augmented features
        if include_gemini:
            gemini_features = self._get_gemini_features(employee, task)
            all_features = np.concatenate([all_features, gemini_features])
        
        return all_features
    
    def build_feature_matrix(
        self,
        employees: List[Dict],
        tasks: List[Dict],
        include_gemini: bool = False
    ) -> Tuple[np.ndarray, List[Tuple[int, int]]]:
        """
        Build feature matrix for multiple employee-task pairs
        
        Args:
            employees: List of employee dictionaries
            tasks: List of task dictionaries
            include_gemini: Whether to include Gemini features
        
        Returns:
            Tuple of (feature matrix, list of (employee_id, task_id) pairs)
        """
        features_list = []
        pair_ids = []
        
        for employee in employees:
            for task in tasks:
                features = self.build_combined_features(
                    employee, 
                    task, 
                    include_gemini
                )
                features_list.append(features)
                pair_ids.append((
                    employee.get('employee_id'),
                    task.get('task_id')
                ))
        
        feature_matrix = np.array(features_list)
        
        logger.info(f"Built feature matrix: {feature_matrix.shape}")
        return feature_matrix, pair_ids
    
    def get_feature_names(self, include_gemini: bool = False) -> List[str]:
        """
        Get list of feature names
        
        Args:
            include_gemini: Whether to include Gemini feature names
        
        Returns:
            List of feature names
        """
        names = [
            # Employee features
            'employee_experience',
            'employee_workload_ratio',
            'employee_availability',
            'employee_performance',
            'employee_active_tasks',
            'employee_avg_completion',
            
            # Task features
            'task_priority',
            'task_complexity',
            'task_estimated_hours',
            'task_time_pressure',
            'task_dependencies',
            'task_age',
            
            # Interaction features
            'skill_match_score',
            'experience_complexity_ratio',
            'workload_capacity_fit',
            'department_match',
            'historical_success_rate'
        ]
        
        if include_gemini:
            names.extend([
                'gemini_skill_quality',
                'gemini_experience_relevance',
                'gemini_complexity_fit',
                'gemini_success_potential'
            ])
        
        return names
    
    def _get_gemini_features(self, employee: Dict, task: Dict) -> np.ndarray:
        """
        Get Gemini-augmented features
        
        Args:
            employee: Employee data dictionary
            task: Task data dictionary
        
        Returns:
            Gemini feature vector
        """
        # TODO: Implement actual Gemini API call
        # For now, return placeholder values
        from gemini_client import get_gemini_client
        
        client = get_gemini_client()
        gemini_data = client.augment_features(task, employee)
        
        return np.array([
            gemini_data.get('skill_match_quality', 0.75),
            gemini_data.get('experience_relevance', 0.70),
            gemini_data.get('complexity_fit', 0.65),
            gemini_data.get('success_potential', 0.80)
        ])
    
    def create_training_dataset(
        self,
        database_connection,
        include_gemini: bool = False
    ) -> pd.DataFrame:
        """
        Create training dataset from database
        
        Args:
            database_connection: Database connection object
            include_gemini: Whether to include Gemini features
        
        Returns:
            DataFrame with features and labels
        """
        # TODO: Implement actual database queries
        # This is a placeholder implementation
        
        logger.info("Creating training dataset from database")
        
        # Fetch historical assignments
        # query = """
        # SELECT ta.*, e.*, t.*
        # FROM Task_Assignments ta
        # JOIN Employees e ON ta.employee_id = e.employee_id
        # JOIN Tasks t ON ta.task_id = t.task_id
        # WHERE ta.status = 'completed'
        # """
        
        # For now, create sample data
        sample_data = []
        
        for i in range(10):
            employee = {
                'employee_id': i % 5 + 1,
                'experience_years': 3.0 + i * 0.5,
                'current_workload': 20 + i * 2,
                'max_workload': 40,
                'availability_status': 'available',
                'performance_rating': 3.5 + (i % 3) * 0.5,
                'active_tasks': i % 5,
                'skills': 'Python, React, PostgreSQL'
            }
            
            task = {
                'task_id': i + 1,
                'priority': ['low', 'medium', 'high'][i % 3],
                'complexity_score': 2.0 + (i % 4),
                'estimated_hours': 10 + i * 2,
                'deadline': datetime.now() + timedelta(days=7 + i),
                'required_skills': 'Python, Flask, PostgreSQL'
            }
            
            features = self.build_combined_features(employee, task, include_gemini)
            
            # Label: success score (0-1)
            label = 0.7 + (i % 3) * 0.1
            
            sample_data.append(np.concatenate([features, [label]]))
        
        # Create DataFrame
        feature_names = self.get_feature_names(include_gemini)
        column_names = feature_names + ['label']
        
        df = pd.DataFrame(sample_data, columns=column_names)
        
        logger.info(f"Created training dataset with {len(df)} samples")
        return df


# Singleton instance
_feature_builder = None

def get_feature_builder() -> FeatureBuilder:
    """Get or create singleton FeatureBuilder instance"""
    global _feature_builder
    if _feature_builder is None:
        _feature_builder = FeatureBuilder()
    return _feature_builder
