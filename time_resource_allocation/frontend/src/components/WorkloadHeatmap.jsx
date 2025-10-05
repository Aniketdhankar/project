/**
 * Workload Heatmap Component
 * Visual representation of employee workload distribution
 */

import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { getWorkloadDistribution } from '../services/api';
import './WorkloadHeatmap.css';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const WorkloadHeatmap = () => {
  const [workloadData, setWorkloadData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWorkloadData();
  }, []);

  const fetchWorkloadData = async () => {
    try {
      setLoading(true);
      const data = await getWorkloadDistribution();
      setWorkloadData(data);
    } catch (error) {
      console.error('Failed to fetch workload data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !workloadData) {
    return <div className="loading">Loading workload data...</div>;
  }

  const chartData = {
    labels: workloadData.map((item) => item.employee),
    datasets: [
      {
        label: 'Current Workload (hours)',
        data: workloadData.map((item) => item.workload),
        backgroundColor: workloadData.map((item) => {
          const utilization = (item.workload / item.max) * 100;
          if (utilization >= 90) return 'rgba(244, 67, 54, 0.7)'; // Red
          if (utilization >= 70) return 'rgba(255, 152, 0, 0.7)'; // Orange
          return 'rgba(76, 175, 80, 0.7)'; // Green
        }),
        borderColor: workloadData.map((item) => {
          const utilization = (item.workload / item.max) * 100;
          if (utilization >= 90) return 'rgba(244, 67, 54, 1)';
          if (utilization >= 70) return 'rgba(255, 152, 0, 1)';
          return 'rgba(76, 175, 80, 1)';
        }),
        borderWidth: 2,
      },
      {
        label: 'Max Capacity (hours)',
        data: workloadData.map((item) => item.max),
        backgroundColor: 'rgba(158, 158, 158, 0.3)',
        borderColor: 'rgba(158, 158, 158, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: false,
      },
      tooltip: {
        callbacks: {
          afterLabel: function (context) {
            const index = context.dataIndex;
            const item = workloadData[index];
            const utilization = ((item.workload / item.max) * 100).toFixed(1);
            return `Tasks: ${item.tasks}\nUtilization: ${utilization}%`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Hours',
        },
      },
    },
  };

  return (
    <div className="workload-heatmap">
      <div className="chart-container">
        <Bar data={chartData} options={options} />
      </div>
      <div className="workload-summary">
        <div className="legend-item">
          <span className="legend-color green"></span>
          <span>Under 70% capacity</span>
        </div>
        <div className="legend-item">
          <span className="legend-color orange"></span>
          <span>70-90% capacity</span>
        </div>
        <div className="legend-item">
          <span className="legend-color red"></span>
          <span>Over 90% capacity</span>
        </div>
      </div>
    </div>
  );
};

export default WorkloadHeatmap;
