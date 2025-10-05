/**
 * Task Detail Modal Component
 * Shows detailed information about a task
 */

import React, { useState, useEffect } from 'react';
import { getModelExplanation } from '../services/api';
import './TaskDetailModal.css';

const TaskDetailModal = ({ task, onClose }) => {
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (task) {
      fetchExplanation();
    }
  }, [task]);

  const fetchExplanation = async () => {
    try {
      setLoading(true);
      const data = await getModelExplanation(task.task_id);
      setExplanation(data);
    } catch (error) {
      console.error('Failed to fetch explanation:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!task) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{task.title}</h2>
          <button className="close-button" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="modal-body">
          <div className="task-info-section">
            <h3>Task Information</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Priority:</span>
                <span className="info-value">{task.priority}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Status:</span>
                <span className="info-value">{task.status}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Estimated Hours:</span>
                <span className="info-value">{task.estimated_hours}h</span>
              </div>
              <div className="info-item">
                <span className="info-label">Complexity:</span>
                <span className="info-value">{task.complexity_score}/5</span>
              </div>
              <div className="info-item">
                <span className="info-label">Deadline:</span>
                <span className="info-value">
                  {new Date(task.deadline).toLocaleString()}
                </span>
              </div>
            </div>
          </div>

          {task.description && (
            <div className="task-info-section">
              <h3>Description</h3>
              <p>{task.description}</p>
            </div>
          )}

          <div className="task-info-section">
            <h3>Required Skills</h3>
            <div className="skills-list">
              {task.required_skills.split(',').map((skill, index) => (
                <span key={index} className="skill-tag">
                  {skill.trim()}
                </span>
              ))}
            </div>
          </div>

          {loading ? (
            <div className="loading-explanation">
              Loading candidate recommendations...
            </div>
          ) : explanation ? (
            <>
              <div className="task-info-section">
                <h3>Top Candidates</h3>
                <div className="candidates-list">
                  {explanation.top_candidates?.map((candidate) => (
                    <div key={candidate.employee_id} className="candidate-card">
                      <div className="candidate-header">
                        <span className="candidate-name">{candidate.name}</span>
                        <span className="candidate-score">
                          {(candidate.score * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="candidate-factors">
                        <div className="factor">
                          <span>Skill Match:</span>
                          <div className="factor-bar">
                            <div
                              className="factor-fill"
                              style={{ width: `${candidate.factors.skill_match * 100}%` }}
                            />
                          </div>
                          <span>{(candidate.factors.skill_match * 100).toFixed(0)}%</span>
                        </div>
                        <div className="factor">
                          <span>Experience:</span>
                          <div className="factor-bar">
                            <div
                              className="factor-fill"
                              style={{ width: `${candidate.factors.experience * 100}%` }}
                            />
                          </div>
                          <span>{(candidate.factors.experience * 100).toFixed(0)}%</span>
                        </div>
                        <div className="factor">
                          <span>Workload:</span>
                          <div className="factor-bar">
                            <div
                              className="factor-fill"
                              style={{ width: `${candidate.factors.workload * 100}%` }}
                            />
                          </div>
                          <span>{(candidate.factors.workload * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="task-info-section">
                <h3>Model Explanation</h3>
                <div className="feature-importance">
                  {Object.entries(explanation.feature_importance || {}).map(
                    ([feature, importance]) => (
                      <div key={feature} className="importance-item">
                        <span className="importance-label">
                          {feature.replace(/_/g, ' ')}:
                        </span>
                        <div className="importance-bar">
                          <div
                            className="importance-fill"
                            style={{ width: `${importance * 100}%` }}
                          />
                        </div>
                        <span className="importance-value">
                          {(importance * 100).toFixed(0)}%
                        </span>
                      </div>
                    )
                  )}
                </div>
              </div>
            </>
          ) : null}
        </div>

        <div className="modal-footer">
          <button className="button button-secondary" onClick={onClose}>
            Close
          </button>
          <button className="button button-primary">
            Assign Task
          </button>
        </div>
      </div>
    </div>
  );
};

export default TaskDetailModal;
