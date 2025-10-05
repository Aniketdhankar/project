"""
Task Assignment Module
Implements task assignment algorithms (Greedy and Hungarian)
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from scipy.optimize import linear_sum_assignment

from score_inference import get_score_inference

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskAssigner:
    """Handles task assignment using various algorithms"""
    
    def __init__(self):
        """Initialize task assigner"""
        self.score_inference = get_score_inference()
    
    def greedy_assignment(
        self,
        tasks: List[Dict],
        employees: List[Dict],
        max_assignments_per_employee: int = 5
    ) -> List[Dict]:
        """
        Greedy task assignment algorithm
        Assigns tasks to best available employee iteratively
        
        Args:
            tasks: List of task dictionaries
            employees: List of employee dictionaries
            max_assignments_per_employee: Maximum tasks per employee
        
        Returns:
            List of assignment dictionaries
        """
        logger.info(f"Running greedy assignment for {len(tasks)} tasks")
        
        assignments = []
        employee_assignments = {emp['employee_id']: 0 for emp in employees}
        employee_workload = {
            emp['employee_id']: emp.get('current_workload', 0) 
            for emp in employees
        }
        
        # Sort tasks by priority
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
                if employee_assignments[emp['employee_id']] < max_assignments_per_employee
                and employee_workload[emp['employee_id']] + task.get('estimated_hours', 0) 
                    <= emp.get('max_workload', 40)
            ]
            
            if not available_employees:
                logger.warning(f"No available employees for task {task.get('task_id')}")
                continue
            
            # Score candidates
            candidates = self.score_inference.score_candidates_for_task(
                task,
                available_employees,
                top_k=1
            )
            
            if candidates:
                best_candidate = candidates[0]
                employee_id = best_candidate['employee_id']
                
                # Create assignment
                assignment = {
                    'task_id': task['task_id'],
                    'employee_id': employee_id,
                    'assignment_method': 'greedy',
                    'assignment_score': best_candidate['match_score'],
                    'task_title': task.get('title'),
                    'employee_name': best_candidate['employee_name'],
                    'estimated_hours': task.get('estimated_hours', 0)
                }
                
                assignments.append(assignment)
                
                # Update counters
                employee_assignments[employee_id] += 1
                employee_workload[employee_id] += task.get('estimated_hours', 0)
                
                logger.info(
                    f"Assigned task {task['task_id']} to employee {employee_id} "
                    f"(score: {best_candidate['match_score']:.3f})"
                )
        
        logger.info(f"Greedy assignment complete: {len(assignments)} assignments made")
        return assignments
    
    def hungarian_assignment(
        self,
        tasks: List[Dict],
        employees: List[Dict]
    ) -> List[Dict]:
        """
        Hungarian algorithm for optimal task assignment
        Finds optimal assignment minimizing total cost
        
        Args:
            tasks: List of task dictionaries
            employees: List of employee dictionaries
        
        Returns:
            List of assignment dictionaries
        """
        logger.info(f"Running Hungarian assignment for {len(tasks)} tasks")
        
        if not tasks or not employees:
            return []
        
        # Build cost matrix
        cost_matrix = np.zeros((len(tasks), len(employees)))
        
        for i, task in enumerate(tasks):
            candidates = self.score_inference.score_candidates_for_task(
                task,
                employees,
                top_k=len(employees)
            )
            
            for j, employee in enumerate(employees):
                # Find score for this employee
                candidate = next(
                    (c for c in candidates if c['employee_id'] == employee['employee_id']),
                    None
                )
                
                if candidate:
                    # Convert score to cost (higher score = lower cost)
                    cost = 1.0 - candidate['match_score']
                else:
                    cost = 1.0
                
                cost_matrix[i, j] = cost
        
        # Run Hungarian algorithm
        task_indices, employee_indices = linear_sum_assignment(cost_matrix)
        
        # Create assignments
        assignments = []
        for task_idx, emp_idx in zip(task_indices, employee_indices):
            task = tasks[task_idx]
            employee = employees[emp_idx]
            
            assignment = {
                'task_id': task['task_id'],
                'employee_id': employee['employee_id'],
                'assignment_method': 'hungarian',
                'assignment_score': 1.0 - cost_matrix[task_idx, emp_idx],
                'task_title': task.get('title'),
                'employee_name': employee.get('name'),
                'estimated_hours': task.get('estimated_hours', 0)
            }
            
            assignments.append(assignment)
            
            logger.info(
                f"Assigned task {task['task_id']} to employee {employee['employee_id']} "
                f"(score: {assignment['assignment_score']:.3f})"
            )
        
        logger.info(f"Hungarian assignment complete: {len(assignments)} assignments made")
        return assignments
    
    def balanced_assignment(
        self,
        tasks: List[Dict],
        employees: List[Dict],
        workload_weight: float = 0.3
    ) -> List[Dict]:
        """
        Balanced assignment considering both match quality and workload distribution
        
        Args:
            tasks: List of task dictionaries
            employees: List of employee dictionaries
            workload_weight: Weight for workload balancing (0-1)
        
        Returns:
            List of assignment dictionaries
        """
        logger.info(f"Running balanced assignment for {len(tasks)} tasks")
        
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
            # Score all employees
            candidates = self.score_inference.score_candidates_for_task(
                task,
                employees,
                top_k=len(employees)
            )
            
            # Adjust scores based on current workload
            for candidate in candidates:
                employee_id = candidate['employee_id']
                employee = next(e for e in employees if e['employee_id'] == employee_id)
                
                # Calculate workload factor (lower workload = higher factor)
                current = employee_workload[employee_id]
                maximum = employee.get('max_workload', 40)
                workload_factor = 1.0 - (current / maximum) if maximum > 0 else 0
                
                # Combine match score with workload factor
                original_score = candidate['match_score']
                adjusted_score = (
                    (1 - workload_weight) * original_score +
                    workload_weight * workload_factor
                )
                candidate['adjusted_score'] = adjusted_score
            
            # Sort by adjusted score
            candidates.sort(key=lambda c: c.get('adjusted_score', 0), reverse=True)
            
            # Check if best candidate has capacity
            best_candidate = candidates[0]
            employee_id = best_candidate['employee_id']
            employee = next(e for e in employees if e['employee_id'] == employee_id)
            
            task_hours = task.get('estimated_hours', 0)
            if employee_workload[employee_id] + task_hours <= employee.get('max_workload', 40):
                # Create assignment
                assignment = {
                    'task_id': task['task_id'],
                    'employee_id': employee_id,
                    'assignment_method': 'balanced',
                    'assignment_score': best_candidate['adjusted_score'],
                    'task_title': task.get('title'),
                    'employee_name': best_candidate['employee_name'],
                    'estimated_hours': task_hours
                }
                
                assignments.append(assignment)
                employee_workload[employee_id] += task_hours
                
                logger.info(
                    f"Assigned task {task['task_id']} to employee {employee_id} "
                    f"(adjusted score: {assignment['assignment_score']:.3f})"
                )
            else:
                logger.warning(
                    f"Best candidate for task {task['task_id']} at capacity, "
                    f"trying next best"
                )
                # Try next best candidates
                for candidate in candidates[1:]:
                    employee_id = candidate['employee_id']
                    employee = next(e for e in employees if e['employee_id'] == employee_id)
                    
                    if employee_workload[employee_id] + task_hours <= employee.get('max_workload', 40):
                        assignment = {
                            'task_id': task['task_id'],
                            'employee_id': employee_id,
                            'assignment_method': 'balanced',
                            'assignment_score': candidate['adjusted_score'],
                            'task_title': task.get('title'),
                            'employee_name': candidate['employee_name'],
                            'estimated_hours': task_hours
                        }
                        
                        assignments.append(assignment)
                        employee_workload[employee_id] += task_hours
                        break
        
        logger.info(f"Balanced assignment complete: {len(assignments)} assignments made")
        return assignments
    
    def assign_and_store(
        self,
        tasks: List[Dict],
        employees: List[Dict],
        method: str = 'balanced',
        database_connection=None
    ) -> List[Dict]:
        """
        Assign tasks and store results in database
        
        Args:
            tasks: List of task dictionaries
            employees: List of employee dictionaries
            method: Assignment method ('greedy', 'hungarian', 'balanced')
            database_connection: Database connection for storing results
        
        Returns:
            List of assignments
        """
        # Select assignment method
        if method == 'greedy':
            assignments = self.greedy_assignment(tasks, employees)
        elif method == 'hungarian':
            assignments = self.hungarian_assignment(tasks, employees)
        elif method == 'balanced':
            assignments = self.balanced_assignment(tasks, employees)
        else:
            raise ValueError(f"Unknown assignment method: {method}")
        
        # Store in database
        if database_connection and assignments:
            self._store_assignments(assignments, database_connection)
        
        return assignments
    
    def _store_assignments(self, assignments: List[Dict], database_connection):
        """Store assignments in database"""
        # TODO: Implement actual database insertion
        logger.info(f"Storing {len(assignments)} assignments in database (placeholder)")
        
        # Example SQL:
        # INSERT INTO Task_Assignments (task_id, employee_id, assignment_method, assignment_score)
        # VALUES (?, ?, ?, ?)
        pass


# Singleton instance
_task_assigner = None

def get_task_assigner() -> TaskAssigner:
    """Get or create singleton TaskAssigner instance"""
    global _task_assigner
    if _task_assigner is None:
        _task_assigner = TaskAssigner()
    return _task_assigner
