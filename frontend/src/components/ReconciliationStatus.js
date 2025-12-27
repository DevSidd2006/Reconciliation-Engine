const ReconciliationStatus = ({ details }) => {
 if (!details) {
 return (
 <div className="card" style={{ marginBottom: '32px' }}>
 <div className="card-header">
 <h3 className="card-title">RECONCILIATION STATUS</h3>
 </div>
 <div style={{ textAlign: 'center', padding: '40px', fontFamily: 'var(--font-mono)' }}>
 LOADING RECONCILIATION DATA...
 </div>
 </div>
 );
 }

 const { statistics = {}, mismatch_breakdown = {}, source_breakdown = {} } = details;

 return (
 <div className="card" style={{ marginBottom: '32px' }}>
 <div className="card-header">
 <h3 className="card-title">RECONCILIATION STATUS</h3>
 </div>
 
 <div className="grid grid-3">
 {/* Reconciliation Progress */}
 <div>
 <h4 style={{ marginBottom: '16px', color: 'var(--primary-black)' }}>
 RECONCILIATION PROGRESS
 </h4>
 <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem' }}>
 <div style={{ marginBottom: '8px' }}>
 <strong>Reconciled:</strong> {statistics?.total_reconciled || 0}
 </div>
 <div style={{ marginBottom: '8px' }}>
 <strong>Pending:</strong> {statistics?.pending_reconciliation || 0}
 </div>
 <div style={{ marginBottom: '8px' }}>
 <strong>Success Rate:</strong> 
 <span style={{ 
 color: (statistics?.success_rate || 0) > 90 ? 'var(--success-green)' : 'var(--error-red)',
 fontWeight: '700',
 marginLeft: '8px'
 }}>
 {statistics?.success_rate || 0}%
 </span>
 </div>
 </div>
 </div>

 {/* Mismatch Breakdown */}
 <div>
 <h4 style={{ marginBottom: '16px', color: 'var(--primary-black)' }}>
 MISMATCH TYPES
 </h4>
 <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem' }}>
 {Object.entries(mismatch_breakdown || {}).length === 0 ? (
 <div style={{ color: 'var(--success-green)', fontWeight: '700' }}>
 NO MISMATCHES
 </div>
 ) : (
 Object.entries(mismatch_breakdown).map(([type, count]) => (
 <div key={type} style={{ 
 marginBottom: '8px',
 display: 'flex',
 justifyContent: 'space-between',
 alignItems: 'center'
 }}>
 <span>{type.replace('_', ' ')}:</span>
 <span style={{ 
 backgroundColor: 'var(--error-red)',
 color: 'var(--primary-white)',
 padding: '2px 8px',
 border: '2px solid var(--primary-black)',
 fontWeight: '700'
 }}>
 {count}
 </span>
 </div>
 ))
 )}
 </div>
 </div>

 {/* Source Activity */}
 <div>
 <h4 style={{ marginBottom: '16px', color: 'var(--primary-black)' }}>
 SOURCE ACTIVITY
 </h4>
 <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem' }}>
 {Object.entries(source_breakdown || {}).map(([source, count]) => (
 <div key={source} style={{ 
 marginBottom: '8px',
 display: 'flex',
 justifyContent: 'space-between',
 alignItems: 'center'
 }}>
 <span style={{
 backgroundColor: source === 'core' ? 'var(--accent-blue)' : 
 source === 'gateway' ? 'var(--accent-magenta)' : 'var(--accent-cyan)',
 color: 'var(--primary-white)',
 padding: '2px 8px',
 border: '2px solid var(--primary-black)',
 fontWeight: '700',
 fontSize: '0.75rem'
 }}>
 {source.toUpperCase()}
 </span>
 <span style={{ fontWeight: '700' }}>{count}</span>
 </div>
 ))}
 </div>
 </div>
 </div>

 {/* Recent Reconciliation Results */}
 {details.recent_reconciled && details.recent_reconciled.length > 0 && (
 <div style={{ marginTop: '24px', borderTop: '3px solid var(--primary-black)', paddingTop: '16px' }}>
 <h4 style={{ marginBottom: '16px', color: 'var(--primary-black)' }}>
 RECENT RECONCILIATION RESULTS
 </h4>
 <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
 {(details.recent_reconciled || []).slice(0, 5).map((result, index) => (
 <div key={index} style={{
 padding: '12px',
 borderBottom: '2px solid var(--gray-200)',
 fontFamily: 'var(--font-mono)',
 fontSize: '0.875rem'
 }}>
 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
 <span style={{ fontWeight: '700' }}>{result.txn_id || 'UNKNOWN'}</span>
 <span className={`status ${result.reconciliation_status === 'MATCHED' ? 'status-success' : 'status-error'}`}>
 {result.reconciliation_status || result.status || 'UNKNOWN'}
 </span>
 </div>
 <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--gray-800)' }}>
 <span>Sources: {(result.reconciled_with_sources || [result.source] || []).join(', ')}</span>
 <span>{result.timestamp ? new Date(result.timestamp).toLocaleTimeString() : 'Unknown time'}</span>
 </div>
 {result.mismatches && result.mismatches.length > 0 && (
 <div style={{ marginTop: '8px', fontSize: '0.75rem' }}>
 <strong>Mismatches:</strong> {(result.mismatches || []).map(m => m.type || 'UNKNOWN').join(', ')}
 </div>
 )}
 </div>
 ))}
 </div>
 </div>
 )}
 </div>
 );
};

export default ReconciliationStatus;
