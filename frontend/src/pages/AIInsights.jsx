import React, { useState, useEffect } from 'react';
import { 
    Brain, 
    TrendingUp, 
    AlertTriangle, 
    Shield, 
    Target,
    Zap,
    BarChart3,
    Eye,
    RefreshCw
} from 'lucide-react';

const InsightCard = ({ title, description, severity, confidence, recommendation, icon: Icon, trend }) => {
    const severityColors = {
        high: 'border-danger-light/30 bg-danger-light/10',
        medium: 'border-warning-light/30 bg-warning-light/10',
        low: 'border-blue-400/30 bg-blue-400/10',
        info: 'border-primary-400/30 bg-primary-400/10'
    };

    const severityTextColors = {
        high: 'text-danger-light',
        medium: 'text-warning-light',
        low: 'text-blue-400',
        info: 'text-primary-400'
    };

    return (
        <div className={`glass-card p-6 border ${severityColors[severity]} hover:scale-105 transition-transform duration-200`}>
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                    <Icon className={`w-6 h-6 ${severityTextColors[severity]}`} />
                    <div>
                        <h3 className="font-semibold text-dark-100">{title}</h3>
                        <p className="text-sm text-dark-400 mt-1">{description}</p>
                    </div>
                </div>
                <div className="text-right">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${severityColors[severity]} ${severityTextColors[severity]}`}>
                        {severity.toUpperCase()}
                    </span>
                    <p className="text-xs text-dark-400 mt-1">{confidence}% confidence</p>
                </div>
            </div>
            
            {trend && (
                <div className="mb-4">
                    <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="w-4 h-4 text-primary-400" />
                        <span className="text-sm text-dark-300">Trend Analysis</span>
                    </div>
                    <p className="text-sm text-dark-400">{trend}</p>
                </div>
            )}
            
            <div className="border-t border-white/10 pt-4">
                <div className="flex items-center gap-2 mb-2">
                    <Target className="w-4 h-4 text-success-light" />
                    <span className="text-sm font-medium text-success-light">Recommendation</span>
                </div>
                <p className="text-sm text-dark-300">{recommendation}</p>
            </div>
        </div>
    );
};

const FraudScoreCard = ({ transaction }) => {
    const getScoreColor = (score) => {
        if (score >= 80) return 'text-danger-light';
        if (score >= 60) return 'text-warning-light';
        if (score >= 40) return 'text-blue-400';
        return 'text-success-light';
    };

    const getScoreBg = (score) => {
        if (score >= 80) return 'bg-danger-light/20';
        if (score >= 60) return 'bg-warning-light/20';
        if (score >= 40) return 'bg-blue-400/20';
        return 'bg-success-light/20';
    };

    return (
        <div className="glass-card p-4 mb-3">
            <div className="flex items-center justify-between">
                <div>
                    <p className="font-mono text-sm text-dark-100">{transaction.id}</p>
                    <p className="text-xs text-dark-400">${transaction.amount} • {transaction.source}</p>
                </div>
                <div className="text-right">
                    <div className={`px-3 py-1 rounded-full ${getScoreBg(transaction.riskScore)}`}>
                        <span className={`font-bold ${getScoreColor(transaction.riskScore)}`}>
                            {transaction.riskScore}
                        </span>
                    </div>
                    <p className="text-xs text-dark-400 mt-1">{transaction.riskLevel}</p>
                </div>
            </div>
            <div className="mt-3">
                <div className="flex flex-wrap gap-1">
                    {transaction.riskFactors.map((factor, index) => (
                        <span key={index} className="px-2 py-1 bg-dark-700 text-xs text-dark-300 rounded">
                            {factor}
                        </span>
                    ))}
                </div>
            </div>
        </div>
    );
};

export const AIInsights = () => {
    const [insights, setInsights] = useState([]);
    const [anomalies, setAnomalies] = useState([]);
    const [fraudScores, setFraudScores] = useState([]);
    const [recommendations, setRecommendations] = useState([]);
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    useEffect(() => {
        generateInsights();
        generateAnomalies();
        generateFraudScores();
        generateRecommendations();
    }, []);

    const generateInsights = () => {
        const sampleInsights = [
            {
                title: 'Unusual Transaction Pattern Detected',
                description: 'Mobile app transactions showing 340% increase in volume since 2 PM',
                severity: 'high',
                confidence: 94,
                icon: AlertTriangle,
                trend: 'Sharp upward trend started at 14:00, peak at 14:30, now stabilizing',
                recommendation: 'Monitor mobile app infrastructure for potential issues. Consider scaling resources.'
            },
            {
                title: 'Gateway Processing Delay Anomaly',
                description: 'Payment gateway response times increased by 180% in last hour',
                severity: 'medium',
                confidence: 87,
                icon: Zap,
                trend: 'Gradual increase over 60 minutes, affecting 23% of transactions',
                recommendation: 'Contact gateway provider. Implement fallback routing for critical transactions.'
            },
            {
                title: 'Recurring Amount Mismatch Pattern',
                description: 'Systematic $0.01 differences detected in core banking system',
                severity: 'medium',
                confidence: 92,
                icon: Target,
                trend: 'Consistent pattern over 3 days, affecting 2.3% of transactions',
                recommendation: 'Review rounding logic in core banking system. Implement standardized rounding rules.'
            },
            {
                title: 'Positive Reconciliation Trend',
                description: 'Overall match rate improved by 2.1% compared to last week',
                severity: 'info',
                confidence: 96,
                icon: TrendingUp,
                trend: 'Steady improvement over 7 days, best performance in 30 days',
                recommendation: 'Document recent changes that contributed to improvement for future reference.'
            }
        ];
        setInsights(sampleInsights);
    };

    const generateAnomalies = () => {
        const sampleAnomalies = [
            {
                type: 'Volume Spike',
                description: 'Transaction volume 4x normal for this time',
                timestamp: '14:23:15',
                severity: 'High',
                affected: '1,247 transactions'
            },
            {
                type: 'Latency Increase',
                description: 'Average processing time increased to 2.3s',
                timestamp: '14:18:42',
                severity: 'Medium',
                affected: '892 transactions'
            },
            {
                type: 'Error Rate Spike',
                description: 'Gateway timeout errors increased 300%',
                timestamp: '14:15:33',
                severity: 'High',
                affected: '156 transactions'
            }
        ];
        setAnomalies(sampleAnomalies);
    };

    const generateFraudScores = () => {
        const sampleScores = [
            {
                id: 'TXN789123',
                amount: '15,750.00',
                source: 'Mobile App',
                riskScore: 89,
                riskLevel: 'High Risk',
                riskFactors: ['Large Amount', 'Off-Hours', 'New Device', 'Velocity']
            },
            {
                id: 'TXN456789',
                amount: '2,340.50',
                source: 'Gateway',
                riskScore: 67,
                riskLevel: 'Medium Risk',
                riskFactors: ['Unusual Pattern', 'Geographic']
            },
            {
                id: 'TXN234567',
                amount: '890.25',
                source: 'Core Banking',
                riskScore: 34,
                riskLevel: 'Low Risk',
                riskFactors: ['Normal Pattern']
            }
        ];
        setFraudScores(sampleScores);
    };

    const generateRecommendations = () => {
        const sampleRecommendations = [
            {
                priority: 'High',
                title: 'Resolve High-Value Mismatches First',
                description: 'Focus on 4 mismatches over $10,000 before smaller discrepancies',
                impact: 'Reduces financial exposure by $47,230',
                effort: 'Low'
            },
            {
                priority: 'Medium',
                title: 'Implement Automated Retry Logic',
                description: 'Add retry mechanism for gateway timeout errors',
                impact: 'Could resolve 67% of timeout-related mismatches automatically',
                effort: 'Medium'
            },
            {
                priority: 'Low',
                title: 'Optimize Mobile App Batch Processing',
                description: 'Process mobile transactions in smaller, more frequent batches',
                impact: 'Reduce average reconciliation time by 23%',
                effort: 'High'
            }
        ];
        setRecommendations(sampleRecommendations);
    };

    const runAnalysis = () => {
        setIsAnalyzing(true);
        setTimeout(() => {
            generateInsights();
            generateAnomalies();
            generateFraudScores();
            generateRecommendations();
            setIsAnalyzing(false);
        }, 3000);
    };

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-dark-100 flex items-center gap-3">
                        <Brain className="w-8 h-8 text-primary-400" />
                        AI Insights & Analytics
                    </h1>
                    <p className="text-dark-400 mt-2">Advanced pattern recognition and predictive analysis</p>
                </div>
                
                <button
                    onClick={runAnalysis}
                    disabled={isAnalyzing}
                    className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white rounded-lg transition-colors"
                >
                    <RefreshCw className={`w-4 h-4 ${isAnalyzing ? 'animate-spin' : ''}`} />
                    {isAnalyzing ? 'Analyzing...' : 'Refresh Analysis'}
                </button>
            </div>

            {/* AI Insights Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {insights.map((insight, index) => (
                    <InsightCard key={index} {...insight} />
                ))}
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-8">
                {/* Anomaly Detection */}
                <div className="glass-card p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <Eye className="w-6 h-6 text-warning-light" />
                        <h3 className="text-xl font-semibold text-dark-100">Anomaly Detection</h3>
                    </div>
                    
                    <div className="space-y-4">
                        {anomalies.map((anomaly, index) => (
                            <div key={index} className="p-4 bg-dark-800/50 rounded-lg">
                                <div className="flex items-center justify-between mb-2">
                                    <h4 className="font-medium text-dark-100">{anomaly.type}</h4>
                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                        anomaly.severity === 'High' ? 'bg-danger-light/20 text-danger-light' :
                                        'bg-warning-light/20 text-warning-light'
                                    }`}>
                                        {anomaly.severity}
                                    </span>
                                </div>
                                <p className="text-sm text-dark-400 mb-2">{anomaly.description}</p>
                                <div className="flex justify-between text-xs text-dark-500">
                                    <span>{anomaly.timestamp}</span>
                                    <span>{anomaly.affected}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Fraud Scoring */}
                <div className="glass-card p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <Shield className="w-6 h-6 text-danger-light" />
                        <h3 className="text-xl font-semibold text-dark-100">Fraud Risk Scoring</h3>
                    </div>
                    
                    <div className="space-y-0">
                        {fraudScores.map((transaction, index) => (
                            <FraudScoreCard key={index} transaction={transaction} />
                        ))}
                    </div>
                    
                    <button className="w-full mt-4 text-sm text-primary-400 hover:text-primary-300 transition-colors">
                        View All Risk Assessments →
                    </button>
                </div>

                {/* AI Recommendations */}
                <div className="glass-card p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <Target className="w-6 h-6 text-success-light" />
                        <h3 className="text-xl font-semibold text-dark-100">AI Recommendations</h3>
                    </div>
                    
                    <div className="space-y-4">
                        {recommendations.map((rec, index) => (
                            <div key={index} className="p-4 bg-dark-800/50 rounded-lg">
                                <div className="flex items-center justify-between mb-2">
                                    <h4 className="font-medium text-dark-100">{rec.title}</h4>
                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                        rec.priority === 'High' ? 'bg-danger-light/20 text-danger-light' :
                                        rec.priority === 'Medium' ? 'bg-warning-light/20 text-warning-light' :
                                        'bg-blue-400/20 text-blue-400'
                                    }`}>
                                        {rec.priority}
                                    </span>
                                </div>
                                <p className="text-sm text-dark-400 mb-3">{rec.description}</p>
                                <div className="space-y-1">
                                    <div className="flex justify-between text-xs">
                                        <span className="text-dark-500">Impact:</span>
                                        <span className="text-success-light">{rec.impact}</span>
                                    </div>
                                    <div className="flex justify-between text-xs">
                                        <span className="text-dark-500">Effort:</span>
                                        <span className="text-dark-300">{rec.effort}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* AI Model Performance */}
            <div className="glass-card p-6">
                <div className="flex items-center gap-3 mb-6">
                    <BarChart3 className="w-6 h-6 text-primary-400" />
                    <h3 className="text-xl font-semibold text-dark-100">AI Model Performance</h3>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="text-center">
                        <p className="text-2xl font-bold text-success-light">94.7%</p>
                        <p className="text-sm text-dark-400">Anomaly Detection Accuracy</p>
                    </div>
                    <div className="text-center">
                        <p className="text-2xl font-bold text-primary-400">87.3%</p>
                        <p className="text-sm text-dark-400">Fraud Detection Rate</p>
                    </div>
                    <div className="text-center">
                        <p className="text-2xl font-bold text-warning-light">2.1%</p>
                        <p className="text-sm text-dark-400">False Positive Rate</p>
                    </div>
                    <div className="text-center">
                        <p className="text-2xl font-bold text-blue-400">156ms</p>
                        <p className="text-sm text-dark-400">Avg Analysis Time</p>
                    </div>
                </div>
            </div>
        </div>
    );
};