# Time & Resource Allocation System (ML-Driven Project Management)

A comprehensive final-year project implementing an intelligent time and resource allocation system using Machine Learning and AI for automated task assignment and real-time progress monitoring.

## 🎯 Project Overview

This system uses LightGBM for predictive modeling and Google Gemini API for intelligent triage and ETA predictions. It features a Flask backend, PostgreSQL database, and React frontend with real-time updates via WebSocket/SSE.

## 📁 Project Structure

```
time_resource_allocation/
│
├── backend/                    # Flask Backend
│   ├── scripts/               # ML and processing scripts
│   │   ├── skill_matching.py
│   │   ├── feature_builder.py
│   │   ├── train_score_model.py
│   │   ├── score_inference.py
│   │   ├── assign_tasks.py
│   │   ├── realtime_detector.py
│   │   ├── eta_predictor.py
│   │   └── gemini_client.py
│   ├── routes/                # Flask API routes
│   │   ├── api.py
│   │   └── websocket.py
│   ├── models/                # Database models
│   │   └── models.py
│   ├── config/                # Configuration files
│   │   └── config.py
│   └── app.py                 # Main Flask application
│
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── WorkloadHeatmap.jsx
│   │   │   ├── TaskQueue.jsx
│   │   │   ├── TaskDetailModal.jsx
│   │   │   └── ProgressCharts.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.js
│   │   └── index.js
│   ├── public/
│   │   └── index.html
│   └── package.json
│
├── database/                  # Database schemas
│   └── schema.sql
│
├── ml_models/                 # Machine Learning models
│   ├── trained/              # Trained model files
│   └── data/                 # Training data
│
├── logs/                      # Application logs
│
├── docs/                      # Documentation
│
└── requirements.txt           # Python dependencies

```

## 🚀 Features

### Backend (Flask + Python)
- **ML Scripts**: Skill matching, feature building, model training, and inference
- **Task Assignment**: Greedy and Hungarian allocation algorithms
- **Real-time Detection**: Anomaly detection with Gemini API triage
- **ETA Prediction**: ML-based deadline prediction with Gemini assistance
- **REST API**: Comprehensive endpoints for task management
- **WebSocket/SSE**: Real-time updates for live monitoring

### Database (PostgreSQL)
- **Employees**: Store employee information and skills
- **Tasks**: Task details, priorities, and deadlines
- **Candidates**: Employee-task matching candidates
- **Model_Scores**: ML model predictions and scores
- **Task_Assignments**: Current task assignments
- **Progress_Logs**: Task progress tracking
- **Anomaly_Triage**: Detected anomalies and resolutions
- **ETA_Explanations**: AI-generated ETA explanations

### Frontend (React + Chart.js)
- **Dashboard**: Overview of system status and metrics
- **Workload Heatmap**: Visual representation of employee workload
- **Task Queue**: Real-time task queue management
- **Task Detail Modal**: Detailed task information and history
- **Progress Charts**: Visual analytics for task progress and trends

### ML & AI Integration
- **LightGBM Models**: Employee-task scoring, priority classification, ETA prediction
- **Gemini API**: Triage notes, recommended actions, feature augmentation
- **Caching**: Model result caching for performance
- **Modular Design**: Easy to extend and customize

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 14+
- PostgreSQL 12+
- Google Cloud API Key (for Gemini)

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

## 📡 API Endpoints

- `POST /trigger_pipeline` - Trigger the ML pipeline
- `GET /assignments` - Get all task assignments
- `GET /task_queue` - Get current task queue
- `GET /employee/{id}/workload` - Get employee workload
- `GET /models/explain/{task_id}` - Get model explanations
- `WebSocket /ws` - Real-time updates

## 🔧 Configuration

Edit `backend/config/config.py` to configure:
- Database connection
- Gemini API key
- Model parameters
- WebSocket settings

## 📊 ML Models

### Employee-Task Scoring
- Predicts match score between employees and tasks
- Features: skills, experience, workload, past performance

### Priority Classification
- Classifies task priority (High, Medium, Low)
- Features: deadline, dependencies, project importance

### ETA Prediction
- Predicts task completion time
- Uses historical data and Gemini API fallback

## 🤖 Gemini Integration

The system uses Google Gemini API for:
- Generating triage notes for anomalies
- Recommending actions for bottlenecks
- Assisting with ETA predictions
- Feature augmentation for ML models

## 📝 Development Notes

This is a final-year project scaffold designed for development and demonstration purposes. It includes:
- Placeholder functions for ML logic
- Sample data and mock responses
- Modular structure for easy extension
- Comments and documentation throughout

## 🔐 Security Notes

- Update `app.secret_key` in production
- Store API keys in environment variables
- Use `.env` file for sensitive configuration
- Implement proper authentication/authorization

## 📄 License

Academic Project - For Educational Purposes

## 👥 Contributors

Final Year Project Team

## 📞 Support

For questions or issues, please refer to the documentation in the `/docs` folder.
