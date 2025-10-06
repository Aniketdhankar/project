// Manager Dashboard JavaScript

// API Base URL
const API_BASE_URL = '/api';

// Global variables
let resourceChart, velocityChart, burndownChart;
let eventSource = null;
let currentFilter = 'all';

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
  checkAuthentication();
  loadDashboardData();
  initializeCharts();
  connectToLiveUpdates();
  setupEventListeners();
});

// Check if user is authenticated
function checkAuthentication() {
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  const token = localStorage.getItem('token');
  
  if (!user || !token || user.role !== 'manager') {
    window.location.href = '/login';
    return;
  }
  
  // Set user name in nav
  document.getElementById('navUserName').textContent = user.name || 'Manager';
}

// Load dashboard data
async function loadDashboardData() {
  try {
    // Load dashboard metrics
    await Promise.all([
      loadDashboardStats(),
      loadTaskQueue(),
      loadEmployeeSummary()
    ]);
  } catch (error) {
    console.error('Error loading dashboard data:', error);
    showToast('Error loading dashboard data', 'danger');
  }
}

// Load dashboard statistics
async function loadDashboardStats() {
  try {
    // Mock data - In production, fetch from API
    const stats = {
      totalTasks: 45,
      completedTasks: 23,
      inProgressTasks: 15,
      overdueTasks: 4
    };
    
    document.getElementById('totalTasks').textContent = stats.totalTasks;
    document.getElementById('completedTasks').textContent = stats.completedTasks;
    document.getElementById('inProgressTasks').textContent = stats.inProgressTasks;
    document.getElementById('overdueTasks').textContent = stats.overdueTasks;
  } catch (error) {
    console.error('Error loading stats:', error);
  }
}

// Load task queue
async function loadTaskQueue() {
  const tableBody = document.getElementById('taskQueueTable');
  
  try {
    // Mock data - In production, fetch from API: GET /api/assignments
    const tasks = [
      { id: 1, title: 'Implement User Authentication', priority: 'high', status: 'in_progress', deadline: '2024-02-15' },
      { id: 2, title: 'Design Database Schema', priority: 'critical', status: 'pending', deadline: '2024-02-10' },
      { id: 3, title: 'Create API Documentation', priority: 'medium', status: 'assigned', deadline: '2024-02-20' },
      { id: 4, title: 'Build Frontend Components', priority: 'high', status: 'in_progress', deadline: '2024-02-18' },
      { id: 5, title: 'Setup CI/CD Pipeline', priority: 'low', status: 'pending', deadline: '2024-02-25' }
    ];
    
    if (tasks.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No tasks found</td></tr>';
      return;
    }
    
    tableBody.innerHTML = tasks.map(task => `
      <tr>
        <td>${task.id}</td>
        <td>${task.title}</td>
        <td><span class="badge badge-priority-${task.priority}">${task.priority.toUpperCase()}</span></td>
        <td><span class="badge badge-status-${task.status}">${task.status.replace('_', ' ').toUpperCase()}</span></td>
        <td>${formatDate(task.deadline)}</td>
        <td>
          <button class="btn btn-sm btn-outline-primary" onclick="viewTaskDetails(${task.id})">
            <i class="bi bi-eye"></i>
          </button>
          <button class="btn btn-sm btn-outline-success" onclick="assignTask(${task.id})">
            <i class="bi bi-person-plus"></i>
          </button>
        </td>
      </tr>
    `).join('');
  } catch (error) {
    console.error('Error loading tasks:', error);
    tableBody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Error loading tasks</td></tr>';
  }
}

// Load employee summary
async function loadEmployeeSummary() {
  try {
    // Mock data - In production, fetch from API
    const summary = {
      total: 25,
      available: 15,
      busy: 8,
      onLeave: 2
    };
    
    document.getElementById('totalEmployees').textContent = summary.total;
    document.getElementById('availableEmployees').textContent = summary.available;
    document.getElementById('busyEmployees').textContent = summary.busy;
    document.getElementById('onLeaveEmployees').textContent = summary.onLeave;
  } catch (error) {
    console.error('Error loading employee summary:', error);
  }
}

// Initialize charts
function initializeCharts() {
  initializeResourceChart();
  initializeVelocityChart();
  initializeBurndownChart();
}

