import { useState, useEffect } from 'react';
import axios from 'axios';

const AnomalyAlerts = () => {
 const [anomalies, setAnomalies] = useState([]);
 const [systemHealth, setSystemHealth] = useState('HEALTHY');
 const [loading, setLoading] = useState(true);
 const [error, setError] = useState(null);
 const [dismissed, setDismissed] = useState(new Set());

 const fetchAnomalies = async () => {
 try {
 setLoading(true);
 const response = await axios.get('/api/analytics/anomalies');
 
 setAnomalies(response.data.anomalies || []);
 setSystemHealth(response.data.system_health || 'HEALTHY');
 setError(null);
 } catch (err) {
 console.error('Error fetching anomalies:', err);
 setError('Failed to load anomaly data');
 } finally {
 setLoading(false);
 }
 };

 useEffect(() => {
 fetchAnomalies();
 
 // Auto-refresh every 30 seconds for real-time anomaly detection
 const interval = setInterval(fetchAnomalies, 30000);
 return () => clearInterval(interval);
 }, []);

 // Listen for dashboard refresh events
 useEffect(() => {
 const handleRefresh = () => fetchAnomalies();
 window.addEventListener('dashboardRefresh', handleRefresh);
 return () => window.removeEventListener('dashboardRefresh', handleRefresh);
 }, []);

 const handleDismiss = (anomalyIndex) => {
 setDismissed(prev => new Set([...prev, anomalyIndex]));
 };

 const getAnomalyIcon = (type) => {
 switch (type) {
 case 'TRANSACTION_SPIKE': return 'TREND';
 case 'MISMATCH_SPIKE': return 'ALERT';
 case 'SOURCE_DELAY': return 'TIME';
 case 'SYSTEM_ERROR': return '';
 case 'UNUSUAL_PATTERN': return '';
 default: return 'WARN';
 }
 };

 const getSeverityColor = (severity) => {
 switch (severity) {
 case 'HIGH': return 'var(--error-red)';
 case 'MEDIUM': return 'var(--accent-orange)';
 case 'LOW': return 'var(--pending-yellow)';
 default: return 'var(--gray-600)';
 }
 };

 const getSystemHealthColor = (health) => {
 switch (health) {
 case 'HEALTHY': return 'var(--success-green)';
 case 'ATTENTION_REQUIRED': return 'var(--accent-orange)';
 case 'CRITICAL': return 'var(--error-red)';
 default: return 'var(--gray-600)';
 }
 };

 const getSystemHealthIcon = (health) => {
 switch (health) {
 case 'HEALTHY': return 'OK';
 case 'ATTENTION_REQUIRED': return 'WARN';
 case 'CRITICAL': return 'ALERT';
 default: return '';
 }
 };

 const visibleAnomalies = anomalies.filter((_, index) => !dismissed.has(index));

 if (loading) {
 return (
 <div className="anomaly-alerts" style={{ marginBottom: '24px' }}>
 <div className="card">
 <div style={{ padding: '24px', textAlign: 'center' }}>
 <div style={{ fontFamily: 'var(--font-mono)' }}>
 SYNC Scanning for anomalies...
 </div>
 </div>
 </div>
 </div>
 );
 }

 if (error) {
 return (
 <div className="anomaly-alerts" style={{ marginBottom: '24px' }}>
 <div className="alert alert-error">
 <h3>ERR Anomaly Detection Error</h3>
 <p>{error}</p>
 <button onClick={fetchAnomalies} className="btn btn-primary" style={{ marginTop: '16px' }}>
 SYNC Retry
 </button>
 </div>
 </div>
 );
 }

 return (
 <div className="anomaly-alerts" style={{ marginBottom: '24px' }}>
 {/* System Health Status */}
 <div className="card" style={{ marginBottom: '16px' }}>
 <div style={{
 padding: '16px 24px',
 backgroundColor: getSystemHealthColor(systemHealth),
 color: systemHealth === 'HEALTHY' ? 'var(--primary-black)' : 'var(--primary-white)',
 display: 'flex',
 justifyContent: 'space-between',
 alignItems: 'center'
 }}>
 <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
 <span style={{ fontSize: '1.5rem' }}>
 {getSystemHealthIcon(systemHealth)}
 </span>
 <div>
 <div style={{ fontWeight: '800', fontSize: '1.1rem' }}>
 SYSTEM HEALTH: {systemHealth}
 </div>
 <div style={{ fontSize: '0.875rem', fontFamily: 'var(--font-mono)' }}>
 {visibleAnomalies.length} active anomalies detected
 </div>
 </div>
 </div>
 <div style={{ fontSize: '0.875rem', fontFamily: 'var(--font-mono)' }}>
 Last scan: {new Date().toLocaleTimeString()}
 </div>
 </div>
 </div>

 {/* Anomaly Alerts */}
 {visibleAnomalies.length > 0 ? (
 <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
 {visibleAnomalies.map((anomaly, index) => (
 <div
 key={index}
 className="alert"
 style={{
 backgroundColor: getSeverityColor(anomaly.severity),
 color: anomaly.severity === 'LOW' ? 'var(--primary-black)' : 'var(--primary-white)',
 padding: '16px 24px',
 border: '3px solid var(--primary-black)',
 position: 'relative'
 }}
 >
 {/* Dismiss button */}
 <button
 onClick={() => handleDismiss(index)}
 style={{
 position: 'absolute',
 top: '8px',
 right: '8px',
 background: 'none',
 border: 'none',
 color: 'inherit',
 fontSize: '1.2rem',
 cursor: 'pointer',
 padding: '4px',
 opacity: 0.7
 }}
 title="Dismiss alert"
 >
 
 </button>

 <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
 <span style={{ fontSize: '1.5rem' }}>
 {getAnomalyIcon(anomaly.type)}
 </span>
 <div>
 <div style={{ fontWeight: '800', fontSize: '1rem' }}>
 {anomaly.severity} SEVERITY ANOMALY
 </div>
 <div style={{ fontSize: '0.875rem', fontFamily: 'var(--font-mono)' }}>
 Type: {anomaly.type?.replace('_', ' ')}
 </div>
 </div>
 </div>

 <div style={{ fontSize: '0.875rem', marginBottom: '8px' }}>
 <strong>Description:</strong> {anomaly.description}
 </div>

 <div style={{ 
 display: 'flex', 
 justifyContent: 'space-between', 
 alignItems: 'center',
 fontSize: '0.75rem',
 fontFamily: 'var(--font-mono)'
 }}>
 <div>
 Detected: {new Date(anomaly.detected_at).toLocaleString()}
 </div>
 {anomaly.source && (
 <div>
 Source: <strong>{anomaly.source.toUpperCase()}</strong>
 </div>
 )}
 </div>

 {/* Action buttons for high severity anomalies */}
 {anomaly.severity === 'HIGH' && (
 <div style={{ marginTop: '12px', display: 'flex', gap: '8px' }}>
 <button
 className="btn"
 style={{
 backgroundColor: 'var(--primary-white)',
 color: 'var(--primary-black)',
 padding: '4px 12px',
 fontSize: '0.75rem',
 fontWeight: '700'
 }}
 >
 ALERT Escalate
 </button>
 <button
 className="btn"
 style={{
 backgroundColor: 'var(--primary-white)',
 color: 'var(--primary-black)',
 padding: '4px 12px',
 fontSize: '0.75rem',
 fontWeight: '700'
 }}
 >
 Notify Team
 </button>
 </div>
 )}
 </div>
 ))}
 </div>
 ) : (
 <div className="card">
 <div style={{ 
 padding: '24px', 
 textAlign: 'center',
 backgroundColor: 'var(--success-green)',
 color: 'var(--primary-white)'
 }}>
 <div style={{ fontSize: '2rem', marginBottom: '8px' }}>OK</div>
 <div style={{ fontWeight: '800', fontSize: '1.1rem', marginBottom: '4px' }}>
 NO ANOMALIES DETECTED
 </div>
 <div style={{ fontSize: '0.875rem', fontFamily: 'var(--font-mono)' }}>
 System operating within normal parameters
 </div>
 </div>
 </div>
 )}

 {/* Anomaly Detection Info */}
 <div className="card" style={{ marginTop: '16px' }}>
 <div style={{ 
 padding: '16px 24px',
 backgroundColor: 'var(--gray-50)',
 borderTop: '2px solid var(--gray-200)'
 }}>
 <div style={{ fontSize: '0.875rem', color: 'var(--gray-600)' }}>
 <strong> Anomaly Detection:</strong> Continuously monitoring for transaction spikes, 
 mismatch increases, source delays, and unusual patterns. 
 Auto-refresh every 30 seconds.
 </div>
 
 <div style={{ 
 marginTop: '12px', 
 display: 'flex', 
 gap: '20px', 
 fontSize: '0.75rem',
 fontFamily: 'var(--font-mono)'
 }}>
 <div>HIGH HIGH: Immediate attention required</div>
 <div>MED MEDIUM: Monitor closely</div>
 <div>LOW LOW: Informational</div>
 </div>
 </div>
 </div>
 </div>
 );
};

export default AnomalyAlerts;
