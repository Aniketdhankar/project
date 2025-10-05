# Project Structure Documentation

This document provides a detailed breakdown of the Time & Resource Allocation System project structure.

## 📁 Complete Folder Structure

```
time_resource_allocation/
│
├── README.md                       # Main project documentation
├── STRUCTURE.md                    # This file - detailed structure guide
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore patterns
│
├── backend/                        # Flask Backend Application
│   ├── app.py                     # Main Flask application entry point
│   │
│   ├── config/                    # Configuration files
│   │   └── config.py             # App configuration (DB, API keys, etc.)
│   │
│   ├── models/                    # Database models
│   │   └── models.py             # SQLAlchemy models
│   │
│   ├── routes/                    # API route handlers
│   │   ├── api.py                # REST API endpoints
│   │   └── websocket.py          # WebSocket/SSE endpoints
│   │
│   └── scripts/                   # ML and processing scripts
│       ├── gemini_client.py      # Gemini API wrapper
│       ├── skill_matching.py     # Skill parsing & matching
│       ├── feature_builder.py    # ML feature engineering
│       ├── train_score_model.py  # Model training
│       ├── score_inference.py    # Inference & scoring
│       ├── assign_tasks.py       # Task assignment algorithms
│       ├── realtime_detector.py  # Anomaly detection
│       └── eta_predictor.py      # ETA prediction
│
├── frontend/                       # React Frontend Application
│   ├── package.json               # npm dependencies
│   │
│   ├── public/                    # Static files
│   │   └── index.html            # HTML template
│   │
│   └── src/                       # React source code
│       ├── index.js              # React entry point
│       ├── App.js                # Main App component
│       ├── App.css               # App styles
│       │
│       ├── components/            # React components
│       │   ├── Dashboard.jsx     # Main dashboard
│       │   ├── Dashboard.css
│       │   ├── WorkloadHeatmap.jsx    # Workload visualization
│       │   ├── WorkloadHeatmap.css
│       │   ├── TaskQueue.jsx     # Task queue display
│       │   ├── TaskQueue.css
│       │   ├── TaskDetailModal.jsx    # Task details modal
│       │   ├── TaskDetailModal.css
│       │   ├── ProgressCharts.jsx     # Analytics charts
│       │   └── ProgressCharts.css
│       │
│       └── services/              # API services
│           └── api.js            # API client & SSE connections
│
├── database/                       # Database schemas
│   └── schema.sql                # PostgreSQL schema with sample data
│
├── ml_models/                      # Machine Learning models
│   ├── trained/                  # Saved trained models
│   │   └── .gitkeep
│   └── data/                     # Training data
│       └── .gitkeep
│
├── logs/                          # Application logs
│   └── .gitkeep
│
└── docs/                          # Additional documentation
    └── .gitkeep
```

## 🔧 Backend Components

### Core Application (app.py)
- Flask application factory
- Blueprint registration
- Error handlers
- CORS configuration

### Configuration (config/config.py)
- Environment-based configuration
- Database connection settings
- API key management
- Feature flags

### Models (models/models.py)
- **Employee**: Employee information and skills
- **Task**: Task details and requirements
- **TaskAssignment**: Assignment records
- **ProgressLog**: Progress tracking
- **AnomalyTriage**: Detected anomalies

### API Routes (routes/api.py)
- `POST /trigger_pipeline` - Trigger ML pipeline
- `GET /assignments` - List assignments
- `GET /task_queue` - Get pending tasks
- `GET /employee/{id}/workload` - Employee workload
- `GET /models/explain/{task_id}` - Model explanations
- `GET /analytics/*` - Various analytics endpoints
- `GET /anomalies` - List anomalies

### WebSocket/SSE (routes/websocket.py)
- `/stream/updates` - Global update stream
- `/stream/task/{id}` - Task-specific updates
- `/stream/employee/{id}` - Employee-specific updates

### ML Scripts

#### gemini_client.py
- Gemini API wrapper with caching
- Retry logic and error handling
- Triage note generation
- ETA prediction assistance
- Feature augmentation

