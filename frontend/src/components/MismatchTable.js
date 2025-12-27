import { useState, useEffect } from 'react';
import axios from 'axios';

const MismatchTable = ({ dateRange, onTransactionClick }) => {
 const [mismatches, setMismatches] = useState([]);
 const [loading, setLoading] = useState(true);
 const [error, setError] = useState(null);
 const [filters, setFilters] = useState({
 mismatch_type: '',
 severity: '',
 status: '',
 search: ''
 });
 const [pagination, setPagination] = useState({
 page: 1,
 limit: 50,
 total: 0
 });

 const fetchMismatches = async () => {
 try {
 setLoading(true);
 const params = {
 limit: pagination.limit,
 ...filters
 };

 // Remove empty filters
 Object.keys(params).forEach(key => {
 if (params[key] === '' || params[key] === null || params[key] === undefined) {
 delete params[key];
 }
 });

 const response = await axios.get('/api/mismatches', { params });
 
 setMismatches(response.data.mismatches || []);
 setPagination(prev => ({
 ...prev,
 total: response.data.total || 0
 }));
 setError(null);
 } catch (err) {
 console.error('Error fetching mismatches:', err);
 setError('Failed to load mismatches');
 } finally {
 setLoading(false);
 }
 };

 useEffect(() => {
 fetchMismatches();
 }, [pagination.limit, filters]);

 // Listen for dashboard refresh events
 useEffect(() => {
 const handleRefresh = () => fetchMismatches();
 window.addEventListener('dashboardRefresh', handleRefresh);
 return () => window.removeEventListener('dashboardRefresh', handleRefresh);
 }, [pagination, filters]);

 const handleFilterChange = (key, value) => {
 setFilters(prev => ({ ...prev, [key]: value }));
 };

 const clearFilters = () => {
 setFilters({
 mismatch_type: '',
 severity: '',
 status: '',
 search: ''
 });
 };

 const getSeverityColor = (severity) => {
 switch (severity) {
 case 'HIGH': return 'var(--error-red)';
 case 'MEDIUM': return 'var(--accent-orange)';
 case 'LOW': return 'var(--pending-yellow)';
 default: return 'var(--gray-600)';
 }
 };

 const getMismatchTypeIcon = (type) => {
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

 const getStatusColor = (status) => {
 switch (status) {
 case 'RESOLVED': return 'var(--success-green)';
 case 'INVESTIGATING': return 'var(--accent-orange)';
 case 'OPEN': return 'var(--error-red)';
 default: return 'var(--gray-600)';
 }
 };

 return (
 <div className="mismatch-table">
 <div className="card">
 <div className="card-header">
 <h3 className="card-title">ALERT MISMATCH ANALYSIS TABLE</h3>
 <div style={{ 
 fontSize: '0.875rem', 
 fontFamily: 'var(--font-mono)',
 color: 'var(--gray-600)'
 }}>
 {pagination.total.toLocaleString()} total mismatches • Critical for auditors
 </div>
 </div>

 {/* Filters */}
 <div className="filters" style={{ 
 padding: '16px 24px',
 borderBottom: '2px solid var(--gray-200)',
 backgroundColor: 'var(--gray-50)'
 }}>
 <div className="grid grid-4" style={{ gap: '12px', marginBottom: '16px' }}>
 {/* Mismatch Type Filter */}
 <div>
 <label style={{ 
 display: 'block', 
 marginBottom: '4px', 
 fontSize: '0.75rem', 
 fontWeight: '700',
 textTransform: 'uppercase'
 }}>
 Mismatch Type
 </label>
 <select
 value={filters.mismatch_type}
 onChange={(e) => handleFilterChange('mismatch_type', e.target.value)}
 style={{
 width: '100%',
 padding: '8px',
 border: '2px solid var(--primary-black)',
 fontSize: '0.875rem',
 fontFamily: 'var(--font-mono)'
 }}
 >
 <option value="">All Types</option>
 <option value="AMOUNT_MISMATCH">Amount Mismatch</option>
 <option value="STATUS_MISMATCH">Status Mismatch</option>
 <option value="TIMESTAMP_MISMATCH">Timestamp Mismatch</option>
 <option value="CURRENCY_MISMATCH">Currency Mismatch</option>
 <option value="ACCOUNT_MISMATCH">Account Mismatch</option>
 <option value="MISSING_FIELD">Missing Field</option>
 <option value="DUPLICATE">Duplicate</option>
 </select>
 </div>

 {/* Severity Filter */}
 <div>
 <label style={{ 
 display: 'block', 
 marginBottom: '4px', 
 fontSize: '0.75rem', 
 fontWeight: '700',
 textTransform: 'uppercase'
 }}>
 Severity
 </label>
 <select
 value={filters.severity}
 onChange={(e) => handleFilterChange('severity', e.target.value)}
 style={{
 width: '100%',
 padding: '8px',
 border: '2px solid var(--primary-black)',
 fontSize: '0.875rem',
 fontFamily: 'var(--font-mono)'
 }}
 >
 <option value="">All Severities</option>
 <option value="HIGH">HIGH High</option>
 <option value="MEDIUM">MED Medium</option>
 <option value="LOW">LOW Low</option>
 </select>
 </div>

 {/* Status Filter */}
 <div>
 <label style={{ 
 display: 'block', 
 marginBottom: '4px', 
 fontSize: '0.75rem', 
 fontWeight: '700',
 textTransform: 'uppercase'
 }}>
 Resolution Status
 </label>
 <select
 value={filters.status}
 onChange={(e) => handleFilterChange('status', e.target.value)}
 style={{
 width: '100%',
 padding: '8px',
 border: '2px solid var(--primary-black)',
 fontSize: '0.875rem',
 fontFamily: 'var(--font-mono)'
 }}
 >
 <option value="">All Status</option>
 <option value="OPEN">HIGH Open</option>
 <option value="INVESTIGATING">MED Investigating</option>
 <option value="RESOLVED">OK Resolved</option>
 </select>
 </div>

 {/* Search */}
 <div>
 <label style={{ 
 display: 'block', 
 marginBottom: '4px', 
 fontSize: '0.75rem', 
 fontWeight: '700',
 textTransform: 'uppercase'
 }}>
 Search Transaction
 </label>
 <input
 type="text"
 placeholder="Transaction ID..."
 value={filters.search}
 onChange={(e) => handleFilterChange('search', e.target.value)}
 style={{
 width: '100%',
 padding: '8px',
 border: '2px solid var(--primary-black)',
 fontSize: '0.875rem',
 fontFamily: 'var(--font-mono)'
 }}
 />
 </div>
 </div>

 {/* Actions */}
 <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
 <button
 onClick={clearFilters}
 className="btn"
 style={{
 backgroundColor: 'var(--gray-400)',
 color: 'var(--primary-white)',
 padding: '8px 16px'
 }}
 >
 DEL Clear Filters
 </button>
 <button
 onClick={fetchMismatches}
 className="btn btn-primary"
 style={{ padding: '8px 16px' }}
 >
 SYNC Refresh
 </button>
 <div style={{ 
 marginLeft: 'auto',
 fontFamily: 'var(--font-mono)',
 fontSize: '0.875rem',
 color: 'var(--gray-600)'
 }}>
 Auditor Priority View
 </div>
 </div>
 </div>

 {/* Table */}
 <div style={{ overflowX: 'auto' }}>
 <table className="table" style={{ minWidth: '1200px' }}>
 <thead>
 <tr>
 <th>Type</th>
 <th>Transaction ID</th>
 <th>Severity</th>
 <th>Details</th>
 <th>Sources Involved</th>
 <th>Status</th>
 <th>Detected At</th>
 <th>Actions</th>
 </tr>
 </thead>
 <tbody>
 {loading ? (
 <tr>
 <td colSpan="8" style={{ textAlign: 'center', padding: '40px' }}>
 <div style={{ fontFamily: 'var(--font-mono)' }}>
 SYNC Loading mismatches...
 </div>
 </td>
 </tr>
 ) : error ? (
 <tr>
 <td colSpan="8" style={{ textAlign: 'center', padding: '40px' }}>
 <div style={{ color: 'var(--error-red)', fontWeight: '700' }}>
 ERR {error}
 </div>
 </td>
 </tr>
 ) : mismatches.length === 0 ? (
 <tr>
 <td colSpan="8" style={{ textAlign: 'center', padding: '40px' }}>
 <div style={{ fontFamily: 'var(--font-mono)', color: 'var(--success-green)', fontWeight: '700' }}>
 OK No mismatches found - System operating perfectly!
 </div>
 </td>
 </tr>
 ) : (
 mismatches.map((mismatch) => (
 <tr 
 key={mismatch.id}
 style={{ 
 cursor: 'pointer',
 backgroundColor: mismatch.severity === 'HIGH' ? 'rgba(244, 67, 54, 0.1)' : 'transparent'
 }}
 onMouseEnter={(e) => e.target.closest('tr').style.backgroundColor = 'var(--gray-100)'}
 onMouseLeave={(e) => e.target.closest('tr').style.backgroundColor = 
 mismatch.severity === 'HIGH' ? 'rgba(244, 67, 54, 0.1)' : 'transparent'}
 >
 <td>
 <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
 <span style={{ fontSize: '1.2rem' }}>
 {getMismatchTypeIcon(mismatch.type)}
 </span>
 <span style={{ 
 fontSize: '0.875rem', 
 fontWeight: '700',
 color: 'var(--primary-black)'
 }}>
 {mismatch.type?.replace('_', ' ')}
 </span>
 </div>
 </td>
 <td style={{ 
 fontFamily: 'var(--font-mono)', 
 fontSize: '0.875rem',
 fontWeight: '700'
 }}>
 {mismatch.txn_id?.substring(0, 12)}...
 </td>
 <td>
 <span style={{
 backgroundColor: getSeverityColor(mismatch.severity),
 color: mismatch.severity === 'LOW' ? 'var(--primary-black)' : 'var(--primary-white)',
 padding: '4px 8px',
 border: '2px solid var(--primary-black)',
 fontSize: '0.75rem',
 fontWeight: '700'
 }}>
 {mismatch.severity}
 </span>
 </td>
 <td style={{ 
 fontSize: '0.875rem',
 maxWidth: '300px',
 overflow: 'hidden',
 textOverflow: 'ellipsis',
 whiteSpace: 'nowrap'
 }}>
 {mismatch.details}
 </td>
 <td>
 <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
 {(mismatch.sources_involved || []).map((source, index) => (
 <span key={index} style={{
 backgroundColor: source === 'core' ? 'var(--accent-blue)' : 
 source === 'gateway' ? 'var(--accent-magenta)' : 'var(--accent-cyan)',
 color: 'var(--primary-white)',
 padding: '2px 6px',
 border: '1px solid var(--primary-black)',
 fontSize: '0.75rem',
 fontWeight: '700',
 textTransform: 'uppercase'
 }}>
 {source}
 </span>
 ))}
 </div>
 </td>
 <td>
 <span style={{
 backgroundColor: getStatusColor(mismatch.status),
 color: 'var(--primary-white)',
 padding: '4px 8px',
 border: '2px solid var(--primary-black)',
 fontSize: '0.75rem',
 fontWeight: '700'
 }}>
 {mismatch.status || 'OPEN'}
 </span>
 </td>
 <td style={{ 
 fontFamily: 'var(--font-mono)', 
 fontSize: '0.875rem'
 }}>
 {new Date(mismatch.detected_at).toLocaleString()}
 </td>
 <td>
 <div style={{ display: 'flex', gap: '4px' }}>
 <button
 onClick={(e) => {
 e.stopPropagation();
 // Find the transaction for this mismatch
 onTransactionClick({ txn_id: mismatch.txn_id });
 }}
 className="btn"
 style={{
 backgroundColor: 'var(--accent-blue)',
 color: 'var(--primary-white)',
 padding: '4px 8px',
 fontSize: '0.75rem'
 }}
 >
 Drill-Down
 </button>
 {mismatch.severity === 'HIGH' && (
 <button
 className="btn"
 style={{
 backgroundColor: 'var(--error-red)',
 color: 'var(--primary-white)',
 padding: '4px 8px',
 fontSize: '0.75rem'
 }}
 >
 ALERT Escalate
 </button>
 )}
 </div>
 </td>
 </tr>
 ))
 )}
 </tbody>
 </table>
 </div>

 {/* Summary Stats */}
 <div className="mismatch-summary" style={{
 padding: '16px 24px',
 borderTop: '2px solid var(--gray-200)',
 backgroundColor: 'var(--gray-50)'
 }}>
 <div className="grid grid-4">
 <div className="metric" style={{ textAlign: 'center' }}>
 <div style={{ 
 fontSize: '1.5rem', 
 fontWeight: '800', 
 color: 'var(--error-red)',
 fontFamily: 'var(--font-mono)'
 }}>
 {mismatches.filter(m => m.severity === 'HIGH').length}
 </div>
 <div style={{ fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase' }}>
 HIGH High Severity
 </div>
 </div>
 
 <div className="metric" style={{ textAlign: 'center' }}>
 <div style={{ 
 fontSize: '1.5rem', 
 fontWeight: '800', 
 color: 'var(--accent-orange)',
 fontFamily: 'var(--font-mono)'
 }}>
 {mismatches.filter(m => m.severity === 'MEDIUM').length}
 </div>
 <div style={{ fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase' }}>
 MED Medium Severity
 </div>
 </div>
 
 <div className="metric" style={{ textAlign: 'center' }}>
 <div style={{ 
 fontSize: '1.5rem', 
 fontWeight: '800', 
 color: 'var(--success-green)',
 fontFamily: 'var(--font-mono)'
 }}>
 {mismatches.filter(m => m.status === 'RESOLVED').length}
 </div>
 <div style={{ fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase' }}>
 OK Resolved
 </div>
 </div>
 
 <div className="metric" style={{ textAlign: 'center' }}>
 <div style={{ 
 fontSize: '1.5rem', 
 fontWeight: '800', 
 color: 'var(--primary-black)',
 fontFamily: 'var(--font-mono)'
 }}>
 {Math.round((mismatches.filter(m => m.status === 'RESOLVED').length / mismatches.length) * 100) || 0}%
 </div>
 <div style={{ fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase' }}>
 CHART Resolution Rate
 </div>
 </div>
 </div>
 </div>
 </div>
 </div>
 );
};

export default MismatchTable;
