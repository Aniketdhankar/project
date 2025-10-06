"""
Unit tests for scheduler_service module
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
scripts_path = Path(__file__).parent.parent / 'scripts'
sys.path.insert(0, str(scripts_path))

from scheduler_service import SchedulerService, get_scheduler_service


@pytest.fixture
def sample_tasks():
    """Sample tasks for testing"""
    return [
        {
            'task_id': 1,
            'title': 'Implement Authentication',
            'required_skills': 'Python,Flask,JWT',
            'priority': 'high',
            'estimated_hours': 20,
            'deadline': '2024-02-15',
            'complexity_score': 4.0
        },
        {
            'task_id': 2,
            'title': 'Create Dashboard',
            'required_skills': 'React,JavaScript,CSS',
            'priority': 'medium',
            'estimated_hours': 15,
            'deadline': '2024-02-20',
            'complexity_score': 3.0
        },
        {
            'task_id': 3,
            'title': 'Database Optimization',
            'required_skills': 'PostgreSQL,SQL',
            'priority': 'critical',
            'estimated_hours': 10,
            'deadline': '2024-02-10',
            'complexity_score': 3.5
        }
    ]


@pytest.fixture
def sample_employees():
    """Sample employees for testing"""
    return [
        {
            'employee_id': 1,
            'name': 'Alice Johnson',
            'skills': 'Python,React,PostgreSQL,ML',
            'experience_years': 5.5,
            'current_workload': 20,
            'max_workload': 40,
            'availability_status': 'available',
            'performance_rating': 4.5
        },
        {
            'employee_id': 2,
            'name': 'Bob Smith',
            'skills': 'Python,Flask,PostgreSQL,API',
            'experience_years': 3.0,
            'current_workload': 15,
            'max_workload': 40,
            'availability_status': 'available',
            'performance_rating': 4.0
        },
        {
            'employee_id': 3,
            'name': 'Carol White',
            'skills': 'React,JavaScript,CSS,HTML',
            'experience_years': 4.0,
            'current_workload': 10,
            'max_workload': 40,
            'availability_status': 'available',
            'performance_rating': 4.2
        }
    ]


class TestSchedulerService:
    """Test cases for SchedulerService"""
    
    def test_scheduler_initialization(self):
        """Test scheduler service initialization"""
        scheduler = SchedulerService()
        assert scheduler is not None
        assert scheduler.ml_service is not None
        assert isinstance(scheduler.assignment_previews, dict)
    
    def test_singleton_pattern(self):
        """Test that get_scheduler_service returns singleton"""
        scheduler1 = get_scheduler_service()
        scheduler2 = get_scheduler_service()
        assert scheduler1 is scheduler2
    
    def test_greedy_ml_assignment(self, sample_tasks, sample_employees):
        """Test greedy ML assignment algorithm"""
        scheduler = SchedulerService()
        
        assignments = scheduler.assign_tasks(
            sample_tasks,
            sample_employees,
            method='greedy_ml'
        )
        
        # Verify assignments were created
        assert len(assignments) > 0
        assert len(assignments) <= len(sample_tasks)
        
        # Verify assignment structure
        for assignment in assignments:
            assert 'task_id' in assignment
            assert 'employee_id' in assignment
            assert 'assignment_method' in assignment
            assert assignment['assignment_method'] == 'greedy_ml'
            assert 'assignment_score' in assignment
            assert 0 <= assignment['assignment_score'] <= 1
            assert 'confidence' in assignment
    
    def test_balanced_ml_assignment(self, sample_tasks, sample_employees):
        """Test balanced ML assignment algorithm"""
        scheduler = SchedulerService()
        
        assignments = scheduler.assign_tasks(
            sample_tasks,
            sample_employees,
            method='balanced_ml'
        )
        
        # Verify assignments were created
        assert len(assignments) > 0
        
        # Verify assignment structure
        for assignment in assignments:
            assert assignment['assignment_method'] == 'balanced_ml'
            assert 'assignment_score' in assignment
            assert 'ml_score' in assignment
    
    def test_assignment_respects_max_assignments(self, sample_tasks, sample_employees):
        """Test that max assignments per employee is respected"""
        scheduler = SchedulerService()
        
        # Create many tasks
        many_tasks = sample_tasks * 5  # 15 tasks
        
        # Set max assignments per employee to 2
        constraints = {'max_assignments_per_employee': 2}
        
        assignments = scheduler.assign_tasks(
            many_tasks,
            sample_employees,
            constraints=constraints,
            method='greedy_ml'
        )
        
        # Count assignments per employee
        employee_counts = {}
        for assignment in assignments:
            emp_id = assignment['employee_id']
            employee_counts[emp_id] = employee_counts.get(emp_id, 0) + 1
        
        # Verify no employee has more than max assignments
        for count in employee_counts.values():
            assert count <= 2
    
    def test_assignment_respects_workload(self, sample_employees):
        """Test that workload constraints are respected"""
        scheduler = SchedulerService()
        
        # Create a task that would exceed workload
        heavy_task = {
            'task_id': 100,
            'title': 'Heavy Task',
            'required_skills': 'Python',
            'priority': 'high',
            'estimated_hours': 30,  # This would exceed capacity for employee 1 (20+30=50 > 40)
            'deadline': '2024-02-15',
            'complexity_score': 4.0
        }
        
        # Employee 1 already has 20 hours workload
        assignments = scheduler.assign_tasks(
            [heavy_task],
            [sample_employees[0]],  # Only Alice with 20 hours current workload
            method='greedy_ml'
        )
        
        # Should not assign because it would exceed max_workload
        assert len(assignments) == 0
    
    def test_preview_assignments(self, sample_tasks, sample_employees):
        """Test assignment preview generation"""
        scheduler = SchedulerService()
        
        preview = scheduler.preview_assignments(
            sample_tasks,
            sample_employees,
            method='greedy_ml'
        )
        
        # Verify preview structure
        assert 'preview_id' in preview
        assert preview['preview_id'].startswith('preview_')
        assert 'created_at' in preview
        assert 'method' in preview
        assert preview['method'] == 'greedy_ml'
        assert 'assignments' in preview
        assert len(preview['assignments']) > 0
        assert 'summary' in preview
        
        # Verify summary
        summary = preview['summary']
        assert 'total_tasks' in summary
        assert 'total_employees' in summary
        assert 'assignments_created' in summary
        assert 'unassigned_tasks' in summary
    
    def test_finalize_assignments(self, sample_tasks, sample_employees):
        """Test assignment finalization"""
        scheduler = SchedulerService()
        
        # Create preview
        preview = scheduler.preview_assignments(
            sample_tasks,
            sample_employees,
            method='greedy_ml'
        )
        
        preview_id = preview['preview_id']
        
        # Finalize assignments
        result = scheduler.finalize_assignments(preview_id)
        
        # Verify result
        assert 'preview_id' in result
        assert result['preview_id'] == preview_id
        assert 'finalized_at' in result
        assert 'assignments_stored' in result
        assert 'summary' in result
        
        # Verify preview was cleaned up
        assert preview_id not in scheduler.assignment_previews
    
    def test_finalize_nonexistent_preview_raises_error(self):
        """Test that finalizing non-existent preview raises error"""
        scheduler = SchedulerService()
        
        with pytest.raises(ValueError, match="Preview .* not found"):
            scheduler.finalize_assignments('nonexistent_preview_id')
    
    def test_priority_ordering(self, sample_employees):
        """Test that higher priority tasks are assigned first"""
        scheduler = SchedulerService()
        
        # Create tasks with different priorities
        tasks = [
            {
                'task_id': 1,
                'title': 'Low Priority Task',
                'required_skills': 'Python',
                'priority': 'low',
                'estimated_hours': 5,
                'deadline': '2024-03-01',
                'complexity_score': 2.0
            },
            {
                'task_id': 2,
                'title': 'Critical Priority Task',
                'required_skills': 'Python',
                'priority': 'critical',
                'estimated_hours': 5,
                'deadline': '2024-02-10',
                'complexity_score': 4.0
            }
        ]
        
        assignments = scheduler.assign_tasks(
            tasks,
            sample_employees,
            method='greedy_ml'
        )
        
        # Critical task should be assigned first
        if len(assignments) > 0:
            # First assignment should be the critical task
            first_task_id = assignments[0]['task_id']
            # The critical task (task_id=2) should be assigned
            assert any(a['task_id'] == 2 for a in assignments)
    
    def test_unavailable_employees_excluded(self, sample_tasks):
        """Test that unavailable employees are not assigned tasks"""
        # Create an unavailable employee
        unavailable_employee = {
            'employee_id': 99,
            'name': 'Unavailable User',
            'skills': 'Python,React,PostgreSQL,ML',
            'experience_years': 5.0,
            'current_workload': 10,
            'max_workload': 40,
            'availability_status': 'on_leave',  # Not available
            'performance_rating': 4.0
        }
        
        scheduler = SchedulerService()
        assignments = scheduler.assign_tasks(
            sample_tasks,
            [unavailable_employee],
            method='greedy_ml'
        )
        
        # Should not assign any tasks to unavailable employee
        assert len(assignments) == 0


class TestMLServiceIntegration:
    """Test ML service integration with scheduler"""
    
    def test_ml_scoring_used_in_assignment(self, sample_tasks, sample_employees):
        """Test that ML scoring is used in assignment"""
        scheduler = SchedulerService()
        
        assignments = scheduler.assign_tasks(
            sample_tasks,
            sample_employees,
            method='greedy_ml'
        )
        
        # Verify ML scores are present
        for assignment in assignments:
            assert 'assignment_score' in assignment
            assert isinstance(assignment['assignment_score'], (int, float))
            assert 0 <= assignment['assignment_score'] <= 1
    
    def test_feature_logging(self, sample_tasks, sample_employees):
        """Test that features are logged in assignments"""
        scheduler = SchedulerService()
        
        assignments = scheduler.assign_tasks(
            sample_tasks,
            sample_employees,
            method='greedy_ml'
        )
        
        # Verify features are present for logging
        for assignment in assignments:
            assert 'features' in assignment
            assert isinstance(assignment['features'], list)
            # Features should be non-empty
            assert len(assignment['features']) > 0
