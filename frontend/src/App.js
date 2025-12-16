import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './styles/brutalism.css';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginForm from './components/LoginForm';
import UserProfile from './components/UserProfile';
import Dashboard from './components/Dashboard';
import OperationsDashboard from './components/OperationsDashboard';
import TransactionStream from './components/TransactionStream';
import MismatchAlerts from './components/MismatchAlerts';
import MetricsGrid from './components/MetricsGrid';
import ReconciliationStatus from './components/ReconciliationStatus';
import RedisMonitor from './components/RedisMonitor';
import ErrorBoundary from './components/ErrorBoundary';

const API_BASE = 'http://localhost:8002/api';

function AuthenticatedApp() {
  const { user, loading: authLoading } = useAuth();

  // Show login form if not authenticated
  if (!user && !authLoading) {
    return <LoginForm />;
  }

  // Show loading while checking authentication
  if (authLoading) {
    return (
      <div className="App">
        <header className="header">
          <div className="container">
            <h1>🏦 RECONCILIATION ENGINE</h1>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '1rem', margin: 0 }}>
              AUTHENTICATING...
            </p>
          </div>
        </header>
        <div className="container">
          <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
            <h2>🔐 VERIFYING CREDENTIALS...</h2>
            <p style={{ fontFamily: 'var(--font-mono)', marginTop: '20px' }}>
              Checking authentication status
            </p>
          </div>
        </div>
      </div>
    );
  }



  return (
    <div className="App">
      <ErrorBoundary>
        <OperationsDashboard />
      </ErrorBoundary>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AuthenticatedApp />
    </AuthProvider>
  );
}

export default App;