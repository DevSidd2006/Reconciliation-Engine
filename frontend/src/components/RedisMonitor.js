const RedisMonitor = ({ redisStats }) => {
 if (!redisStats || redisStats.status !== 'CONNECTED') {
 return (
 <div className="card" style={{ marginBottom: '32px' }}>
 <div className="card-header">
 <h3 className="card-title">REDIS CACHE STATUS</h3>
 </div>
 <div style={{ textAlign: 'center', padding: '40px', fontFamily: 'var(--font-mono)' }}>
 <div style={{ color: 'var(--error-red)', fontWeight: '700', fontSize: '1.2rem' }}>
 REDIS DISCONNECTED
 </div>
 <p style={{ marginTop: '16px', color: 'var(--gray-800)' }}>
 Cache performance monitoring unavailable
 </p>
 </div>
 </div>
 );
 }

 const { performance = {}, banking_metrics = {} } = redisStats;
 const { inflight_transactions = {} } = banking_metrics;

 const getCacheHealthColor = (hitRatio) => {
 if (hitRatio >= 80) return 'var(--success-green)';
 if (hitRatio >= 60) return 'var(--accent-orange)';
 return 'var(--error-red)';
 };

 const formatUptime = (seconds) => {
 const hours = Math.floor(seconds / 3600);
 const minutes = Math.floor((seconds % 3600) / 60);
 return `${hours}h ${minutes}m`;
 };

 return (
 <div className="card" style={{ marginBottom: '32px' }}>
 <div className="card-header">
 <h3 className="card-title">REDIS CACHE PERFORMANCE</h3>
 </div>
 
 <div className="grid grid-4">
 {/* Cache Hit Ratio */}
 <div className="metric">
 <span 
 className="metric-value" 
 style={{ 
 color: getCacheHealthColor(performance.cache_hit_ratio || 0),
 fontSize: '2.5rem'
 }}
 >
 {performance.cache_hit_ratio || 0}%
 </span>
 <span className="metric-label">Cache Hit Ratio</span>
 </div>

 {/* Memory Usage */}
 <div className="metric">
 <span className="metric-value" style={{ fontSize: '2rem' }}>
 {performance.memory_usage || '0B'}
 </span>
 <span className="metric-label">Memory Usage</span>
 </div>

 {/* Connected Clients */}
 <div className="metric">
 <span className="metric-value" style={{ fontSize: '2.5rem' }}>
 {performance.connected_clients || 0}
 </span>
 <span className="metric-label">Active Connections</span>
 </div>

 {/* Uptime */}
 <div className="metric">
 <span className="metric-value" style={{ fontSize: '1.5rem' }}>
 {formatUptime(performance.uptime_seconds || 0)}
 </span>
 <span className="metric-label">Redis Uptime</span>
 </div>
 </div>

 {/* Banking-Specific Metrics */}
 <div style={{ marginTop: '24px', borderTop: '3px solid var(--primary-black)', paddingTop: '16px' }}>
 <h4 style={{ marginBottom: '16px', color: 'var(--primary-black)' }}>
 BANKING CACHE METRICS
 </h4>
 
 <div className="grid grid-4">
 {/* In-Flight Transactions by Source */}
 <div className="metric">
 <span 
 className="metric-value" 
 style={{ 
 color: 'var(--accent-blue)',
 fontSize: '2rem'
 }}
 >
 {inflight_transactions.core || 0}
 </span>
 <span className="metric-label">Core Banking</span>
 </div>

 <div className="metric">
 <span 
 className="metric-value" 
 style={{ 
 color: 'var(--accent-magenta)',
 fontSize: '2rem'
 }}
 >
 {inflight_transactions.gateway || 0}
 </span>
 <span className="metric-label">Payment Gateway</span>
 </div>

 <div className="metric">
 <span 
 className="metric-value" 
 style={{ 
 color: 'var(--accent-cyan)',
 fontSize: '2rem'
 }}
 >
 {inflight_transactions.mobile || 0}
 </span>
 <span className="metric-label">Mobile App</span>
 </div>

 <div className="metric">
 <span 
 className="metric-value" 
 style={{ 
 color: 'var(--primary-black)',
 fontSize: '2rem'
 }}
 >
 {inflight_transactions.total || 0}
 </span>
 <span className="metric-label">Total In-Flight</span>
 </div>
 </div>
 </div>

 {/* Performance Indicators */}
 <div style={{ marginTop: '24px', borderTop: '3px solid var(--primary-black)', paddingTop: '16px' }}>
 <h4 style={{ marginBottom: '16px', color: 'var(--primary-black)' }}>
 PERFORMANCE INDICATORS
 </h4>
 
 <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem' }}>
 <div style={{ 
 display: 'flex', 
 justifyContent: 'space-between', 
 marginBottom: '12px',
 padding: '8px 12px',
 backgroundColor: 'var(--gray-100)',
 border: '2px solid var(--primary-black)'
 }}>
 <span><strong>Total Commands Processed:</strong></span>
 <span style={{ fontWeight: '700' }}>
 {(performance.total_commands || 0).toLocaleString()}
 </span>
 </div>
 
 <div style={{ 
 display: 'flex', 
 justifyContent: 'space-between', 
 marginBottom: '12px',
 padding: '8px 12px',
 backgroundColor: performance.cache_hit_ratio >= 80 ? 'var(--success-green)' : 
 performance.cache_hit_ratio >= 60 ? 'var(--accent-orange)' : 'var(--error-red)',
 color: 'var(--primary-white)',
 border: '2px solid var(--primary-black)'
 }}>
 <span><strong>Cache Performance:</strong></span>
 <span style={{ fontWeight: '700' }}>
 {performance.cache_hit_ratio >= 80 ? 'EXCELLENT' : 
 performance.cache_hit_ratio >= 60 ? 'GOOD' : 'NEEDS OPTIMIZATION'}
 </span>
 </div>

 <div style={{ 
 display: 'flex', 
 justifyContent: 'space-between', 
 padding: '8px 12px',
 backgroundColor: inflight_transactions.total > 100 ? 'var(--accent-orange)' : 'var(--success-green)',
 color: inflight_transactions.total > 100 ? 'var(--primary-black)' : 'var(--primary-white)',
 border: '2px solid var(--primary-black)'
 }}>
 <span><strong>Transaction Load:</strong></span>
 <span style={{ fontWeight: '700' }}>
 {inflight_transactions.total > 100 ? 'HIGH VOLUME' : 'NORMAL'}
 </span>
 </div>
 </div>
 </div>
 </div>
 );
};

export default RedisMonitor;
