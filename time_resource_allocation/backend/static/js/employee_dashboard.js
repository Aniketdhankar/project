// Employee Dashboard JavaScript

// API Base URL
const API_BASE_URL = '/api';

// Global variables
let taskDistributionChart;
let eventSource = null;
let myTasks = [];
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
  
  if (!user || !token || user.role !== 'employee') {
    window.location.href = '/login';
    return;
  }
  
  // Set user name in nav
  document.getElementById('navUserName').textContent = user.name || 'Employee';
}

// Load dashboard data
async function loadDashboardData() {
  try {
    await Promise.all([
      loadDashboardStats(),
      loadMyTasks(),
      loadRecentActivity(),
      loadMyStats()
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
      myTasks: 8,
      completedTasks: 15,
      hoursThisWeek: 32.5,
      workloadPercentage: 81
    };
    
    document.getElementById('myTasks').textContent = stats.myTasks;
    document.getElementById('completedTasks').textContent = stats.completedTasks;
    document.getElementById('hoursThisWeek').textContent = stats.hoursThisWeek;
    document.getElementById('workloadPercentage').textContent = stats.workloadPercentage + '%';
  } catch (error) {
    console.error('Error loading stats:', error);
  }
}

// Load my tasks
async function loadMyTasks() {
  const tableBody = document.getElementById('myTasksTable');
  
  try {
    // Get current user
    const user = JSON.parse(localStorage.getItem('user'));
    
    // Mock data - In production: GET /api/assignments?employee_id={user.id}
    myTasks = [
      { id: 1, title: 'Implement User Authentication', priority: 'high', status: 'in_progress', progress: 65, deadline: '2024-02-15' },
      { id: 2, title: 'Fix Login Bug', priority: 'critical', status: 'in_progress', progress: 90, deadline: '2024-02-10' },
      { id: 3, title: 'Update Documentation', priority: 'medium', status: 'assigned', progress: 0, deadline: '2024-02-20' },
      { id: 4, title: 'Code Review', priority: 'low', status: 'assigned', progress: 0, deadline: '2024-02-25' }
    ];
    
    renderTaskTable(myTasks);
    
    // Populate task dropdowns
    populateTaskDropdowns(myTasks);
  } catch (error) {
    console.error('Error loading tasks:', error);
    tableBody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Error loading tasks</td></tr>';
  }
}

// Render task table
function renderTaskTable(tasks) {
  const tableBody = document.getElementById('myTasksTable');
  
  // Apply filter
  let filteredTasks = tasks;
  if (currentFilter !== 'all') {
    filteredTasks = tasks.filter(t => t.status === currentFilter);
  }
  
  if (filteredTasks.length === 0) {
    tableBody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No tasks found</td></tr>';
    return;
  }
  
  tableBody.innerHTML = filteredTasks.map(task => `
    <tr>
      <td>${task.title}</td>
      <td><span class="badge badge-priority-${task.priority}">${task.priority.toUpperCase()}</span></td>
      <td><span class="badge badge-status-${task.status}">${task.status.replace('_', ' ').toUpperCase()}</span></td>
      <td>
        <div class="progress" style="height: 20px;">
          <div class="progress-bar ${task.progress >= 80 ? 'bg-success' : task.progress >= 50 ? 'bg-info' : 'bg-warning'}" 
               style="width: ${task.progress}%" role="progressbar">
            ${task.progress}%
          </div>
        </div>
      </td>
      <td>${formatDate(task.deadline)}</td>
      <td>
        <button class="btn btn-sm btn-outline-primary" onclick="updateTaskProgress(${task.id})" title="Update Progress">
          <i class="bi bi-graph-up"></i>
        </button>
        <button class="btn btn-sm btn-outline-info" onclick="viewTaskDetails(${task.id})" title="View Details">
          <i class="bi bi-eye"></i>
        </button>
      </td>
    </tr>
  `).join('');
}

// Populate task dropdowns
function populateTaskDropdowns(tasks) {
  const timesheetTask = document.getElementById('timesheetTask');
  const progressTask = document.getElementById('progressTask');
  
  const activeTasks = tasks.filter(t => t.status !== 'completed');
  const options = activeTasks.map(task => 
    `<option value="${task.id}">${task.title}</option>`
  ).join('');
  
  timesheetTask.innerHTML = '<option value="">Select a task...</option>' + options;
  progressTask.innerHTML = '<option value="">Select a task...</option>' + options;
}

// Load recent activity
async function loadRecentActivity() {
  const container = document.getElementById('recentActivity');
  
  try {
    // Mock data - In production, fetch from API
    const activities = [
      { type: 'progress', message: 'Updated progress on "Fix Login Bug" to 90%', time: '10 minutes ago' },
      { type: 'timesheet', message: 'Submitted timesheet for 8 hours', time: '2 hours ago' },
      { type: 'assignment', message: 'New task assigned: "Update Documentation"', time: '5 hours ago' },
      { type: 'completion', message: 'Completed task "Setup Environment"', time: '1 day ago' }
    ];
    
    container.innerHTML = activities.map(activity => `
      <div class="list-group-item">
        <div class="d-flex w-100 justify-content-between">
          <p class="mb-1">${activity.message}</p>
          <small class="text-muted">${activity.time}</small>
        </div>
      </div>
    `).join('');
  } catch (error) {
    console.error('Error loading activity:', error);
    container.innerHTML = '<p class="text-center text-danger">Error loading activity</p>';
  }
}

// Load my stats
async function loadMyStats() {
  try {
    // Mock data - In production, fetch from API
    const stats = {
      monthlyCompleted: 15,
      avgCompletionTime: '2.5 days',
      performanceRating: 4.2
    };
    
    document.getElementById('monthlyCompleted').textContent = stats.monthlyCompleted;
    document.getElementById('avgCompletionTime').textContent = stats.avgCompletionTime;
    document.getElementById('performanceRating').textContent = stats.performanceRating + '/5';
    
    const performancePercentage = (stats.performanceRating / 5) * 100;
    const performanceBar = document.getElementById('performanceBar');
    performanceBar.style.width = performancePercentage + '%';
    performanceBar.textContent = performancePercentage.toFixed(0) + '%';
  } catch (error) {
    console.error('Error loading stats:', error);
  }
}

// Initialize charts
function initializeCharts() {
  initializeTaskDistributionChart();
}

// Initialize task distribution chart
function initializeTaskDistributionChart() {
  const ctx = document.getElementById('taskDistributionChart').getContext('2d');
  
  taskDistributionChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['In Progress', 'Assigned', 'Completed', 'Blocked'],
      datasets: [{
        data: [4, 2, 15, 1],
        backgroundColor: [
          'rgba(13, 110, 253, 0.8)',
          'rgba(255, 193, 7, 0.8)',
          'rgba(25, 135, 84, 0.8)',
          'rgba(220, 53, 69, 0.8)'
        ],
        borderWidth: 2,
        borderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  });
}

// Connect to live updates
function connectToLiveUpdates() {
  const liveUpdatesContainer = document.getElementById('liveUpdates');
  const connectionStatus = document.getElementById('connectionStatus');
  
  try {
    // Get current user
    const user = JSON.parse(localStorage.getItem('user'));
    
    // In production: connect to employee-specific stream
    // eventSource = new EventSource(`${API_BASE_URL}/stream/employee/${user.id}`);
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
      addLiveUpdate(`New task assigned: "${data.task_title}"`, 'info');
      loadMyTasks();
      loadDashboardStats();
      break;
    case 'progress':
      addLiveUpdate(`Progress update acknowledged on "${data.task_title}"`, 'primary');
      break;
    case 'feedback':
      addLiveUpdate(`Manager feedback: ${data.message}`, 'warning');
      break;
    case 'completion':
      addLiveUpdate(`Task "${data.task_title}" marked as completed!`, 'success');
      loadMyTasks();
      loadDashboardStats();
      break;
    case 'heartbeat':
      // Ignore heartbeat messages
      break;
    default:
      addLiveUpdate('System update received', 'secondary');
  }
}

// Add live update
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
  
  // Timesheet form
  const timesheetForm = document.getElementById('timesheetForm');
  timesheetForm.addEventListener('submit', handleTimesheetSubmit);
  
  // Progress update form
  const updateProgressForm = document.getElementById('updateProgressForm');
  updateProgressForm.addEventListener('submit', handleProgressUpdate);
  
  // Set today's date as default for timesheet
  document.getElementById('timesheetDate').valueAsDate = new Date();
}

