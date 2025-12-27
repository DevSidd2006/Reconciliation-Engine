import React, { useState, useEffect } from 'react';
import { AlertTriangle, Clock } from 'lucide-react';
import { useSocket } from '../../hooks/useSocket';
import { formatRelativeTime, getMismatchBadge } from '../../utils/helpers';

export const RecentActivity = () => {
    const { subscribe, unsubscribe } = useSocket();
    const [activities, setActivities] = useState([]);

    useEffect(() => {
        const handleMismatch = (mismatch) => {
            setActivities((prev) => {
                const newActivities = [mismatch, ...prev];
                return newActivities.slice(0, 10); // Keep only last 10
            });
        };

        subscribe('new_mismatch', handleMismatch);

        return () => {
            unsubscribe('new_mismatch', handleMismatch);
        };
    }, [subscribe, unsubscribe]);

    if (activities.length === 0) {
        return (
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-dark-100 mb-4">Recent Mismatches</h3>
                <div className="text-center py-8">
                    <AlertTriangle className="w-12 h-12 text-dark-600 mx-auto mb-3" />
                    <p className="text-dark-400">No recent mismatches detected</p>
                    <p className="text-xs text-dark-500 mt-1">Waiting for real-time updates...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-dark-100 mb-4">Recent Mismatches</h3>

            <div className="space-y-3 max-h-[400px] overflow-y-auto custom-scrollbar">
                {activities.map((activity, index) => (
                    <div
                        key={activity.id || index}
                        className="p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-all duration-200 animate-slide-in-right"
                    >
                        <div className="flex items-start justify-between gap-3">
                            <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                    <span className={`${getMismatchBadge(activity.mismatch_type)}`}>
                                        {activity.mismatch_type?.replace('_', ' ')}
                                    </span>
                                </div>

                                <p className="text-sm text-dark-200 mb-1">
                                    Transaction ID: <span className="font-mono text-primary-400">{activity.txn_id}</span>
                                </p>

                                <p className="text-xs text-dark-400 line-clamp-2">{activity.details}</p>
                            </div>

                            <div className="flex items-center gap-1 text-xs text-dark-500">
                                <Clock className="w-3 h-3" />
                                {formatRelativeTime(activity.detected_at)}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
