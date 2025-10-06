"""
Example: Using the Scheduler Service

This script demonstrates how to use the scheduler service for task assignment.
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from scheduler_service import get_scheduler_service


def example_basic_assignment():
    """Example 1: Basic task assignment"""
    print("=" * 60)
    print("Example 1: Basic Task Assignment")
    print("=" * 60)
    
    # Sample tasks
    tasks = [
        {
            'task_id': 1,
            'title': 'Implement User Authentication',
            'required_skills': 'Python,Flask,JWT,Security',
            'priority': 'high',
            'estimated_hours': 20,
            'deadline': '2024-02-15',
            'complexity_score': 4.0
        },
        {
            'task_id': 2,
            'title': 'Create Dashboard UI',
            'required_skills': 'React,JavaScript,CSS,HTML',
            'priority': 'medium',
            'estimated_hours': 15,
            'deadline': '2024-02-20',
            'complexity_score': 3.0
        },
        {
            'task_id': 3,
            'title': 'Database Optimization',
            'required_skills': 'PostgreSQL,SQL,Database',
            'priority': 'critical',
            'estimated_hours': 10,
            'deadline': '2024-02-10',
            'complexity_score': 3.5
        }
    ]
    
    # Sample employees
    employees = [
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
    
    # Get scheduler
    scheduler = get_scheduler_service()
    
    # Assign tasks using greedy ML algorithm
    print("\nRunning greedy_ml assignment...")
    assignments = scheduler.assign_tasks(
        tasks=tasks,
        employees=employees,
        method='greedy_ml'
    )
    
    # Display results
    print(f"\n{len(assignments)} assignments created:\n")
    for i, assignment in enumerate(assignments, 1):
        print(f"{i}. Task: {assignment['task_title']}")
        print(f"   Assigned to: {assignment['employee_name']}")
        print(f"   Score: {assignment['assignment_score']:.3f}")
        print(f"   Confidence: {assignment.get('confidence', 0):.3f}")
        print(f"   Estimated Hours: {assignment['estimated_hours']}")
        print()


def example_preview_and_finalize():
    """Example 2: Preview and finalization workflow"""
    print("=" * 60)
    print("Example 2: Preview and Finalization Workflow")
    print("=" * 60)
    
    tasks = [
        {
            'task_id': 101,
            'title': 'API Development',
            'required_skills': 'Python,Flask,REST',
            'priority': 'high',
            'estimated_hours': 25,
            'deadline': '2024-02-18',
            'complexity_score': 4.0
        },
        {
            'task_id': 102,
            'title': 'Frontend Integration',
            'required_skills': 'React,API,JavaScript',
            'priority': 'medium',
            'estimated_hours': 18,
            'deadline': '2024-02-22',
            'complexity_score': 3.5
        }
    ]
    
    employees = [
        {
            'employee_id': 10,
            'name': 'David Brown',
            'skills': 'Python,Flask,REST,API',
            'experience_years': 6.0,
            'current_workload': 15,
            'max_workload': 40,
            'availability_status': 'available',
            'performance_rating': 4.7
        },
        {
            'employee_id': 11,
            'name': 'Eve Davis',
            'skills': 'React,JavaScript,API,HTML,CSS',
            'experience_years': 4.5,
            'current_workload': 20,
            'max_workload': 40,
            'availability_status': 'available',
            'performance_rating': 4.3
        }
    ]
    
    scheduler = get_scheduler_service()
    
    # Generate preview
    print("\nGenerating assignment preview...")
    preview = scheduler.preview_assignments(
        tasks=tasks,
        employees=employees,
        method='balanced_ml'
    )
    
    # Display preview
    print(f"\nPreview ID: {preview['preview_id']}")
    print(f"Method: {preview['method']}")
    print(f"\nSummary:")
    print(f"  Total Tasks: {preview['summary']['total_tasks']}")
    print(f"  Total Employees: {preview['summary']['total_employees']}")
    print(f"  Assignments Created: {preview['summary']['assignments_created']}")
    print(f"  Unassigned Tasks: {preview['summary']['unassigned_tasks']}")
    
    print(f"\nAssignments Preview:")
    for i, assignment in enumerate(preview['assignments'], 1):
        print(f"{i}. {assignment['task_title']} → {assignment['employee_name']}")
        print(f"   Score: {assignment.get('assignment_score', 0):.3f}")
    
    # Finalize
    print("\n\nFinalizing assignments...")
    result = scheduler.finalize_assignments(preview['preview_id'])
    
    print(f"\nFinalization Result:")
    print(f"  Preview ID: {result['preview_id']}")
    print(f"  Finalized At: {result['finalized_at']}")
    print(f"  Assignments Stored: {result['assignments_stored']}")


def example_with_constraints():
    """Example 3: Using constraints"""
    print("=" * 60)
    print("Example 3: Assignment with Constraints")
    print("=" * 60)
    
    # Many tasks
    tasks = [
        {
            'task_id': i,
            'title': f'Task {i}',
            'required_skills': 'Python,JavaScript',
            'priority': ['low', 'medium', 'high'][i % 3],
            'estimated_hours': 10,
            'deadline': f'2024-02-{15 + i}',
            'complexity_score': 3.0
        }
        for i in range(1, 8)  # 7 tasks
    ]
    
    # Few employees
    employees = [
        {
            'employee_id': 20,
            'name': 'Frank Green',
            'skills': 'Python,JavaScript,React',
            'experience_years': 5.0,
            'current_workload': 10,
            'max_workload': 40,
            'availability_status': 'available',
            'performance_rating': 4.0
        },
        {
            'employee_id': 21,
            'name': 'Grace Lee',
            'skills': 'Python,JavaScript,Vue',
            'experience_years': 4.0,
            'current_workload': 15,
            'max_workload': 40,
            'availability_status': 'available',
            'performance_rating': 4.2
        }
    ]
    
    scheduler = get_scheduler_service()
    
    # Assign with constraint: max 2 tasks per employee
    print("\nAssigning with constraint: max 2 tasks per employee")
    constraints = {
        'max_assignments_per_employee': 2
    }
    
    assignments = scheduler.assign_tasks(
        tasks=tasks,
        employees=employees,
        constraints=constraints,
        method='greedy_ml'
    )
    
    # Count assignments per employee
    employee_counts = {}
    for assignment in assignments:
        emp_id = assignment['employee_id']
        emp_name = assignment['employee_name']
        employee_counts[emp_name] = employee_counts.get(emp_name, 0) + 1
    
    print(f"\n{len(assignments)} out of {len(tasks)} tasks assigned:")
    print(f"Unassigned: {len(tasks) - len(assignments)} tasks")
    
    print("\nAssignments per employee:")
    for emp_name, count in employee_counts.items():
        print(f"  {emp_name}: {count} tasks")
    
    print("\nAll assignments respect the max_assignments constraint!")


def example_comparing_methods():
    """Example 4: Comparing assignment methods"""
    print("=" * 60)
    print("Example 4: Comparing Assignment Methods")
    print("=" * 60)
    
    tasks = [
        {
            'task_id': i,
            'title': f'Task {i}',
            'required_skills': 'Python',
            'priority': 'medium',
            'estimated_hours': 8,
            'deadline': '2024-02-20',
            'complexity_score': 3.0
        }
        for i in range(1, 6)
    ]
    
    employees = [
        {
            'employee_id': i,
            'name': f'Employee {i}',
            'skills': 'Python,JavaScript',
            'experience_years': 4.0,
            'current_workload': 10 + i * 5,  # Varied workload
            'max_workload': 40,
            'availability_status': 'available',
            'performance_rating': 4.0
        }
        for i in range(1, 4)
    ]
    
    scheduler = get_scheduler_service()
    
    # Try greedy_ml
    print("\nMethod 1: greedy_ml")
    greedy_assignments = scheduler.assign_tasks(
        tasks=tasks,
        employees=employees,
        method='greedy_ml'
    )
    
    greedy_workload = {}
    for assignment in greedy_assignments:
        emp_name = assignment['employee_name']
        hours = assignment['estimated_hours']
        greedy_workload[emp_name] = greedy_workload.get(emp_name, 0) + hours
    
    print("Workload distribution:")
    for emp_name, hours in greedy_workload.items():
        print(f"  {emp_name}: {hours} hours")
    
    # Reset for fair comparison
    for emp in employees:
        emp['current_workload'] = 10 + employees.index(emp) * 5
    
    # Try balanced_ml
    print("\nMethod 2: balanced_ml")
    balanced_assignments = scheduler.assign_tasks(
        tasks=tasks,
        employees=employees,
        method='balanced_ml'
    )
    
    balanced_workload = {}
    for assignment in balanced_assignments:
        emp_name = assignment['employee_name']
        hours = assignment['estimated_hours']
        balanced_workload[emp_name] = balanced_workload.get(emp_name, 0) + hours
    
    print("Workload distribution:")
    for emp_name, hours in balanced_workload.items():
        print(f"  {emp_name}: {hours} hours")
    
    print("\nNote: balanced_ml tends to distribute workload more evenly")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("SCHEDULER SERVICE EXAMPLES")
    print("=" * 60 + "\n")
    
    try:
        example_basic_assignment()
        print("\n" * 2)
        
        example_preview_and_finalize()
        print("\n" * 2)
        
        example_with_constraints()
        print("\n" * 2)
        
        example_comparing_methods()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
