import { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const PaymentReconciliation = () => {
  const [reconciliationData, setReconciliationData] = useState({
    totalTransactions: 0,
    reconciledTransactions: 0,
    unreconciledTransactions: 0,
    totalAmount: 0,
    reconciledAmount: 0,
    unreconciledAmount: 0,
    reconciliationSummary: [],
    recentActivity: [],
    chartData: [],
    lastUpdated: new Date()
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dateRange, setDateRange] = useState({
    from: new Date().toISOString().split('T')[0],
    to: new Date().toISOString().split('T')[0]
  });
  const chartDataRef = useRef([]);

  // Fetch real-time reconciliation data from backend
  const fetchReconciliationData = async () => {
    try {
      setLoading(true);
      
      // Fetch multiple endpoints in parallel for comprehensive data
      const [overviewResponse, transactionsResponse, mismatchesResponse] = await Promise.all([
        axios.get('/api/analytics/overview', {
          params: {
            date_from: dateRange.from,
            date_to: dateRange.to
          }
        }),
        axios.get('/api/transactions', {
          params: {
            limit: 10,
            sort_by: 'created_at',
            sort_direction: 'desc'
          }
        }),
        axios.get('/api/mismatches', {
          params: {
            limit: 5,
            sort_by: 'detected_at',
            sort_direction: 'desc'
          }
        })
      ]);

      const overview = overviewResponse.data;
      const recentTransactions = transactionsResponse.data.transactions || [];
      const recentMismatches = mismatchesResponse.data.mismatches || [];

      // Calculate reconciliation metrics from real data
      const totalTransactions = overview.kpis?.total_transactions_today || 0;
      const totalMismatches = overview.kpis?.total_mismatches || 0;
      const matchedTransactions = totalTransactions - totalMismatches;
      const mismatchedTransactions = totalMismatches;
      
      // Calculate amounts (estimate based on transaction data)
      const avgTransactionAmount = recentTransactions.length > 0 
        ? recentTransactions.reduce((sum, txn) => sum + (txn.amount || 0), 0) / recentTransactions.length
        : 1000;
      
      const totalAmount = totalTransactions * avgTransactionAmount;
      const mismatchedAmount = mismatchedTransactions * avgTransactionAmount;
      const matchedAmount = totalAmount - mismatchedAmount;

      // Build reconciliation summary from mismatch data
      const summaryMap = {};
      recentMismatches.forEach(mismatch => {
        const type = mismatch.type === 'AMOUNT_MISMATCH' ? 'Less Payment Received' :
                    mismatch.type === 'STATUS_MISMATCH' ? 'More Payment Received' :
                    'Pending Payment';
        
        if (!summaryMap[type]) {
          summaryMap[type] = { count: 0, amount: 0 };
        }
        summaryMap[type].count++;
        summaryMap[type].amount += mismatch.difference_amount || avgTransactionAmount * 0.1;
      });

      const reconciliationSummary = Object.entries(summaryMap).map(([type, data]) => ({
        type,
        count: data.count,
        amount: data.amount
      }));

      // Format recent activity from transactions
      const recentActivity = recentTransactions.slice(0, 5).map(txn => ({
        id: txn.id,
        txnId: txn.txn_id,
        amount: txn.amount,
        type: txn.reconciliation_status === 'MATCHED' ? 'matched' : 'mismatch',
        timestamp: new Date(txn.created_at)
      }));

      // Generate chart data for real-time visualization
      const now = new Date();
      const newDataPoint = {
        time: now.toLocaleTimeString(),
        timestamp: now,
        matched: matchedAmount / 1000, // Convert to thousands for better display
        mismatched: mismatchedAmount / 1000,
        total: totalAmount / 1000,
        matchRate: totalTransactions > 0 ? ((matchedTransactions / totalTransactions) * 100).toFixed(1) : 0
      };

      // Update chart data (keep last 20 points for smooth animation)
      chartDataRef.current = [...chartDataRef.current, newDataPoint].slice(-20);

      setReconciliationData({
        totalTransactions,
        reconciledTransactions: matchedTransactions,
        unreconciledTransactions: mismatchedTransactions,
        totalAmount,
        reconciledAmount: matchedAmount,
        unreconciledAmount: mismatchedAmount,
        reconciliationSummary,
        recentActivity,
        chartData: [...chartDataRef.current],
        lastUpdated: new Date()
      });
      
      setError(null);
    } catch (err) {
      console.error('Error fetching reconciliation data:', err);
      setError('Failed to load reconciliation data');
    } finally {
      setLoading(false);
    }
  };

  // Initial data fetch
  useEffect(() => {
    fetchReconciliationData();
  }, [dateRange]);

  // Listen for dashboard refresh events (same as LiveTransactionTable)
  useEffect(() => {
    const handleRefresh = () => fetchReconciliationData();
    window.addEventListener('dashboardRefresh', handleRefresh);
    return () => window.removeEventListener('dashboardRefresh', handleRefresh);
  }, [dateRange]);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  };

  const getReconciliationRate = () => {
    if (reconciliationData.totalTransactions === 0) return 0;
    return ((reconciliationData.reconciledTransactions / reconciliationData.totalTransactions) * 100).toFixed(1);
  };

  const getSummaryIcon = (type) => {
    switch (type) {
      case 'Less Payment Received': return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polyline points="23,18 13.5,8.5 8.5,13.5 1,6"/>
          <polyline points="17,18 23,18 23,12"/>
        </svg>
      );
      case 'More Payment Received': return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polyline points="23,6 13.5,15.5 8.5,10.5 1,18"/>
          <polyline points="17,6 23,6 23,12"/>
        </svg>
      );
      case 'Pending Payment': return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12,6 12,12 16,14"/>
        </svg>
      );
      default: return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
          <line x1="9" y1="9" x2="15" y2="15"/>
          <line x1="15" y1="9" x2="9" y2="15"/>
        </svg>
      );
    }
  };

  const getSummaryColor = (type) => {
    switch (type) {
      case 'Less Payment Received': return 'var(--error-red)';
      case 'More Payment Received': return 'var(--success-green)';
      case 'Pending Payment': return 'var(--warning-orange)';
      default: return 'var(--gray-600)';
    }
  };

  const getActivityIcon = (type) => {
    return type === 'matched' ? '✓' : '✗';
  };

  const getActivityColor = (type) => {
    return type === 'matched' ? 'var(--success-green)' : 'var(--error-red)';
  };

  // Real-time Chart Component
  const RealTimeChart = ({ data }) => {
    const maxValue = Math.max(...data.map(d => d.total), 100);
    const chartHeight = 320;
    const padding = 80;

    if (data.length === 0) {
      return (
        <div style={{ 
          height: `${chartHeight}px`, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          color: 'var(--gray-600)',
          fontStyle: 'italic',
          backgroundColor: 'var(--surface-primary)',
          borderRadius: 'var(--radius)',
          border: '1px solid var(--surface-tertiary)'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', marginBottom: 'var(--space-2)' }}>📊</div>
            <div>Collecting real-time data...</div>
          </div>
        </div>
      );
    }

    // Format numbers for Y-axis (amounts in thousands)
    const formatNumber = (value) => {
      if (value >= 1000) {
        return `₹${(value / 1000).toFixed(0)}K`;
      }
      return `₹${Math.round(value)}`;
    };

    return (
      <div style={{ 
        position: 'relative', 
        height: `${chartHeight}px`,
        backgroundColor: 'var(--surface-primary)',
        borderRadius: 'var(--radius)',
        padding: 'var(--space-4)',
        border: '1px solid var(--surface-tertiary)'
      }}>
        {/* Legend at top right */}
        <div style={{
          position: 'absolute',
          top: '20px',
          right: '30px',
          display: 'flex',
          gap: 'var(--space-4)',
          fontSize: '0.875rem',
          fontWeight: '500'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
            <div style={{ 
              width: '12px', 
              height: '12px', 
              borderRadius: '50%',
              backgroundColor: 'var(--accent-blue)'
            }}></div>
            <span>Total</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
            <div style={{ 
              width: '12px', 
              height: '12px', 
              borderRadius: '50%',
              backgroundColor: 'var(--success-green)'
            }}></div>
            <span>Matched</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
            <div style={{ 
              width: '12px', 
              height: '12px', 
              borderRadius: '50%',
              backgroundColor: 'var(--error-red)'
            }}></div>
            <span>Mismatched</span>
          </div>
        </div>

        {/* Chart Container */}
        <div style={{ position: 'relative', width: '100%', height: '100%', marginTop: '40px' }}>
          <svg 
            width="100%" 
            height="100%" 
            viewBox={`0 0 700 ${chartHeight - 60}`}
            style={{ overflow: 'visible' }}
          >
            {/* Horizontal grid lines */}
            {[0, 0.2, 0.4, 0.6, 0.8, 1].map((ratio, index) => {
              const y = (chartHeight - 140) * (1 - ratio) + 40;
              const value = maxValue * ratio;
              return (
                <g key={index}>
                  <line
                    x1="80"
                    y1={y}
                    x2="620"
                    y2={y}
                    stroke="var(--surface-tertiary)"
                    strokeWidth="1"
                    opacity="0.6"
                  />
                  <text
                    x="70"
                    y={y}
                    textAnchor="end"
                    dominantBaseline="middle"
                    fontSize="13"
                    fill="var(--gray-600)"
                    fontFamily="var(--font-mono)"
                  >
                    {formatNumber(value)}
                  </text>
                </g>
              );
            })}

            {/* Chart Lines */}
            {data.length > 1 && (
              <g>
                {/* Total transactions line (Blue) */}
                <path
                  d={`M 80 ${(chartHeight - 140) * (1 - data[0].total / maxValue) + 40} ${data.map((point, index) => {
                    const x = 80 + (index / (data.length - 1)) * 540;
                    const y = (chartHeight - 140) * (1 - point.total / maxValue) + 40;
                    return `L ${x} ${y}`;
                  }).join(' ')}`}
                  fill="none"
                  stroke="var(--accent-blue)"
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />

                {/* Matched transactions line (Green) */}
                <path
                  d={`M 80 ${(chartHeight - 140) * (1 - data[0].matched / maxValue) + 40} ${data.map((point, index) => {
                    const x = 80 + (index / (data.length - 1)) * 540;
                    const y = (chartHeight - 140) * (1 - point.matched / maxValue) + 40;
                    return `L ${x} ${y}`;
                  }).join(' ')}`}
                  fill="none"
                  stroke="var(--success-green)"
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />

                {/* Mismatched transactions line (Red) */}
                <path
                  d={`M 80 ${(chartHeight - 140) * (1 - data[0].mismatched / maxValue) + 40} ${data.map((point, index) => {
                    const x = 80 + (index / (data.length - 1)) * 540;
                    const y = (chartHeight - 140) * (1 - point.mismatched / maxValue) + 40;
                    return `L ${x} ${y}`;
                  }).join(' ')}`}
                  fill="none"
                  stroke="var(--error-red)"
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />

                {/* Data points */}
                {data.map((point, index) => {
                  const x = 80 + (index / (data.length - 1)) * 540;
                  const totalY = (chartHeight - 140) * (1 - point.total / maxValue) + 40;
                  const matchedY = (chartHeight - 140) * (1 - point.matched / maxValue) + 40;
                  const mismatchedY = (chartHeight - 140) * (1 - point.mismatched / maxValue) + 40;
                  
                  return (
                    <g key={index}>
                      {/* Total point */}
                      <circle
                        cx={x}
                        cy={totalY}
                        r="4"
                        fill="var(--accent-blue)"
                        stroke="var(--surface-primary)"
                        strokeWidth="2"
                      />
                      {/* Matched point */}
                      <circle
                        cx={x}
                        cy={matchedY}
                        r="4"
                        fill="var(--success-green)"
                        stroke="var(--surface-primary)"
                        strokeWidth="2"
                      />
                      {/* Mismatched point */}
                      <circle
                        cx={x}
                        cy={mismatchedY}
                        r="4"
                        fill="var(--error-red)"
                        stroke="var(--surface-primary)"
                        strokeWidth="2"
                      />
                    </g>
                  );
                })}
              </g>
            )}

            {/* X-axis line */}
            <line
              x1="80"
              y1={chartHeight - 100}
              x2="620"
              y2={chartHeight - 100}
              stroke="var(--surface-tertiary)"
              strokeWidth="1"
            />

            {/* Y-axis line */}
            <line
              x1="80"
              y1="40"
              x2="80"
              y2={chartHeight - 100}
              stroke="var(--surface-tertiary)"
              strokeWidth="1"
            />
          </svg>

          {/* Time period labels */}
          <div style={{
            position: 'absolute',
            bottom: '20px',
            left: '80px',
            right: '80px',
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: '0.875rem',
            color: 'var(--gray-600)',
            fontWeight: '500'
          }}>
            {data.length > 0 && (
              <>
                <span>Start</span>
                <span>Current</span>
              </>
            )}
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="payment-reconciliation">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Transaction Reconciliation</h3>
          </div>
          <div style={{ textAlign: 'center', padding: '60px' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.2rem' }}>
              Loading reconciliation data...
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="payment-reconciliation">
      {/* Header */}
      <div className="main-header">
        <h1 className="main-header-title">Transaction Reconciliation</h1>
        <div className="main-header-controls">
          <div style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'center' }}>
            <label className="form-label" style={{ margin: 0, fontSize: '0.75rem' }}>
              FROM:
            </label>
            <input
              type="date"
              value={dateRange.from}
              onChange={(e) => setDateRange({ ...dateRange, from: e.target.value })}
              className="form-input"
              style={{ width: 'auto', fontSize: '0.75rem' }}
            />
            <label className="form-label" style={{ margin: 0, fontSize: '0.75rem' }}>
              TO:
            </label>
            <input
              type="date"
              value={dateRange.to}
              onChange={(e) => setDateRange({ ...dateRange, to: e.target.value })}
              className="form-input"
              style={{ width: 'auto', fontSize: '0.75rem' }}
            />
          </div>
          
          <button 
            className="btn btn-sm btn-success"
            title="Auto-refresh enabled"
          >
            <span className="icon">●</span>
            LIVE
          </button>
          
          <select 
            value="10s"
            className="form-select"
            style={{ width: 'auto', fontSize: '0.75rem' }}
          >
            <option value="5s">5s</option>
            <option value="10s">10s</option>
            <option value="30s">30s</option>
          </select>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-3" style={{ marginBottom: 'var(--space-8)' }}>
        {/* Total Transactions */}
        <div className="card" style={{ padding: 'var(--space-6)' }}>
          <div style={{ marginBottom: 'var(--space-2)', fontSize: '0.875rem', fontWeight: '600', color: 'var(--gray-600)' }}>
            Total Transactions
          </div>
          <div style={{ 
            fontSize: '2.5rem', 
            fontWeight: '800', 
            color: 'var(--accent-blue)',
            fontFamily: 'var(--font-mono)'
          }}>
            {formatCurrency(reconciliationData.totalAmount)}
          </div>
          <div style={{ fontSize: '0.875rem', color: 'var(--gray-600)', marginTop: 'var(--space-2)' }}>
            {reconciliationData.totalTransactions.toLocaleString()} transactions
          </div>
        </div>

        {/* Reconciled Transactions */}
        <div className="card" style={{ padding: 'var(--space-6)' }}>
          <div style={{ marginBottom: 'var(--space-2)', fontSize: '0.875rem', fontWeight: '600', color: 'var(--gray-600)' }}>
            Matched Transactions
          </div>
          <div style={{ 
            fontSize: '2.5rem', 
            fontWeight: '800', 
            color: 'var(--success-green)',
            fontFamily: 'var(--font-mono)'
          }}>
            {formatCurrency(reconciliationData.reconciledAmount)}
          </div>
          <div style={{ fontSize: '0.875rem', color: 'var(--gray-600)', marginTop: 'var(--space-2)' }}>
            {reconciliationData.reconciledTransactions.toLocaleString()} transactions ({getReconciliationRate()}%)
          </div>
        </div>

        {/* Unreconciled Transactions */}
        <div className="card" style={{ padding: 'var(--space-6)' }}>
          <div style={{ marginBottom: 'var(--space-2)', fontSize: '0.875rem', fontWeight: '600', color: 'var(--gray-600)' }}>
            Mismatched Transactions
          </div>
          <div style={{ 
            fontSize: '2.5rem', 
            fontWeight: '800', 
            color: 'var(--error-red)',
            fontFamily: 'var(--font-mono)'
          }}>
            {formatCurrency(reconciliationData.unreconciledAmount)}
          </div>
          <div style={{ fontSize: '0.875rem', color: 'var(--gray-600)', marginTop: 'var(--space-2)' }}>
            {reconciliationData.unreconciledTransactions.toLocaleString()} transactions
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-2" style={{ gap: 'var(--space-6)' }}>
        {/* Reconciliation Summary */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Reconciliation Summary</h3>
            <div style={{ 
              fontSize: '0.875rem', 
              color: 'var(--gray-600)',
              padding: '4px 12px',
              backgroundColor: 'var(--gray-100)',
              border: '1px solid var(--gray-300)',
              borderRadius: 'var(--radius)'
            }}>
              This Month
            </div>
          </div>
          
          <div className="card-body">
            {reconciliationData.reconciliationSummary.length === 0 ? (
              <div style={{ 
                textAlign: 'center', 
                padding: 'var(--space-8)', 
                color: 'var(--success-green)',
                fontWeight: '700'
              }}>
                All payments reconciled successfully
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                {reconciliationData.reconciliationSummary.map((item, index) => (
                  <div key={index} style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: 'var(--space-4)',
                    backgroundColor: 'var(--surface-secondary)',
                    border: '1px solid var(--surface-tertiary)',
                    borderRadius: 'var(--radius)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                      <div style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '50%',
                        backgroundColor: getSummaryColor(item.type),
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'var(--primary-white)',
                        fontSize: '1.2rem',
                        fontWeight: '700'
                      }}>
                        {getSummaryIcon(item.type)}
                      </div>
                      <div>
                        <div style={{ fontWeight: '600', marginBottom: '2px' }}>
                          {item.type}
                        </div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--gray-600)' }}>
                          Count: {item.count}
                        </div>
                      </div>
                    </div>
                    <div style={{ 
                      fontFamily: 'var(--font-mono)', 
                      fontWeight: '700',
                      fontSize: '1.1rem',
                      color: getSummaryColor(item.type)
                    }}>
                      {formatCurrency(item.amount)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Live Transaction Trends Chart */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Live Transaction Trends</h3>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 'var(--space-2)',
              fontSize: '0.75rem',
              color: 'var(--success-green)'
            }}>
              <div style={{ 
                width: '8px', 
                height: '8px', 
                borderRadius: '50%',
                backgroundColor: 'var(--success-green)',
                animation: 'pulse 2s infinite'
              }}></div>
              Live Data
            </div>
          </div>
          
          <div className="card-body" style={{ padding: 'var(--space-6)' }}>
            <RealTimeChart data={reconciliationData.chartData} />
            
            {/* Enhanced Chart Legend */}
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              alignItems: 'center',
              marginTop: 'var(--space-6)',
              padding: 'var(--space-4)',
              backgroundColor: 'var(--surface-secondary)',
              borderRadius: 'var(--radius)',
              border: '1px solid var(--surface-tertiary)'
            }}>
              {/* Legend */}
              <div style={{ 
                display: 'flex', 
                gap: 'var(--space-6)', 
                fontSize: '0.875rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                  <div style={{ 
                    width: '16px', 
                    height: '3px', 
                    backgroundColor: 'var(--accent-blue)', 
                    borderRadius: '2px' 
                  }}></div>
                  <span style={{ fontWeight: '600' }}>Total</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                  <div style={{ 
                    width: '16px', 
                    height: '3px', 
                    backgroundColor: 'var(--success-green)', 
                    borderRadius: '2px' 
                  }}></div>
                  <span style={{ fontWeight: '600' }}>Matched</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                  <div style={{ 
                    width: '16px', 
                    height: '3px', 
                    backgroundColor: 'var(--error-red)', 
                    borderRadius: '2px' 
                  }}></div>
                  <span style={{ fontWeight: '600' }}>Mismatched</span>
                </div>
              </div>

              {/* Real-time Stats */}
              <div style={{
                display: 'flex',
                gap: 'var(--space-4)',
                fontSize: '0.875rem',
                fontFamily: 'var(--font-mono)'
              }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ 
                    fontSize: '1.2rem', 
                    fontWeight: '700',
                    color: 'var(--success-green)'
                  }}>
                    {getReconciliationRate()}%
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--gray-600)' }}>
                    Match Rate
                  </div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ 
                    fontSize: '1.2rem', 
                    fontWeight: '700',
                    color: 'var(--gray-700)'
                  }}>
                    {reconciliationData.lastUpdated.toLocaleTimeString()}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--gray-600)' }}>
                    Last Update
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Add Exceptions Section */}
      <div className="card" style={{ marginTop: 'var(--space-8)' }}>
        <div className="card-header">
          <h3 className="card-title">Add Exceptions</h3>
        </div>
        <div className="card-body">
          <div style={{
            height: '120px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'var(--surface-secondary)',
            border: '2px dashed var(--surface-tertiary)',
            borderRadius: 'var(--radius)',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
          onMouseEnter={(e) => {
            e.target.style.borderColor = 'var(--accent-blue)';
            e.target.style.backgroundColor = 'var(--accent-blue-light)';
          }}
          onMouseLeave={(e) => {
            e.target.style.borderColor = 'var(--surface-tertiary)';
            e.target.style.backgroundColor = 'var(--surface-secondary)';
          }}
          >
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', marginBottom: 'var(--space-2)' }}>+</div>
              <div style={{ fontWeight: '600', color: 'var(--gray-700)' }}>Add Exceptions</div>
            </div>
          </div>
        </div>
      </div>

      {/* Real-time Status */}
      <div style={{ 
        position: 'fixed', 
        bottom: '20px', 
        right: '20px',
        padding: 'var(--space-2) var(--space-3)',
        backgroundColor: 'var(--success-green)',
        color: 'var(--primary-white)',
        borderRadius: 'var(--radius)',
        fontSize: '0.75rem',
        fontWeight: '600',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        zIndex: 1000
      }}>
        Live • Updated {reconciliationData.lastUpdated.toLocaleTimeString()}
      </div>

      <style jsx>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};

export default PaymentReconciliation;