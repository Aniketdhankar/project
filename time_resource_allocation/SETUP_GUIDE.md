# Setup Guide - Time & Resource Allocation System

Complete step-by-step guide to set up and run the Time & Resource Allocation System for your Final Year Project.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** (with pip)
- **Node.js 14+** (with npm)
- **PostgreSQL 12+**
- **Git**

## 🚀 Quick Start

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd project/time_resource_allocation
```

### Step 2: Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual values
nano .env  # or use your preferred editor
```

**Important variables to configure:**
- `SECRET_KEY`: Generate a strong random key
- `DATABASE_URL`: Your PostgreSQL connection string
- `GEMINI_API_KEY`: Your Google Gemini API key (optional for MVP)

### Step 3: Set Up the Database

```bash
# Create the database
createdb time_resource_allocation

# Run the schema script
psql -U postgres -d time_resource_allocation -f database/schema.sql
```

**Verify the setup:**
```bash
psql -U postgres -d time_resource_allocation -c "\dt"
```

You should see 8 tables listed.

### Step 4: Set Up the Backend

```bash
# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the Flask app
cd backend
python app.py
```

The backend should now be running on `http://localhost:5000`

**Test the backend:**
```bash
curl http://localhost:5000/
# Should return: {"name": "Time & Resource Allocation System API", ...}
```

### Step 5: Set Up the Frontend

Open a new terminal window:

```bash
cd time_resource_allocation/frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend should automatically open in your browser at `http://localhost:3000`

## 🔧 Detailed Configuration

### Database Configuration

**Option 1: Local PostgreSQL**
```
DATABASE_URL=postgresql://username:password@localhost:5432/time_resource_allocation
```

**Option 2: Remote PostgreSQL (e.g., Heroku)**
```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### Gemini API Setup (Optional)

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Generate an API key
3. Add to `.env`:
```
GEMINI_API_KEY=your_api_key_here
```

**Note:** The system works without Gemini by using fallback ML models.

### CORS Configuration

If running frontend and backend on different ports:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5000
```

## 🧪 Testing the System

### 1. Test Backend API

```bash
# Health check
curl http://localhost:5000/api/health

# Get dashboard analytics
curl http://localhost:5000/api/analytics/dashboard

# Get task queue
curl http://localhost:5000/api/task_queue

# Get assignments
curl http://localhost:5000/api/assignments
```

### 2. Test Frontend

1. Open `http://localhost:3000` in your browser
2. You should see the dashboard with:
   - Metrics cards at the top
   - Workload heatmap
   - Task queue
   - Progress charts
   - Live updates section

### 3. Test ML Pipeline

```bash
# Trigger the ML pipeline
curl -X POST http://localhost:5000/api/trigger_pipeline \
  -H "Content-Type: application/json" \
  -d '{"method": "balanced", "include_gemini": false}'
```

## 🔬 Running ML Scripts Independently

### Train Models

```bash
cd backend/scripts
python train_score_model.py
```

This will:
- Create sample training data
- Train LightGBM models
- Save models to `ml_models/trained/`

### Test Skill Matching

```python
from skill_matching import get_skill_matcher, initialize_skill_matcher

# Initialize
initialize_skill_matcher(None)  # Pass DB connection in production

# Get matcher
matcher = get_skill_matcher()

# Test similarity
score = matcher.calculate_similarity(
    "Python, React, PostgreSQL",
    "Python, Flask, PostgreSQL"
)
print(f"Similarity: {score}")
```

### Test Assignment Algorithms

```python
from assign_tasks import get_task_assigner

assigner = get_task_assigner()

# Sample data
tasks = [{"task_id": 1, "title": "Test", "priority": "high", ...}]
employees = [{"employee_id": 1, "name": "Alice", ...}]

# Run assignment
assignments = assigner.greedy_assignment(tasks, employees)
print(assignments)
```

## 📊 Working with the Database

### View Sample Data

```sql
-- List all employees
SELECT * FROM Employees;

-- List all tasks
SELECT * FROM Tasks;

-- View active assignments
SELECT * FROM active_assignments_view;

-- View employee workload
SELECT * FROM employee_workload_view;
```

### Add Test Data

