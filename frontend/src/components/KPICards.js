import { useState, useEffect } from 'react';
import axios from 'axios';

const KPICards = ({ dateRange }) => {
 const [kpis, setKpis] = useState({
 total_transactions_today: 0,
 total_transactions_all_time: 0,
 total_mismatches: 0,
 reconciliation_accuracy: 100,
 pending_transactions: 0,
 duplicates_detected: 0,
 delayed_transactions: 0
 });
 const [trends, setTrends] = useState({});
 const [loading, setLoading] = useState(true);
 const [error, setError] = useState(null);

 const fetchKPIs = async () => {
 try {
 setLoading(true);
 const response = await axios.get('/api/analytics/overview', {
 params: {
 date_from: dateRange.from,
 date_to: dateRange.to
 }
 });

 setKpis(response.data.kpis);
 setTrends(response.data.trends);
 setError(null);
 } catch (err) {
 console.error('Error fetching KPIs:', err);
 setError('Failed to load KPI data');
 } finally {
 setLoading(false);
 }
 };

 useEffect(() => {
 fetchKPIs();
 }, [dateRange]);

 // Listen for dashboard refresh events
 useEffect(() => {
 const handleRefresh = () => fetchKPIs();
 window.addEventListener('dashboardRefresh', handleRefresh);
 return () => window.removeEventListener('dashboardRefresh', handleRefresh);
 }, [dateRange]);

 const kpiCards = [
 {
 title: 'Total Transactions Today',
 value: kpis.total_transactions_today,
 icon: 'TXN',
 color: 'var(--accent-blue)',
 trend: trends.transactions_vs_yesterday,
 format: 'number'
 },
 {
 title: 'Total Transactions (All Time)',
 value: kpis.total_transactions_all_time,
 icon: 'ALL',
 color: 'var(--accent-cyan)',
 trend: 'up',
 format: 'number'
 },
 {
 title: 'Total Mismatches',
 value: kpis.total_mismatches,
 icon: 'ERR',
 color: 'var(--error-red)',
 trend: trends.mismatches_vs_yesterday,
 format: 'number'
 },
 {
 title: 'Reconciliation Accuracy',
 value: kpis.reconciliation_accuracy,
 icon: 'ACC',
 color: kpis.reconciliation_accuracy >= 90 ? 'var(--success-green)' : 
 kpis.reconciliation_accuracy >= 70 ? 'var(--accent-orange)' : 'var(--error-red)',
 trend: trends.accuracy_trend,
 format: 'percentage'
 },
 {
 title: 'Pending Transactions',
 value: kpis.pending_transactions,
 icon: 'PND',
 color: 'var(--accent-orange)',
 trend: 'stable',
 format: 'number'
 },
 {
 title: 'Duplicates Detected',
 value: kpis.duplicates_detected,
 icon: 'DUP',
 color: 'var(--accent-magenta)',
 trend: 'stable',
 format: 'number'
 },
 {
 title: 'Delayed Transactions',
 value: kpis.delayed_transactions,
 icon: 'DLY',
 color: kpis.delayed_transactions > 10 ? 'var(--error-red)' : 'var(--success-green)',
 trend: 'stable',
 format: 'number',
 subtitle: '(>5 min delay)'
 }
 ];

 const formatValue = (value, format) => {
 switch (format) {
 case 'percentage':
 return `${value}%`;
 case 'number':
 return value.toLocaleString();
 default:
 return value;
 }
 };

 const getTrendIcon = (trend) => {
 switch (trend) {
 case 'up': return (
   <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
     <polyline points="23,6 13.5,15.5 8.5,10.5 1,18"/>
     <polyline points="17,6 23,6 23,12"/>
   </svg>
 );
 case 'down': return (
   <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
     <polyline points="23,18 13.5,8.5 8.5,13.5 1,6"/>
     <polyline points="17,18 23,18 23,12"/>
   </svg>
 );
 case 'stable': return (
   <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
     <line x1="5" y1="12" x2="19" y2="12"/>
     <polyline points="12,5 19,12 12,19"/>
   </svg>
 );
 default: return (
   <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
     <line x1="5" y1="12" x2="19" y2="12"/>
     <polyline points="12,5 19,12 12,19"/>
   </svg>
 );
 }
 };

 const getTrendColor = (trend) => {
 switch (trend) {
 case 'up': return 'var(--success-green)';
 case 'down': return 'var(--error-red)';
 case 'stable': return 'var(--gray-600)';
 default: return 'var(--gray-600)';
 }
 };

 if (loading) {
 return (
 <div className="kpi-cards-loading" style={{ marginBottom: 'var(--space-8)' }}>
 <div className="grid grid-3">
 {[1, 2, 3, 4, 5, 6, 7].map(i => (
 <div key={i} className="card" style={{ padding: 'var(--space-6)', textAlign: 'center' }}>
 <div style={{ 
 backgroundColor: 'var(--gray-200)', 
 height: '60px', 
 marginBottom: 'var(--space-4)',
 borderRadius: 'var(--radius)',
 animation: 'pulse 1.5s ease-in-out infinite'
 }}></div>
 <div style={{ 
 backgroundColor: 'var(--gray-200)', 
 height: '20px', 
 marginBottom: 'var(--space-2)',
 borderRadius: 'var(--radius)',
 animation: 'pulse 1.5s ease-in-out infinite'
 }}></div>
 </div>
 ))}
 </div>
 </div>
 );
 }

 if (error) {
 return (
 <div className="alert alert-error" style={{ marginBottom: 'var(--space-8)' }}>
 <h3>KPI Loading Error</h3>
 <p>{error}</p>
 <button className="btn btn-primary" onClick={fetchKPIs} style={{ marginTop: 'var(--space-4)' }}>
 Retry
 </button>
 </div>
 );
 }

 return (
 <div className="kpi-cards" style={{ marginBottom: 'var(--space-8)' }}>
 <div className="card-header" style={{ marginBottom: 'var(--space-4)' }}>
 <h3 className="card-title">
 Key Performance Indicators
 </h3>
 </div>

 <div className="grid grid-3">
 {kpiCards.map((kpi, index) => (
 <div key={index} className="metric">
 {/* Icon */}
 <div style={{ 
 fontSize: '1.5rem', 
 fontWeight: 'bold',
 fontFamily: 'var(--font-mono)',
 marginBottom: 'var(--space-3)',
 color: kpi.color
 }}>
 {kpi.icon}
 </div>

 {/* Value */}
 <div className="metric-value" style={{ color: kpi.color }}>
 {formatValue(kpi.value, kpi.format)}
 </div>

 {/* Title */}
 <div className="metric-label">
 {kpi.title}
 </div>

 {/* Subtitle */}
 {kpi.subtitle && (
 <div className="text-xs text-gray-500" style={{ marginTop: 'var(--space-1)' }}>
 {kpi.subtitle}
 </div>
 )}

 {/* Trend */}
 <div className="metric-change" style={{ 
 color: getTrendColor(kpi.trend),
 display: 'flex', 
 alignItems: 'center', 
 justifyContent: 'center',
 gap: 'var(--space-1)',
 marginTop: 'var(--space-2)'
 }}>
 <span>{getTrendIcon(kpi.trend)}</span>
 <span className="text-xs font-semibold">
 {kpi.trend || 'STABLE'}
 </span>
 </div>
 </div>
 ))}
 </div>

 {/* Summary Alert */}
 <div className={`alert ${
 kpis.reconciliation_accuracy >= 90 ? 'alert-success' : 
 kpis.reconciliation_accuracy >= 70 ? 'alert-warning' : 'alert-error'
 }`} style={{ marginTop: 'var(--space-6)' }}>
 <div className="font-semibold" style={{ marginBottom: 'var(--space-2)' }}>
 System Status: {
 kpis.reconciliation_accuracy >= 90 ? 'Excellent' :
 kpis.reconciliation_accuracy >= 70 ? 'Attention Needed' : 'Critical'
 }
 </div>
 <div className="text-sm font-mono">
 {kpis.total_transactions_today} transactions processed today with {kpis.reconciliation_accuracy}% accuracy
 {kpis.pending_transactions > 0 && ` • ${kpis.pending_transactions} pending reconciliation`}
 {kpis.delayed_transactions > 0 && ` • ${kpis.delayed_transactions} delayed transactions`}
 </div>
 </div>
 </div>
 );
};

export default KPICards;