// Initialize resource utilization chart
function initializeResourceChart() {
  const ctx = document.getElementById('resourceChart').getContext('2d');
  
  resourceChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank'],
      datasets: [{
        label: 'Workload (%)',
        data: [85, 72, 90, 45, 68, 55],
        backgroundColor: [
          'rgba(220, 53, 69, 0.7)',
          'rgba(255, 193, 7, 0.7)',
          'rgba(220, 53, 69, 0.7)',
          'rgba(25, 135, 84, 0.7)',
          'rgba(255, 193, 7, 0.7)',
          'rgba(25, 135, 84, 0.7)'
        ],
        borderColor: [
          'rgba(220, 53, 69, 1)',
          'rgba(255, 193, 7, 1)',
          'rgba(220, 53, 69, 1)',
          'rgba(25, 135, 84, 1)',
          'rgba(255, 193, 7, 1)',
          'rgba(25, 135, 84, 1)'
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            callback: function(value) {
              return value + '%';
            }
          }
        }
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return 'Workload: ' + context.parsed.y + '%';
            }
          }
        }
      }
    }
  });
}

// Initialize velocity chart
function initializeVelocityChart() {
  const ctx = document.getElementById('velocityChart').getContext('2d');
  
  velocityChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
      datasets: [{
        label: 'Tasks Completed',
        data: [12, 15, 18, 14, 20, 23],
        borderColor: 'rgba(13, 110, 253, 1)',
        backgroundColor: 'rgba(13, 110, 253, 0.1)',
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true
        }
      },
      plugins: {
        legend: {
          display: false
        }
      }
    }
  });
}

// Initialize burndown chart
function initializeBurndownChart() {
  const ctx = document.getElementById('burndownChart').getContext('2d');
  
  burndownChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
      datasets: [
        {
          label: 'Ideal',
          data: [100, 85, 70, 55, 40, 25, 0],
          borderColor: 'rgba(108, 117, 125, 0.5)',
          borderDash: [5, 5],
          fill: false
        },
        {
          label: 'Actual',
          data: [100, 90, 75, 68, 50, 35, 20],
          borderColor: 'rgba(13, 110, 253, 1)',
          backgroundColor: 'rgba(13, 110, 253, 0.1)',
          tension: 0.4,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      scales: {
        y: {
          beginAtZero: true,
          max: 100
        }
      }
    }
  });
}

// Connect to live updates (Server-Sent Events)
function connectToLiveUpdates() {
  const liveUpdatesContainer = document.getElementById('liveUpdates');
  const connectionStatus = document.getElementById('connectionStatus');
  
  try {
    eventSource = new EventSource(`${API_BASE_URL}/stream/updates`);
    
    eventSource.onopen = () => {
      connectionStatus.textContent = 'Connected';
      connectionStatus.className = 'badge bg-success';
      addLiveUpdate('Connected to live updates', 'success');
    };
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleLiveUpdate(data);
    };
    
    eventSource.onerror = () => {
      connectionStatus.textContent = 'Disconnected';
      connectionStatus.className = 'badge bg-danger';
      
      // Attempt to reconnect after 5 seconds
      setTimeout(() => {
        if (eventSource) {
          eventSource.close();
        }
        connectToLiveUpdates();
      }, 5000);
    };
  } catch (error) {
    console.error('Error connecting to live updates:', error);
    connectionStatus.textContent = 'Error';
    connectionStatus.className = 'badge bg-warning';
  }
}

// Handle live update
function handleLiveUpdate(data) {
  console.log('Live update:', data);
  
  switch (data.type) {
    case 'assignment':
      addLiveUpdate(`Task "${data.task_title}" assigned to ${data.employee_name}`, 'info');
      loadTaskQueue();
      break;
    case 'progress':
      addLiveUpdate(`Progress update on task "${data.task_title}": ${data.progress}%`, 'primary');
      break;
    case 'anomaly':
      addLiveUpdate(`Anomaly detected: ${data.description}`, 'warning');
      break;
    case 'completion':
      addLiveUpdate(`Task "${data.task_title}" completed!`, 'success');
      loadDashboardStats();
      loadTaskQueue();
      break;
    case 'heartbeat':
      // Ignore heartbeat messages
      break;
    default:
      addLiveUpdate('System update received', 'secondary');
  }
}

// Add live update to container
function addLiveUpdate(message, type = 'info') {
  const liveUpdatesContainer = document.getElementById('liveUpdates');
  
  // Remove "waiting" message if present
  const waitingMsg = liveUpdatesContainer.querySelector('.text-muted');
  if (waitingMsg) {
    waitingMsg.remove();
  }
  
  const update = document.createElement('div');
  update.className = 'update-item';
  update.innerHTML = `
    <div class="d-flex justify-content-between align-items-start">
      <div>
        <i class="bi bi-dot text-${type === 'success' ? 'success' : type === 'warning' ? 'warning' : type === 'danger' ? 'danger' : 'primary'}"></i>
        ${message}
      </div>
      <span class="update-time">${new Date().toLocaleTimeString()}</span>
    </div>
  `;
  
  liveUpdatesContainer.insertBefore(update, liveUpdatesContainer.firstChild);
  
  // Keep only last 10 updates
  while (liveUpdatesContainer.children.length > 10) {
    liveUpdatesContainer.removeChild(liveUpdatesContainer.lastChild);
  }
}

