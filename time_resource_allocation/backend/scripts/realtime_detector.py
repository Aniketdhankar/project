"""
Real-time Anomaly Detector
Monitors task progress and detects anomalies with Gemini API triage
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

from gemini_client import get_gemini_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealtimeDetector:
    """Detects anomalies in task execution and generates triage recommendations"""
    
    def __init__(self):
        """Initialize real-time detector"""
        self.gemini_client = get_gemini_client()
        
        # Anomaly detection thresholds
        self.thresholds = {
            'deadline_risk_days': 3,  # Days before deadline to flag risk
            'progress_delay_ratio': 0.3,  # If progress < expected by this ratio
            'workload_overload_ratio': 0.9,  # If workload > max by this ratio
            'stagnation_days': 2,  # Days without progress update
        }
    
    def check_deadline_risk(
        self,
        task: Dict,
        assignment: Dict,
        progress: Dict
    ) -> Optional[Dict]:
        """
        Check if task is at risk of missing deadline
        
        Args:
            task: Task data dictionary
            assignment: Assignment data dictionary
            progress: Latest progress data dictionary
        
        Returns:
            Anomaly dictionary if risk detected, None otherwise
        """
        deadline = task.get('deadline')
        if not deadline:
            return None
        
        if isinstance(deadline, str):
            deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
        
        days_remaining = (deadline - datetime.now()).days
        
        # Check if deadline is near
        if days_remaining <= self.thresholds['deadline_risk_days']:
            progress_pct = progress.get('progress_percentage', 0)
            
            # If not close to completion, flag as risk
            if progress_pct < 90:
                severity = 'critical' if days_remaining <= 1 else 'high'
                
                return {
                    'anomaly_type': 'deadline_risk',
                    'severity': severity,
                    'task_id': task['task_id'],
                    'employee_id': assignment.get('employee_id'),
                    'description': (
                        f"Task is {progress_pct:.1f}% complete with {days_remaining} days "
                        f"remaining until deadline"
                    ),
                    'detected_at': datetime.now(),
                    'metadata': {
                        'days_remaining': days_remaining,
                        'progress_percentage': progress_pct,
                        'deadline': deadline.isoformat()
                    }
                }
        
        return None
    
    def check_progress_delay(
        self,
        task: Dict,
        assignment: Dict,
        progress: Dict
    ) -> Optional[Dict]:
        """
        Check if task progress is significantly delayed
        
        Args:
            task: Task data dictionary
            assignment: Assignment data dictionary
            progress: Latest progress data dictionary
        
        Returns:
            Anomaly dictionary if delay detected, None otherwise
        """
        assigned_at = assignment.get('assigned_at')
        if not assigned_at:
            return None
        
        if isinstance(assigned_at, str):
            assigned_at = datetime.fromisoformat(assigned_at.replace('Z', '+00:00'))
        
        # Calculate expected progress
        estimated_hours = task.get('estimated_hours', 40)
        hours_spent = progress.get('hours_spent', 0)
        progress_pct = progress.get('progress_percentage', 0)
        
        # Simple linear expected progress
        days_elapsed = (datetime.now() - assigned_at).days
        expected_daily_progress = 100 / (estimated_hours / 8)  # Assuming 8 hours/day
        expected_progress = min(expected_daily_progress * days_elapsed, 100)
        
        # Check if actual progress is significantly behind
        progress_gap = expected_progress - progress_pct
        
        if progress_gap > (expected_progress * self.thresholds['progress_delay_ratio']):
            return {
                'anomaly_type': 'progress_delay',
                'severity': 'medium' if progress_gap < 30 else 'high',
                'task_id': task['task_id'],
                'employee_id': assignment.get('employee_id'),
                'description': (
                    f"Task progress ({progress_pct:.1f}%) is behind expected "
                    f"({expected_progress:.1f}%) by {progress_gap:.1f}%"
                ),
                'detected_at': datetime.now(),
                'metadata': {
                    'actual_progress': progress_pct,
                    'expected_progress': expected_progress,
                    'progress_gap': progress_gap,
                    'hours_spent': hours_spent
                }
            }
        
        return None
    
    def check_workload_overload(
        self,
        employee: Dict,
        assignments: List[Dict]
    ) -> Optional[Dict]:
        """
        Check if employee is overloaded
        
        Args:
            employee: Employee data dictionary
            assignments: List of current assignments for employee
        
        Returns:
            Anomaly dictionary if overload detected, None otherwise
        """
        current_workload = employee.get('current_workload', 0)
        max_workload = employee.get('max_workload', 40)
        
        workload_ratio = current_workload / max_workload if max_workload > 0 else 0
        
        if workload_ratio > self.thresholds['workload_overload_ratio']:
            return {
                'anomaly_type': 'workload_overload',
                'severity': 'high' if workload_ratio > 1.0 else 'medium',
                'employee_id': employee['employee_id'],
                'description': (
                    f"Employee workload ({current_workload:.1f}h) exceeds "
                    f"{workload_ratio*100:.1f}% of capacity ({max_workload}h)"
                ),
                'detected_at': datetime.now(),
                'metadata': {
                    'current_workload': current_workload,
                    'max_workload': max_workload,
                    'workload_ratio': workload_ratio,
                    'active_tasks': len(assignments)
                }
            }
        
        return None
    
    def check_stagnation(
        self,
        task: Dict,
        progress_logs: List[Dict]
    ) -> Optional[Dict]:
        """
        Check if task has stagnated (no progress updates)
        
        Args:
            task: Task data dictionary
            progress_logs: List of progress log entries
        
        Returns:
            Anomaly dictionary if stagnation detected, None otherwise
        """
        if not progress_logs:
            return None
        
        # Get most recent progress log
        latest_log = max(
            progress_logs,
            key=lambda l: l.get('logged_at', datetime.min)
        )
        
        logged_at = latest_log.get('logged_at')
        if isinstance(logged_at, str):
            logged_at = datetime.fromisoformat(logged_at.replace('Z', '+00:00'))
        
        days_since_update = (datetime.now() - logged_at).days
        
        if days_since_update >= self.thresholds['stagnation_days']:
            # Check if task is completed
            if task.get('status') != 'completed':
                return {
                    'anomaly_type': 'stagnation',
                    'severity': 'medium',
                    'task_id': task['task_id'],
                    'description': (
                        f"No progress updates for {days_since_update} days"
                    ),
                    'detected_at': datetime.now(),
                    'metadata': {
                        'days_since_update': days_since_update,
                        'last_update': logged_at.isoformat(),
                        'last_progress': latest_log.get('progress_percentage', 0)
                    }
                }
        
        return None
    
    def detect_anomalies(
        self,
        tasks: List[Dict],
        employees: List[Dict],
        assignments: List[Dict],
        progress_logs: List[Dict]
    ) -> List[Dict]:
        """
        Run all anomaly detection checks
        
        Args:
            tasks: List of task dictionaries
            employees: List of employee dictionaries
            assignments: List of assignment dictionaries
            progress_logs: List of progress log dictionaries
        
        Returns:
            List of detected anomalies
        """
        logger.info("Running anomaly detection...")
        
        anomalies = []
        
        # Check each task
        for task in tasks:
            if task.get('status') in ['completed', 'cancelled']:
                continue
            
            # Find assignment for task
            assignment = next(
                (a for a in assignments if a['task_id'] == task['task_id']),
                None
            )
            
            if not assignment:
                continue
            
            # Get latest progress
            task_progress_logs = [
                p for p in progress_logs 
                if p.get('task_id') == task['task_id']
            ]
            
            latest_progress = max(
                task_progress_logs,
                key=lambda p: p.get('logged_at', datetime.min),
                default={'progress_percentage': 0, 'hours_spent': 0}
            )
            
            # Run checks
            deadline_anomaly = self.check_deadline_risk(task, assignment, latest_progress)
            if deadline_anomaly:
                anomalies.append(deadline_anomaly)
            
            delay_anomaly = self.check_progress_delay(task, assignment, latest_progress)
            if delay_anomaly:
                anomalies.append(delay_anomaly)
            
            stagnation_anomaly = self.check_stagnation(task, task_progress_logs)
            if stagnation_anomaly:
                anomalies.append(stagnation_anomaly)
        
        # Check employee workload
        for employee in employees:
            emp_assignments = [
                a for a in assignments
                if a.get('employee_id') == employee['employee_id']
            ]
            
            overload_anomaly = self.check_workload_overload(employee, emp_assignments)
            if overload_anomaly:
                anomalies.append(overload_anomaly)
        
        logger.info(f"Detected {len(anomalies)} anomalies")
        return anomalies
    
    def generate_triage(
        self,
        anomaly: Dict,
        task: Dict,
        employee: Optional[Dict] = None
    ) -> Dict:
        """
        Generate triage notes and recommendations using Gemini
        
        Args:
            anomaly: Anomaly dictionary
            task: Task data dictionary
            employee: Employee data dictionary (optional)
        
        Returns:
            Enhanced anomaly with triage notes and recommendations
        """
        logger.info(f"Generating triage for anomaly: {anomaly['anomaly_type']}")
        
        # Prepare data for Gemini
        anomaly_data = {
            'task_title': task.get('title'),
            'task_description': task.get('description'),
            'anomaly_type': anomaly['anomaly_type'],
            'severity': anomaly['severity'],
            'description': anomaly['description'],
            'employee_name': employee.get('name') if employee else 'Unknown',
            'workload': employee.get('current_workload') if employee else 'Unknown',
            'progress': anomaly.get('metadata', {}).get('actual_progress', 0)
        }
        
        # Get triage from Gemini
        triage_result = self.gemini_client.generate_triage_notes(anomaly_data)
        
        # Enhance anomaly with triage information
        anomaly['gemini_triage_notes'] = triage_result['triage_notes']
        anomaly['recommended_actions'] = triage_result['recommended_actions']
        anomaly['triage_priority'] = triage_result['priority']
        
        return anomaly
    
    def process_and_store_anomalies(
        self,
        anomalies: List[Dict],
        tasks_dict: Dict[int, Dict],
        employees_dict: Dict[int, Dict],
        database_connection=None
    ) -> List[Dict]:
        """
        Process anomalies with triage and store in database
        
        Args:
            anomalies: List of detected anomalies
            tasks_dict: Dictionary mapping task_id to task data
            employees_dict: Dictionary mapping employee_id to employee data
            database_connection: Database connection
        
        Returns:
            List of processed anomalies with triage
        """
        logger.info(f"Processing {len(anomalies)} anomalies with triage...")
        
        processed_anomalies = []
        
        for anomaly in anomalies:
            task_id = anomaly.get('task_id')
            employee_id = anomaly.get('employee_id')
            
            task = tasks_dict.get(task_id)
            employee = employees_dict.get(employee_id)
            
            if task:
                # Generate triage
                enhanced_anomaly = self.generate_triage(anomaly, task, employee)
                processed_anomalies.append(enhanced_anomaly)
        
        # Store in database
        if database_connection and processed_anomalies:
            self._store_anomalies(processed_anomalies, database_connection)
        
        logger.info(f"Processed {len(processed_anomalies)} anomalies")
        return processed_anomalies
    
    def _store_anomalies(self, anomalies: List[Dict], database_connection):
        """Store anomalies in database"""
        # TODO: Implement actual database insertion
        logger.info(f"Storing {len(anomalies)} anomalies in database (placeholder)")
        pass


# Singleton instance
_realtime_detector = None

def get_realtime_detector() -> RealtimeDetector:
    """Get or create singleton RealtimeDetector instance"""
    global _realtime_detector
    if _realtime_detector is None:
        _realtime_detector = RealtimeDetector()
    return _realtime_detector
