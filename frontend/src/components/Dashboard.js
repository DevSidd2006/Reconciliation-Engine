import React from 'react';

const Dashboard = ({ transactions = [], mismatches = [], reconciliationDetails }) => {
 // Calculate statistics with safe defaults
 const stats = {
 bySource: (transactions || []).reduce((acc, txn) => {
 if (txn && txn.source) {
 acc[txn.source] = (acc[txn.source] || 0) + 1;
 }
 return acc;
 }, {}),
 byStatus: (transactions || []).reduce((acc, txn) => {
 if (txn && txn.status) {
 acc[txn.status] = (acc[txn.status] || 0) + 1;
 }
 return acc;
 }, {}),
 byMismatchType: (mismatches || []).reduce((acc, mismatch) => {
 if (mismatch && mismatch.type) {
 acc[mismatch.type] = (acc[mismatch.type] || 0) + 1;
 }
 return acc;
 }, {})
 };

 const recentTransactions = (transactions || []).slice(0, 10);

 return (
 <div className="grid grid-2" style={{ marginTop: '32px' }}>
 {/* Recent Transactions Table */}
 <div className="card">
 <div className="card-header">
 <h3 className="card-title">Recent Transactions</h3>
 </div>
 
 <table className="table">
 <thead>
 <tr>
 <th>TXN ID</th>
 <th>Amount</th>
 <th>Source</th>
 <th>Status</th>
 <th>Time</th>
 </tr>
 </thead>
 <tbody>
 {recentTransactions.map((txn) => (
 <tr key={txn.id}>
 <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem' }}>
 {txn.txn_id.substring(0, 12)}...
 </td>
 <td style={{ fontFamily: 'var(--font-mono)', fontWeight: '700' }}>
 ₹{txn.amount}
 </td>
 <td>
 <span 
 style={{
 backgroundColor: txn.source === 'core' ? 'var(--accent-blue)' : 
 txn.source === 'gateway' ? 'var(--accent-magenta)' : 'var(--accent-cyan)',
 color: 'var(--primary-white)',
 padding: '4px 8px',
 border: '2px solid var(--primary-black)',
 fontSize: '0.75rem',
 fontWeight: '700'
 }}
 >
 {txn.source.toUpperCase()}
 </span>
 </td>
 <td>
 <span 
 className={`status ${
 txn.status === 'SUCCESS' ? 'status-success' : 
 txn.status === 'FAILED' ? 'status-error' : 'status-warning'
 }`}
 style={{ fontSize: '0.75rem' }}
 >
 {txn.status}
 </span>
 </td>
 <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
 {new Date(txn.timestamp).toLocaleTimeString()}
 </td>
 </tr>
 ))}
 </tbody>
 </table>
 </div>

 {/* Statistics */}
 <div>
 {/* Source Distribution */}
 <div className="card" style={{ marginBottom: '24px' }}>
 <div className="card-header">
 <h3 className="card-title">Source Distribution</h3>
 </div>
 
 <div className="grid grid-3">
 {Object.entries(stats.bySource).map(([source, count]) => (
 <div key={source} className="metric">
 <span className="metric-value" style={{ fontSize: '2rem' }}>
 {count}
 </span>
 <span className="metric-label">{source.toUpperCase()}</span>
 </div>
 ))}
 </div>
 </div>

 {/* Status Distribution */}
 <div className="card">
 <div className="card-header">
 <h3 className="card-title">Status Breakdown</h3>
 </div>
 
 <div className="grid grid-3">
 {Object.entries(stats.byStatus).map(([status, count]) => (
 <div key={status} className="metric">
 <span 
 className="metric-value" 
 style={{ 
 fontSize: '2rem',
 color: status === 'SUCCESS' ? 'var(--success-green)' : 
 status === 'FAILED' ? 'var(--error-red)' : 'var(--accent-orange)'
 }}
 >
 {count}
 </span>
 <span className="metric-label">{status}</span>
 </div>
 ))}
 </div>
 </div>
 </div>
 </div>
 );
};

export default Dashboard;
