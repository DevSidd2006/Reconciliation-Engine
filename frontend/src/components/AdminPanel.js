import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const AdminPanel = () => {
  const { user, isAdmin } = useAuth();
  const [systemHealth, setSystemHealth] = useState(null);
  const [redisStats, setRedisStats] = useState(null);
  const [kafkaStatus, setKafkaStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('health');
  const [operationLoading, setOperationLoading] = useState({});

  const fetchSystemData = async () => {
    try {
      setLoading(true);
      
      const [healthResponse, redisResponse] = await Promise.all([
        axios.get('/api/health'),
        axios.get('/api/redis/stats').catch(() => ({ data: null })) // Redis stats might not be available
      ]);

      setSystemHealth(healthResponse.data);
      setRedisStats(redisResponse.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching system data:', err);
      setError('Failed to load system data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAdmin()) {
      fetchSystemData();
    }
  }, [isAdmin]);

  const handleOperation = async (operation, endpoint, successMessage) => {
    setOperationLoading(prev => ({ ...prev, [operation]: true }));
    
    try {
      await axios.post(endpoint);
      alert(successMessage);
      fetchSystemData(); // Refresh data
    } catch (err) {
      console.error(`${operation} failed:`, err);
      alert(`${operation} failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setOperationLoading(prev => ({ ...prev, [operation]: false }));
    }
  };

  const downloadReport = async (reportType) => {
    try {
      const response = await axios.get(`/api/reports/${reportType}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${reportType}_report_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Download failed:', err);
      alert('Report download failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  if (!isAdmin()) {
    return (
      <div className="admin-panel">
        <div className="alert alert-error">
          <h3>🚫 Access Denied</h3>
          <p>Administrator privileges required to access this panel.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="admin-panel">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">⚙️ ADMIN PANEL</h3>
          </div>
          <div style={{ textAlign: 'center', padding: '60px' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.2rem' }}>
              🔄 Loading system data...
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="admin-panel">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">⚙️ ADMIN PANEL</h3>
          </div>
          <div className="alert alert-error">
            <h3>❌ Error Loading System Data</h3>
            <p>{error}</p>
            <button onClick={fetchSystemData} className="btn btn-primary" style={{ marginTop: '16px' }}>
              🔄 Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-panel">
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">⚙️ ADMIN PANEL</h3>
          <div style={{ 
            fontSize: '0.875rem', 
            fontFamily: 'var(--font-mono)',
            color: 'var(--gray-600)'
          }}>
            System administration & maintenance • User: {user?.username}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="tab-navigation" style={{
          padding: '16px 24px',
          borderBottom: '2px solid var(--gray-200)',
          backgroundColor: 'var(--gray-50)'
        }}>
          <div style={{ display: 'flex', gap: '8px' }}>
            {[
              { id: 'health', label: '🏥 System Health', icon: '🏥' },
              { id: 'operations', label: '🔧 Operations', icon: '🔧' },
              { id: 'reports', label: '📊 Reports', icon: '📊' },
              { id: 'maintenance', label: '🛠️ Maintenance', icon: '🛠️' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className="btn"
                style={{
                  backgroundColor: activeTab === tab.id ? 'var(--primary-black)' : 'var(--gray-200)',
                  color: activeTab === tab.id ? 'var(--primary-white)' : 'var(--primary-black)',
                  padding: '8px 16px',
                  fontSize: '0.875rem',
                  fontWeight: '700'
                }}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div style={{ padding: '24px' }}>
          {activeTab === 'health' && (
            <div className="health-tab">
              <h4 style={{ marginBottom: '20px' }}>🏥 SYSTEM HEALTH STATUS</h4>
              
              {/* Database Health */}
              <div className="card" style={{ marginBottom: '20px' }}>
                <div className="card-header">
                  <h5>🗄️ Database Status</h5>
                </div>
                <div style={{ padding: '16px' }}>
                  <div className="grid grid-2">
                    <div>
                      <div style={{ fontWeight: '700', marginBottom: '4px' }}>Connection Status:</div>
                      <span style={{
                        backgroundColor: systemHealth?.database_connected ? 'var(--success-green)' : 'var(--error-red)',
                        color: 'var(--primary-white)',
                        padding: '4px 8px',
                        border: '2px solid var(--primary-black)',
                        fontSize: '0.875rem',
                        fontWeight: '700'
                      }}>
                        {systemHealth?.database_connected ? '✅ CONNECTED' : '❌ DISCONNECTED'}
                      </span>
                    </div>
                    <div>
                      <div style={{ fontWeight: '700', marginBottom: '4px' }}>Total Transactions:</div>
                      <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.2rem', fontWeight: '700' }}>
                        {systemHealth?.total_transactions?.toLocaleString() || 0}
                      </div>
                    </div>
                  </div>
                  
                  {systemHealth?.last_transaction && (
                    <div style={{ marginTop: '12px' }}>
                      <div style={{ fontWeight: '700', marginBottom: '4px' }}>Last Transaction:</div>
                      <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem' }}>
                        {new Date(systemHealth.last_transaction).toLocaleString()}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Redis Health */}
              {redisStats && (
                <div className="card" style={{ marginBottom: '20px' }}>
                  <div className="card-header">
                    <h5>🔴 Redis Cache Status</h5>
                  </div>
                  <div style={{ padding: '16px' }}>
                    <div className="grid grid-3">
                      <div>
                        <div style={{ fontWeight: '700', marginBottom: '4px' }}>Connection:</div>
                        <span style={{
                          backgroundColor: redisStats.connected ? 'var(--success-green)' : 'var(--error-red)',
                          color: 'var(--primary-white)',
                          padding: '4px 8px',
                          border: '2px solid var(--primary-black)',
                          fontSize: '0.875rem',
                          fontWeight: '700'
                        }}>
                          {redisStats.connected ? '✅ CONNECTED' : '❌ DISCONNECTED'}
                        </span>
                      </div>
                      <div>
                        <div style={{ fontWeight: '700', marginBottom: '4px' }}>Hit Ratio:</div>
                        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.2rem', fontWeight: '700' }}>
                          {redisStats.hit_ratio}%
                        </div>
                      </div>
                      <div>
                        <div style={{ fontWeight: '700', marginBottom: '4px' }}>Operations/sec:</div>
                        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.2rem', fontWeight: '700' }}>
                          {redisStats.operations_per_second}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* System Status Summary */}
              <div className="card">
                <div className="card-header">
                  <h5>📊 System Summary</h5>
                </div>
                <div style={{ padding: '16px' }}>
                  <div style={{
                    padding: '16px',
                    backgroundColor: systemHealth?.status === 'HEALTHY' ? 'var(--success-green)' : 
                                   systemHealth?.status === 'IDLE' ? 'var(--warning-orange)' : 'var(--error-red)',
                    color: 'var(--primary-white)',
                    border: '3px solid var(--primary-black)',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: '800', marginBottom: '8px' }}>
                      {systemHealth?.status === 'HEALTHY' ? '✅ SYSTEM HEALTHY' :
                       systemHealth?.status === 'IDLE' ? '⏸️ SYSTEM IDLE' : '🚨 SYSTEM ERROR'}
                    </div>
                    <div style={{ fontSize: '0.875rem', fontFamily: 'var(--font-mono)' }}>
                      Transactions in last hour: {systemHealth?.transactions_last_hour || 0}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'operations' && (
            <div className="operations-tab">
              <h4 style={{ marginBottom: '20px' }}>🔧 SYSTEM OPERATIONS</h4>
              
              <div className="grid grid-2" style={{ gap: '20px' }}>
                {/* Cache Operations */}
                <div className="card">
                  <div className="card-header">
                    <h5>🔴 Redis Cache Operations</h5>
                  </div>
                  <div style={{ padding: '16px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      <button
                        onClick={() => handleOperation('clearCache', '/api/redis/clear', 'Cache cleared successfully!')}
                        disabled={operationLoading.clearCache}
                        className="btn"
                        style={{
                          backgroundColor: 'var(--error-red)',
                          color: 'var(--primary-white)',
                          padding: '12px'
                        }}
                      >
                        {operationLoading.clearCache ? '🔄 Clearing...' : '🗑️ Clear All Cache'}
                      </button>
                      
                      <button
                        onClick={() => handleOperation('flushStats', '/api/redis/flush-stats', 'Statistics flushed successfully!')}
                        disabled={operationLoading.flushStats}
                        className="btn"
                        style={{
                          backgroundColor: 'var(--warning-orange)',
                          color: 'var(--primary-black)',
                          padding: '12px'
                        }}
                      >
                        {operationLoading.flushStats ? '🔄 Flushing...' : '📊 Flush Statistics'}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Database Operations */}
                <div className="card">
                  <div className="card-header">
                    <h5>🗄️ Database Operations</h5>
                  </div>
                  <div style={{ padding: '16px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      <button
                        onClick={() => handleOperation('recreateTables', '/api/database/recreate-tables', 'Tables recreated successfully!')}
                        disabled={operationLoading.recreateTables}
                        className="btn"
                        style={{
                          backgroundColor: 'var(--error-red)',
                          color: 'var(--primary-white)',
                          padding: '12px'
                        }}
                      >
                        {operationLoading.recreateTables ? '🔄 Recreating...' : '🔄 Recreate Tables'}
                      </button>
                      
                      <button
                        onClick={() => handleOperation('vacuum', '/api/database/vacuum', 'Database optimized successfully!')}
                        disabled={operationLoading.vacuum}
                        className="btn"
                        style={{
                          backgroundColor: 'var(--accent-blue)',
                          color: 'var(--primary-white)',
                          padding: '12px'
                        }}
                      >
                        {operationLoading.vacuum ? '🔄 Optimizing...' : '⚡ Optimize Database'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Reconciliation Operations */}
              <div className="card" style={{ marginTop: '20px' }}>
                <div className="card-header">
                  <h5>🔄 Reconciliation Operations</h5>
                </div>
                <div style={{ padding: '16px' }}>
                  <div className="grid grid-3" style={{ gap: '12px' }}>
                    <button
                      onClick={() => handleOperation('reprocessAll', '/api/reconciliation/reprocess-all', 'Reprocessing all transactions...')}
                      disabled={operationLoading.reprocessAll}
                      className="btn"
                      style={{
                        backgroundColor: 'var(--warning-orange)',
                        color: 'var(--primary-black)',
                        padding: '12px'
                      }}
                    >
                      {operationLoading.reprocessAll ? '🔄 Processing...' : '🔄 Reprocess All'}
                    </button>
                    
                    <button
                      onClick={() => handleOperation('retryFailed', '/api/reconciliation/retry-failed', 'Retrying failed reconciliations...')}
                      disabled={operationLoading.retryFailed}
                      className="btn"
                      style={{
                        backgroundColor: 'var(--accent-magenta)',
                        color: 'var(--primary-white)',
                        padding: '12px'
                      }}
                    >
                      {operationLoading.retryFailed ? '🔄 Retrying...' : '🔁 Retry Failed'}
                    </button>
                    
                    <button
                      onClick={() => handleOperation('clearMismatches', '/api/reconciliation/clear-resolved', 'Resolved mismatches cleared!')}
                      disabled={operationLoading.clearMismatches}
                      className="btn"
                      style={{
                        backgroundColor: 'var(--success-green)',
                        color: 'var(--primary-white)',
                        padding: '12px'
                      }}
                    >
                      {operationLoading.clearMismatches ? '🔄 Clearing...' : '✅ Clear Resolved'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'reports' && (
            <div className="reports-tab">
              <h4 style={{ marginBottom: '20px' }}>📊 SYSTEM REPORTS</h4>
              
              <div className="grid grid-2" style={{ gap: '20px' }}>
                {/* Transaction Reports */}
                <div className="card">
                  <div className="card-header">
                    <h5>💳 Transaction Reports</h5>
                  </div>
                  <div style={{ padding: '16px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      <button
                        onClick={() => downloadReport('transactions')}
                        className="btn btn-primary"
                        style={{ padding: '12px' }}
                      >
                        📄 Download All Transactions (CSV)
                      </button>
                      
                      <button
                        onClick={() => downloadReport('transactions-today')}
                        className="btn"
                        style={{
                          backgroundColor: 'var(--accent-blue)',
                          color: 'var(--primary-white)',
                          padding: '12px'
                        }}
                      >
                        📅 Download Today's Transactions (CSV)
                      </button>
                      
                      <button
                        onClick={() => downloadReport('reconciliation-summary')}
                        className="btn"
                        style={{
                          backgroundColor: 'var(--accent-cyan)',
                          color: 'var(--primary-white)',
                          padding: '12px'
                        }}
                      >
                        📊 Reconciliation Summary (CSV)
                      </button>
                    </div>
                  </div>
                </div>

                {/* Mismatch Reports */}
                <div className="card">
                  <div className="card-header">
                    <h5>🚨 Mismatch Reports</h5>
                  </div>
                  <div style={{ padding: '16px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      <button
                        onClick={() => downloadReport('mismatches')}
                        className="btn"
                        style={{
                          backgroundColor: 'var(--error-red)',
                          color: 'var(--primary-white)',
                          padding: '12px'
                        }}
                      >
                        🚨 Download All Mismatches (CSV)
                      </button>
                      
                      <button
                        onClick={() => downloadReport('high-severity-mismatches')}
                        className="btn"
                        style={{
                          backgroundColor: 'var(--warning-orange)',
                          color: 'var(--primary-black)',
                          padding: '12px'
                        }}
                      >
                        🔴 High Severity Mismatches (CSV)
                      </button>
                      
                      <button
                        onClick={() => downloadReport('audit-trail')}
                        className="btn"
                        style={{
                          backgroundColor: 'var(--accent-magenta)',
                          color: 'var(--primary-white)',
                          padding: '12px'
                        }}
                      >
                        📋 Audit Trail Report (CSV)
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'maintenance' && (
            <div className="maintenance-tab">
              <h4 style={{ marginBottom: '20px' }}>🛠️ SYSTEM MAINTENANCE</h4>
              
              {/* Maintenance Schedule */}
              <div className="card" style={{ marginBottom: '20px' }}>
                <div className="card-header">
                  <h5>📅 Maintenance Schedule</h5>
                </div>
                <div style={{ padding: '16px' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div style={{ 
                      padding: '12px', 
                      backgroundColor: 'var(--gray-100)', 
                      border: '2px solid var(--gray-300)' 
                    }}>
                      <div style={{ fontWeight: '700', marginBottom: '4px' }}>🔄 Daily Reconciliation Cleanup</div>
                      <div style={{ fontSize: '0.875rem', color: 'var(--gray-600)' }}>
                        Runs daily at 2:00 AM • Cleans up resolved mismatches older than 30 days
                      </div>
                    </div>
                    
                    <div style={{ 
                      padding: '12px', 
                      backgroundColor: 'var(--gray-100)', 
                      border: '2px solid var(--gray-300)' 
                    }}>
                      <div style={{ fontWeight: '700', marginBottom: '4px' }}>📊 Weekly Performance Report</div>
                      <div style={{ fontSize: '0.875rem', color: 'var(--gray-600)' }}>
                        Runs weekly on Sunday • Generates system performance analytics
                      </div>
                    </div>
                    
                    <div style={{ 
                      padding: '12px', 
                      backgroundColor: 'var(--gray-100)', 
                      border: '2px solid var(--gray-300)' 
                    }}>
                      <div style={{ fontWeight: '700', marginBottom: '4px' }}>🗄️ Monthly Database Optimization</div>
                      <div style={{ fontSize: '0.875rem', color: 'var(--gray-600)' }}>
                        Runs monthly on 1st • Optimizes database indexes and cleans up old data
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* System Information */}
              <div className="card">
                <div className="card-header">
                  <h5>ℹ️ System Information</h5>
                </div>
                <div style={{ padding: '16px' }}>
                  <div className="grid grid-2" style={{ gap: '16px' }}>
                    <div>
                      <div style={{ fontWeight: '700', marginBottom: '8px' }}>Application Version:</div>
                      <div style={{ fontFamily: 'var(--font-mono)' }}>v2.0.0 (Phase 5)</div>
                    </div>
                    
                    <div>
                      <div style={{ fontWeight: '700', marginBottom: '8px' }}>Last Deployment:</div>
                      <div style={{ fontFamily: 'var(--font-mono)' }}>
                        {new Date().toLocaleDateString()}
                      </div>
                    </div>
                    
                    <div>
                      <div style={{ fontWeight: '700', marginBottom: '8px' }}>Environment:</div>
                      <div style={{ fontFamily: 'var(--font-mono)' }}>Development</div>
                    </div>
                    
                    <div>
                      <div style={{ fontWeight: '700', marginBottom: '8px' }}>Admin User:</div>
                      <div style={{ fontFamily: 'var(--font-mono)' }}>{user?.username}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;