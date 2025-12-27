import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const TransactionDrillDown = ({ transaction, onClose }) => {
 const { isAdmin } = useAuth();
 const [transactionDetails, setTransactionDetails] = useState(null);
 const [mismatches, setMismatches] = useState([]);
 const [loading, setLoading] = useState(true);
 const [error, setError] = useState(null);
 const [manualReconciling, setManualReconciling] = useState(false);

 const fetchTransactionDetails = async () => {
 try {
 setLoading(true);
 
 const [detailsResponse, mismatchesResponse] = await Promise.all([
 axios.get(`/api/transactions/${transaction.txn_id}`),
 axios.get(`/api/mismatches`, { 
 params: { txn_id: transaction.txn_id } 
 })
 ]);

 setTransactionDetails(detailsResponse.data);
 setMismatches(mismatchesResponse.data.mismatches || []);
 setError(null);
 } catch (err) {
 console.error('Error fetching transaction details:', err);
 setError('Failed to load transaction details');
 } finally {
 setLoading(false);
 }
 };

 useEffect(() => {
 if (transaction?.txn_id) {
 fetchTransactionDetails();
 }
 }, [transaction]);

 const handleManualReconciliation = async () => {
 if (!isAdmin()) {
 alert('Only administrators can trigger manual reconciliation');
 return;
 }

 try {
 setManualReconciling(true);
 
 const response = await axios.post(`/api/analytics/reconcile/${transaction.txn_id}`);
 
 if (response.data.reconciliation_triggered) {
 alert('Manual reconciliation triggered successfully!');
 // Refresh the data
 fetchTransactionDetails();
 }
 } catch (err) {
 console.error('Manual reconciliation failed:', err);
 alert('Manual reconciliation failed: ' + (err.response?.data?.detail || err.message));
 } finally {
 setManualReconciling(false);
 }
 };

 const getSourceColor = (source) => {
 switch (source) {
 case 'core': return 'var(--accent-blue)';
 case 'gateway': return 'var(--accent-magenta)';
 case 'mobile': return 'var(--accent-cyan)';
 default: return 'var(--gray-600)';
 }
 };

 const getStatusColor = (status) => {
 switch (status) {
 case 'SUCCESS': return 'var(--success-green)';
 case 'FAILED': return 'var(--error-red)';
 case 'PENDING': return 'var(--accent-orange)';
 default: return 'var(--gray-600)';
 }
 };

 const formatTimestamp = (timestamp) => {
 return new Date(timestamp).toLocaleString('en-US', {
 year: 'numeric',
 month: '2-digit',
 day: '2-digit',
 hour: '2-digit',
 minute: '2-digit',
 second: '2-digit',
 fractionalSecondDigits: 3
 });
 };

 const calculateTimeDifference = (sources) => {
 if (sources.length < 2) return null;
 
 const timestamps = sources.map(s => new Date(s.timestamp)).sort();
 const maxDiff = timestamps[timestamps.length - 1] - timestamps[0];
 return Math.round(maxDiff / 1000); // seconds
 };

 if (loading) {
 return (
 <div className="transaction-drilldown">
 <div className="card">
 <div className="card-header">
 <h3 className="card-title">TRANSACTION DRILL-DOWN</h3>
 <button onClick={onClose} className="btn" style={{ backgroundColor: 'var(--gray-400)' }}>
 Close
 </button>
 </div>
 <div style={{ textAlign: 'center', padding: '60px' }}>
 <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.2rem' }}>
 Loading transaction details...
 </div>
 </div>
 </div>
 </div>
 );
 }

 if (error) {
 return (
 <div className="transaction-drilldown">
 <div className="card">
 <div className="card-header">
 <h3 className="card-title">TRANSACTION DRILL-DOWN</h3>
 <button onClick={onClose} className="btn" style={{ backgroundColor: 'var(--gray-400)' }}>
 Close
 </button>
 </div>
 <div className="alert alert-error">
 <h3>Error Loading Transaction</h3>
 <p>{error}</p>
 <button onClick={fetchTransactionDetails} className="btn btn-primary" style={{ marginTop: '16px' }}>
 Retry
 </button>
 </div>
 </div>
 </div>
 );
 }

 const sources = transactionDetails?.sources || [];
 const timeDifference = calculateTimeDifference(sources);

 return (
 <div className="transaction-drilldown">
 <div className="card">
 <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
 <div>
 <h3 className="card-title">TRANSACTION DRILL-DOWN</h3>
 <div style={{ 
 fontFamily: 'var(--font-mono)', 
 fontSize: '0.875rem', 
 color: 'var(--gray-600)',
 marginTop: '4px'
 }}>
 Transaction ID: {transaction.txn_id}
 </div>
 </div>
 <div style={{ display: 'flex', gap: '8px' }}>
 {isAdmin() && (
 <button
 onClick={handleManualReconciliation}
 disabled={manualReconciling}
 className="btn"
 style={{
 backgroundColor: 'var(--accent-orange)',
 color: 'var(--primary-black)',
 padding: '8px 16px'
 }}
 >
 {manualReconciling ? 'Processing...' : 'Re-run Reconciliation'}
 </button>
 )}
 <button 
 onClick={onClose} 
 className="btn" 
 style={{ 
 backgroundColor: 'var(--gray-400)',
 color: 'var(--primary-white)',
 padding: '8px 16px'
 }}
 >
 Close
 </button>
 </div>
 </div>

 {/* Transaction Overview */}
 <div style={{ padding: '24px', borderBottom: '2px solid var(--gray-200)' }}>
 <h4 style={{ marginBottom: '16px', color: 'var(--primary-black)' }}>
 TRANSACTION OVERVIEW
 </h4>
 
 <div className="grid grid-3" style={{ gap: '16px' }}>
 <div className="metric">
 <div style={{ fontSize: '1.5rem', fontWeight: '800', color: 'var(--primary-black)' }}>
 {sources.length}
 </div>
 <div style={{ fontSize: '0.875rem', fontWeight: '700', textTransform: 'uppercase' }}>
 Sources Found
 </div>
 </div>
 
 <div className="metric">
 <div style={{ fontSize: '1.5rem', fontWeight: '800', color: 'var(--error-red)' }}>
 {mismatches.length}
 </div>
 <div style={{ fontSize: '0.875rem', fontWeight: '700', textTransform: 'uppercase' }}>
 Mismatches Detected
 </div>
 </div>
 
 <div className="metric">
 <div style={{ 
 fontSize: '1.5rem', 
 fontWeight: '800', 
 color: timeDifference > 300 ? 'var(--error-red)' : 'var(--success-green)'
 }}>
 {timeDifference ? `${timeDifference}s` : 'N/A'}
 </div>
 <div style={{ fontSize: '0.875rem', fontWeight: '700', textTransform: 'uppercase' }}>
 Max Time Difference
 </div>
 </div>
 </div>
 </div>

 {/* Source Comparison Matrix */}
 <div style={{ padding: '24px', borderBottom: '2px solid var(--gray-200)' }}>
 <h4 style={{ marginBottom: '16px', color: 'var(--primary-black)' }}>
 SOURCE COMPARISON MATRIX
 </h4>
 
 <div style={{ overflowX: 'auto' }}>
 <table className="table" style={{ minWidth: '800px' }}>
 <thead>
 <tr>
 <th>System</th>
 <th>Amount</th>
 <th>Status</th>
 <th>Timestamp</th>
 <th>Currency</th>
 <th>Account ID</th>
 <th>Reconciliation Status</th>
 </tr>
 </thead>
 <tbody>
 {sources.map((source, index) => (
 <tr key={index}>
 <td>
 <span style={{
 backgroundColor: getSourceColor(source.source),
 color: 'var(--primary-white)',
 padding: '6px 12px',
 border: '2px solid var(--primary-black)',
 fontSize: '0.875rem',
 fontWeight: '700',
 textTransform: 'uppercase'
 }}>
 {source.source}
 </span>
 </td>
 <td style={{ 
 fontFamily: 'var(--font-mono)', 
 fontWeight: '700',
 fontSize: '1rem'
 }}>
 ₹{source.amount?.toLocaleString()}
 </td>
 <td>
 <span style={{
 backgroundColor: getStatusColor(source.status),
 color: source.status === 'PENDING' ? 'var(--primary-black)' : 'var(--primary-white)',
 padding: '4px 8px',
 border: '2px solid var(--primary-black)',
 fontSize: '0.75rem',
 fontWeight: '700'
 }}>
 {source.status}
 </span>
 </td>
 <td style={{ 
 fontFamily: 'var(--font-mono)', 
 fontSize: '0.875rem'
 }}>
 {formatTimestamp(source.timestamp)}
 </td>
 <td style={{ 
 fontFamily: 'var(--font-mono)', 
 fontSize: '0.875rem'
 }}>
 {source.currency || 'INR'}
 </td>
 <td style={{ 
 fontFamily: 'var(--font-mono)', 
 fontSize: '0.875rem'
 }}>
 {source.account_id || 'N/A'}
 </td>
 <td>
 <span style={{
 backgroundColor: source.reconciliation_status === 'MATCHED' ? 'var(--success-green)' : 
 source.reconciliation_status === 'MISMATCH' ? 'var(--error-red)' : 'var(--accent-orange)',
 color: 'var(--primary-white)',
 padding: '4px 8px',
 border: '2px solid var(--primary-black)',
 fontSize: '0.75rem',
 fontWeight: '700'
 }}>
 {source.reconciliation_status || 'PENDING'}
 </span>
 </td>
 </tr>
 ))}
 </tbody>
 </table>
 </div>
 </div>

 {/* Mismatch Details */}
 {mismatches.length > 0 && (
 <div style={{ padding: '24px', borderBottom: '2px solid var(--gray-200)' }}>
 <h4 style={{ marginBottom: '16px', color: 'var(--primary-black)' }}>
 DETECTED MISMATCHES
 </h4>
 
 <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
 {mismatches.map((mismatch, index) => (
 <div key={index} className="alert" style={{
 backgroundColor: mismatch.severity === 'HIGH' ? 'var(--error-red)' : 
 mismatch.severity === 'MEDIUM' ? 'var(--accent-orange)' : 'var(--pending-yellow)',
 color: mismatch.severity === 'LOW' ? 'var(--primary-black)' : 'var(--primary-white)',
 padding: '16px',
 border: '3px solid var(--primary-black)'
 }}>
 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
 <div style={{ fontWeight: '800', fontSize: '1rem' }}>
 {mismatch.type?.replace('_', ' ')} - {mismatch.severity} SEVERITY
 </div>
 <div style={{ fontSize: '0.875rem', fontFamily: 'var(--font-mono)' }}>
 Detected: {new Date(mismatch.detected_at).toLocaleString()}
 </div>
 </div>
 <div style={{ fontSize: '0.875rem', marginBottom: '8px' }}>
 <strong>Details:</strong> {mismatch.details}
 </div>
 {mismatch.expected_value && mismatch.actual_value && (
 <div style={{ fontSize: '0.875rem', fontFamily: 'var(--font-mono)' }}>
 <strong>Expected:</strong> {mismatch.expected_value} | 
 <strong> Actual:</strong> {mismatch.actual_value}
 {mismatch.difference_amount && (
 <span> | <strong>Difference:</strong> ₹{mismatch.difference_amount}</span>
 )}
 </div>
 )}
 </div>
 ))}
 </div>
 </div>
 )}

 {/* Resolution Actions */}
 <div style={{ padding: '24px' }}>
 <h4 style={{ marginBottom: '16px', color: 'var(--primary-black)' }}>
 RESOLUTION ACTIONS
 </h4>
 
 <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
 <button
 onClick={() => window.open(`/api/transactions/${transaction.txn_id}`, '_blank')}
 className="btn"
 style={{
 backgroundColor: 'var(--accent-blue)',
 color: 'var(--primary-white)',
 padding: '8px 16px'
 }}
 >
 Export Details
 </button>
 
 <button
 onClick={() => {
 const details = JSON.stringify(transactionDetails, null, 2);
 navigator.clipboard.writeText(details);
 alert('Transaction details copied to clipboard!');
 }}
 className="btn"
 style={{
 backgroundColor: 'var(--accent-cyan)',
 color: 'var(--primary-white)',
 padding: '8px 16px'
 }}
 >
 Copy to Clipboard
 </button>
 
 {mismatches.length > 0 && (
 <button
 className="btn"
 style={{
 backgroundColor: 'var(--error-red)',
 color: 'var(--primary-white)',
 padding: '8px 16px'
 }}
 >
 Escalate to Support
 </button>
 )}
 
 <button
 onClick={() => {
 const mailto = `mailto:support@bank.com?subject=Transaction Investigation: ${transaction.txn_id}&body=Transaction requires investigation. See attached details.`;
 window.location.href = mailto;
 }}
 className="btn"
 style={{
 backgroundColor: 'var(--accent-magenta)',
 color: 'var(--primary-white)',
 padding: '8px 16px'
 }}
 >
 Email Investigation
 </button>
 </div>
 </div>
 </div>
 </div>
 );
};

export default TransactionDrillDown;
