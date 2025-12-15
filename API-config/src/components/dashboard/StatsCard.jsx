import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

export const StatsCard = ({ title, value, change, changeType, icon: Icon, loading }) => {
    const isPositive = changeType === 'positive';
    const TrendIcon = isPositive ? TrendingUp : TrendingDown;

    if (loading) {
        return (
            <div className="glass-card p-6 animate-pulse">
                <div className="h-4 bg-white/10 rounded w-1/2 mb-4"></div>
                <div className="h-8 bg-white/10 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-white/10 rounded w-1/3"></div>
            </div>
        );
    }

    return (
        <div className="glass-card-hover p-6 group">
            <div className="flex items-start justify-between mb-4">
                <div>
                    <p className="text-sm text-dark-400 font-medium">{title}</p>
                </div>
                {Icon && (
                    <div className="p-3 rounded-lg bg-primary-500/20 text-primary-400 group-hover:scale-110 transition-transform">
                        <Icon className="w-5 h-5" />
                    </div>
                )}
            </div>

            <div className="space-y-2">
                <h3 className="text-3xl font-bold text-dark-100">{value}</h3>

                {change !== undefined && (
                    <div className="flex items-center gap-1">
                        <TrendIcon className={`w-4 h-4 ${isPositive ? 'text-success-light' : 'text-danger-light'}`} />
                        <span className={`text-sm font-medium ${isPositive ? 'text-success-light' : 'text-danger-light'}`}>
                            {change}%
                        </span>
                        <span className="text-xs text-dark-500 ml-1">vs last hour</span>
                    </div>
                )}
            </div>
        </div>
    );
};
