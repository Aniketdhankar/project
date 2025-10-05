/**
 * Progress Charts Component
 * Displays various analytics charts for task progress and trends
 */

import React, { useState, useEffect } from 'react';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { getDashboardAnalytics } from '../services/api';
import './ProgressCharts.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const ProgressCharts = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const data = await getDashboardAnalytics();
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !analytics) {
    return <div className="loading">Loading charts...</div>;
  }

  // Task Status Distribution (Doughnut Chart)
  const statusData = {
    labels: ['Completed', 'In Progress', 'Pending'],
    datasets: [
      {
        data: [
          analytics.completed_tasks,
          analytics.in_progress_tasks,
          analytics.pending_tasks,
        ],
        backgroundColor: [
          'rgba(76, 175, 80, 0.8)',
          'rgba(33, 150, 243, 0.8)',
          'rgba(255, 152, 0, 0.8)',
        ],
        borderColor: [
          'rgba(76, 175, 80, 1)',
          'rgba(33, 150, 243, 1)',
          'rgba(255, 152, 0, 1)',
        ],
        borderWidth: 2,
      },
    ],
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
      },
      title: {
        display: true,
        text: 'Task Status Distribution',
      },
    },
  };

  // Mock trend data (in a real app, this would come from the API)
  const trendData = {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    datasets: [
      {
        label: 'Tasks Completed',
        data: [8, 12, 15, analytics.completed_tasks || 12],
        borderColor: 'rgba(76, 175, 80, 1)',
        backgroundColor: 'rgba(76, 175, 80, 0.2)',
        tension: 0.4,
      },
      {
        label: 'Tasks Created',
        data: [10, 15, 18, analytics.total_tasks || 25],
        borderColor: 'rgba(33, 150, 243, 1)',
        backgroundColor: 'rgba(33, 150, 243, 0.2)',
        tension: 0.4,
      },
    ],
  };

  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Task Trends Over Time',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <div className="progress-charts">
      <div className="charts-grid">
        <div className="chart-card">
          <Doughnut data={statusData} options={doughnutOptions} />
        </div>
        <div className="chart-card chart-wide">
          <Line data={trendData} options={lineOptions} />
        </div>
      </div>

      <div className="stats-summary">
        <div className="stat-item">
          <div className="stat-label">Completion Rate</div>
          <div className="stat-value">
            {((analytics.completed_tasks / analytics.total_tasks) * 100).toFixed(1)}%
          </div>
        </div>
        <div className="stat-item">
          <div className="stat-label">Avg Utilization</div>
          <div className="stat-value">{analytics.avg_utilization}%</div>
        </div>
        <div className="stat-item">
          <div className="stat-label">Recent Assignments</div>
          <div className="stat-value">{analytics.recent_assignments}</div>
        </div>
        <div className="stat-item">
          <div className="stat-label">Open Anomalies</div>
          <div className="stat-value" style={{ color: analytics.open_anomalies > 0 ? '#F44336' : '#4CAF50' }}>
            {analytics.open_anomalies}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressCharts;
