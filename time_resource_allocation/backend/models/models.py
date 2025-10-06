"""
Database Models
SQLAlchemy models for the application
"""

from datetime import datetime
from extensions import db


class Employee(db.Model):
    """Employee model"""
    __tablename__ = 'employees'
    
    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    role = db.Column(db.String(100))
    department = db.Column(db.String(100))
    skills = db.Column(db.Text)
    skill_embeddings = db.Column(db.LargeBinary)
    experience_years = db.Column(db.Numeric(4, 2))
    current_workload = db.Column(db.Integer, default=0)
    max_workload = db.Column(db.Integer, default=40)
    availability_status = db.Column(db.String(50), default='available')
    performance_rating = db.Column(db.Numeric(3, 2), default=3.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignments = db.relationship('TaskAssignment', back_populates='employee')
    progress_logs = db.relationship('ProgressLog', back_populates='employee')
    
    def to_dict(self):
        return {
            'employee_id': self.employee_id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'department': self.department,
            'skills': self.skills,
            'experience_years': float(self.experience_years) if self.experience_years else None,
            'current_workload': self.current_workload,
            'max_workload': self.max_workload,
            'availability_status': self.availability_status,
            'performance_rating': float(self.performance_rating) if self.performance_rating else None
        }


class Task(db.Model):
    """Task model"""
    __tablename__ = 'tasks'
    
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    required_skills = db.Column(db.Text)
    skill_embeddings = db.Column(db.LargeBinary)
    priority = db.Column(db.String(20), default='medium')
    estimated_hours = db.Column(db.Numeric(6, 2))
    deadline = db.Column(db.DateTime)
    project_id = db.Column(db.Integer)
    status = db.Column(db.String(50), default='pending')
    dependencies = db.Column(db.Text)
    complexity_score = db.Column(db.Numeric(3, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    
    # Relationships
    assignments = db.relationship('TaskAssignment', back_populates='task')
    progress_logs = db.relationship('ProgressLog', back_populates='task')
    
    def to_dict(self):
        return {
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description,
            'required_skills': self.required_skills,
            'priority': self.priority,
            'estimated_hours': float(self.estimated_hours) if self.estimated_hours else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'project_id': self.project_id,
            'status': self.status,
            'dependencies': self.dependencies,
            'complexity_score': float(self.complexity_score) if self.complexity_score else None
        }


class TaskAssignment(db.Model):
    """Task Assignment model"""
    __tablename__ = 'task_assignments'
    
    assignment_id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    estimated_completion = db.Column(db.DateTime)
    actual_hours = db.Column(db.Numeric(6, 2))
    assignment_method = db.Column(db.String(50))
    assignment_score = db.Column(db.Numeric(5, 4))
    status = db.Column(db.String(50), default='assigned')
    notes = db.Column(db.Text)
    
    # Relationships
    task = db.relationship('Task', back_populates='assignments')
    employee = db.relationship('Employee', back_populates='assignments')
    
    def to_dict(self):
        return {
            'assignment_id': self.assignment_id,
            'task_id': self.task_id,
            'employee_id': self.employee_id,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'estimated_completion': self.estimated_completion.isoformat() if self.estimated_completion else None,
            'actual_hours': float(self.actual_hours) if self.actual_hours else None,
            'assignment_method': self.assignment_method,
            'assignment_score': float(self.assignment_score) if self.assignment_score else None,
            'status': self.status,
            'notes': self.notes
        }


class ProgressLog(db.Model):
    """Progress Log model"""
    __tablename__ = 'progress_logs'
    
    log_id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    progress_percentage = db.Column(db.Numeric(5, 2))
    hours_spent = db.Column(db.Numeric(6, 2))
    status_update = db.Column(db.String(50))
    blockers = db.Column(db.Text)
    notes = db.Column(db.Text)
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    task = db.relationship('Task', back_populates='progress_logs')
    employee = db.relationship('Employee', back_populates='progress_logs')
    
    def to_dict(self):
        return {
            'log_id': self.log_id,
            'task_id': self.task_id,
            'employee_id': self.employee_id,
            'progress_percentage': float(self.progress_percentage) if self.progress_percentage else None,
            'hours_spent': float(self.hours_spent) if self.hours_spent else None,
            'status_update': self.status_update,
            'blockers': self.blockers,
            'notes': self.notes,
            'logged_at': self.logged_at.isoformat() if self.logged_at else None
        }


class AnomalyTriage(db.Model):
    """Anomaly Triage model"""
    __tablename__ = 'anomaly_triage'
    
    anomaly_id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'))
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    anomaly_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20), default='medium')
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    gemini_triage_notes = db.Column(db.Text)
    recommended_actions = db.Column(db.JSON)
    status = db.Column(db.String(50), default='open')
    resolved_at = db.Column(db.DateTime)
    resolution_notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'anomaly_id': self.anomaly_id,
            'task_id': self.task_id,
            'employee_id': self.employee_id,
            'anomaly_type': self.anomaly_type,
            'severity': self.severity,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'description': self.description,
            'gemini_triage_notes': self.gemini_triage_notes,
            'recommended_actions': self.recommended_actions,
            'status': self.status,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolution_notes': self.resolution_notes
        }


