import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './styles/professional.css';
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
 <div className="header-content">
 <h1>Banking Reconciliation Engine</h1>
 <p className="header-subtitle">
 Authenticating...
 </p>
 </div>
 </header>
 <div className="container" style={{ marginTop: 'var(--space-12)' }}>
 <div className="card text-center">
 <div className="card-body">
 <h2> Verifying Credentials...</h2>
 <p className="text-gray-600" style={{ marginTop: 'var(--space-4)' }}>
 Checking authentication status
 </p>
 <div className="loading" style={{ 
 height: '4px', 
 backgroundColor: 'var(--gray-200)', 
 borderRadius: 'var(--radius)',
 marginTop: 'var(--space-6)'
 }}></div>
 </div>
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
