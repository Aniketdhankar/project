// Manager Employees JavaScript

// API Base URL
const API_BASE_URL = '/api';

// Global variables
let employees = [];
let currentFilters = {
  search: '',
  department: '',
  status: ''
};

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
  checkAuthentication();
  loadEmployees();
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

// Load employees
async function loadEmployees() {
  const tableBody = document.getElementById('employeeTable');
  
  try {
    // Mock data - In production: GET /api/employees
    employees = [
      {
        id: 1,
        name: 'Alice Johnson',
        email: 'alice@example.com',
        department: 'engineering',
        role: 'Senior Developer',
        skills: 'Python, JavaScript, React, SQL',
        availability_status: 'available',
        current_workload: 32,
        max_workload: 40,
        performance_rating: 4.5,
        experience_years: 5
      },
      {
        id: 2,
        name: 'Bob Smith',
        email: 'bob@example.com',
        department: 'engineering',
        role: 'Backend Developer',
        skills: 'Java, Spring Boot, MySQL',
        availability_status: 'busy',
        current_workload: 38,
        max_workload: 40,
        performance_rating: 4.2,
        experience_years: 4
      },
      {
        id: 3,
        name: 'Charlie Brown',
        email: 'charlie@example.com',
        department: 'design',
        role: 'UI/UX Designer',
        skills: 'Figma, Sketch, Adobe XD',
        availability_status: 'available',
        current_workload: 20,
        max_workload: 40,
        performance_rating: 4.7,
        experience_years: 3
      },
      {
        id: 4,
        name: 'Diana Prince',
        email: 'diana@example.com',
        department: 'marketing',
        role: 'Marketing Manager',
        skills: 'SEO, Content Marketing, Analytics',
        availability_status: 'on_leave',
        current_workload: 0,
        max_workload: 40,
        performance_rating: 4.3,
        experience_years: 6
      },
      {
        id: 5,
        name: 'Eve Williams',
        email: 'eve@example.com',
        department: 'engineering',
        role: 'Frontend Developer',
        skills: 'React, Vue, TypeScript, CSS',
        availability_status: 'available',
        current_workload: 25,
        max_workload: 40,
        performance_rating: 4.0,
        experience_years: 2.5
      }
    ];
    
    renderEmployeeTable(employees);
  } catch (error) {
    console.error('Error loading employees:', error);
    tableBody.innerHTML = '<tr><td colspan="9" class="text-center text-danger">Error loading employees</td></tr>';
  }
}

