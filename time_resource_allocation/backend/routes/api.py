"""
API Routes
Flask API endpoints for the application
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
import sys
from pathlib import Path

# Add scripts directory to path for imports
scripts_path = Path(__file__).parent.parent / 'scripts'
sys.path.insert(0, str(scripts_path))

# Placeholder for database access (implement with actual DB)
# from models.models import db, Employee, Task, TaskAssignment, ProgressLog

logger = logging.getLogger(__name__)

api = Blueprint('api', __name__)


# ========================================
# Pipeline Endpoints
# ========================================

@api.route('/trigger_pipeline', methods=['POST'])
def trigger_pipeline():
    """
    Trigger the ML pipeline to score tasks and make assignments
    
    Request JSON:
    {
        "method": "greedy_ml|balanced_ml",
        "include_gemini": true|false,
        "max_assignments_per_employee": 5,
        "preview_only": false
    }
    """
    try:
        from scheduler_service import get_scheduler_service
        
        data = request.get_json() or {}
        method = data.get('method', 'greedy_ml')
        include_gemini = data.get('include_gemini', False)
        max_assignments = data.get('max_assignments_per_employee', 5)
        preview_only = data.get('preview_only', False)
        
        logger.info(f"Triggering pipeline with method={method}, gemini={include_gemini}")
        
        # TODO: Fetch pending tasks and available employees from database
        # For now, use sample data
        sample_tasks = [
            {
                'task_id': 1,
                'title': 'Implement User Authentication',
                'required_skills': 'Python,Flask,JWT',
                'priority': 'high',
                'estimated_hours': 20,
                'deadline': '2024-02-15',
                'complexity_score': 4.0
            },
            {
                'task_id': 2,
                'title': 'Create Dashboard UI',
                'required_skills': 'React,JavaScript,CSS',
                'priority': 'medium',
                'estimated_hours': 15,
                'deadline': '2024-02-20',
                'complexity_score': 3.0
            }
        ]
        
        sample_employees = [
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
            }
        ]
        
        # Get scheduler service
        scheduler = get_scheduler_service()
        
        # Prepare constraints
        constraints = {
            'max_assignments_per_employee': max_assignments,
            'include_gemini': include_gemini
        }
        
        if preview_only:
            # Generate preview only
            preview = scheduler.preview_assignments(
                sample_tasks, sample_employees, constraints, method
            )
            
            result = {
                'status': 'success',
                'message': 'Assignment preview generated',
                'preview': preview,
                'timestamp': datetime.now().isoformat()
            }
        else:
            # Generate and finalize assignments
            preview = scheduler.preview_assignments(
                sample_tasks, sample_employees, constraints, method
            )
            
            # TODO: Pass database connection
            finalized = scheduler.finalize_assignments(preview['preview_id'])
            
            result = {
                'status': 'success',
                'message': 'Pipeline completed successfully',
                'finalized': finalized,
                'timestamp': datetime.now().isoformat()
            }
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error triggering pipeline: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ========================================
# Assignment Endpoints
# ========================================

@api.route('/assignments', methods=['GET'])
def get_assignments():
    """
    Get all task assignments with optional filtering
    
    Query params:
    - status: Filter by status (assigned, in_progress, completed)
    - employee_id: Filter by employee
    - task_id: Filter by task
    - page: Page number (default 1)
    - per_page: Results per page (default 20)
    """
    try:
        # Get query parameters
        status = request.args.get('status')
        employee_id = request.args.get('employee_id', type=int)
        task_id = request.args.get('task_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        logger.info(f"Fetching assignments: status={status}, emp={employee_id}, task={task_id}")
        
        # TODO: Implement actual database query
        # query = TaskAssignment.query
        # if status:
        #     query = query.filter_by(status=status)
        # if employee_id:
        #     query = query.filter_by(employee_id=employee_id)
        # if task_id:
        #     query = query.filter_by(task_id=task_id)
        # 
        # pagination = query.paginate(page=page, per_page=per_page)
        # assignments = [a.to_dict() for a in pagination.items]
        
        # Placeholder response
        assignments = [
            {
                'assignment_id': 1,
                'task_id': 1,
                'employee_id': 1,
                'task_title': 'Implement User Authentication',
                'employee_name': 'Alice Johnson',
                'status': 'in_progress',
                'assigned_at': '2024-01-15T10:00:00',
                'estimated_completion': '2024-01-22T17:00:00',
                'progress': 45
            },
            {
                'assignment_id': 2,
                'task_id': 2,
                'employee_id': 3,
                'task_title': 'Create Dashboard UI',
                'employee_name': 'Carol White',
                'status': 'assigned',
                'assigned_at': '2024-01-16T09:00:00',
                'estimated_completion': '2024-01-26T17:00:00',
                'progress': 0
            }
        ]
        
        return jsonify({
            'assignments': assignments,
            'page': page,
            'per_page': per_page,
            'total': len(assignments)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching assignments: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api.route('/assignments/<int:assignment_id>', methods=['GET'])
def get_assignment(assignment_id):
    """Get details of a specific assignment"""
    try:
        # TODO: Implement database query
        # assignment = TaskAssignment.query.get_or_404(assignment_id)
        
        # Placeholder response
        assignment = {
            'assignment_id': assignment_id,
            'task_id': 1,
            'employee_id': 1,
            'task_title': 'Implement User Authentication',
            'employee_name': 'Alice Johnson',
            'status': 'in_progress',
            'assigned_at': '2024-01-15T10:00:00',
            'started_at': '2024-01-15T14:00:00',
            'estimated_completion': '2024-01-22T17:00:00',
            'assignment_score': 0.87,
            'assignment_method': 'balanced',
            'progress': 45
        }
        
        return jsonify(assignment), 200
        
    except Exception as e:
        logger.error(f"Error fetching assignment {assignment_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api.route('/assignments/preview', methods=['POST'])
def preview_assignments():
    """
    Preview task assignments without finalizing
    
    Request JSON:
    {
        "tasks": [...],
        "employees": [...],
        "method": "greedy_ml|balanced_ml",
        "constraints": {
            "max_assignments_per_employee": 5,
            "include_gemini": false
        }
    }
    """
    try:
        from scheduler_service import get_scheduler_service
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        tasks = data.get('tasks', [])
        employees = data.get('employees', [])
        method = data.get('method', 'greedy_ml')
        constraints = data.get('constraints', {})
        
        if not tasks:
            return jsonify({'error': 'No tasks provided'}), 400
        if not employees:
            return jsonify({'error': 'No employees provided'}), 400
        
        logger.info(f"Generating assignment preview for {len(tasks)} tasks")
        
        scheduler = get_scheduler_service()
        preview = scheduler.preview_assignments(tasks, employees, constraints, method)
        
        return jsonify(preview), 200
        
    except Exception as e:
        logger.error(f"Error generating preview: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@api.route('/assignments/finalize/<preview_id>', methods=['POST'])
def finalize_assignments(preview_id):
    """
    Finalize assignments from a preview
    
    Path params:
    - preview_id: Preview identifier
    """
    try:
        from scheduler_service import get_scheduler_service
        
        logger.info(f"Finalizing assignments for preview {preview_id}")
        
        scheduler = get_scheduler_service()
        
        # TODO: Pass database connection
        result = scheduler.finalize_assignments(preview_id)
        
        return jsonify(result), 200
        
    except ValueError as e:
        logger.warning(f"Preview not found: {str(e)}")
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error finalizing assignments: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ========================================
# Task Queue Endpoints
# ========================================

@api.route('/task_queue', methods=['GET'])
def get_task_queue():
    """
    Get pending tasks in the queue
    
    Query params:
    - priority: Filter by priority
    - status: Filter by status (default: pending)
    """
    try:
        priority = request.args.get('priority')
        status = request.args.get('status', 'pending')
        
        # TODO: Implement database query
        # query = Task.query.filter_by(status=status)
        # if priority:
        #     query = query.filter_by(priority=priority)
        # tasks = [t.to_dict() for t in query.all()]
        
        # Placeholder response
        tasks = [
            {
                'task_id': 3,
                'title': 'Train ML Model',
                'priority': 'critical',
                'estimated_hours': 24.0,
                'deadline': '2024-01-20T17:00:00',
                'required_skills': 'Python,LightGBM,ML',
                'complexity_score': 4.5,
                'status': 'pending'
            },
            {
                'task_id': 4,
                'title': 'API Documentation',
                'priority': 'medium',
                'estimated_hours': 8.0,
                'deadline': '2024-01-28T17:00:00',
                'required_skills': 'API,Documentation',
                'complexity_score': 2.0,
                'status': 'pending'
            }
        ]
        
        return jsonify({
            'tasks': tasks,
            'count': len(tasks)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching task queue: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ========================================
# Employee Workload Endpoints
# ========================================

@api.route('/employee/<int:employee_id>/workload', methods=['GET'])
def get_employee_workload(employee_id):
    """Get workload information for an employee"""
    try:
        # TODO: Implement database query
        # employee = Employee.query.get_or_404(employee_id)
        # assignments = TaskAssignment.query.filter_by(
        #     employee_id=employee_id,
        #     status='assigned'
        # ).all()
        
        # Placeholder response
        workload = {
            'employee_id': employee_id,
            'name': 'Alice Johnson',
            'current_workload': 32,
            'max_workload': 40,
            'utilization_percentage': 80,
            'active_tasks': 3,
            'tasks': [
                {
                    'task_id': 1,
                    'title': 'Implement User Authentication',
                    'estimated_hours': 16,
                    'progress': 45,
                    'deadline': '2024-01-22T17:00:00'
                },
                {
                    'task_id': 5,
                    'title': 'Setup CI/CD Pipeline',
                    'estimated_hours': 12,
                    'progress': 20,
                    'deadline': '2024-01-26T17:00:00'
                }
            ],
            'availability_status': 'available',
            'performance_rating': 4.5
        }
        
        return jsonify(workload), 200
        
    except Exception as e:
        logger.error(f"Error fetching workload for employee {employee_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ========================================
# Model Explanation Endpoints
# ========================================

@api.route('/models/explain/<int:task_id>', methods=['GET'])
def explain_model_prediction(task_id):
    """
    Get model explanation for task assignment predictions
    
    Query params:
    - employee_id: Specific employee to explain (optional)
    """
    try:
        employee_id = request.args.get('employee_id', type=int)
        
        # TODO: Implement actual model explanation (SHAP values, feature importance)
        
        # Placeholder response
        explanation = {
            'task_id': task_id,
            'task_title': 'Implement User Authentication',
            'top_candidates': [
                {
                    'employee_id': 1,
                    'name': 'Alice Johnson',
                    'score': 0.87,
                    'factors': {
                        'skill_match': 0.92,
                        'experience': 0.85,
                        'workload': 0.80,
                        'availability': 1.0
                    }
                },
                {
                    'employee_id': 2,
                    'name': 'Bob Smith',
                    'score': 0.81,
                    'factors': {
                        'skill_match': 0.88,
                        'experience': 0.75,
                        'workload': 0.90,
                        'availability': 1.0
                    }
                }
            ],
            'feature_importance': {
                'skill_match_score': 0.35,
                'employee_experience': 0.25,
                'workload_capacity_fit': 0.20,
                'employee_performance': 0.15,
                'task_complexity': 0.05
            }
        }
        
        return jsonify(explanation), 200
        
    except Exception as e:
        logger.error(f"Error explaining model for task {task_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ========================================
# Analytics Endpoints
# ========================================

@api.route('/analytics/dashboard', methods=['GET'])
def get_dashboard_analytics():
    """Get analytics data for dashboard"""
    try:
        # TODO: Implement actual analytics queries
        
        # Placeholder response
        analytics = {
            'total_tasks': 25,
            'completed_tasks': 12,
            'in_progress_tasks': 8,
            'pending_tasks': 5,
            'total_employees': 5,
            'avg_utilization': 75.2,
            'open_anomalies': 3,
            'tasks_at_risk': 2,
            'recent_assignments': 5,
            'completion_rate': 48.0
        }
        
        return jsonify(analytics), 200
        
    except Exception as e:
        logger.error(f"Error fetching dashboard analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api.route('/analytics/workload_distribution', methods=['GET'])
def get_workload_distribution():
    """Get workload distribution across employees"""
    try:
        # TODO: Implement actual workload query
        
        # Placeholder response
        distribution = [
            {'employee': 'Alice Johnson', 'workload': 32, 'max': 40, 'tasks': 3},
            {'employee': 'Bob Smith', 'workload': 28, 'max': 40, 'tasks': 2},
            {'employee': 'Carol White', 'workload': 35, 'max': 40, 'tasks': 3},
            {'employee': 'David Brown', 'workload': 20, 'max': 40, 'tasks': 2},
            {'employee': 'Eve Davis', 'workload': 25, 'max': 40, 'tasks': 2}
        ]
        
        return jsonify(distribution), 200
        
    except Exception as e:
        logger.error(f"Error fetching workload distribution: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ========================================
# Anomaly Endpoints
# ========================================

@api.route('/anomalies', methods=['GET'])
def get_anomalies():
    """Get detected anomalies"""
    try:
        status = request.args.get('status', 'open')
        
        # TODO: Implement database query
        
        # Placeholder response
        anomalies = [
            {
                'anomaly_id': 1,
                'task_id': 1,
                'task_title': 'Implement User Authentication',
                'employee_name': 'Alice Johnson',
                'anomaly_type': 'progress_delay',
                'severity': 'medium',
                'description': 'Task progress behind schedule',
                'detected_at': '2024-01-18T10:00:00',
                'recommended_actions': [
                    'Review task requirements',
                    'Schedule check-in meeting'
                ]
            }
        ]
        
        return jsonify({
            'anomalies': anomalies,
            'count': len(anomalies)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching anomalies: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ========================================
# Health Check
# ========================================

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200
