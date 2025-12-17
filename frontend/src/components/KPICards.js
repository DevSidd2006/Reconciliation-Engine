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
      icon: '💳',
      color: 'var(--accent-blue)',
      trend: trends.transactions_vs_yesterday,
      format: 'number'
    },
    {
      title: 'Total Transactions (All Time)',
      value: kpis.total_transactions_all_time,
      icon: '🏦',
      color: 'var(--accent-cyan)',
      trend: 'up',
      format: 'number'
    },
    {
      title: 'Total Mismatches',
      value: kpis.total_mismatches,
      icon: '🚨',
      color: 'var(--error-red)',
      trend: trends.mismatches_vs_yesterday,
      format: 'number'
    },
    {
      title: 'Reconciliation Accuracy',
      value: kpis.reconciliation_accuracy,
      icon: '🎯',
      color: kpis.reconciliation_accuracy >= 90 ? 'var(--success-green)' : 
             kpis.reconciliation_accuracy >= 70 ? 'var(--warning-orange)' : 'var(--error-red)',
      trend: trends.accuracy_trend,
      format: 'percentage'
    },
    {
      title: 'Pending Transactions',
      value: kpis.pending_transactions,
      icon: '⏳',
      color: 'var(--warning-orange)',
      trend: 'stable',
      format: 'number'
    },
    {
      title: 'Duplicates Detected',
      value: kpis.duplicates_detected,
      icon: '🔄',
      color: 'var(--accent-magenta)',
      trend: 'stable',
      format: 'number'
    },
    {
      title: 'Delayed Transactions',
      value: kpis.delayed_transactions,
      icon: '⏰',
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
      case 'up': return '📈';
      case 'down': return '📉';
      case 'stable': return '➡️';
      default: return '➡️';
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
      <div className="kpi-cards-loading" style={{ marginBottom: '32px' }}>
        <div className="grid grid-3">
          {[1, 2, 3, 4, 5, 6, 7].map(i => (
            <div key={i} className="card" style={{ padding: '24px', textAlign: 'center' }}>
              <div style={{ 
                backgroundColor: 'var(--gray-200)', 
                height: '60px', 
                marginBottom: '16px',
                animation: 'pulse 1.5s ease-in-out infinite'
              }}></div>
              <div style={{ 
                backgroundColor: 'var(--gray-200)', 
                height: '20px', 
                marginBottom: '8px',
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
      <div className="alert alert-error" style={{ marginBottom: '32px' }}>
        <h3>❌ KPI Loading Error</h3>
        <p>{error}</p>
        <button className="btn btn-primary" onClick={fetchKPIs} style={{ marginTop: '16px' }}>
          🔄 Retry
        </button>
      </div>
    );
  }

  return (
    <div className="kpi-cards" style={{ marginBottom: '32px' }}>
      <div className="card-header" style={{ marginBottom: '16px' }}>
        <h3 className="card-title">📊 KEY PERFORMANCE INDICATORS</h3>
      </div>

      <div className="grid grid-3">
        {kpiCards.map((kpi, index) => (
          <div key={index} className="card kpi-card" style={{ 
            textAlign: 'center',
            padding: '24px',
            position: 'relative',
            overflow: 'hidden'
          }}>
            {/* Background accent */}
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '4px',
              backgroundColor: kpi.color
            }}></div>

            {/* Icon */}
            <div style={{ 
              fontSize: '3rem', 
              marginBottom: '16px',
              filter: 'drop-shadow(2px 2px 0px var(--primary-black))'
            }}>
              {kpi.icon}
            </div>

            {/* Value */}
            <div style={{ 
              fontSize: '2.5rem', 
              fontWeight: '800', 
              color: kpi.color,
              marginBottom: '8px',
              fontFamily: 'var(--font-mono)'
            }}>
              {formatValue(kpi.value, kpi.format)}
            </div>

            {/* Title */}
            <div style={{ 
              fontSize: '0.875rem', 
              fontWeight: '700',
              color: 'var(--primary-black)',
              marginBottom: '8px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              {kpi.title}
            </div>

            {/* Subtitle */}
            {kpi.subtitle && (
              <div style={{ 
                fontSize: '0.75rem', 
                color: 'var(--gray-600)',
                fontFamily: 'var(--font-mono)',
                marginBottom: '8px'
              }}>
                {kpi.subtitle}
              </div>
            )}

            {/* Trend */}
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              gap: '4px',
              fontSize: '0.75rem',
              color: getTrendColor(kpi.trend),
              fontWeight: '700'
            }}>
              <span>{getTrendIcon(kpi.trend)}</span>
              <span style={{ textTransform: 'uppercase' }}>
                {kpi.trend || 'STABLE'}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Summary Alert */}
      <div className="kpi-summary" style={{ 
        marginTop: '24px',
        padding: '16px',
        backgroundColor: kpis.reconciliation_accuracy >= 90 ? 'var(--success-green)' : 
                         kpis.reconciliation_accuracy >= 70 ? 'var(--warning-orange)' : 'var(--error-red)',
        color: 'var(--primary-white)',
        border: '3px solid var(--primary-black)',
        textAlign: 'center'
      }}>
        <div style={{ fontWeight: '800', fontSize: '1.1rem', marginBottom: '8px' }}>
          🏦 SYSTEM STATUS: {
            kpis.reconciliation_accuracy >= 90 ? '✅ EXCELLENT' :
            kpis.reconciliation_accuracy >= 70 ? '⚠️ ATTENTION NEEDED' : '🚨 CRITICAL'
          }
        </div>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem' }}>
          {kpis.total_transactions_today} transactions processed today with {kpis.reconciliation_accuracy}% accuracy
          {kpis.pending_transactions > 0 && ` • ${kpis.pending_transactions} pending reconciliation`}
          {kpis.delayed_transactions > 0 && ` • ${kpis.delayed_transactions} delayed transactions`}
        </div>
      </div>
    </div>
  );
};

export default KPICards;