// Render employee table
function renderEmployeeTable(employeeList) {
  const tableBody = document.getElementById('employeeTable');
  
  if (employeeList.length === 0) {
    tableBody.innerHTML = '<tr><td colspan="9" class="text-center text-muted">No employees found</td></tr>';
    return;
  }
  
  tableBody.innerHTML = employeeList.map(emp => {
    const workloadPercentage = Math.round((emp.current_workload / emp.max_workload) * 100);
    const workloadClass = workloadPercentage > 80 ? 'high' : workloadPercentage > 50 ? 'medium' : 'low';
    
    return `
      <tr>
        <td>${emp.id}</td>
        <td>
          <strong>${emp.name}</strong><br>
          <small class="text-muted">${emp.role || '-'}</small>
        </td>
        <td><small>${emp.email}</small></td>
        <td><span class="badge bg-secondary">${emp.department.toUpperCase()}</span></td>
        <td>
          <small class="text-truncate-2" title="${emp.skills}">${emp.skills}</small>
        </td>
        <td>
          <span class="status-dot ${emp.availability_status}"></span>
          ${emp.availability_status.replace('_', ' ').toUpperCase()}
        </td>
        <td>
          <div class="workload-bar">
            <div class="workload-fill ${workloadClass}" style="width: ${workloadPercentage}%"></div>
          </div>
          <small class="text-muted">${emp.current_workload}/${emp.max_workload}h</small>
        </td>
        <td>
          <span class="badge bg-warning text-dark">${emp.performance_rating}/5</span>
        </td>
        <td>
          <div class="btn-group btn-group-sm">
            <button class="btn btn-outline-primary" onclick="editEmployee(${emp.id})" title="Edit">
              <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-outline-info" onclick="viewWorkload(${emp.id})" title="View Workload">
              <i class="bi bi-bar-chart"></i>
            </button>
            <button class="btn btn-outline-danger" onclick="deleteEmployee(${emp.id})" title="Delete">
              <i class="bi bi-trash"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

// Apply filters
function applyFilters() {
  currentFilters.search = document.getElementById('searchEmployee').value.toLowerCase();
  currentFilters.department = document.getElementById('filterDepartment').value;
  currentFilters.status = document.getElementById('filterStatus').value;
  
  let filteredEmployees = employees;
  
  // Apply search filter
  if (currentFilters.search) {
    filteredEmployees = filteredEmployees.filter(emp => 
      emp.name.toLowerCase().includes(currentFilters.search) ||
      emp.email.toLowerCase().includes(currentFilters.search) ||
      emp.skills.toLowerCase().includes(currentFilters.search)
    );
  }
  
  // Apply department filter
  if (currentFilters.department) {
    filteredEmployees = filteredEmployees.filter(emp => 
      emp.department === currentFilters.department
    );
  }
  
  // Apply status filter
  if (currentFilters.status) {
    filteredEmployees = filteredEmployees.filter(emp => 
      emp.availability_status === currentFilters.status
    );
  }
  
  renderEmployeeTable(filteredEmployees);
}

// Setup event listeners
function setupEventListeners() {
  // Logout button
  document.getElementById('logoutBtn').addEventListener('click', (e) => {
    e.preventDefault();
    logout();
  });
  
  // Add employee form
  const addEmployeeForm = document.getElementById('addEmployeeForm');
  addEmployeeForm.addEventListener('submit', handleAddEmployee);
  
  // Edit employee form
  const editEmployeeForm = document.getElementById('editEmployeeForm');
  editEmployeeForm.addEventListener('submit', handleEditEmployee);
  
  // Search on input
  document.getElementById('searchEmployee').addEventListener('input', applyFilters);
}

// Handle add employee
async function handleAddEmployee(e) {
  e.preventDefault();
  
  const formData = new FormData(e.target);
  const employeeData = Object.fromEntries(formData.entries());
  
  try {
    // In production: POST /api/employees
    console.log('Adding employee:', employeeData);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Add to local array (mock)
    const newEmployee = {
      id: employees.length + 1,
      ...employeeData,
      availability_status: 'available',
      current_workload: 0,
      performance_rating: 3.0
    };
    employees.push(newEmployee);
    
    showToast('Employee added successfully!', 'success');
    
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('addEmployeeModal'));
    modal.hide();
    
    // Reset form
    e.target.reset();
    
    // Reload table
    renderEmployeeTable(employees);
  } catch (error) {
    console.error('Error adding employee:', error);
    showToast('Failed to add employee', 'danger');
  }
}

// Edit employee
function editEmployee(employeeId) {
  const employee = employees.find(e => e.id === employeeId);
  if (!employee) return;
  
  // Populate form
  document.getElementById('editEmpId').value = employee.id;
  document.getElementById('editEmpName').value = employee.name;
  document.getElementById('editEmpEmail').value = employee.email;
  document.getElementById('editEmpRole').value = employee.role || '';
  document.getElementById('editEmpDepartment').value = employee.department;
  document.getElementById('editEmpSkills').value = employee.skills;
  document.getElementById('editEmpExperience').value = employee.experience_years || '';
  document.getElementById('editEmpMaxWorkload').value = employee.max_workload;
  document.getElementById('editEmpStatus').value = employee.availability_status;
  
  // Show modal
  const modal = new bootstrap.Modal(document.getElementById('editEmployeeModal'));
  modal.show();
}

// Handle edit employee
async function handleEditEmployee(e) {
  e.preventDefault();
  
  const formData = new FormData(e.target);
  const employeeData = Object.fromEntries(formData.entries());
  const employeeId = parseInt(employeeData.employee_id);
  
  try {
    // In production: PUT /api/employees/{id}
    console.log('Updating employee:', employeeData);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Update local array (mock)
    const index = employees.findIndex(e => e.id === employeeId);
    if (index !== -1) {
      employees[index] = { ...employees[index], ...employeeData };
    }
    
    showToast('Employee updated successfully!', 'success');
    
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('editEmployeeModal'));
    modal.hide();
    
    // Reload table
    renderEmployeeTable(employees);
  } catch (error) {
    console.error('Error updating employee:', error);
    showToast('Failed to update employee', 'danger');
  }
}

// View workload
async function viewWorkload(employeeId) {
  const employee = employees.find(e => e.id === employeeId);
  if (!employee) return;
  
  const modalContent = document.getElementById('workloadModalContent');
  
  // Show modal
  const modal = new bootstrap.Modal(document.getElementById('viewWorkloadModal'));
  modal.show();
  
  try {
    modalContent.innerHTML = '<div class="text-center"><div class="spinner-border"></div><p class="mt-2">Loading workload...</p></div>';
    
    // In production: GET /api/employee/{id}/workload
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Mock workload data
    const workloadData = {
      employee: employee,
      current_tasks: [
        { title: 'Implement User Auth', hours: 15, progress: 65 },
        { title: 'Fix Login Bug', hours: 8, progress: 90 },
        { title: 'Code Review', hours: 5, progress: 30 }
      ],
      upcoming_tasks: [
        { title: 'Database Migration', hours: 20, deadline: '2024-02-25' }
      ]
    };
    
    const workloadPercentage = Math.round((employee.current_workload / employee.max_workload) * 100);
    
    modalContent.innerHTML = `
      <div class="mb-4">
        <h5>${employee.name}</h5>
        <p class="text-muted">${employee.role} - ${employee.department}</p>
      </div>
      
      <div class="row mb-4">
        <div class="col-md-6">
          <div class="card">
            <div class="card-body text-center">
              <h6>Current Workload</h6>
              <h3>${employee.current_workload}/${employee.max_workload}h</h3>
              <div class="progress mt-2" style="height: 20px;">
                <div class="progress-bar ${workloadPercentage > 80 ? 'bg-danger' : workloadPercentage > 50 ? 'bg-warning' : 'bg-success'}" 
                     style="width: ${workloadPercentage}%">
                  ${workloadPercentage}%
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card">
            <div class="card-body text-center">
              <h6>Performance Rating</h6>
              <h3>${employee.performance_rating}/5</h3>
              <div class="text-warning mt-2">
                ${'★'.repeat(Math.floor(employee.performance_rating))}${'☆'.repeat(5 - Math.floor(employee.performance_rating))}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <h6>Current Tasks</h6>
      <div class="table-responsive mb-4">
        <table class="table table-sm">
          <thead>
            <tr>
              <th>Task</th>
              <th>Hours</th>
              <th>Progress</th>
            </tr>
          </thead>
          <tbody>
            ${workloadData.current_tasks.map(task => `
              <tr>
                <td>${task.title}</td>
                <td>${task.hours}h</td>
                <td>
                  <div class="progress" style="height: 15px;">
                    <div class="progress-bar" style="width: ${task.progress}%">${task.progress}%</div>
                  </div>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
      
      <h6>Upcoming Tasks</h6>
      <div class="list-group">
        ${workloadData.upcoming_tasks.map(task => `
          <div class="list-group-item">
            <div class="d-flex justify-content-between">
              <span>${task.title}</span>
              <span class="text-muted">${task.hours}h - Due: ${task.deadline}</span>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  } catch (error) {
    console.error('Error loading workload:', error);
    modalContent.innerHTML = '<p class="text-center text-danger">Error loading workload</p>';
  }
}

// Delete employee
async function deleteEmployee(employeeId) {
  const employee = employees.find(e => e.id === employeeId);
  if (!employee) return;
  
  if (!confirm(`Are you sure you want to delete ${employee.name}?`)) {
    return;
  }
  
  try {
    // In production: DELETE /api/employees/{id}
    console.log('Deleting employee:', employeeId);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Remove from local array (mock)
    employees = employees.filter(e => e.id !== employeeId);
    
    showToast('Employee deleted successfully!', 'success');
    
    // Reload table
    renderEmployeeTable(employees);
  } catch (error) {
    console.error('Error deleting employee:', error);
    showToast('Failed to delete employee', 'danger');
  }
}

// Show toast notification
function showToast(message, type = 'info') {
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
  
  toastEl.addEventListener('hidden.bs.toast', () => {
    toastEl.remove();
  });
}

// Logout function
function logout() {
  localStorage.removeItem('user');
  localStorage.removeItem('token');
  window.location.href = '/login';
}
