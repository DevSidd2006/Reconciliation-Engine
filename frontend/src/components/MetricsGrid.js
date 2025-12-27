import React from 'react';

const MetricsGrid = ({ metrics }) => {
 return (
 <div className="grid grid-4" style={{ marginBottom: '32px' }}>
 <div className="metric">
 <span className="metric-value">{metrics.totalTransactions || 0}</span>
 <span className="metric-label">Reconciled Transactions</span>
 </div>
 
 <div className="metric">
 <span className="metric-value" style={{ color: 'var(--error-red)' }}>
 {metrics.totalMismatches || 0}
 </span>
 <span className="metric-label">Mismatches Detected</span>
 </div>
 
 <div className="metric">
 <span className="metric-value" style={{ color: 'var(--accent-orange)' }}>
 {metrics.pendingReconciliation || 0}
 </span>
 <span className="metric-label">Pending Reconciliation</span>
 </div>
 
 <div className="metric">
 <span className="metric-value" style={{ color: 'var(--success-green)' }}>
 {metrics.successRate || 100}%
 </span>
 <span className="metric-label">Reconciliation Success Rate</span>
 </div>
 </div>
 );
};

export default MetricsGrid;
