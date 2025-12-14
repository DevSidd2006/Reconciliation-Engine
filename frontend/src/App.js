import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './styles/brutalism.css';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginForm from './components/LoginForm';
import UserProfile from './components/UserProfile';
import Dashboard from './components/Dashboard';
import TransactionStream from './components/TransactionStream';
import MismatchAlerts from './components/MismatchAlerts';
import MetricsGrid from './components/MetricsGrid';
import ReconciliationStatus from './components/ReconciliationStatus';
import RedisMonitor from './components/RedisMonitor';
import ErrorBoundary from './components/ErrorBoundary';

const API_BASE = 'http://localhost:8000/api';

function AuthenticatedApp() {
  const { user, loading: authLoading } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [mismatches, setMismatches] = useState([]);
  const [metrics, setMetrics] = useState({
    totalTransactions: 0,
    totalMismatches: 0,
    successRate: 100,
    pendingReconciliation: 0,
    systemStatus: 'ONLINE'
  });
  const [reconciliationDetails, setReconciliationDetails] = useState(null);
  const [redisStats, setRedisStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch real data from backend
  const fetchData = async () => {
    try {
      console.log('Fetching data from backend...');
      
      const [txnResponse, mismatchResponse, metricsResponse, detailsResponse, redisResponse] = await Promise.all([
        axios.get(`${API_BASE}/transactions`, { timeout: 10000 }),
        axios.get(`${API_BASE}/mismatches`, { timeout: 10000 }),
        axios.get(`${API_BASE}/metrics`, { timeout: 10000 }),
        axios.get(`${API_BASE}/reconciliation-details`, { timeout: 10000 }),
        axios.get(`${API_BASE}/redis-stats`, { timeout: 10000 })
      ]);

      console.log('Data fetched successfully');
      
      setTransactions(txnResponse.data.transactions || []);
      setMismatches(mismatchResponse.data.mismatches || []);
      setMetrics(metricsResponse.data || {
        totalTransactions: 0,
        totalMismatches: 0,
        successRate: 100,
        pendingReconciliation: 0,
        systemStatus: 'ONLINE'
      });
      setReconciliationDetails(detailsResponse.data || null);
      setRedisStats(redisResponse.data || null);
      setError(null);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError(`Failed to connect to reconciliation engine: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Real-time data updates
  useEffect(() => {
    // Initial fetch
    fetchData();

    // Set up polling for real-time updates
    const interval = setInterval(fetchData, 3000); // Poll every 3 seconds

    return () => clearInterval(interval);
  }, []);

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

  if (loading) {
    return (
      <div className="App">
        <header className="header">
          <div className="container">
            <h1>🏦 RECONCILIATION ENGINE</h1>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '1rem', margin: 0 }}>
              LOADING REAL-TIME DATA...
            </p>
          </div>
        </header>
        <div className="container">
          <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
            <h2>⏳ INITIALIZING RECONCILIATION ENGINE...</h2>
            <p style={{ fontFamily: 'var(--font-mono)', marginTop: '20px' }}>
              Connecting to Kafka streams and loading transaction data
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="App">
        <header className="header">
          <div className="container">
            <h1>🏦 RECONCILIATION ENGINE</h1>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '1rem', margin: 0 }}>
              CONNECTION ERROR
            </p>
          </div>
        </header>
        <div className="container">
          <div className="alert alert-error">
            <h3>❌ SYSTEM ERROR</h3>
            <p>{error}</p>
            <button className="btn btn-primary" onClick={fetchData} style={{ marginTop: '16px' }}>
              RETRY CONNECTION
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="header">
        <div className="container">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h1>🏦 RECONCILIATION ENGINE</h1>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: '1rem', margin: 0 }}>
                REAL-TIME TRANSACTION RECONCILIATION & MISMATCH DETECTION
              </p>
            </div>
            <div style={{ textAlign: 'right', fontFamily: 'var(--font-mono)', fontSize: '0.875rem' }}>
              <div style={{ color: 'var(--success-green)', fontWeight: '700' }}>
                🔐 AUTHENTICATED
              </div>
              <div>
                👤 {user?.username} ({user?.roles?.join(', ')})
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container">
        <ErrorBoundary>
          <UserProfile />
        </ErrorBoundary>
        
        <ErrorBoundary>
          <MetricsGrid metrics={metrics} />
        </ErrorBoundary>
        
        <ErrorBoundary>
          <ReconciliationStatus details={reconciliationDetails} />
        </ErrorBoundary>
        
        <ErrorBoundary>
          <RedisMonitor redisStats={redisStats} />
        </ErrorBoundary>
        
        <div className="grid grid-2">
          <div>
            <ErrorBoundary>
              <TransactionStream transactions={transactions} />
            </ErrorBoundary>
          </div>
          <div>
            <ErrorBoundary>
              <MismatchAlerts mismatches={mismatches} />
            </ErrorBoundary>
          </div>
        </div>
        
        <ErrorBoundary>
          <Dashboard 
            transactions={transactions} 
            mismatches={mismatches} 
            reconciliationDetails={reconciliationDetails}
          />
        </ErrorBoundary>
      </div>
    </div>
  );
}

}

function App() {
  return (
    <AuthProvider>
      <AuthenticatedApp />
    </AuthProvider>
  );
}

export default App;