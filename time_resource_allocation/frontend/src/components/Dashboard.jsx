/**
 * Dashboard Component
 * Main dashboard showing system overview and key metrics
 */

import React, { useState, useEffect } from 'react';
import { getDashboardAnalytics, connectToUpdatesStream } from '../services/api';
import WorkloadHeatmap from './WorkloadHeatmap';
import TaskQueue from './TaskQueue';
import ProgressCharts from './ProgressCharts';
import './Dashboard.css';

const Dashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [liveUpdates, setLiveUpdates] = useState([]);

  useEffect(() => {
    fetchAnalytics();

    // Connect to live updates stream
    const eventSource = connectToUpdatesStream(
      handleLiveUpdate,
      handleStreamError
    );

    return () => {
      eventSource.close();
    };
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const data = await getDashboardAnalytics();
      setAnalytics(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch analytics data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLiveUpdate = (update) => {
    setLiveUpdates((prev) => [update, ...prev].slice(0, 10));
    
    // Refresh analytics on certain events
    if (['assignment_created', 'task_completed'].includes(update.type)) {
      fetchAnalytics();
    }
  };

  const handleStreamError = (error) => {
    console.error('Live updates stream error:', error);
  };

  if (loading) {
    return <div className="dashboard-loading">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="dashboard-error">{error}</div>;
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Time & Resource Allocation Dashboard</h1>
        <button onClick={fetchAnalytics} className="refresh-button">
          Refresh
        </button>
      </header>

      {/* Key Metrics */}
      <div className="metrics-grid">
        <MetricCard
          title="Total Tasks"
          value={analytics.total_tasks}
          subtitle={`${analytics.completed_tasks} completed`}
          color="#4CAF50"
        />
        <MetricCard
          title="In Progress"
          value={analytics.in_progress_tasks}
          subtitle={`${analytics.pending_tasks} pending`}
          color="#2196F3"
        />
        <MetricCard
          title="Avg Utilization"
          value={`${analytics.avg_utilization}%`}
          subtitle={`${analytics.total_employees} employees`}
          color="#FF9800"
        />
        <MetricCard
          title="Open Issues"
          value={analytics.open_anomalies}
          subtitle={`${analytics.tasks_at_risk} at risk`}
          color={analytics.tasks_at_risk > 0 ? '#F44336' : '#4CAF50'}
        />
      </div>

      {/* Main Content Grid */}
      <div className="dashboard-content">
        <div className="dashboard-section">
          <h2>Workload Distribution</h2>
          <WorkloadHeatmap />
        </div>

        <div className="dashboard-section">
          <h2>Task Queue</h2>
          <TaskQueue />
        </div>

        <div className="dashboard-section full-width">
          <h2>Progress & Analytics</h2>
          <ProgressCharts />
        </div>

        <div className="dashboard-section">
          <h2>Live Updates</h2>
          <div className="live-updates">
            {liveUpdates.length === 0 ? (
              <p className="no-updates">No recent updates</p>
            ) : (
              liveUpdates.map((update, index) => (
                <div key={index} className="update-item">
                  <span className="update-type">{update.type}</span>
                  <span className="update-time">
                    {new Date(update.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const MetricCard = ({ title, value, subtitle, color }) => {
  return (
    <div className="metric-card" style={{ borderLeftColor: color }}>
      <h3>{title}</h3>
      <div className="metric-value">{value}</div>
      <div className="metric-subtitle">{subtitle}</div>
    </div>
  );
};

export default Dashboard;
