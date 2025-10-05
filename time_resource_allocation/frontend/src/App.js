/**
 * Main App Component
 * Root component for the Time & Resource Allocation System
 */

import React from 'react';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  return (
    <div className="App">
      <nav className="navbar">
        <div className="navbar-brand">
          <h1>⚡ Time & Resource Allocation System</h1>
        </div>
        <div className="navbar-menu">
          <a href="#dashboard" className="nav-link active">
            Dashboard
          </a>
          <a href="#tasks" className="nav-link">
            Tasks
          </a>
          <a href="#employees" className="nav-link">
            Employees
          </a>
          <a href="#analytics" className="nav-link">
            Analytics
          </a>
          <a href="#settings" className="nav-link">
            Settings
          </a>
        </div>
      </nav>

      <main className="main-content">
        <Dashboard />
      </main>

      <footer className="footer">
        <p>© 2024 Time & Resource Allocation System - Final Year Project</p>
      </footer>
    </div>
  );
}

export default App;
