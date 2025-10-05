/**
 * Task Queue Component
 * Displays pending tasks in the queue
 */

import React, { useState, useEffect } from 'react';
import { getTaskQueue } from '../services/api';
import TaskDetailModal from './TaskDetailModal';
import './TaskQueue.css';

const TaskQueue = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTask, setSelectedTask] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchTasks();
  }, [filter]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const params = filter !== 'all' ? { priority: filter } : {};
      const data = await getTaskQueue(params);
      setTasks(data.tasks || []);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical':
        return '#F44336';
      case 'high':
        return '#FF9800';
      case 'medium':
        return '#2196F3';
      case 'low':
        return '#4CAF50';
      default:
        return '#999';
    }
  };

  const getPriorityBadge = (priority) => {
    return (
      <span
        className="priority-badge"
        style={{ backgroundColor: getPriorityColor(priority) }}
      >
        {priority}
      </span>
    );
  };

  if (loading) {
    return <div className="loading">Loading tasks...</div>;
  }

  return (
    <div className="task-queue">
      <div className="queue-filters">
        <button
          className={filter === 'all' ? 'active' : ''}
          onClick={() => setFilter('all')}
        >
          All
        </button>
        <button
          className={filter === 'critical' ? 'active' : ''}
          onClick={() => setFilter('critical')}
        >
          Critical
        </button>
        <button
          className={filter === 'high' ? 'active' : ''}
          onClick={() => setFilter('high')}
        >
          High
        </button>
        <button
          className={filter === 'medium' ? 'active' : ''}
          onClick={() => setFilter('medium')}
        >
          Medium
        </button>
      </div>

      <div className="task-list">
        {tasks.length === 0 ? (
          <div className="no-tasks">No pending tasks</div>
        ) : (
          tasks.map((task) => (
            <div
              key={task.task_id}
              className="task-item"
              onClick={() => setSelectedTask(task)}
            >
              <div className="task-header">
                <h4>{task.title}</h4>
                {getPriorityBadge(task.priority)}
              </div>
              <div className="task-details">
                <span className="task-meta">
                  ⏱️ {task.estimated_hours}h
                </span>
                <span className="task-meta">
                  📅 {new Date(task.deadline).toLocaleDateString()}
                </span>
                <span className="task-meta">
                  ⚙️ {task.complexity_score}/5
                </span>
              </div>
              <div className="task-skills">
                {task.required_skills}
              </div>
            </div>
          ))
        )}
      </div>

      {selectedTask && (
        <TaskDetailModal
          task={selectedTask}
          onClose={() => setSelectedTask(null)}
        />
      )}
    </div>
  );
};

export default TaskQueue;
