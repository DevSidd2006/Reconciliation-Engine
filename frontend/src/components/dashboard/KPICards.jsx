import React from 'react';
import { 
    TrendingUp, 
    CheckCircle, 
    AlertTriangle, 
    Clock, 
    Shield 
} from 'lucide-react';

const KPICard = ({ title, value, change, changeType, icon: Icon, color }) => {
    const colorClasses = {
        primary: 'from-primary-600 to-primary-500',
        success: 'from-success-600 to-success-500',
        warning: 'from-warning-600 to-warning-500',
        danger: 'from-danger-600 to-danger-500',
        info: 'from-blue-600 to-blue-500'
    };

    return (
        <div className="glass-card p-6 hover:scale-105 transition-transform duration-200">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-dark-400 text-sm font-medium">{title}</p>
                    <p className="text-2xl font-bold text-dark-100 mt-1">{value}</p>
                    {change && (
                        <div className={`flex items-center gap-1 mt-2 text-sm ${
                            changeType === 'positive' ? 'text-success-light' : 'text-danger-light'
                        }`}>
                            <TrendingUp className="w-4 h-4" />
                            <span>{change}</span>
                        </div>
                    )}
                </div>
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${colorClasses[color]} flex items-center justify-center`}>
                    <Icon className="w-6 h-6 text-white" />
                </div>
            </div>
        </div>
    );
};

export const KPICards = ({ stats }) => {
    const kpiData = [
        {
            title: 'Total Transactions (Today)',
            value: stats?.totalTransactions?.toLocaleString() || '0',
            change: '+12.5%',
            changeType: 'positive',
            icon: TrendingUp,
            color: 'primary'
        },
        {
            title: 'Matched Transactions',
            value: stats?.matchedTransactions?.toLocaleString() || '0',
            change: '+8.2%',
            changeType: 'positive',
            icon: CheckCircle,
            color: 'success'
        },
        {
            title: 'Mismatches',
            value: stats?.mismatches?.toLocaleString() || '0',
            change: '-2.1%',
            changeType: 'positive',
            icon: AlertTriangle,
            color: 'danger'
        },
        {
            title: 'Pending Transactions',
            value: stats?.pendingTransactions?.toLocaleString() || '0',
            change: '+5.3%',
            changeType: 'negative',
            icon: Clock,
            color: 'warning'
        },
        {
            title: 'High-Risk Alerts',
            value: stats?.highRiskAlerts?.toLocaleString() || '0',
            change: '-15.7%',
            changeType: 'positive',
            icon: Shield,
            color: 'info'
        }
    ];

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
            {kpiData.map((kpi, index) => (
                <KPICard key={index} {...kpi} />
            ))}
        </div>
    );
};