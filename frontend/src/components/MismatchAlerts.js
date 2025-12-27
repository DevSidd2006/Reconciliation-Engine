import React from 'react';

const MismatchAlerts = ({ mismatches = [] }) => {
 const getSeverityColor = (severity) => {
 switch (severity) {
 case 'HIGH': return 'var(--error-red)';
 case 'MEDIUM': return 'var(--accent-orange)';
 case 'LOW': return 'var(--pending-yellow)';
 default: return 'var(--gray-800)';
 }
 };

 const getMismatchIcon = (type) => {
 switch (type) {
 case 'AMOUNT_MISMATCH': return 'AMT';
 case 'STATUS_MISMATCH': return 'WARN';
 case 'TIMESTAMP_MISMATCH': return 'TIME';
 case 'CURRENCY_MISMATCH': return '';
 case 'ACCOUNT_MISMATCH': return 'BANK';
 case 'MISSING_FIELD': return '';
 case 'DUPLICATE': return 'SYNC';
 default: return 'ERR';
 }
 };

 return (
 <div className="card">
 <div className="card-header">
 <h3 className="card-title">ALERT Mismatch Alerts</h3>
 </div>
 
 <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
 {!mismatches || mismatches.length === 0 ? (
 <div style={{ 
 textAlign: 'center', 
 padding: '40px', 
 fontFamily: 'var(--font-mono)',
 color: 'var(--success-green)',
 fontWeight: '700'
 }}>
 OK NO MISMATCHES DETECTED
 </div>
 ) : (
 mismatches.map((mismatch) => (
 <div 
 key={mismatch.id}
 className="alert"
 style={{
 backgroundColor: getSeverityColor(mismatch.severity),
 color: mismatch.severity === 'LOW' ? 'var(--primary-black)' : 'var(--primary-white)',
 marginBottom: '16px',
 padding: '16px'
 }}
 >
 <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
 <span style={{ fontSize: '1.5rem', marginRight: '12px' }}>
 {getMismatchIcon(mismatch.type)}
 </span>
 <div>
 <div style={{ fontWeight: '800', fontSize: '1rem', textTransform: 'uppercase' }}>
 {mismatch.type.replace('_', ' ')}
 </div>
 <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem', opacity: 0.9 }}>
 TXN: {mismatch.txn_id}
 </div>
 </div>
 <div style={{ marginLeft: 'auto' }}>
 <span 
 style={{
 backgroundColor: mismatch.severity === 'LOW' ? 'var(--primary-black)' : 'rgba(255,255,255,0.2)',
 color: mismatch.severity === 'LOW' ? 'var(--primary-white)' : 'inherit',
 padding: '4px 8px',
 border: '2px solid currentColor',
 fontSize: '0.75rem',
 fontWeight: '700'
 }}
 >
 {mismatch.severity}
 </span>
 </div>
 </div>
 
 <div style={{ 
 fontFamily: 'var(--font-mono)', 
 fontSize: '0.875rem',
 marginBottom: '8px',
 opacity: 0.9
 }}>
 {mismatch.details}
 </div>
 
 <div style={{ 
 fontSize: '0.75rem', 
 fontFamily: 'var(--font-mono)',
 opacity: 0.8
 }}>
 {new Date(mismatch.timestamp).toLocaleString()}
 </div>
 </div>
 ))
 )}
 </div>
 </div>
 );
};

export default MismatchAlerts;
