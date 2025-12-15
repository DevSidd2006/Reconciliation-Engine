import { useState, useEffect } from 'react';
import axios from 'axios';

const AnalyticsCharts = ({ dateRange }) => {
  const [chartData, setChartData] = useState({
    mismatchTypes: [],
    sourceDistribution: [],
    timeline: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeChart, setActiveChart] = useState('mismatches');

  const fetchChartData = async () => {
    try {
      setLoading(true);
      
      const [mismatchTypesResponse, sourceDistResponse, timelineResponse] = await Promise.all([
        axios.get('/api/analytics/mismatch-type-counts'),
        axios.get('/api/analytics/source-distribution'),
        axios.get('/api/analytics/timeline', { params: { hours: 24, interval: 'hour' } })
      ]);

      setChartData({
        mismatchTypes: mismatchTypesResponse.data.mismatch_types || [],
        sourceDistribution: sourceDistResponse.data.distribution || [],
        timeline: timelineResponse.data.timeline || []
      });
      setError(null);
    } catch (err) {
      console.error('Error fetching chart data:', err);
      setError('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChartData();
  }, [dateRange]);

  // Listen for dashboard refresh events
  useEffect(() => {
    const handleRefresh = () => fetchChartData();
    window.addEventListener('dashboardRefresh', handleRefresh);
    return () => window.removeEventListener('dashboardRefresh', handleRefresh);
  }, [dateRange]);

  const renderBarChart = (data, title, colorKey = 'color') => {
    if (!data || data.length === 0) {
      return (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--gray-600)' }}>
          📊 No data available
        </div>
      );
    }

    const maxValue = Math.max(...data.map(item => item.count || 0));
    const colors = ['var(--error-red)', 'var(--warning-orange)', 'var(--pending-yellow)', 'var(--accent-blue)', 'var(--accent-magenta)', 'var(--success-green)'];

    return (
      <div>
        <h4 style={{ marginBottom: '20px', textAlign: 'center' }}>{title}</h4>
        
        {/* Enhanced bar chart with animations */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {data.map((item, index) => {
            const barColor = item[colorKey] || colors[index % colors.length];
            const percentage = maxValue > 0 ? (item.count / maxValue) * 100 : 0;
            
            return (
              <div key={index} style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '16px',
                padding: '12px',
                border: '2px solid var(--primary-black)',
                backgroundColor: 'var(--gray-50)'
              }}>
                <div style={{ 
                  minWidth: '140px', 
                  fontSize: '0.875rem', 
                  fontWeight: '700',
                  textAlign: 'right'
                }}>
                  {item.type || item.source || item.label}
                </div>
                
                <div style={{ 
                  flex: 1, 
                  height: '40px', 
                  backgroundColor: 'var(--gray-200)',
                  border: '2px solid var(--primary-black)',
                  position: 'relative',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    height: '100%',
                    width: `${percentage}%`,
                    backgroundColor: barColor,
                    transition: 'width 1s ease',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    position: 'relative'
                  }}>
                    <span style={{ 
                      color: 'var(--primary-white)', 
                      fontSize: '0.875rem', 
                      fontWeight: '700',
                      fontFamily: 'var(--font-mono)',
                      textShadow: '1px 1px 2px rgba(0,0,0,0.5)'
                    }}>
                      {item.count}
                    </span>
                    
                    {/* Gradient overlay for visual appeal */}
                    <div style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: '50%',
                      background: 'linear-gradient(to bottom, rgba(255,255,255,0.2), transparent)'
                    }}></div>
                  </div>
                </div>
                
                <div style={{ 
                  minWidth: '80px', 
                  fontSize: '0.875rem', 
                  fontFamily: 'var(--font-mono)',
                  color: 'var(--gray-600)',
                  textAlign: 'center'
                }}>
                  {item.percentage ? `${item.percentage}%` : `${Math.round(percentage)}%`}
                </div>
                
                {/* Severity indicator for mismatch types */}
                {item.type && (
                  <div style={{
                    padding: '4px 8px',
                    backgroundColor: item.type.includes('AMOUNT') ? 'var(--error-red)' : 
                                   item.type.includes('STATUS') ? 'var(--warning-orange)' : 'var(--accent-blue)',
                    color: 'var(--primary-white)',
                    fontSize: '0.75rem',
                    fontWeight: '700',
                    border: '1px solid var(--primary-black)'
                  }}>
                    {item.type.includes('AMOUNT') ? 'HIGH' : 
                     item.type.includes('STATUS') ? 'MED' : 'LOW'}
                  </div>
                )}
              </div>
            );
          })}
        </div>
        
        {/* Summary stats */}
        <div style={{
          marginTop: '20px',
          padding: '16px',
          backgroundColor: 'var(--primary-black)',
          color: 'var(--primary-white)',
          border: '2px solid var(--primary-black)',
          display: 'flex',
          justifyContent: 'space-around',
          textAlign: 'center'
        }}>
          <div>
            <div style={{ fontSize: '1.2rem', fontWeight: '800', fontFamily: 'var(--font-mono)' }}>
              {data.reduce((sum, item) => sum + item.count, 0)}
            </div>
            <div style={{ fontSize: '0.75rem', fontWeight: '700' }}>TOTAL</div>
          </div>
          <div>
            <div style={{ fontSize: '1.2rem', fontWeight: '800', fontFamily: 'var(--font-mono)' }}>
              {data.length}
            </div>
            <div style={{ fontSize: '0.75rem', fontWeight: '700' }}>CATEGORIES</div>
          </div>
          <div>
            <div style={{ fontSize: '1.2rem', fontWeight: '800', fontFamily: 'var(--font-mono)' }}>
              {maxValue}
            </div>
            <div style={{ fontSize: '0.75rem', fontWeight: '700' }}>HIGHEST</div>
          </div>
        </div>
      </div>
    );
  };

  const renderPieChart = (data, title) => {
    if (!data || data.length === 0) {
      return (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--gray-600)' }}>
          🥧 No data available
        </div>
      );
    }

    const total = data.reduce((sum, item) => sum + item.count, 0);
    const colors = ['var(--accent-blue)', 'var(--accent-magenta)', 'var(--accent-cyan)', 'var(--warning-orange)', 'var(--success-green)', 'var(--error-red)'];
    
    // Calculate angles for pie slices
    let currentAngle = 0;
    const slices = data.map((item, index) => {
      const percentage = (item.count / total) * 100;
      const angle = (item.count / total) * 360;
      const startAngle = currentAngle;
      currentAngle += angle;
      
      return {
        ...item,
        percentage: Math.round(percentage * 10) / 10,
        startAngle,
        endAngle: currentAngle,
        color: item.color || colors[index % colors.length]
      };
    });

    // Create SVG path for pie slice
    const createPieSlice = (centerX, centerY, radius, startAngle, endAngle, color) => {
      const start = polarToCartesian(centerX, centerY, radius, endAngle);
      const end = polarToCartesian(centerX, centerY, radius, startAngle);
      const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
      
      const d = [
        "M", centerX, centerY,
        "L", start.x, start.y,
        "A", radius, radius, 0, largeArcFlag, 0, end.x, end.y,
        "Z"
      ].join(" ");
      
      return d;
    };

    const polarToCartesian = (centerX, centerY, radius, angleInDegrees) => {
      const angleInRadians = (angleInDegrees - 90) * Math.PI / 180.0;
      return {
        x: centerX + (radius * Math.cos(angleInRadians)),
        y: centerY + (radius * Math.sin(angleInRadians))
      };
    };

    return (
      <div>
        <h4 style={{ marginBottom: '20px', textAlign: 'center' }}>{title}</h4>
        
        <div style={{ display: 'flex', gap: '40px', alignItems: 'center', justifyContent: 'center' }}>
          {/* SVG Pie Chart */}
          <div style={{ position: 'relative' }}>
            <svg width="280" height="280" style={{ border: '3px solid var(--primary-black)' }}>
              {slices.map((slice, index) => (
                <g key={index}>
                  <path
                    d={createPieSlice(140, 140, 120, slice.startAngle, slice.endAngle, slice.color)}
                    fill={slice.color}
                    stroke="var(--primary-black)"
                    strokeWidth="2"
                    style={{ cursor: 'pointer' }}
                  />
                  {/* Add percentage labels for larger slices */}
                  {slice.percentage > 8 && (
                    <text
                      x={140 + 80 * Math.cos(((slice.startAngle + slice.endAngle) / 2 - 90) * Math.PI / 180)}
                      y={140 + 80 * Math.sin(((slice.startAngle + slice.endAngle) / 2 - 90) * Math.PI / 180)}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      fill="var(--primary-white)"
                      fontSize="14"
                      fontWeight="700"
                      fontFamily="var(--font-mono)"
                    >
                      {slice.percentage}%
                    </text>
                  )}
                </g>
              ))}
              {/* Center circle for donut effect */}
              <circle
                cx="140"
                cy="140"
                r="40"
                fill="var(--primary-white)"
                stroke="var(--primary-black)"
                strokeWidth="3"
              />
              {/* Center text */}
              <text
                x="140"
                y="135"
                textAnchor="middle"
                dominantBaseline="middle"
                fill="var(--primary-black)"
                fontSize="16"
                fontWeight="800"
                fontFamily="var(--font-mono)"
              >
                TOTAL
              </text>
              <text
                x="140"
                y="150"
                textAnchor="middle"
                dominantBaseline="middle"
                fill="var(--primary-black)"
                fontSize="14"
                fontWeight="700"
                fontFamily="var(--font-mono)"
              >
                {total.toLocaleString()}
              </text>
            </svg>
          </div>

          {/* Legend */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', minWidth: '200px' }}>
            {slices.map((slice, index) => (
              <div key={index} style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '12px',
                padding: '8px 12px',
                border: '2px solid var(--primary-black)',
                backgroundColor: 'var(--gray-50)'
              }}>
                <div style={{
                  width: '20px',
                  height: '20px',
                  backgroundColor: slice.color,
                  border: '2px solid var(--primary-black)'
                }}></div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.875rem', fontWeight: '700' }}>
                    {slice.source || slice.type || slice.label}
                  </div>
                  <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--gray-600)' }}>
                    {slice.count.toLocaleString()} ({slice.percentage}%)
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderTimelineChart = (data, title) => {
    if (!data || data.length === 0) {
      return (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--gray-600)' }}>
          📈 No timeline data available
        </div>
      );
    }

    const maxTransactions = Math.max(...data.map(item => item.transactions || 0));
    const maxMismatches = Math.max(...data.map(item => item.mismatches || 0));

    return (
      <div>
        <h4 style={{ marginBottom: '20px', textAlign: 'center' }}>{title}</h4>
        
        {/* Legend */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '16px', height: '16px', backgroundColor: 'var(--accent-blue)', border: '2px solid var(--primary-black)' }}></div>
            <span style={{ fontSize: '0.875rem', fontWeight: '700' }}>Transactions</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '16px', height: '16px', backgroundColor: 'var(--error-red)', border: '2px solid var(--primary-black)' }}></div>
            <span style={{ fontSize: '0.875rem', fontWeight: '700' }}>Mismatches</span>
          </div>
        </div>

        {/* Timeline bars */}
        <div style={{ display: 'flex', alignItems: 'end', gap: '4px', height: '200px', padding: '0 20px' }}>
          {data.map((item, index) => (
            <div key={index} style={{ 
              flex: 1, 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center',
              gap: '4px'
            }}>
              {/* Transaction bar */}
              <div style={{
                width: '100%',
                height: `${(item.transactions / maxTransactions) * 150}px`,
                backgroundColor: 'var(--accent-blue)',
                border: '1px solid var(--primary-black)',
                minHeight: '2px',
                position: 'relative'
              }} title={`${item.hour}: ${item.transactions} transactions`}>
                {item.transactions > 0 && (
                  <div style={{
                    position: 'absolute',
                    top: '-20px',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    fontSize: '0.75rem',
                    fontFamily: 'var(--font-mono)',
                    fontWeight: '700'
                  }}>
                    {item.transactions}
                  </div>
                )}
              </div>
              
              {/* Mismatch bar */}
              <div style={{
                width: '100%',
                height: `${(item.mismatches / Math.max(maxMismatches, 1)) * 30}px`,
                backgroundColor: 'var(--error-red)',
                border: '1px solid var(--primary-black)',
                minHeight: '2px'
              }} title={`${item.hour}: ${item.mismatches} mismatches`}></div>
              
              {/* Hour label */}
              <div style={{ 
                fontSize: '0.75rem', 
                fontFamily: 'var(--font-mono)',
                transform: 'rotate(-45deg)',
                transformOrigin: 'center',
                marginTop: '8px'
              }}>
                {item.hour}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderGaugeChart = (value, max, title, color = 'var(--accent-blue)') => {
    const percentage = Math.min((value / max) * 100, 100);
    const angle = (percentage / 100) * 180; // Half circle
    
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
        <h4 style={{ margin: '0', textAlign: 'center', fontSize: '1rem', fontWeight: '700' }}>{title}</h4>
        
        <div style={{ position: 'relative', width: '200px', height: '140px' }}>
          <svg width="200" height="120" style={{ overflow: 'visible' }}>
            {/* Background arc */}
            <path
              d="M 20 100 A 80 80 0 0 1 180 100"
              fill="none"
              stroke="#cccccc"
              strokeWidth="20"
              strokeLinecap="round"
            />
            {/* Progress arc */}
            <path
              d="M 20 100 A 80 80 0 0 1 180 100"
              fill="none"
              stroke={color}
              strokeWidth="20"
              strokeLinecap="round"
              strokeDasharray={`${(angle / 180) * 251.3} 251.3`}
              style={{ transition: 'stroke-dasharray 1s ease' }}
            />
            {/* Center text - only the main value */}
            <text
              x="100"
              y="90"
              textAnchor="middle"
              dominantBaseline="middle"
              fill="#000000"
              fontSize="32"
              fontWeight="800"
              fontFamily="monospace"
            >
              {value.toLocaleString()}
            </text>
          </svg>
          
          {/* Percentage indicator - positioned below the gauge */}
          <div style={{
            position: 'absolute',
            bottom: '0px',
            left: '50%',
            transform: 'translateX(-50%)',
            backgroundColor: color,
            color: '#ffffff',
            padding: '6px 16px',
            border: '3px solid #000000',
            fontSize: '16px',
            fontWeight: '800',
            fontFamily: 'monospace',
            zIndex: 10,
            borderRadius: '0px'
          }}>
            {Math.round(percentage)}%
          </div>
        </div>
      </div>
    );
  };

  const renderHeatmap = (data, title) => {
    if (!data || data.length === 0) {
      return (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--gray-600)' }}>
          🔥 No heatmap data available
        </div>
      );
    }

    const maxValue = Math.max(...data.map(item => item.transactions || 0));
    const hours = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', 
                  '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23'];
    
    const getIntensity = (value) => {
      if (!value || maxValue === 0) return 0;
      return (value / maxValue);
    };

    const getHeatColor = (intensity) => {
      if (intensity === 0) return 'var(--gray-200)';
      if (intensity < 0.25) return 'var(--pending-yellow)';
      if (intensity < 0.5) return 'var(--warning-orange)';
      if (intensity < 0.75) return 'var(--accent-magenta)';
      return 'var(--error-red)';
    };

    return (
      <div>
        <h4 style={{ marginBottom: '20px', textAlign: 'center' }}>{title}</h4>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', alignItems: 'center' }}>
          {/* Hour labels */}
          <div style={{ display: 'flex', gap: '2px', marginBottom: '8px' }}>
            {hours.map(hour => (
              <div key={hour} style={{
                width: '30px',
                textAlign: 'center',
                fontSize: '0.75rem',
                fontFamily: 'var(--font-mono)',
                fontWeight: '700'
              }}>
                {hour}
              </div>
            ))}
          </div>
          
          {/* Heatmap grid */}
          <div style={{ display: 'flex', gap: '2px' }}>
            {hours.map(hour => {
              const hourData = data.find(item => item.hour?.includes(hour)) || { transactions: 0 };
              const intensity = getIntensity(hourData.transactions);
              
              return (
                <div
                  key={hour}
                  style={{
                    width: '30px',
                    height: '30px',
                    backgroundColor: getHeatColor(intensity),
                    border: '1px solid var(--primary-black)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.75rem',
                    fontWeight: '700',
                    fontFamily: 'var(--font-mono)',
                    color: intensity > 0.5 ? 'var(--primary-white)' : 'var(--primary-black)',
                    cursor: 'pointer'
                  }}
                  title={`${hour}:00 - ${hourData.transactions} transactions`}
                >
                  {hourData.transactions > 0 ? hourData.transactions : ''}
                </div>
              );
            })}
          </div>
          
          {/* Legend */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '16px' }}>
            <span style={{ fontSize: '0.875rem', fontWeight: '700' }}>Less</span>
            {[0, 0.25, 0.5, 0.75, 1].map(intensity => (
              <div
                key={intensity}
                style={{
                  width: '20px',
                  height: '20px',
                  backgroundColor: getHeatColor(intensity),
                  border: '1px solid var(--primary-black)'
                }}
              />
            ))}
            <span style={{ fontSize: '0.875rem', fontWeight: '700' }}>More</span>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="analytics-charts">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">📈 ANALYTICS & CHARTS</h3>
          </div>
          <div style={{ textAlign: 'center', padding: '60px' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.2rem' }}>
              🔄 Loading analytics data...
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-charts">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">📈 ANALYTICS & CHARTS</h3>
          </div>
          <div className="alert alert-error">
            <h3>❌ Error Loading Analytics</h3>
            <p>{error}</p>
            <button onClick={fetchChartData} className="btn btn-primary" style={{ marginTop: '16px' }}>
              🔄 Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-charts">
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">📈 ANALYTICS & CHARTS</h3>
          <div style={{ fontSize: '0.875rem', fontFamily: 'var(--font-mono)', color: 'var(--gray-600)' }}>
            Banking-grade visual analytics for operations teams
          </div>
        </div>

        {/* Chart Navigation */}
        <div className="chart-navigation" style={{
          padding: '16px 24px',
          borderBottom: '2px solid var(--gray-200)',
          backgroundColor: 'var(--gray-50)'
        }}>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {[
              { id: 'mismatches', label: 'Mismatch Types', icon: '📊' },
              { id: 'sources', label: 'Source Distribution', icon: '🥧' },
              { id: 'timeline', label: 'Timeline Analysis', icon: '📈' },
              { id: 'performance', label: 'Performance Gauge', icon: '⚡' },
              { id: 'heatmap', label: 'Activity Heatmap', icon: '🔥' }
            ].map(chart => (
              <button
                key={chart.id}
                onClick={() => setActiveChart(chart.id)}
                className="btn"
                style={{
                  backgroundColor: activeChart === chart.id ? 'var(--primary-black)' : 'var(--gray-200)',
                  color: activeChart === chart.id ? 'var(--primary-white)' : 'var(--primary-black)',
                  padding: '8px 16px',
                  fontSize: '0.875rem',
                  fontWeight: '700'
                }}
              >
                {chart.icon} {chart.label}
              </button>
            ))}
          </div>
        </div>

        {/* Chart Content */}
        <div style={{ padding: '24px' }}>
          {activeChart === 'mismatches' && renderBarChart(
            chartData.mismatchTypes,
            '📊 MISMATCHES BY TYPE (Bar Chart)'
          )}

          {activeChart === 'sources' && renderPieChart(
            chartData.sourceDistribution,
            '🥧 TRANSACTION SOURCE DISTRIBUTION (Donut Chart)'
          )}

          {activeChart === 'timeline' && renderTimelineChart(
            chartData.timeline,
            '📈 TRANSACTIONS & MISMATCHES TIMELINE (Last 24 Hours)'
          )}

          {activeChart === 'performance' && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '40px' }}>
              {renderGaugeChart(
                chartData.sourceDistribution.reduce((sum, item) => sum + item.count, 0),
                10000,
                '⚡ TRANSACTION THROUGHPUT',
                'var(--success-green)'
              )}
              {renderGaugeChart(
                chartData.mismatchTypes.reduce((sum, item) => sum + item.count, 0),
                100,
                '🚨 MISMATCH RATE',
                'var(--error-red)'
              )}
              {renderGaugeChart(
                Math.round(((chartData.sourceDistribution.reduce((sum, item) => sum + item.count, 0) - 
                           chartData.mismatchTypes.reduce((sum, item) => sum + item.count, 0)) / 
                           Math.max(chartData.sourceDistribution.reduce((sum, item) => sum + item.count, 0), 1)) * 100),
                100,
                '✅ SUCCESS RATE',
                'var(--accent-blue)'
              )}
            </div>
          )}

          {activeChart === 'heatmap' && renderHeatmap(
            chartData.timeline,
            '🔥 TRANSACTION ACTIVITY HEATMAP (24 Hours)'
          )}
        </div>

        {/* Chart Summary */}
        <div style={{
          padding: '20px 24px',
          borderTop: '2px solid #ccc',
          backgroundColor: '#000000',
          color: '#ffffff'
        }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '20px' }}>
            <div style={{ 
              textAlign: 'center', 
              padding: '16px', 
              border: '3px solid #ff4444',
              backgroundColor: '#111111'
            }}>
              <div style={{ 
                fontSize: '2rem', 
                fontWeight: '800', 
                color: '#ff4444', 
                fontFamily: 'monospace',
                marginBottom: '8px'
              }}>
                {chartData.mismatchTypes.reduce((sum, item) => sum + item.count, 0).toLocaleString()}
              </div>
              <div style={{ 
                fontSize: '12px', 
                fontWeight: '700', 
                textTransform: 'uppercase',
                color: '#ffffff',
                lineHeight: '1.3',
                letterSpacing: '1px'
              }}>
                🚨 TOTAL MISMATCHES
              </div>
            </div>
            
            <div style={{ 
              textAlign: 'center', 
              padding: '16px', 
              border: '3px solid #4488ff',
              backgroundColor: '#111111'
            }}>
              <div style={{ 
                fontSize: '2rem', 
                fontWeight: '800', 
                color: '#4488ff', 
                fontFamily: 'monospace',
                marginBottom: '8px'
              }}>
                {chartData.sourceDistribution.reduce((sum, item) => sum + item.count, 0).toLocaleString()}
              </div>
              <div style={{ 
                fontSize: '12px', 
                fontWeight: '700', 
                textTransform: 'uppercase',
                color: '#ffffff',
                lineHeight: '1.3',
                letterSpacing: '1px'
              }}>
                💳 TOTAL TRANSACTIONS
              </div>
            </div>
            
            <div style={{ 
              textAlign: 'center', 
              padding: '16px', 
              border: '3px solid #44ff44',
              backgroundColor: '#111111'
            }}>
              <div style={{ 
                fontSize: '2rem', 
                fontWeight: '800', 
                color: '#44ff44', 
                fontFamily: 'monospace',
                marginBottom: '8px'
              }}>
                {Math.round(((chartData.sourceDistribution.reduce((sum, item) => sum + item.count, 0) - 
                           chartData.mismatchTypes.reduce((sum, item) => sum + item.count, 0)) / 
                           Math.max(chartData.sourceDistribution.reduce((sum, item) => sum + item.count, 0), 1)) * 100)}%
              </div>
              <div style={{ 
                fontSize: '12px', 
                fontWeight: '700', 
                textTransform: 'uppercase',
                color: '#ffffff',
                lineHeight: '1.3',
                letterSpacing: '1px'
              }}>
                ✅ SUCCESS RATE
              </div>
            </div>
            
            <div style={{ 
              textAlign: 'center', 
              padding: '16px', 
              border: '3px solid #ffaa44',
              backgroundColor: '#111111'
            }}>
              <div style={{ 
                fontSize: '2rem', 
                fontWeight: '800', 
                color: '#ffaa44', 
                fontFamily: 'monospace',
                marginBottom: '8px'
              }}>
                {chartData.timeline.length}
              </div>
              <div style={{ 
                fontSize: '12px', 
                fontWeight: '700', 
                textTransform: 'uppercase',
                color: '#ffffff',
                lineHeight: '1.3',
                letterSpacing: '1px'
              }}>
                ⏰ HOURS ANALYZED
              </div>
            </div>
            
            <div style={{ 
              textAlign: 'center', 
              padding: '16px', 
              border: '3px solid #ff44aa',
              backgroundColor: '#111111'
            }}>
              <div style={{ 
                fontSize: '2rem', 
                fontWeight: '800', 
                color: '#ff44aa', 
                fontFamily: 'monospace',
                marginBottom: '8px'
              }}>
                {chartData.sourceDistribution.length}
              </div>
              <div style={{ 
                fontSize: '12px', 
                fontWeight: '700', 
                textTransform: 'uppercase',
                color: '#ffffff',
                lineHeight: '1.3',
                letterSpacing: '1px'
              }}>
                🏦 ACTIVE SOURCES
              </div>
            </div>
            
            <div style={{ 
              textAlign: 'center', 
              padding: '16px', 
              border: '3px solid #44ffaa',
              backgroundColor: '#111111'
            }}>
              <div style={{ 
                fontSize: '2rem', 
                fontWeight: '800', 
                color: '#44ffaa', 
                fontFamily: 'monospace',
                marginBottom: '8px'
              }}>
                {Math.round((chartData.timeline.reduce((sum, item) => sum + (item.transactions || 0), 0) / 
                           Math.max(chartData.timeline.length, 1)) * 10) / 10}
              </div>
              <div style={{ 
                fontSize: '12px', 
                fontWeight: '700', 
                textTransform: 'uppercase',
                color: '#ffffff',
                lineHeight: '1.3',
                letterSpacing: '1px'
              }}>
                📊 AVG PER HOUR
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsCharts;