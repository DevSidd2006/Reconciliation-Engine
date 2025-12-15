import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle, CheckCircle, TrendingUp } from 'lucide-react';
import { StatsCard } from '../components/dashboard/StatsCard';
import { RealtimeChart } from '../components/dashboard/RealtimeChart';
import { RecentActivity } from '../components/dashboard/RecentActivity';
import { useSocket } from '../hooks/useSocket';
import { transactionAPI, mismatchAPI } from '../services/api';

export const Dashboard = () => {
    const { subscribe, unsubscribe } = useSocket();
    const [stats, setStats] = useState({
        totalTransactions: 0,
        successfulTransactions: 0,
        totalMismatches: 0,
        resolvedMismatches: 0,
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadStats();

        // Subscribe to real-time updates
        const handleTransaction = () => {
            setStats((prev) => ({
                ...prev,
                totalTransactions: prev.totalTransactions + 1,
            }));
        };

        const handleMismatch = () => {
            setStats((prev) => ({
                ...prev,
                totalMismatches: prev.totalMismatches + 1,
            }));
        };

        subscribe('new_transaction', handleTransaction);
        subscribe('new_mismatch', handleMismatch);

        // Refresh stats periodically
        const interval = setInterval(loadStats, 30000);

        return () => {
            unsubscribe('new_transaction', handleTransaction);
            unsubscribe('new_mismatch', handleMismatch);
            clearInterval(interval);
        };
    }, [subscribe, unsubscribe]);

    const loadStats = async () => {
        try {
            setLoading(true);
            // Mock data for now - replace with actual API calls when backend is ready
            setStats({
                totalTransactions: Math.floor(Math.random() * 10000) + 5000,
                successfulTransactions: Math.floor(Math.random() * 9000) + 4500,
                totalMismatches: Math.floor(Math.random() * 100) + 50,
                resolvedMismatches: Math.floor(Math.random() * 50) + 20,
            });
        } catch (error) {
            console.error('Failed to load stats:', error);
        } finally {
            setLoading(false);
        }
    };

    const successRate = stats.totalTransactions > 0
        ? ((stats.successfulTransactions / stats.totalTransactions) * 100).toFixed(1)
        : 0;

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div>
                <h1 className="text-3xl font-bold text-gradient mb-2">Dashboard</h1>
                <p className="text-dark-400">Real-time transaction reconciliation monitoring</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatsCard
                    title="Total Transactions"
                    value={stats.totalTransactions.toLocaleString()}
                    change={5.2}
                    changeType="positive"
                    icon={Activity}
                    loading={loading}
                />
                <StatsCard
                    title="Success Rate"
                    value={`${successRate}%`}
                    change={2.1}
                    changeType="positive"
                    icon={CheckCircle}
                    loading={loading}
                />
                <StatsCard
                    title="Total Mismatches"
                    value={stats.totalMismatches.toLocaleString()}
                    change={-3.5}
                    changeType="negative"
                    icon={AlertTriangle}
                    loading={loading}
                />
                <StatsCard
                    title="Resolved"
                    value={stats.resolvedMismatches.toLocaleString()}
                    change={8.3}
                    changeType="positive"
                    icon={TrendingUp}
                    loading={loading}
                />
            </div>

            {/* Chart */}
            <RealtimeChart />

            {/* Recent Activity */}
            <RecentActivity />
        </div>
    );
};
