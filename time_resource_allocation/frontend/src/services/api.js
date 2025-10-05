/**
 * API Service
 * Handles all HTTP requests to the Flask backend
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// =====================================
// Pipeline API
// =====================================

export const triggerPipeline = (method = 'balanced', includeGemini = false) => {
  return api.post('/trigger_pipeline', {
    method,
    include_gemini: includeGemini,
  });
};

// =====================================
// Assignments API
// =====================================

export const getAssignments = (params = {}) => {
  return api.get('/assignments', { params });
};

export const getAssignment = (assignmentId) => {
  return api.get(`/assignments/${assignmentId}`);
};

// =====================================
// Tasks API
// =====================================

export const getTaskQueue = (params = {}) => {
  return api.get('/task_queue', { params });
};

// =====================================
// Employee API
// =====================================

export const getEmployeeWorkload = (employeeId) => {
  return api.get(`/employee/${employeeId}/workload`);
};

// =====================================
// Model Explanations API
// =====================================

export const getModelExplanation = (taskId, employeeId = null) => {
  const params = employeeId ? { employee_id: employeeId } : {};
  return api.get(`/models/explain/${taskId}`, { params });
};

// =====================================
// Analytics API
// =====================================

export const getDashboardAnalytics = () => {
  return api.get('/analytics/dashboard');
};

export const getWorkloadDistribution = () => {
  return api.get('/analytics/workload_distribution');
};

// =====================================
// Anomalies API
// =====================================

export const getAnomalies = (status = 'open') => {
  return api.get('/anomalies', { params: { status } });
};

// =====================================
// SSE (Server-Sent Events) Connections
// =====================================

export const connectToUpdatesStream = (onMessage, onError) => {
  const eventSource = new EventSource(`${API_BASE_URL}/stream/updates`);

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('Error parsing SSE message:', error);
    }
  };

  eventSource.onerror = (error) => {
    console.error('SSE Error:', error);
    if (onError) onError(error);
  };

  return eventSource;
};

export const connectToTaskStream = (taskId, onMessage, onError) => {
  const eventSource = new EventSource(`${API_BASE_URL}/stream/task/${taskId}`);

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('Error parsing SSE message:', error);
    }
  };

  eventSource.onerror = (error) => {
    console.error('SSE Error:', error);
    if (onError) onError(error);
  };

  return eventSource;
};

export const connectToEmployeeStream = (employeeId, onMessage, onError) => {
  const eventSource = new EventSource(`${API_BASE_URL}/stream/employee/${employeeId}`);

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('Error parsing SSE message:', error);
    }
  };

  eventSource.onerror = (error) => {
    console.error('SSE Error:', error);
    if (onError) onError(error);
  };

  return eventSource;
};

export default api;