// Setup event listeners
function setupEventListeners() {
  // Logout button
  document.getElementById('logoutBtn').addEventListener('click', (e) => {
    e.preventDefault();
    logout();
  });
  
  // Create task form
  const createTaskForm = document.getElementById('createTaskForm');
  createTaskForm.addEventListener('submit', handleCreateTask);
  
  // Auto-assign button
  document.getElementById('autoAssignBtn').addEventListener('click', handleAutoAssign);
  
  // Assignment preview modal
  const assignmentPreviewModal = document.getElementById('assignmentPreviewModal');
  assignmentPreviewModal.addEventListener('show.bs.modal', loadAssignmentPreview);
}

// Handle create task
async function handleCreateTask(e) {
  e.preventDefault();
  
  const formData = new FormData(e.target);
  const taskData = Object.fromEntries(formData.entries());
  
  try {
    // In production: POST /api/tasks
    console.log('Creating task:', taskData);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    showToast('Task created successfully!', 'success');
    
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('createTaskModal'));
    modal.hide();
    
    // Reset form
    e.target.reset();
    
    // Reload task queue
    await loadTaskQueue();
    await loadDashboardStats();
  } catch (error) {
    console.error('Error creating task:', error);
    showToast('Failed to create task', 'danger');
  }
}

// Handle auto-assign
async function handleAutoAssign() {
  const btn = document.getElementById('autoAssignBtn');
  const originalHTML = btn.innerHTML;
  
  try {
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Processing...';
    
    // In production: POST /api/trigger_pipeline
    console.log('Triggering auto-assignment...');
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    showToast('Auto-assignment completed! 5 tasks assigned.', 'success');
    addLiveUpdate('Auto-assignment pipeline executed successfully', 'success');
    
    // Reload data
    await loadTaskQueue();
    await loadDashboardStats();
  } catch (error) {
    console.error('Error in auto-assign:', error);
    showToast('Auto-assignment failed', 'danger');
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalHTML;
  }
}

// Load assignment preview
async function loadAssignmentPreview() {
  const container = document.getElementById('assignmentPreviewContent');
  
  try {
    container.innerHTML = '<div class="text-center"><div class="spinner-border"></div><p class="mt-2">Loading preview...</p></div>';
    
    // In production: GET /api/assignments?status=pending
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const preview = [
      { task: 'Implement User Auth', employee: 'Alice Johnson', score: 0.92 },
      { task: 'Design Database', employee: 'Bob Smith', score: 0.88 },
      { task: 'Create API Docs', employee: 'Charlie Brown', score: 0.85 }
    ];
    
    container.innerHTML = `
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>Task</th>
              <th>Recommended Employee</th>
              <th>Match Score</th>
            </tr>
          </thead>
          <tbody>
            ${preview.map(item => `
              <tr>
                <td>${item.task}</td>
                <td>${item.employee}</td>
                <td>
                  <div class="progress" style="height: 20px;">
                    <div class="progress-bar bg-success" style="width: ${item.score * 100}%">
                      ${(item.score * 100).toFixed(0)}%
                    </div>
                  </div>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  } catch (error) {
    console.error('Error loading preview:', error);
    container.innerHTML = '<p class="text-center text-danger">Error loading preview</p>';
  }
}

// Filter tasks
function filterTasks(status) {
  currentFilter = status;
  loadTaskQueue();
  
  // Update button states
  document.querySelectorAll('.btn-group button').forEach(btn => {
    btn.classList.remove('active');
  });
  event.target.classList.add('active');
}

// View task details
function viewTaskDetails(taskId) {
  console.log('Viewing task:', taskId);
  showToast('Task details view coming soon', 'info');
}

// Assign task
function assignTask(taskId) {
  console.log('Assigning task:', taskId);
  showToast('Manual assignment coming soon', 'info');
}

// Show toast notification
function showToast(message, type = 'info') {
  // Create toast container if it doesn't exist
  let toastContainer = document.getElementById('toastContainer');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toastContainer';
    toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
    toastContainer.style.zIndex = '11';
    document.body.appendChild(toastContainer);
  }
  
  const toastEl = document.createElement('div');
  toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
  toastEl.setAttribute('role', 'alert');
  toastEl.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
  `;
  
  toastContainer.appendChild(toastEl);
  const toast = new bootstrap.Toast(toastEl);
  toast.show();
  
  // Remove toast element after it's hidden
  toastEl.addEventListener('hidden.bs.toast', () => {
    toastEl.remove();
  });
}

// Logout function
function logout() {
  localStorage.removeItem('user');
  localStorage.removeItem('token');
  if (eventSource) {
    eventSource.close();
  }
  window.location.href = '/login';
}

// Format date
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  if (eventSource) {
    eventSource.close();
  }
});
