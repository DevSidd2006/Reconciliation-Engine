import React, { useState, useEffect } from 'react';
import { AlertTriangle, TrendingUp, Clock, Shield, Brain, ChevronRight } from 'lucide-react';

const InsightCard = ({ type, message, severity, timestamp, icon: Icon }) => {
    const severityColors = {
        high: 'border-danger-light/30 bg-danger-light/10 text-danger-light',
        medium: 'border-warning-light/30 bg-warning-light/10 text-warning-light',
        low: 'border-blue-400/30 bg-blue-400/10 text-blue-400',
        info: 'border-primary-400/30 bg-primary-400/10 text-primary-400'
    };

    return (
        <div className={`p-4 rounded-lg border ${severityColors[severity]} mb-3 last:mb-0`}>
            <div className="flex items-start gap-3">
                <Icon className="w-5 h-5 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                    <p className="text-sm font-medium">{message}</p>
                    <p className="text-xs opacity-75 mt-1">{timestamp}</p>
                </div>
                <ChevronRight className="w-4 h-4 opacity-50" />
            </div>
        </div>
    );
};

export const AIInsightPanel = () => {
    const [insights, setInsights] = useState([]);

    useEffect(() => {
        // Simulate AI insights
        const generateInsights = () => {
            const sampleInsights = [
                {
                    type: 'anomaly',
                    message: 'Unusual spike in timestamp mismatches since 2:03 PM',
                    severity: 'high',
                    timestamp: '2 minutes ago',
                    icon: AlertTriangle
                },
                {
                    type: 'performance',
                    message: 'Gateway delays increased to 1.4 seconds (avg: 0.8s)',
                    severity: 'medium',
                    timestamp: '5 minutes ago',
                    icon: Clock
                },
                {
                    type: 'security',
                    message: 'High-value mismatches detected: 4 cases over $10,000',
                    severity: 'high',
                    timestamp: '8 minutes ago',
                    icon: Shield
                },
                {
                    type: 'trend',
                    message: 'Mobile app transaction volume up 23% from yesterday',
                    severity: 'info',
                    timestamp: '12 minutes ago',
                    icon: TrendingUp
                },
                {
                    type: 'prediction',
                    message: 'AI predicts 15% increase in reconciliation load at 3 PM',
                    severity: 'low',
                    timestamp: '15 minutes ago',
                    icon: Brain
                }
            ];

            setInsights(sampleInsights);
        };

        generateInsights();
        
        // Update insights every 2 minutes
        const interval = setInterval(generateInsights, 120000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h3 className="text-xl font-semibold text-dark-100 flex items-center gap-2">
                        <Brain className="w-5 h-5 text-primary-400" />
                        AI Insights & Alerts
                    </h3>
                    <p className="text-dark-400 text-sm">Real-time anomaly detection and predictions</p>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-primary-400 rounded-full animate-pulse"></div>
                    <span className="text-sm text-primary-400">Active</span>
                </div>
            </div>

            <div className="space-y-0">
                {insights.length > 0 ? (
                    insights.map((insight, index) => (
                        <InsightCard key={index} {...insight} />
                    ))
                ) : (
                    <div className="text-center py-8">
                        <Brain className="w-12 h-12 text-dark-500 mx-auto mb-3" />
                        <p className="text-dark-400">No insights available</p>
                        <p className="text-dark-500 text-sm">AI is analyzing transaction patterns...</p>
                    </div>
                )}
            </div>

            <div className="mt-6 pt-4 border-t border-white/10">
                <button className="w-full text-sm text-primary-400 hover:text-primary-300 transition-colors flex items-center justify-center gap-2">
                    View All AI Insights
                    <ChevronRight className="w-4 h-4" />
                </button>
            </div>
        </div>
    );
};