#### skill_matching.py
- Skill parsing and normalization
- TF-IDF vectorization
- Similarity calculation
- Candidate matching

#### feature_builder.py
- Employee feature extraction
- Task feature extraction
- Interaction feature calculation
- Training dataset creation

#### train_score_model.py
- LightGBM model training
- Cross-validation
- Model persistence
- Training metrics

#### score_inference.py
- Model loading
- Batch scoring
- Confidence estimation
- Priority prediction

#### assign_tasks.py
- Greedy assignment algorithm
- Hungarian algorithm (optimal)
- Balanced assignment
- Workload consideration

#### realtime_detector.py
- Deadline risk detection
- Progress delay detection
- Workload overload detection
- Stagnation detection
- Gemini-powered triage

#### eta_predictor.py
- ML-based ETA prediction
- Gemini fallback
- Progress-adjusted updates
- Confidence scoring

## ⚛️ Frontend Components

### Dashboard.jsx
- Main dashboard view
- Metrics overview cards
- Live updates stream
- Component composition

### WorkloadHeatmap.jsx
- Bar chart visualization
- Color-coded utilization
- Interactive tooltips
- Chart.js integration

### TaskQueue.jsx
- Task listing
- Priority filtering
- Task selection
- Real-time updates

### TaskDetailModal.jsx
- Detailed task information
- Candidate recommendations
- ML model explanation
- Feature importance display

### ProgressCharts.jsx
- Doughnut chart (status distribution)
- Line chart (trends)
- Statistics summary
- Multiple chart types

### API Service (services/api.js)
- Axios HTTP client
- Request/response interceptors
- SSE connection management
- API endpoint wrappers

## 🗄️ Database Schema

### Tables
1. **Employees** - Employee profiles and skills
2. **Tasks** - Task definitions and requirements
3. **Candidates** - Scored employee-task matches
4. **Model_Scores** - ML model predictions
5. **Task_Assignments** - Active assignments
6. **Progress_Logs** - Progress updates
7. **Anomaly_Triage** - Detected anomalies
8. **ETA_Explanations** - ETA predictions

### Views
- `active_assignments_view` - Active assignments with details
- `employee_workload_view` - Workload summary
- `open_anomalies_view` - Open anomalies

## 🚀 Deployment & Setup

### Backend Setup
```bash
cd backend
pip install -r ../requirements.txt
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Database Setup
```bash
psql -U postgres -f database/schema.sql
```

## 🔑 Key Features

### ML Pipeline
1. Skill matching and embedding generation
2. Feature engineering for employee-task pairs
3. LightGBM model training and inference
4. Multiple assignment algorithms
5. Real-time anomaly detection
6. ETA prediction with Gemini fallback

### Frontend Features
1. Real-time dashboard updates via SSE
2. Interactive Chart.js visualizations
3. Workload heatmap with color coding
4. Task queue with filtering
5. Detailed task modals with ML explanations
6. Progress tracking and analytics

### API Features
1. RESTful endpoints
2. WebSocket/SSE for real-time updates
3. Comprehensive error handling
4. CORS support
5. Pagination
6. Filtering and search

## 📝 Notes

- All ML scripts include placeholder implementations
- Database operations use SQLAlchemy ORM
- Frontend uses React hooks and functional components
- Charts use Chart.js via react-chartjs-2
- Real-time updates via Server-Sent Events (SSE)
- Modular design for easy extension

## 🔄 Data Flow

1. **Task Creation** → Stored in database
2. **Pipeline Trigger** → ML scoring begins
3. **Skill Matching** → Generate embeddings and similarity scores
4. **Feature Building** → Extract features for ML models
5. **Model Inference** → Score all employee-task pairs
6. **Task Assignment** → Apply assignment algorithm
7. **Progress Tracking** → Log updates and check for anomalies
8. **Anomaly Detection** → Identify issues, generate triage
9. **ETA Updates** → Adjust estimates based on progress
10. **Real-time Streaming** → Push updates to frontend via SSE
