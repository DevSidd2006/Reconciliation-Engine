import { useState, useEffect } from 'react';
import axios from 'axios';

const LiveTransactionTable = ({ dateRange, onTransactionClick }) => {
 const [transactions, setTransactions] = useState([]);
 const [loading, setLoading] = useState(true);
 const [error, setError] = useState(null);
 const [filters, setFilters] = useState({
 source: '',
 status: '',
 amount_min: '',
 amount_max: '',
 search: ''
 });
 const [pagination, setPagination] = useState({
 page: 1,
 limit: 50,
 total: 0
 });
 const [sortBy, setSortBy] = useState({
 field: 'created_at',
 direction: 'desc'
 });

 const fetchTransactions = async () => {
 try {
 setLoading(true);
 const params = {
 limit: pagination.limit,
 page: pagination.page,
 ...filters,
 sort_by: sortBy.field,
 sort_direction: sortBy.direction
 };

 // Remove empty filters
 Object.keys(params).forEach(key => {
 if (params[key] === '' || params[key] === null || params[key] === undefined) {
 delete params[key];
 }
 });

 const response = await axios.get('/api/transactions', { params });
 
 setTransactions(response.data.transactions || []);
 setPagination(prev => ({
 ...prev,
 total: response.data.total || 0
 }));
 setError(null);
 } catch (err) {
 console.error('Error fetching transactions:', err);
 setError('Failed to load transactions');
 } finally {
 setLoading(false);
 }
 };

 useEffect(() => {
 fetchTransactions();
 }, [pagination.page, pagination.limit, filters, sortBy]);

 // Listen for dashboard refresh events
 useEffect(() => {
 const handleRefresh = () => fetchTransactions();
 window.addEventListener('dashboardRefresh', handleRefresh);
 return () => window.removeEventListener('dashboardRefresh', handleRefresh);
 }, [pagination, filters, sortBy]);

 const handleSort = (field) => {
 setSortBy(prev => ({
 field,
 direction: prev.field === field && prev.direction === 'asc' ? 'desc' : 'asc'
 }));
 };

 const handleFilterChange = (key, value) => {
 setFilters(prev => ({ ...prev, [key]: value }));
 setPagination(prev => ({ ...prev, page: 1 })); // Reset to first page
 };

 const clearFilters = () => {
 setFilters({
 source: '',
 status: '',
 amount_min: '',
 amount_max: '',
 search: ''
 });
 };

 const getStatusColor = (status) => {
 switch (status) {
 case 'SUCCESS': return 'var(--success-green)';
 case 'FAILED': return 'var(--error-red)';
 case 'PENDING': return 'var(--accent-orange)';
 default: return 'var(--gray-600)';
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

 const getReconciliationStatusColor = (status) => {
 switch (status) {
 case 'MATCHED': return 'var(--success-green)';
 case 'MISMATCH': return 'var(--error-red)';
 case 'PENDING': return 'var(--accent-orange)';
 default: return 'var(--gray-600)';
 }
 };

 const getSortIcon = (field) => {
 if (sortBy.field !== field) return '↕';
 return sortBy.direction === 'asc' ? '' : '';
 };

 const totalPages = Math.ceil(pagination.total / pagination.limit);

 return (
 <div className="live-transaction-table">
 <div className="card">
 <div className="card-header">
 <h3 className="card-title"> LIVE TRANSACTION TABLE</h3>
 <div style={{ 
 fontSize: '0.875rem', 
 fontFamily: 'var(--font-mono)',
 color: 'var(--gray-600)'
 }}>
 {pagination.total.toLocaleString()} total transactions
 </div>
 </div>

 {/* Filters */}
 <div className="filters" style={{ 
 padding: '16px 24px',
 borderBottom: '2px solid var(--gray-200)',
 backgroundColor: 'var(--gray-50)'
 }}>
 <div className="grid grid-4" style={{ gap: '12px', marginBottom: '16px' }}>
 {/* Source Filter */}
 <div>
 <label style={{ 
 display: 'block', 
 marginBottom: '4px', 
 fontSize: '0.75rem', 
 fontWeight: '700',
 textTransform: 'uppercase'
 }}>
 Source
 </label>
 <select
 value={filters.source}
 onChange={(e) => handleFilterChange('source', e.target.value)}
 style={{
 width: '100%',
 padding: '8px',
 border: '2px solid var(--primary-black)',
 fontSize: '0.875rem',
 fontFamily: 'var(--font-mono)'
 }}
 >
 <option value="">All Sources</option>
 <option value="core">Core Banking</option>
 <option value="gateway">Payment Gateway</option>
 <option value="mobile">Mobile App</option>
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
 Status
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
 <option value="SUCCESS">Success</option>
 <option value="FAILED">Failed</option>
 <option value="PENDING">Pending</option>
 </select>
 </div>

 {/* Amount Range */}
 <div>
 <label style={{ 
 display: 'block', 
 marginBottom: '4px', 
 fontSize: '0.75rem', 
 fontWeight: '700',
 textTransform: 'uppercase'
 }}>
 Min Amount
 </label>
 <input
 type="number"
 placeholder="0"
 value={filters.amount_min}
 onChange={(e) => handleFilterChange('amount_min', e.target.value)}
 style={{
 width: '100%',
 padding: '8px',
 border: '2px solid var(--primary-black)',
 fontSize: '0.875rem',
 fontFamily: 'var(--font-mono)'
 }}
 />
 </div>

 <div>
 <label style={{ 
 display: 'block', 
 marginBottom: '4px', 
 fontSize: '0.75rem', 
 fontWeight: '700',
 textTransform: 'uppercase'
 }}>
 Max Amount
 </label>
 <input
 type="number"
 placeholder="∞"
 value={filters.amount_max}
 onChange={(e) => handleFilterChange('amount_max', e.target.value)}
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

 {/* Search and Actions */}
 <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
 <input
 type="text"
 placeholder="Search transaction ID..."
 value={filters.search}
 onChange={(e) => handleFilterChange('search', e.target.value)}
 style={{
 flex: 1,
 padding: '8px 12px',
 border: '2px solid var(--primary-black)',
 fontSize: '0.875rem',
 fontFamily: 'var(--font-mono)'
 }}
 />
 <button
 onClick={clearFilters}
 className="btn"
 style={{
 backgroundColor: 'var(--gray-400)',
 color: 'var(--primary-white)',
 padding: '8px 16px'
 }}
 >
 DEL Clear
 </button>
 <button
 onClick={fetchTransactions}
 className="btn btn-primary"
 style={{ padding: '8px 16px' }}
 >
 SYNC Refresh
 </button>
 </div>
 </div>

 {/* Table */}
 <div style={{ overflowX: 'auto' }}>
 <table className="table" style={{ minWidth: '1000px' }}>
 <thead>
 <tr>
 <th 
 onClick={() => handleSort('txn_id')}
 style={{ cursor: 'pointer', userSelect: 'none' }}
 >
 Transaction ID {getSortIcon('txn_id')}
 </th>
 <th 
 onClick={() => handleSort('amount')}
 style={{ cursor: 'pointer', userSelect: 'none' }}
 >
 Amount {getSortIcon('amount')}
 </th>
 <th 
 onClick={() => handleSort('source')}
 style={{ cursor: 'pointer', userSelect: 'none' }}
 >
 Source {getSortIcon('source')}
 </th>
 <th 
 onClick={() => handleSort('status')}
 style={{ cursor: 'pointer', userSelect: 'none' }}
 >
 Status {getSortIcon('status')}
 </th>
 <th 
 onClick={() => handleSort('reconciliation_status')}
 style={{ cursor: 'pointer', userSelect: 'none' }}
 >
 Reconciliation {getSortIcon('reconciliation_status')}
 </th>
 <th>Currency</th>
 <th 
 onClick={() => handleSort('created_at')}
 style={{ cursor: 'pointer', userSelect: 'none' }}
 >
 Timestamp {getSortIcon('created_at')}
 </th>
 <th>Actions</th>
 </tr>
 </thead>
 <tbody>
 {loading ? (
 <tr>
 <td colSpan="8" style={{ textAlign: 'center', padding: '40px' }}>
 <div style={{ fontFamily: 'var(--font-mono)' }}>
 SYNC Loading transactions...
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
 ) : transactions.length === 0 ? (
 <tr>
 <td colSpan="8" style={{ textAlign: 'center', padding: '40px' }}>
 <div style={{ fontFamily: 'var(--font-mono)', color: 'var(--gray-600)' }}>
 No transactions found
 </div>
 </td>
 </tr>
 ) : (
 transactions.map((txn) => (
 <tr 
 key={txn.id}
 onClick={() => onTransactionClick(txn)}
 style={{ 
 cursor: 'pointer',
 transition: 'background-color 0.2s'
 }}
 onMouseEnter={(e) => e.target.closest('tr').style.backgroundColor = 'var(--gray-100)'}
 onMouseLeave={(e) => e.target.closest('tr').style.backgroundColor = 'transparent'}
 >
 <td style={{ 
 fontFamily: 'var(--font-mono)', 
 fontSize: '0.875rem',
 fontWeight: '700'
 }}>
 {txn.txn_id.substring(0, 12)}...
 </td>
 <td style={{ 
 fontFamily: 'var(--font-mono)', 
 fontWeight: '700',
 color: 'var(--primary-black)'
 }}>
 ₹{txn.amount?.toLocaleString()}
 </td>
 <td>
 <span style={{
 backgroundColor: getSourceColor(txn.source),
 color: 'var(--primary-white)',
 padding: '4px 8px',
 border: '2px solid var(--primary-black)',
 fontSize: '0.75rem',
 fontWeight: '700',
 textTransform: 'uppercase'
 }}>
 {txn.source}
 </span>
 </td>
 <td>
 <span style={{
 backgroundColor: getStatusColor(txn.status),
 color: txn.status === 'PENDING' ? 'var(--primary-black)' : 'var(--primary-white)',
 padding: '4px 8px',
 border: '2px solid var(--primary-black)',
 fontSize: '0.75rem',
 fontWeight: '700'
 }}>
 {txn.status}
 </span>
 </td>
 <td>
 <span style={{
 backgroundColor: getReconciliationStatusColor(txn.reconciliation_status),
 color: txn.reconciliation_status === 'PENDING' ? 'var(--primary-black)' : 'var(--primary-white)',
 padding: '4px 8px',
 border: '2px solid var(--primary-black)',
 fontSize: '0.75rem',
 fontWeight: '700'
 }}>
 {txn.reconciliation_status || 'PENDING'}
 </span>
 </td>
 <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem' }}>
 {txn.currency || 'INR'}
 </td>
 <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem' }}>
 {new Date(txn.created_at).toLocaleString()}
 </td>
 <td>
 <button
 onClick={(e) => {
 e.stopPropagation();
 onTransactionClick(txn);
 }}
 className="btn"
 style={{
 backgroundColor: 'var(--accent-blue)',
 color: 'var(--primary-white)',
 padding: '4px 8px',
 fontSize: '0.75rem'
 }}
 >
 View
 </button>
 </td>
 </tr>
 ))
 )}
 </tbody>
 </table>
 </div>

 {/* Pagination */}
 <div className="pagination" style={{
 padding: '16px 24px',
 borderTop: '2px solid var(--gray-200)',
 display: 'flex',
 justifyContent: 'space-between',
 alignItems: 'center'
 }}>
 <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem' }}>
 Showing {((pagination.page - 1) * pagination.limit) + 1} to {Math.min(pagination.page * pagination.limit, pagination.total)} of {pagination.total.toLocaleString()} transactions
 </div>
 
 <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
 <button
 onClick={() => setPagination(prev => ({ ...prev, page: Math.max(1, prev.page - 1) }))}
 disabled={pagination.page === 1}
 className="btn"
 style={{
 backgroundColor: pagination.page === 1 ? 'var(--gray-300)' : 'var(--primary-black)',
 color: 'var(--primary-white)',
 padding: '8px 12px'
 }}
 >
 Previous
 </button>
 
 <span style={{ 
 fontFamily: 'var(--font-mono)', 
 fontSize: '0.875rem',
 padding: '0 12px'
 }}>
 Page {pagination.page} of {totalPages}
 </span>
 
 <button
 onClick={() => setPagination(prev => ({ ...prev, page: Math.min(totalPages, prev.page + 1) }))}
 disabled={pagination.page === totalPages}
 className="btn"
 style={{
 backgroundColor: pagination.page === totalPages ? 'var(--gray-300)' : 'var(--primary-black)',
 color: 'var(--primary-white)',
 padding: '8px 12px'
 }}
 >
 Next 
 </button>
 </div>
 </div>
 </div>
 </div>
 );
};

export default LiveTransactionTable;