// Handle timesheet submission
async function handleTimesheetSubmit(e) {
  e.preventDefault();
  
  const formData = new FormData(e.target);
  const timesheetData = Object.fromEntries(formData.entries());
  
  try {
    // In production: POST /api/timesheets
    console.log('Submitting timesheet:', timesheetData);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    showToast('Timesheet submitted successfully!', 'success');
    
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('timesheetModal'));
    modal.hide();
    
    // Reset form
    e.target.reset();
    document.getElementById('timesheetDate').valueAsDate = new Date();
    
    // Reload data
    await loadDashboardStats();
    await loadRecentActivity();
  } catch (error) {
    console.error('Error submitting timesheet:', error);
    showToast('Failed to submit timesheet', 'danger');
  }
}

// Handle progress update
async function handleProgressUpdate(e) {
  e.preventDefault();
  
  const formData = new FormData(e.target);
  const progressData = Object.fromEntries(formData.entries());
  
  try {
    // In production: PUT /api/assignments/{id}/progress
    console.log('Updating progress:', progressData);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    showToast('Progress updated successfully!', 'success');
    
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('updateProgressModal'));
    modal.hide();
    
    // Reset form
    e.target.reset();
    document.getElementById('progressPercentage').value = 0;
    document.getElementById('progressValue').textContent = '0%';
    
    // Reload data
    await loadMyTasks();
    await loadDashboardStats();
    await loadRecentActivity();
  } catch (error) {
    console.error('Error updating progress:', error);
    showToast('Failed to update progress', 'danger');
  }
}

// Filter my tasks
function filterMyTasks(status) {
  currentFilter = status;
  renderTaskTable(myTasks);
  
  // Update button states
  document.querySelectorAll('.btn-group button').forEach(btn => {
    btn.classList.remove('active');
  });
  event.target.classList.add('active');
}

// Refresh my tasks
function refreshMyTasks() {
  loadMyTasks();
  showToast('Tasks refreshed', 'info');
}

// Update task progress (from table button)
function updateTaskProgress(taskId) {
  const task = myTasks.find(t => t.id === taskId);
  if (!task) return;
  
  // Populate modal with task data
  document.getElementById('progressTask').value = taskId;
  document.getElementById('progressPercentage').value = task.progress;
  document.getElementById('progressValue').textContent = task.progress + '%';
  document.getElementById('progressStatus').value = task.status;
  
  // Show modal
  const modal = new bootstrap.Modal(document.getElementById('updateProgressModal'));
  modal.show();
}

// View task details
function viewTaskDetails(taskId) {
  const task = myTasks.find(t => t.id === taskId);
  if (!task) return;
  
  console.log('Viewing task:', task);
  showToast('Task details view coming soon', 'info');
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