class User(db.Model):
    """User model for authentication and role management (Employee/Manager)"""
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='employee')  # 'employee' or 'manager'
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationship
    employee = db.relationship('Employee', backref='user', uselist=False)
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'employee_id': self.employee_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class Skill(db.Model):
    """Skill model for tracking available skills"""
    __tablename__ = 'skills'
    
    skill_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    employee_skills = db.relationship('EmployeeSkill', back_populates='skill', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'skill_id': self.skill_id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class EmployeeSkill(db.Model):
    """EmployeeSkill model for many-to-many relationship between employees and skills"""
    __tablename__ = 'employee_skills'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.skill_id'), nullable=False)
    proficiency_level = db.Column(db.String(50), default='beginner')  # beginner, intermediate, advanced, expert
    years_of_experience = db.Column(db.Numeric(4, 2))
    last_used = db.Column(db.DateTime)
    certified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = db.relationship('Employee', backref='employee_skills')
    skill = db.relationship('Skill', back_populates='employee_skills')
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'skill_id': self.skill_id,
            'proficiency_level': self.proficiency_level,
            'years_of_experience': float(self.years_of_experience) if self.years_of_experience else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'certified': self.certified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Project(db.Model):
    """Project model for organizing tasks"""
    __tablename__ = 'projects'
    
    project_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    client = db.Column(db.String(255))
    status = db.Column(db.String(50), default='active')  # active, completed, on_hold, cancelled
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    budget = db.Column(db.Numeric(12, 2))
    priority = db.Column(db.String(20), default='medium')
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = db.relationship('Task', backref='project', foreign_keys='Task.project_id')
    manager = db.relationship('Employee', foreign_keys=[manager_id])
    
    def to_dict(self):
        return {
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'client': self.client,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'budget': float(self.budget) if self.budget else None,
            'priority': self.priority,
            'manager_id': self.manager_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Timesheet(db.Model):
    """Timesheet model for tracking work hours"""
    __tablename__ = 'timesheets'
    
    timesheet_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    hours_worked = db.Column(db.Numeric(5, 2), nullable=False)
    description = db.Column(db.Text)
    is_billable = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(50), default='submitted')  # draft, submitted, approved, rejected
    submitted_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = db.relationship('Employee', foreign_keys=[employee_id], backref='timesheets')
    task = db.relationship('Task', backref='timesheets')
    approver = db.relationship('Employee', foreign_keys=[approved_by])
    
    def to_dict(self):
        return {
            'timesheet_id': self.timesheet_id,
            'employee_id': self.employee_id,
            'task_id': self.task_id,
            'date': self.date.isoformat() if self.date else None,
            'hours_worked': float(self.hours_worked) if self.hours_worked else None,
            'description': self.description,
            'is_billable': self.is_billable,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'approved_by': self.approved_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ModelTrainingRow(db.Model):
    """ModelTrainingRow model for storing ML training data"""
    __tablename__ = 'model_training_rows'
    
    row_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('task_assignments.assignment_id'))
    features = db.Column(db.JSON, nullable=False)  # Stores feature dictionary
    label = db.Column(db.Numeric(5, 4))  # Success score or performance metric
    outcome = db.Column(db.String(50))  # success, failure, pending
    actual_hours = db.Column(db.Numeric(6, 2))
    completion_rate = db.Column(db.Numeric(5, 2))
    quality_score = db.Column(db.Numeric(3, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_for_training = db.Column(db.Boolean, default=False)
    training_date = db.Column(db.DateTime)
    
    # Relationships
    employee = db.relationship('Employee', backref='training_rows')
    task = db.relationship('Task', backref='training_rows')
    assignment = db.relationship('TaskAssignment', backref='training_rows')
    
    def to_dict(self):
        return {
            'row_id': self.row_id,
            'employee_id': self.employee_id,
            'task_id': self.task_id,
            'assignment_id': self.assignment_id,
            'features': self.features,
            'label': float(self.label) if self.label else None,
            'outcome': self.outcome,
            'actual_hours': float(self.actual_hours) if self.actual_hours else None,
            'completion_rate': float(self.completion_rate) if self.completion_rate else None,
            'quality_score': float(self.quality_score) if self.quality_score else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'used_for_training': self.used_for_training,
            'training_date': self.training_date.isoformat() if self.training_date else None
        }
