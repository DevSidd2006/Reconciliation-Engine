import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import KPICards from './KPICards';
import LiveTransactionTable from './LiveTransactionTable';
import MismatchTable from './MismatchTable';
import TransactionDrillDown from './TransactionDrillDown';
import AnalyticsCharts from './AnalyticsCharts';
import AnomalyAlerts from './AnomalyAlerts';
import AdminPanel from './AdminPanel';

const OperationsDashboard = () => {
  const { user, isAdmin, isAuditor } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(10); // seconds
  const [dateRange, setDateRange] = useState({
    from: new Date().toISOString().split('T')[0],
    to: new Date().toISOString().split('T')[0]
  });

  // Auto-refresh functionality
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      // Trigger refresh of active components
      window.dispatchEvent(new CustomEvent('dashboardRefresh'));
    }, refreshInterval * 1000);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval]);

  const handleTransactionClick = (transaction) => {
    setSelectedTransaction(transaction);
    setActiveTab('drilldown');
  };

  const tabs = [
    { id: 'overview', label: '📊 Overview', icon: '📊' },
    { id: 'transactions', label: '💳 Transactions', icon: '💳' },
    { id: 'mismatches', label: '🚨 Mismatches', icon: '🚨' },
    { id: 'analytics', label: '📈 Analytics', icon: '📈' },
    ...(selectedTransaction ? [{ id: 'drilldown', label: '🔍 Drill-Down', icon: '🔍' }] : []),
    ...(isAdmin() ? [{ id: 'admin', label: '⚙️ Admin', icon: '⚙️' }] : [])
  ];

  return (
    <div className="operations-dashboard">
      {/* Header */}
      <div className="dashboard-header" style={{
        padding: '24px',
        borderBottom: '3px solid var(--primary-black)',
        backgroundColor: 'var(--primary-white)',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '2rem', fontWeight: '800' }}>
              🏦 BANKING OPERATIONS DASHBOARD
            </h1>
            <p style={{ 
              margin: '8px 0 0 0', 
              fontFamily: 'var(--font-mono)', 
              color: 'var(--gray-800)' 
            }}>
              Real-time Transaction Reconciliation & Monitoring
            </p>
          </div>

          {/* Controls */}
          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
            {/* Date Range Picker */}
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <label style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem', fontWeight: '700' }}>
                FROM:
              </label>
              <input
                type="date"
                value={dateRange.from}
                onChange={(e) => setDateRange({ ...dateRange, from: e.target.value })}
                style={{
                  padding: '8px',
                  border: '2px solid var(--primary-black)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.875rem'
                }}
              />
              <label style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem', fontWeight: '700' }}>
                TO:
              </label>
              <input
                type="date"
                value={dateRange.to}
                onChange={(e) => setDateRange({ ...dateRange, to: e.target.value })}
                style={{
                  padding: '8px',
                  border: '2px solid var(--primary-black)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.875rem'
                }}
              />
            </div>

            {/* Auto-refresh Controls */}
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <button
                onClick={() => setAutoRefresh(!autoRefresh)}
                className="btn"
                style={{
                  backgroundColor: autoRefresh ? 'var(--success-green)' : 'var(--gray-400)',
                  color: 'var(--primary-white)',
                  padding: '8px 12px',
                  fontSize: '0.875rem'
                }}
              >
                {autoRefresh ? '🔄 AUTO' : '⏸️ MANUAL'}
              </button>
              
              <select
                value={refreshInterval}
                onChange={(e) => setRefreshInterval(parseInt(e.target.value))}
                disabled={!autoRefresh}
                style={{
                  padding: '8px',
                  border: '2px solid var(--primary-black)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.875rem'
                }}
              >
                <option value={5}>5s</option>
                <option value={10}>10s</option>
                <option value={30}>30s</option>
                <option value={60}>1m</option>
              </select>
            </div>

            {/* User Info */}
            <div style={{
              padding: '8px 12px',
              backgroundColor: 'var(--accent-blue)',
              color: 'var(--primary-white)',
              border: '2px solid var(--primary-black)',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.875rem',
              fontWeight: '700'
            }}>
              👤 {user?.username} ({user?.roles?.join(', ')})
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation" style={{
        display: 'flex',
        gap: '4px',
        marginBottom: '24px',
        padding: '0 24px'
      }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className="btn"
            style={{
              backgroundColor: activeTab === tab.id ? 'var(--primary-black)' : 'var(--gray-200)',
              color: activeTab === tab.id ? 'var(--primary-white)' : 'var(--primary-black)',
              padding: '12px 20px',
              fontSize: '0.875rem',
              fontWeight: '700',
              border: '2px solid var(--primary-black)'
            }}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="tab-content" style={{ padding: '0 24px' }}>
        {activeTab === 'overview' && (
          <div>
            <KPICards dateRange={dateRange} />
            <AnomalyAlerts />
          </div>
        )}

        {activeTab === 'transactions' && (
          <LiveTransactionTable 
            dateRange={dateRange}
            onTransactionClick={handleTransactionClick}
          />
        )}

        {activeTab === 'mismatches' && (
          <MismatchTable 
            dateRange={dateRange}
            onTransactionClick={handleTransactionClick}
          />
        )}

        {activeTab === 'analytics' && (
          <AnalyticsCharts dateRange={dateRange} />
        )}

        {activeTab === 'drilldown' && selectedTransaction && (
          <TransactionDrillDown 
            transaction={selectedTransaction}
            onClose={() => {
              setSelectedTransaction(null);
              setActiveTab('transactions');
            }}
          />
        )}

        {activeTab === 'admin' && isAdmin() && (
          <AdminPanel />
        )}
      </div>
    </div>
  );
};

export default OperationsDashboard;