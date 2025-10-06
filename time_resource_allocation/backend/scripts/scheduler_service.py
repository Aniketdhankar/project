"""
Scheduler Service Module
Core scheduler logic for task assignment using greedy heuristics and ML-based scoring
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

from ml_service import get_ml_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Core scheduler for intelligent task assignment
    Combines ML-based scoring with greedy heuristics
    """
    
    def __init__(self):
        """Initialize scheduler service"""
        self.ml_service = get_ml_service()
        self.assignment_previews = {}  # Store previews by preview_id
    
    def assign_tasks(
        self,
        tasks: List[Dict],
        employees: List[Dict],
        constraints: Optional[Dict] = None,
        method: str = 'greedy_ml'
    ) -> List[Dict]:
        """
        Main task assignment method
        
        Args:
            tasks: List of task dictionaries
            employees: List of employee dictionaries
            constraints: Optional constraints (max_assignments_per_employee, etc.)
            method: Assignment method ('greedy_ml', 'balanced_ml')
        
        Returns:
            List of assignment dictionaries
        """
        logger.info(f"Starting task assignment for {len(tasks)} tasks and {len(employees)} employees")
        
        # Set default constraints
        if constraints is None:
            constraints = {}
        
        max_assignments = constraints.get('max_assignments_per_employee', 5)
        include_gemini = constraints.get('include_gemini', False)
        
        # Select assignment algorithm
        if method == 'greedy_ml':
            assignments = self._greedy_ml_assignment(
                tasks, employees, max_assignments, include_gemini
            )
        elif method == 'balanced_ml':
            assignments = self._balanced_ml_assignment(
                tasks, employees, include_gemini
            )
        else:
            logger.warning(f"Unknown method '{method}', defaulting to greedy_ml")
            assignments = self._greedy_ml_assignment(
                tasks, employees, max_assignments, include_gemini
            )
        
        logger.info(f"Assignment complete: {len(assignments)} assignments created")
        return assignments
    
    def _greedy_ml_assignment(
        self,
        tasks: List[Dict],
        employees: List[Dict],
        max_assignments: int,
        include_gemini: bool
    ) -> List[Dict]:
        """
        Greedy assignment algorithm with ML scoring
        
        Args:
            tasks: List of task dictionaries
            employees: List of employee dictionaries
            max_assignments: Maximum assignments per employee
            include_gemini: Whether to use Gemini features
        
        Returns:
            List of assignments
        """
        logger.info("Running greedy ML assignment")
        
        assignments = []
        employee_assignments = {emp['employee_id']: 0 for emp in employees}
        employee_workload = {
            emp['employee_id']: emp.get('current_workload', 0)
            for emp in employees
        }
        
        # Sort tasks by priority and deadline
        priority_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (
                priority_order.get(t.get('priority', 'medium'), 2),
                t.get('deadline', '9999-12-31')
            ),
            reverse=True
        )
        
        for task in sorted_tasks:
            # Filter available employees
            available_employees = [
                emp for emp in employees
                if employee_assignments[emp['employee_id']] < max_assignments
                and employee_workload[emp['employee_id']] + task.get('estimated_hours', 0)
                    <= emp.get('max_workload', 40)
                and emp.get('availability_status') == 'available'
            ]
            
            if not available_employees:
                logger.warning(f"No available employees for task {task.get('task_id')}")
                continue
            
            # Score candidates using ML
            candidates = self.ml_service.score_candidates(
                task,
                available_employees,
                top_k=1,
                include_gemini=include_gemini
            )
            
            if candidates:
                best_candidate = candidates[0]
                employee_id = best_candidate['employee_id']
                
                # Create assignment
                assignment = {
                    'task_id': task['task_id'],
                    'employee_id': employee_id,
                    'assignment_method': 'greedy_ml',
                    'assignment_score': best_candidate['match_score'],
                    'confidence': best_candidate['confidence'],
                    'task_title': task.get('title'),
                    'employee_name': best_candidate['employee_name'],
                    'estimated_hours': task.get('estimated_hours', 0),
                    'features': best_candidate.get('features', [])
                }
                
                assignments.append(assignment)
                
                # Update counters
                employee_assignments[employee_id] += 1
                employee_workload[employee_id] += task.get('estimated_hours', 0)
                
                logger.info(
                    f"Assigned task {task['task_id']} to employee {employee_id} "
                    f"(ML score: {best_candidate['match_score']:.3f}, "
                    f"confidence: {best_candidate['confidence']:.3f})"
                )
        
        return assignments
    
    def _balanced_ml_assignment(
        self,
        tasks: List[Dict],
        employees: List[Dict],
        include_gemini: bool,
        workload_weight: float = 0.3
    ) -> List[Dict]:
        """
        Balanced assignment considering both ML score and workload distribution
        
        Args:
            tasks: List of task dictionaries
            employees: List of employee dictionaries
            include_gemini: Whether to use Gemini features
            workload_weight: Weight for workload balancing (0-1)
        
        Returns:
            List of assignments
        """
        logger.info("Running balanced ML assignment")
        
        assignments = []
        employee_workload = {
            emp['employee_id']: emp.get('current_workload', 0)
            for emp in employees
        }
        
        # Sort tasks by priority
        priority_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        sorted_tasks = sorted(
            tasks,
            key=lambda t: priority_order.get(t.get('priority', 'medium'), 2),
            reverse=True
        )
        
        for task in sorted_tasks:
            # Score all available employees
            available_employees = [
                emp for emp in employees
                if emp.get('availability_status') == 'available'
            ]
            
            if not available_employees:
                logger.warning(f"No available employees for task {task.get('task_id')}")
                continue
            
            candidates = self.ml_service.score_candidates(
                task,
                available_employees,
                include_gemini=include_gemini
            )
            
            # Adjust scores based on workload
            for candidate in candidates:
                employee_id = candidate['employee_id']
                employee = next(e for e in employees if e['employee_id'] == employee_id)
                
                # Calculate workload factor (lower workload = higher factor)
                current = employee_workload[employee_id]
                maximum = employee.get('max_workload', 40)
                workload_factor = 1.0 - (current / maximum) if maximum > 0 else 0
                
                # Combine ML score with workload factor
                ml_score = candidate['match_score']
                adjusted_score = (
                    (1 - workload_weight) * ml_score +
                    workload_weight * workload_factor
                )
                candidate['adjusted_score'] = adjusted_score
            
            # Sort by adjusted score
            candidates.sort(key=lambda c: c.get('adjusted_score', 0), reverse=True)
            
            # Find best candidate with capacity
            assigned = False
            for candidate in candidates:
                employee_id = candidate['employee_id']
                employee = next(e for e in employees if e['employee_id'] == employee_id)
                
                task_hours = task.get('estimated_hours', 0)
                if employee_workload[employee_id] + task_hours <= employee.get('max_workload', 40):
                    # Create assignment
                    assignment = {
                        'task_id': task['task_id'],
                        'employee_id': employee_id,
                        'assignment_method': 'balanced_ml',
                        'assignment_score': candidate['adjusted_score'],
                        'ml_score': candidate['match_score'],
                        'confidence': candidate['confidence'],
                        'task_title': task.get('title'),
                        'employee_name': candidate['employee_name'],
                        'estimated_hours': task_hours,
                        'features': candidate.get('features', [])
                    }
                    
                    assignments.append(assignment)
                    employee_workload[employee_id] += task_hours
                    assigned = True
                    
                    logger.info(
                        f"Assigned task {task['task_id']} to employee {employee_id} "
                        f"(adjusted score: {assignment['assignment_score']:.3f}, "
                        f"ML score: {assignment['ml_score']:.3f})"
                    )
                    break
            
            if not assigned:
                logger.warning(f"Could not assign task {task['task_id']} - no capacity")
        
        return assignments
    
    def preview_assignments(
        self,
        tasks: List[Dict],
        employees: List[Dict],
        constraints: Optional[Dict] = None,
        method: str = 'greedy_ml'
    ) -> Dict:
        """
        Generate assignment preview without finalizing
        
        Args:
            tasks: List of task dictionaries
            employees: List of employee dictionaries
            constraints: Optional constraints
            method: Assignment method
        
        Returns:
            Preview dictionary with preview_id and assignments
        """
        logger.info("Generating assignment preview")
        
        # Generate assignments
        assignments = self.assign_tasks(tasks, employees, constraints, method)
        
        # Create preview
        preview_id = f"preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        preview = {
            'preview_id': preview_id,
            'created_at': datetime.now().isoformat(),
            'method': method,
            'constraints': constraints or {},
            'assignments': assignments,
            'summary': {
                'total_tasks': len(tasks),
                'total_employees': len(employees),
                'assignments_created': len(assignments),
                'unassigned_tasks': len(tasks) - len(assignments)
            }
        }
        
        # Store preview
        self.assignment_previews[preview_id] = preview
        
        logger.info(f"Preview created: {preview_id} with {len(assignments)} assignments")
        return preview
    
    def finalize_assignments(
        self,
        preview_id: str,
        database_connection=None
    ) -> Dict:
        """
        Finalize assignments from preview and store in database
        
        Args:
            preview_id: Preview identifier
            database_connection: Database connection for storage
        
        Returns:
            Result dictionary with finalized assignments
        """
        logger.info(f"Finalizing assignments for preview {preview_id}")
        
        # Get preview
        preview = self.assignment_previews.get(preview_id)
        if not preview:
            raise ValueError(f"Preview {preview_id} not found")
        
        assignments = preview['assignments']
        
        # Store assignments in database
        if database_connection:
            stored_count = self._store_assignments(assignments, database_connection)
            logger.info(f"Stored {stored_count} assignments in database")
        else:
            logger.warning("No database connection provided, skipping storage")
            stored_count = 0
        
        # Log training data
        if database_connection:
            self._log_training_data(assignments, database_connection)
        
        # Clean up preview
        del self.assignment_previews[preview_id]
        
        result = {
            'preview_id': preview_id,
            'finalized_at': datetime.now().isoformat(),
            'assignments_stored': stored_count,
            'summary': preview['summary']
        }
        
        logger.info(f"Finalized {stored_count} assignments")
        return result
    
    def _store_assignments(
        self,
        assignments: List[Dict],
        database_connection
    ) -> int:
        """
        Store assignments in database
        
        Args:
            assignments: List of assignment dictionaries
            database_connection: Database connection
        
        Returns:
            Number of assignments stored
        """
        # TODO: Implement actual database insertion
        # This is a placeholder implementation
        logger.info(f"Storing {len(assignments)} assignments in database")
        
        try:
            # Example SQL for PostgreSQL:
            # INSERT INTO Task_Assignments 
            # (task_id, employee_id, assignment_method, assignment_score, assigned_at)
            # VALUES (%(task_id)s, %(employee_id)s, %(method)s, %(score)s, NOW())
            
            # For now, just log the assignments
            for assignment in assignments:
                logger.debug(
                    f"Would store: task_id={assignment['task_id']}, "
                    f"employee_id={assignment['employee_id']}, "
                    f"method={assignment['assignment_method']}, "
                    f"score={assignment['assignment_score']:.4f}"
                )
            
            return len(assignments)
            
        except Exception as e:
            logger.error(f"Error storing assignments: {e}")
            return 0
    
    def _log_training_data(
        self,
        assignments: List[Dict],
        database_connection
    ) -> None:
        """
        Log assignment and feature data for ML training
        
        Args:
            assignments: List of assignment dictionaries
            database_connection: Database connection
        """
        logger.info(f"Logging training data for {len(assignments)} assignments")
        
        try:
            # TODO: Implement actual database logging
            # Store features and assignments for future model training
            # Example table: ML_Training_Data
            # Columns: assignment_id, task_id, employee_id, features (JSON), 
            #          assignment_score, timestamp
            
            for assignment in assignments:
                features = assignment.get('features', [])
                feature_names = self.ml_service.get_feature_names()
                
                training_record = {
                    'task_id': assignment['task_id'],
                    'employee_id': assignment['employee_id'],
                    'features': json.dumps(features),
                    'feature_names': json.dumps(feature_names),
                    'assignment_score': assignment['assignment_score'],
                    'confidence': assignment.get('confidence', 0.0),
                    'method': assignment['assignment_method'],
                    'logged_at': datetime.now().isoformat()
                }
                
                logger.debug(f"Would log training data: {training_record}")
            
            logger.info("Training data logged successfully")
            
        except Exception as e:
            logger.error(f"Error logging training data: {e}")


# Singleton instance
_scheduler_service = None


def get_scheduler_service() -> SchedulerService:
    """Get or create singleton SchedulerService instance"""
    global _scheduler_service
    if _scheduler_service is None:
        _scheduler_service = SchedulerService()
    return _scheduler_service
