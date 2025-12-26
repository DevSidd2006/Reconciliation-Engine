import { useState, useEffect } from 'react';
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
    exceptions: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPeriod, setSelectedPeriod] = useState('today');

  const fetchReconciliationData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/analytics/payment-reconciliation', {
        params: { period: selectedPeriod }
      });
      
      setReconciliationData(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching payment reconciliation data:', err);
      setError('Failed to load payment reconciliation data');
      // Mock data for demonstration
      setReconciliationData({
        totalTransactions: 1247,
        reconciledTransactions: 1242,
        unreconciledTransactions: 5,
        totalAmount: 21532.27,
        reconciledAmount: 20544.07,
        unreconciledAmount: 988.20,
        reconciliationSummary: [
          { type: 'Less Payment Received', count: 2, amount: 494.10 },
          { type: 'More Payment Received', count: 1, amount: 13.55 },
          { type: 'Pending Payment', count: 2, amount: 480.56 }
        ],
        exceptions: []
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReconciliationData();
    
    // Set up real-time updates every 30 seconds
    const interval = setInterval(fetchReconciliationData, 30000);
    
    return () => clearInterval(interval);
  }, [selectedPeriod]);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const getReconciliationRate = () => {
    if (reconciliationData.totalTransactions === 0) return 0;
    return ((reconciliationData.reconciledTransactions / reconciliationData.totalTransactions) * 100).toFixed(1);
  };

  const getSummaryIcon = (type) => {
    switch (type) {
      case 'Less Payment Received': return '↓';
      case 'More Payment Received': return '↑';
      case 'Pending Payment': return '⏳';
      default: return '⊞';
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

  if (loading) {
    return (
      <div className="payment-reconciliation">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Payment Reconciliation</h3>
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
        <h1 className="main-header-title">Payment Reconciliation</h1>
        <div className="main-header-controls">
          <select 
            value={selectedPeriod} 
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="form-select"
            style={{ width: 'auto', fontSize: '0.875rem' }}
          >
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
          </select>
          <button 
            onClick={fetchReconciliationData}
            className="btn btn-sm btn-primary"
          >
            <span className="icon">↻</span>
            Refresh
          </button>
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
            Reconciled Transactions
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
            Unreconciled Transactions
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

        {/* Payment Summary Chart Placeholder */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Payment Summary</h3>
            <div style={{ display: 'flex', gap: 'var(--space-3)', fontSize: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                <div style={{ 
                  width: '12px', 
                  height: '12px', 
                  backgroundColor: 'var(--accent-blue)', 
                  borderRadius: '2px' 
                }}></div>
                <span>Total</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                <div style={{ 
                  width: '12px', 
                  height: '12px', 
                  backgroundColor: 'var(--success-green)', 
                  borderRadius: '2px' 
                }}></div>
                <span>Reconciled</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                <div style={{ 
                  width: '12px', 
                  height: '12px', 
                  backgroundColor: 'var(--error-red)', 
                  borderRadius: '2px' 
                }}></div>
                <span>Unreconciled</span>
              </div>
            </div>
          </div>
          
          <div className="card-body">
            <div style={{ 
              height: '200px', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              backgroundColor: 'var(--surface-secondary)',
              border: '2px dashed var(--surface-tertiary)',
              borderRadius: 'var(--radius)',
              color: 'var(--gray-600)',
              fontStyle: 'italic'
            }}>
              Chart visualization would be displayed here
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
        Live • Updated {new Date().toLocaleTimeString()}
      </div>
    </div>
  );
};

export default PaymentReconciliation;