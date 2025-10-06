-- =====================================================
-- Time & Resource Allocation System - Database Schema
-- PostgreSQL Database Schema
-- =====================================================

-- Drop existing tables if they exist (for development)
DROP TABLE IF EXISTS Model_Training_Rows CASCADE;
DROP TABLE IF EXISTS ETA_Explanations CASCADE;
DROP TABLE IF EXISTS Anomaly_Triage CASCADE;
DROP TABLE IF EXISTS Progress_Logs CASCADE;
DROP TABLE IF EXISTS Task_Assignments CASCADE;
DROP TABLE IF EXISTS Model_Scores CASCADE;
DROP TABLE IF EXISTS Candidates CASCADE;
DROP TABLE IF EXISTS Tasks CASCADE;
DROP TABLE IF EXISTS Employees CASCADE;

-- =====================================================
-- 1. Employees Table
-- =====================================================
CREATE TABLE Employees (
    employee_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(100),
    department VARCHAR(100),
    skills TEXT,  -- JSON or comma-separated list of skills
    skill_embeddings BYTEA,  -- Store embeddings for similarity matching
    experience_years DECIMAL(4,2),
    current_workload INTEGER DEFAULT 0,
    max_workload INTEGER DEFAULT 40,  -- Maximum hours per week
    availability_status VARCHAR(50) DEFAULT 'available',  -- available, busy, on_leave
    performance_rating DECIMAL(3,2) DEFAULT 3.0,  -- 0-5 scale
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups
CREATE INDEX idx_employees_email ON Employees(email);
CREATE INDEX idx_employees_availability ON Employees(availability_status);
CREATE INDEX idx_employees_department ON Employees(department);

-- =====================================================
-- 2. Tasks Table
-- =====================================================
CREATE TABLE Tasks (
    task_id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    required_skills TEXT,  -- JSON or comma-separated list
    skill_embeddings BYTEA,
    priority VARCHAR(20) DEFAULT 'medium',  -- low, medium, high, critical
    estimated_hours DECIMAL(6,2),
    deadline TIMESTAMP,
    project_id INTEGER,
    status VARCHAR(50) DEFAULT 'pending',  -- pending, assigned, in_progress, completed, blocked
    dependencies TEXT,  -- JSON array of task_ids
    complexity_score DECIMAL(3,2),  -- 1-5 scale
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES Employees(employee_id)
);

-- Index for faster lookups
CREATE INDEX idx_tasks_status ON Tasks(status);
CREATE INDEX idx_tasks_priority ON Tasks(priority);
CREATE INDEX idx_tasks_deadline ON Tasks(deadline);
CREATE INDEX idx_tasks_project ON Tasks(project_id);

-- =====================================================
-- 3. Candidates Table
-- =====================================================
CREATE TABLE Candidates (
    candidate_id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES Tasks(task_id) ON DELETE CASCADE,
    employee_id INTEGER REFERENCES Employees(employee_id) ON DELETE CASCADE,
    skill_match_score DECIMAL(5,4),  -- 0-1 scale
    workload_score DECIMAL(5,4),
    experience_score DECIMAL(5,4),
    availability_score DECIMAL(5,4),
    combined_score DECIMAL(5,4),  -- Weighted combination
    ranking INTEGER,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(task_id, employee_id)
);

-- Index for faster lookups
CREATE INDEX idx_candidates_task ON Candidates(task_id);
CREATE INDEX idx_candidates_employee ON Candidates(employee_id);
CREATE INDEX idx_candidates_score ON Candidates(combined_score DESC);

-- =====================================================
-- 4. Model_Scores Table
-- =====================================================
CREATE TABLE Model_Scores (
    score_id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES Tasks(task_id) ON DELETE CASCADE,
    employee_id INTEGER REFERENCES Employees(employee_id) ON DELETE CASCADE,
    model_name VARCHAR(100) NOT NULL,  -- e.g., 'lightgbm_scorer', 'priority_classifier'
    model_version VARCHAR(50),
    predicted_score DECIMAL(5,4),
    predicted_class VARCHAR(50),  -- For classification models
    confidence DECIMAL(5,4),
    feature_importance JSON,  -- Store SHAP values or feature importance
    prediction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(task_id, employee_id, model_name, model_version)
);

-- Index for faster lookups
CREATE INDEX idx_model_scores_task ON Model_Scores(task_id);
CREATE INDEX idx_model_scores_employee ON Model_Scores(employee_id);
CREATE INDEX idx_model_scores_model ON Model_Scores(model_name);

-- =====================================================
-- 5. Task_Assignments Table
-- =====================================================
CREATE TABLE Task_Assignments (
    assignment_id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES Tasks(task_id) ON DELETE CASCADE,
    employee_id INTEGER REFERENCES Employees(employee_id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_completion TIMESTAMP,
    actual_hours DECIMAL(6,2),
    assignment_method VARCHAR(50),  -- 'greedy', 'hungarian', 'manual'
    assignment_score DECIMAL(5,4),
    status VARCHAR(50) DEFAULT 'assigned',  -- assigned, in_progress, completed, cancelled
    notes TEXT,
    UNIQUE(task_id, employee_id)
);

-- Index for faster lookups
CREATE INDEX idx_assignments_task ON Task_Assignments(task_id);
CREATE INDEX idx_assignments_employee ON Task_Assignments(employee_id);
CREATE INDEX idx_assignments_status ON Task_Assignments(status);
CREATE INDEX idx_assignments_assigned_at ON Task_Assignments(assigned_at);

-- =====================================================
-- 6. Progress_Logs Table
-- =====================================================
CREATE TABLE Progress_Logs (
    log_id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES Tasks(task_id) ON DELETE CASCADE,
    employee_id INTEGER REFERENCES Employees(employee_id) ON DELETE CASCADE,
    progress_percentage DECIMAL(5,2),  -- 0-100
    hours_spent DECIMAL(6,2),
    status_update VARCHAR(50),
    blockers TEXT,
    notes TEXT,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups
CREATE INDEX idx_progress_logs_task ON Progress_Logs(task_id);
CREATE INDEX idx_progress_logs_employee ON Progress_Logs(employee_id);
CREATE INDEX idx_progress_logs_time ON Progress_Logs(logged_at);

-- =====================================================
-- 7. Anomaly_Triage Table
-- =====================================================
CREATE TABLE Anomaly_Triage (
    anomaly_id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES Tasks(task_id) ON DELETE CASCADE,
    employee_id INTEGER REFERENCES Employees(employee_id) ON DELETE CASCADE,
    anomaly_type VARCHAR(100) NOT NULL,  -- 'deadline_risk', 'blocked', 'overload', 'quality_issue'
    severity VARCHAR(20) DEFAULT 'medium',  -- low, medium, high, critical
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    gemini_triage_notes TEXT,  -- AI-generated triage analysis
    recommended_actions JSON,  -- AI-generated recommendations
    status VARCHAR(50) DEFAULT 'open',  -- open, investigating, resolved, false_positive
    resolved_at TIMESTAMP,
    resolution_notes TEXT
);

-- Index for faster lookups
CREATE INDEX idx_anomaly_task ON Anomaly_Triage(task_id);
CREATE INDEX idx_anomaly_employee ON Anomaly_Triage(employee_id);
CREATE INDEX idx_anomaly_type ON Anomaly_Triage(anomaly_type);
CREATE INDEX idx_anomaly_status ON Anomaly_Triage(status);
CREATE INDEX idx_anomaly_detected ON Anomaly_Triage(detected_at);

-- =====================================================
-- 8. ETA_Explanations Table
-- =====================================================
CREATE TABLE ETA_Explanations (
    explanation_id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES Tasks(task_id) ON DELETE CASCADE,
    employee_id INTEGER REFERENCES Employees(employee_id),
    predicted_eta TIMESTAMP,
    predicted_hours DECIMAL(6,2),
    confidence_score DECIMAL(5,4),
    model_used VARCHAR(100),  -- 'lightgbm', 'gemini_api', 'hybrid'
    factors JSON,  -- Key factors affecting the ETA
    gemini_explanation TEXT,  -- Natural language explanation from Gemini
    historical_accuracy DECIMAL(5,4),  -- Accuracy of past predictions
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups
CREATE INDEX idx_eta_task ON ETA_Explanations(task_id);
CREATE INDEX idx_eta_employee ON ETA_Explanations(employee_id);
CREATE INDEX idx_eta_generated ON ETA_Explanations(generated_at);

-- =====================================================
-- Sample Data Insertion (For Development/Testing)
-- =====================================================

-- Sample Employees
INSERT INTO Employees (name, email, role, department, skills, experience_years, max_workload, performance_rating) VALUES
('Alice Johnson', 'alice@example.com', 'Senior Developer', 'Engineering', 'Python,React,PostgreSQL,ML', 5.5, 40, 4.5),
('Bob Smith', 'bob@example.com', 'Backend Developer', 'Engineering', 'Python,Flask,PostgreSQL,API', 3.0, 40, 4.0),
('Carol White', 'carol@example.com', 'Frontend Developer', 'Engineering', 'React,JavaScript,CSS,Chart.js', 4.0, 40, 4.2),
('David Brown', 'david@example.com', 'ML Engineer', 'Data Science', 'Python,TensorFlow,LightGBM,ML', 6.0, 40, 4.7),
('Eve Davis', 'eve@example.com', 'Full Stack Developer', 'Engineering', 'Python,React,PostgreSQL,Docker', 4.5, 40, 4.3);

-- Sample Tasks
INSERT INTO Tasks (title, description, required_skills, priority, estimated_hours, deadline, status, complexity_score) VALUES
('Implement User Authentication', 'Build JWT-based authentication system', 'Python,Flask,PostgreSQL', 'high', 16.0, NOW() + INTERVAL '7 days', 'pending', 3.5),
('Create Dashboard UI', 'Design and implement React dashboard with Chart.js', 'React,JavaScript,Chart.js', 'high', 20.0, NOW() + INTERVAL '10 days', 'pending', 3.0),
('Train ML Model', 'Train and validate LightGBM scoring model', 'Python,LightGBM,ML', 'critical', 24.0, NOW() + INTERVAL '5 days', 'pending', 4.5),
('API Documentation', 'Write comprehensive API documentation', 'API,Documentation', 'medium', 8.0, NOW() + INTERVAL '14 days', 'pending', 2.0),
('Setup CI/CD Pipeline', 'Configure automated testing and deployment', 'Docker,CI/CD,DevOps', 'medium', 12.0, NOW() + INTERVAL '12 days', 'pending', 3.0);

-- =====================================================
-- Triggers for Automatic Updates
-- =====================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to tables
CREATE TRIGGER update_employees_updated_at BEFORE UPDATE ON Employees
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON Tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- Views for Common Queries
-- =====================================================

-- View: Active assignments with employee and task details
CREATE VIEW active_assignments_view AS
SELECT 
    ta.assignment_id,
    ta.task_id,
    t.title AS task_title,
    t.priority,
    t.deadline,
    ta.employee_id,
    e.name AS employee_name,
    e.department,
    ta.status,
    ta.assigned_at,
    ta.estimated_completion,
    COALESCE(pl.progress_percentage, 0) AS progress_percentage
FROM Task_Assignments ta
JOIN Tasks t ON ta.task_id = t.task_id
JOIN Employees e ON ta.employee_id = e.employee_id
LEFT JOIN LATERAL (
    SELECT progress_percentage 
    FROM Progress_Logs 
    WHERE task_id = ta.task_id AND employee_id = ta.employee_id 
    ORDER BY logged_at DESC 
    LIMIT 1
) pl ON true
WHERE ta.status IN ('assigned', 'in_progress');

-- View: Employee workload summary
CREATE VIEW employee_workload_view AS
SELECT 
    e.employee_id,
    e.name,
    e.department,
    e.current_workload,
    e.max_workload,
    COUNT(ta.assignment_id) AS active_tasks,
    SUM(t.estimated_hours) AS total_estimated_hours,
    ROUND((e.current_workload::DECIMAL / e.max_workload) * 100, 2) AS workload_percentage
FROM Employees e
LEFT JOIN Task_Assignments ta ON e.employee_id = ta.employee_id AND ta.status IN ('assigned', 'in_progress')
LEFT JOIN Tasks t ON ta.task_id = t.task_id
GROUP BY e.employee_id, e.name, e.department, e.current_workload, e.max_workload;

-- View: Open anomalies requiring attention
CREATE VIEW open_anomalies_view AS
SELECT 
    an.anomaly_id,
    an.task_id,
    t.title AS task_title,
    an.employee_id,
    e.name AS employee_name,
    an.anomaly_type,
    an.severity,
    an.detected_at,
    an.gemini_triage_notes,
    an.recommended_actions
FROM Anomaly_Triage an
JOIN Tasks t ON an.task_id = t.task_id
LEFT JOIN Employees e ON an.employee_id = e.employee_id
WHERE an.status = 'open'
ORDER BY an.severity DESC, an.detected_at DESC;

-- =====================================================
-- 8. Model Training Rows Table
-- =====================================================
-- Stores historical assignment data for ML model training
CREATE TABLE Model_Training_Rows (
    training_row_id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES Employees(employee_id) ON DELETE CASCADE,
    task_id INTEGER REFERENCES Tasks(task_id) ON DELETE CASCADE,
    assignment_id INTEGER REFERENCES Task_Assignments(assignment_id) ON DELETE SET NULL,
    
    -- Employee features (snapshot at assignment time)
    emp_experience_years DECIMAL(4,2),
    emp_workload_ratio DECIMAL(5,4),  -- current_workload / max_workload
    emp_performance_rating DECIMAL(3,2),
    emp_active_tasks INTEGER,
    emp_availability VARCHAR(50),
    
    -- Task features
    task_priority VARCHAR(20),
    task_complexity_score DECIMAL(3,2),
    task_estimated_hours DECIMAL(6,2),
    task_urgency_score DECIMAL(5,4),  -- Calculated urgency based on deadline
    
    -- Interaction features
    skill_match_score DECIMAL(5,4),  -- 0-1 scale
    workload_compatibility DECIMAL(5,4),  -- 0-1 scale
    
    -- Labels/outcomes (filled when assignment completes)
    success_score DECIMAL(5,4),  -- Overall success score (0-1)
    completed_on_time BOOLEAN,
    actual_hours DECIMAL(6,2),
    quality_rating DECIMAL(3,2),  -- 0-5 scale (from feedback/review)
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(assignment_id)  -- One training row per assignment
);

-- Indexes for faster queries
CREATE INDEX idx_training_employee ON Model_Training_Rows(employee_id);
CREATE INDEX idx_training_task ON Model_Training_Rows(task_id);
CREATE INDEX idx_training_assignment ON Model_Training_Rows(assignment_id);
CREATE INDEX idx_training_created ON Model_Training_Rows(created_at);

-- =====================================================
-- END OF SCHEMA
-- =====================================================