```sql
-- Add a new employee
INSERT INTO Employees (name, email, role, department, skills, experience_years)
VALUES ('John Doe', 'john@example.com', 'Developer', 'Engineering', 
        'Python,Flask,API', 4.0);

-- Add a new task
INSERT INTO Tasks (title, description, required_skills, priority, 
                   estimated_hours, deadline, status)
VALUES ('Build API Endpoint', 'Create REST API for user management',
        'Python,Flask,PostgreSQL', 'high', 12.0, 
        NOW() + INTERVAL '7 days', 'pending');
```

## 🐛 Troubleshooting

### Backend Issues

**Problem: "ModuleNotFoundError: No module named 'flask'"**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Unix/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Problem: "psycopg2 installation error"**
```bash
# Install PostgreSQL development files
# Ubuntu/Debian:
sudo apt-get install libpq-dev python3-dev

# Then reinstall
pip install psycopg2-binary
```

**Problem: "Database connection failed"**
- Check PostgreSQL is running: `pg_isready`
- Verify DATABASE_URL in .env
- Check PostgreSQL logs for errors

### Frontend Issues

**Problem: "npm install" fails**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Problem: "React app won't start"**
```bash
# Check port 3000 is available
lsof -i :3000  # Unix/Mac
netstat -ano | findstr :3000  # Windows

# Try a different port
PORT=3001 npm start
```

**Problem: "API calls fail (CORS errors)"**
- Verify CORS_ORIGINS in backend .env
- Check REACT_APP_API_URL in frontend

### Database Issues

**Problem: "Database does not exist"**
```bash
# Create the database
createdb time_resource_allocation

# Or using psql
psql -U postgres -c "CREATE DATABASE time_resource_allocation;"
```

**Problem: "Permission denied for schema public"**
```sql
-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE time_resource_allocation TO your_user;
```

## 🎓 Development Workflow

### Making Changes

1. **Backend changes:**
   - Edit Python files in `backend/`
   - Flask auto-reloads in development mode
   - No restart needed

2. **Frontend changes:**
   - Edit React files in `frontend/src/`
   - React automatically reloads
   - See changes immediately

3. **Database changes:**
   - Edit `database/schema.sql`
   - Re-run schema script
   - Or use migrations (SQLAlchemy-Alembic)

### Adding New Features

**New API Endpoint:**
1. Add route to `backend/routes/api.py`
2. Implement logic
3. Test with curl or Postman
4. Add to API service in `frontend/src/services/api.js`
5. Use in React components

**New ML Model:**
1. Add training script to `backend/scripts/`
2. Train model
3. Add inference function to `score_inference.py`
4. Integrate into pipeline

**New React Component:**
1. Create component in `frontend/src/components/`
2. Add CSS file
3. Import and use in parent components

## 📚 Additional Resources

- **Flask Documentation:** https://flask.palletsprojects.com/
- **React Documentation:** https://react.dev/
- **Chart.js Documentation:** https://www.chartjs.org/
- **LightGBM Documentation:** https://lightgbm.readthedocs.io/
- **PostgreSQL Documentation:** https://www.postgresql.org/docs/

## 🤝 Getting Help

For issues specific to this project:
1. Check the STRUCTURE.md for architecture details
2. Review the README.md for feature information
3. Look at code comments for implementation details
4. Check logs in `logs/` directory

## ✅ Verification Checklist

Before considering setup complete:

- [ ] PostgreSQL is running and database is created
- [ ] Backend starts without errors on port 5000
- [ ] Frontend starts without errors on port 3000
- [ ] Can access dashboard at http://localhost:3000
- [ ] API health check returns success
- [ ] Sample data is visible in the database
- [ ] Charts are rendering correctly
- [ ] No console errors in browser
- [ ] No errors in backend logs

## 🎯 Next Steps

Once setup is complete:

1. **Familiarize with the codebase:**
   - Read through main components
   - Understand data flow
   - Review ML pipeline

2. **Customize for your project:**
   - Modify database schema if needed
   - Add your own features
   - Customize UI/styling

3. **Develop your features:**
   - Add real ML models
   - Integrate actual APIs
   - Implement authentication

4. **Prepare for demo:**
   - Add more sample data
   - Test all features
   - Prepare presentation materials

Good luck with your Final Year Project! 🚀
