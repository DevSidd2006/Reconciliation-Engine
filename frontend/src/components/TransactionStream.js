import React from 'react';

const TransactionStream = ({ transactions = [] }) => {
 const getStatusColor = (status) => {
 switch (status) {
 case 'SUCCESS': return 'var(--success-green)';
 case 'FAILED': return 'var(--error-red)';
 case 'PENDING': return 'var(--accent-orange)';
 default: return 'var(--gray-800)';
 }
 };

 const getSourceColor = (source) => {
 switch (source) {
 case 'core': return 'var(--accent-blue)';
 case 'gateway': return 'var(--accent-magenta)';
 case 'mobile': return 'var(--accent-cyan)';
 default: return 'var(--gray-800)';
 }
 };

 return (
 <div className="card">
 <div className="card-header">
 <h3 className="card-title">Live Transaction Stream</h3>
 </div>
 
 <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
 {!transactions || transactions.length === 0 ? (
 <div style={{ 
 textAlign: 'center', 
 padding: '40px', 
 fontFamily: 'var(--font-mono)',
 color: 'var(--gray-800)'
 }}>
 WAITING FOR TRANSACTIONS...
 </div>
 ) : (
 transactions.map((txn) => (
 <div 
 key={txn.id} 
 style={{
 padding: '16px',
 borderBottom: '2px solid var(--gray-200)',
 fontFamily: 'var(--font-mono)',
 fontSize: '0.875rem'
 }}
 >
 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
 <span style={{ fontWeight: '700', color: 'var(--primary-black)' }}>
 {txn.txn_id}
 </span>
 <span 
 className="status"
 style={{ 
 backgroundColor: getStatusColor(txn.status),
 color: txn.status === 'PENDING' ? 'var(--primary-black)' : 'var(--primary-white)'
 }}
 >
 {txn.status}
 </span>
 </div>
 
 <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
 <span>
 <strong>Amount:</strong> ₹{txn.amount}
 </span>
 <span 
 style={{ 
 backgroundColor: getSourceColor(txn.source),
 color: 'var(--primary-white)',
 padding: '4px 8px',
 border: '2px solid var(--primary-black)',
 fontSize: '0.75rem',
 fontWeight: '700'
 }}
 >
 {txn.source.toUpperCase()}
 </span>
 </div>
 
 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
 <span style={{ color: 'var(--gray-800)', fontSize: '0.75rem' }}>
 {new Date(txn.timestamp).toLocaleTimeString()}
 </span>
 {txn.mismatch !== 'CORRECT' && (
 <span 
 className="status status-error"
 style={{ fontSize: '0.75rem' }}
 >
 {txn.mismatch}
 </span>
 )}
 </div>
 </div>
 ))
 )}
 </div>
 </div>
 );
};

export default TransactionStream;
