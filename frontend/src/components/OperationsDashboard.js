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
import PaymentReconciliation from './PaymentReconciliation';
import SystemHealth from './SystemHealth';
import Sidebar from './Sidebar';

const OperationsDashboard = () => {
 const { user, isAdmin, isAuditor, logout } = useAuth();
 const [activeTab, setActiveTab] = useState('overview');
 const [selectedTransaction, setSelectedTransaction] = useState(null);
 const [autoRefresh, setAutoRefresh] = useState(true);
 const [refreshInterval, setRefreshInterval] = useState(10); // seconds
 const [currentTheme, setCurrentTheme] = useState('dark'); // Add theme state
 const [dateRange, setDateRange] = useState({
 from: new Date().toISOString().split('T')[0],
 to: new Date().toISOString().split('T')[0]
 });

 // Listen for theme changes
 useEffect(() => {
 const handleThemeChange = (event) => {
 setCurrentTheme(event.detail.theme);
 };
 
 window.addEventListener('themeChanged', handleThemeChange);
 return () => window.removeEventListener('themeChanged', handleThemeChange);
 }, []);

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

 const getPageTitle = () => {
 switch (activeTab) {
 case 'overview': return 'Dashboard Overview';
 case 'transactions': return 'Live Transactions';
 case 'mismatches': return 'Reconciliation Mismatches';
 case 'analytics': return 'Analytics & Reports';
 case 'system-health': return 'System Health Monitor';
 case 'reconciliation': return 'Transaction Reconciliation';
 case 'drilldown': return 'Transaction Details';
 case 'admin': return 'System Administration';
 default: return 'Banking Operations';
 }
 };

 return (
   <div className="dashboard-layout" style={{ 
     backgroundColor: 'var(--bg-secondary)', 
     color: 'var(--text-primary)',
     minHeight: '100vh',
     transition: 'background-color 0.3s ease, color 0.3s ease'
   }}>
     {/* Sidebar Navigation */}
     <Sidebar 
       activeTab={activeTab}
       setActiveTab={setActiveTab}
       selectedTransaction={selectedTransaction}
       onLogout={logout}
     />

     {/* Main Content */}
     <div className="main-content" style={{
       backgroundColor: 'var(--bg-secondary)',
       color: 'var(--text-primary)'
     }}>
       {/* Header */}
       <div className="main-header" style={{
         backgroundColor: 'var(--bg-primary)',
         color: 'var(--text-primary)',
         borderBottom: '1px solid var(--border-color)'
       }}>
         <h1 className="main-header-title">
           {getPageTitle()}
           <span style={{
             marginLeft: '12px',
             padding: '4px 8px',
             fontSize: '10px',
             backgroundColor: currentTheme === 'light' ? 'var(--primary-blue)' : 'var(--success-green)',
             color: 'white',
             borderRadius: '4px',
             fontWeight: 'normal'
           }}>
             {currentTheme === 'light' ? 'LIGHT MODE' : 'DARK MODE'}
           </span>
         </h1>
 
 <div className="main-header-controls">
 {/* Date Range Picker */}
 <div style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'center' }}>
 <label className="form-label" style={{ margin: 0, fontSize: '0.75rem' }}>
 FROM:
 </label>
 <input
 type="date"
 value={dateRange.from}
 onChange={(e) => setDateRange({ ...dateRange, from: e.target.value })}
 className="form-input"
 style={{ width: 'auto', fontSize: '0.75rem' }}
 />
 <label className="form-label" style={{ margin: 0, fontSize: '0.75rem' }}>
 TO:
 </label>
 <input
 type="date"
 value={dateRange.to}
 onChange={(e) => setDateRange({ ...dateRange, to: e.target.value })}
 className="form-input"
 style={{ width: 'auto', fontSize: '0.75rem' }}
 />
 </div>

 {/* Auto-refresh Controls */}
 <div style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'center' }}>
 <button
 onClick={() => setAutoRefresh(!autoRefresh)}
 className={`btn btn-sm ${autoRefresh ? 'btn-success' : 'btn-secondary'}`}
 title={autoRefresh ? 'Auto-refresh enabled' : 'Auto-refresh disabled'}
 >
 <span className="icon">
   {autoRefresh ? (
     <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
       <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
       <path d="M21 3v5h-5"/>
       <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
       <path d="M3 21v-5h5"/>
     </svg>
   ) : (
     <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
       <rect x="6" y="4" width="4" height="16"/>
       <rect x="14" y="4" width="4" height="16"/>
     </svg>
   )}
 </span>
 {autoRefresh ? 'AUTO' : 'MANUAL'}
 </button>
 
 <select
 value={refreshInterval}
 onChange={(e) => setRefreshInterval(parseInt(e.target.value))}
 disabled={!autoRefresh}
 className="form-select"
 style={{ width: 'auto', fontSize: '0.75rem' }}
 >
 <option value={5}>5s</option>
 <option value={10}>10s</option>
 <option value={30}>30s</option>
 <option value={60}>1m</option>
 </select>
 </div>
 </div>
 </div>

 {/* Content Area */}
 <div className="main-content-area">
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

 {activeTab === 'system-health' && (
 <SystemHealth />
 )}

 {activeTab === 'reconciliation' && (
 <PaymentReconciliation />
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

 {activeTab === 'admin' && (
 <AdminPanel />
 )}
 </div>
 </div>
 </div>
 );
};

export default OperationsDashboard;
