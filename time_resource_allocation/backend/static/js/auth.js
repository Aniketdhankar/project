// Authentication JavaScript

// Show alert message
function showAlert(message, type = 'danger') {
  const alertContainer = document.getElementById('alertContainer');
  const alert = document.createElement('div');
  alert.className = `alert alert-${type} alert-dismissible fade show`;
  alert.role = 'alert';
  alert.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  alertContainer.appendChild(alert);
  
  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    alert.remove();
  }, 5000);
}

// Login form handler
const loginForm = document.getElementById('loginForm');
if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const remember = document.getElementById('remember').checked;
    
    // Disable submit button
    const submitBtn = loginForm.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Logging in...';
    
    try {
      // Mock login - In production, this would call the backend API
      // For demonstration, we'll use hardcoded credentials
      if (email && password) {
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Store user info in localStorage
        const user = {
          email: email,
          role: email.includes('manager') ? 'manager' : 'employee',
          name: email.split('@')[0].replace('.', ' ').replace(/\b\w/g, c => c.toUpperCase())
        };
        
        localStorage.setItem('user', JSON.stringify(user));
        localStorage.setItem('token', 'demo-token-' + Date.now());
        
        showAlert('Login successful! Redirecting...', 'success');
        
        // Redirect based on role
        setTimeout(() => {
          if (user.role === 'manager') {
            window.location.href = '/manager/dashboard';
          } else {
            window.location.href = '/employee/dashboard';
          }
        }, 1000);
      } else {
        throw new Error('Please enter email and password');
      }
    } catch (error) {
      showAlert(error.message || 'Login failed. Please try again.', 'danger');
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="bi bi-box-arrow-in-right"></i> Login';
    }
  });
}

// Register form handler
const registerForm = document.getElementById('registerForm');
if (registerForm) {
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const role = document.getElementById('role').value;
    const department = document.getElementById('department').value;
    const skills = document.getElementById('skills').value;
    
    // Validate passwords match
    if (password !== confirmPassword) {
      showAlert('Passwords do not match!', 'danger');
      return;
    }
    
    // Validate password length
    if (password.length < 8) {
      showAlert('Password must be at least 8 characters long', 'danger');
      return;
    }
    
    // Disable submit button
    const submitBtn = registerForm.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Registering...';
    
    try {
      // Mock registration - In production, this would call the backend API
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Store user info in localStorage
      const user = {
        name: name,
        email: email,
        role: role,
        department: department,
        skills: skills.split(',').map(s => s.trim())
      };
      
      localStorage.setItem('user', JSON.stringify(user));
      localStorage.setItem('token', 'demo-token-' + Date.now());
      
      showAlert('Registration successful! Redirecting to dashboard...', 'success');
      
      // Redirect based on role
      setTimeout(() => {
        if (role === 'manager') {
          window.location.href = '/manager/dashboard';
        } else {
          window.location.href = '/employee/dashboard';
        }
      }, 1500);
    } catch (error) {
      showAlert(error.message || 'Registration failed. Please try again.', 'danger');
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="bi bi-person-plus"></i> Register';
    }
  });
}

// Check if user is already logged in
function checkAuth() {
  const token = localStorage.getItem('token');
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  
  if (token && user) {
    // User is logged in, redirect to appropriate dashboard
    const currentPath = window.location.pathname;
    if (currentPath === '/login' || currentPath === '/register' || currentPath === '/') {
      if (user.role === 'manager') {
        window.location.href = '/manager/dashboard';
      } else {
        window.location.href = '/employee/dashboard';
      }
    }
  } else {
    // User is not logged in, redirect to login if on protected page
    const currentPath = window.location.pathname;
    if (currentPath.includes('/manager/') || currentPath.includes('/employee/')) {
      window.location.href = '/login';
    }
  }
}

// Logout function
function logout() {
  localStorage.removeItem('user');
  localStorage.removeItem('token');
  window.location.href = '/login';
}

// Initialize auth check
document.addEventListener('DOMContentLoaded', () => {
  // Only check auth on auth pages
  const currentPath = window.location.pathname;
  if (currentPath === '/login' || currentPath === '/register') {
    checkAuth();
  }
});
