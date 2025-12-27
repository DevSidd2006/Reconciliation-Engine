import React, { useState, useEffect } from 'react';
import { Search, Filter, AlertTriangle } from 'lucide-react';
import { mismatchAPI } from '../services/api';
import { LoadingSpinner, LoadingSkeleton } from '../components/common/LoadingSpinner';
import { formatDate, getMismatchBadge, getMismatchColor } from '../utils/helpers';

export const Mismatches = () => {
    const [mismatches, setMismatches] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [typeFilter, setTypeFilter] = useState('all');

    useEffect(() => {
        loadMismatches();
    }, []);

    const loadMismatches = async () => {
        try {
            setLoading(true);
            // Mock data for now - replace with actual API call when backend is ready
            const mockMismatches = Array.from({ length: 15 }, (_, i) => ({
                id: `MISM${String(i + 1).padStart(6, '0')}`,
                txn_id: `TXN${String(Math.floor(Math.random() * 1000)).padStart(6, '0')}`,
                mismatch_type: ['amount_mismatch', 'status_mismatch', 'timestamp_mismatch', 'missing_transaction'][Math.floor(Math.random() * 4)],
                detected_at: new Date(Date.now() - Math.random() * 86400000).toISOString(),
                details: 'Core banking shows $1,234.56 but gateway shows $1,234.57. Difference: $0.01',
            }));
            setMismatches(mockMismatches);
        } catch (error) {
            console.error('Failed to load mismatches:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredMismatches = mismatches.filter((mismatch) => {
        const matchesSearch = mismatch.txn_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
            mismatch.id.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesType = typeFilter === 'all' || mismatch.mismatch_type === typeFilter;
        return matchesSearch && matchesType;
    });

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div>
                <h1 className="text-3xl font-bold text-gradient mb-2">Mismatches</h1>
                <p className="text-dark-400">Review and resolve transaction discrepancies</p>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[
                    { type: 'amount_mismatch', label: 'Amount', count: mismatches.filter(m => m.mismatch_type === 'amount_mismatch').length },
                    { type: 'status_mismatch', label: 'Status', count: mismatches.filter(m => m.mismatch_type === 'status_mismatch').length },
                    { type: 'timestamp_mismatch', label: 'Timestamp', count: mismatches.filter(m => m.mismatch_type === 'timestamp_mismatch').length },
                    { type: 'missing_transaction', label: 'Missing', count: mismatches.filter(m => m.mismatch_type === 'missing_transaction').length },
                ].map((item) => (
                    <div key={item.type} className="glass-card p-4">
                        <p className="text-sm text-dark-400 mb-2">{item.label} Mismatches</p>
                        <p className="text-2xl font-bold text-dark-100">{item.count}</p>
                    </div>
                ))}
            </div>

            {/* Filters */}
            <div className="glass-card p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Search */}
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
                        <input
                            type="text"
                            placeholder="Search by Mismatch ID or Transaction ID..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="input-field pl-10"
                        />
                    </div>

                    {/* Type Filter */}
                    <select
                        value={typeFilter}
                        onChange={(e) => setTypeFilter(e.target.value)}
                        className="input-field"
                    >
                        <option value="all">All Types</option>
                        <option value="amount_mismatch">Amount Mismatch</option>
                        <option value="status_mismatch">Status Mismatch</option>
                        <option value="timestamp_mismatch">Timestamp Mismatch</option>
                        <option value="missing_transaction">Missing Transaction</option>
                    </select>
                </div>
            </div>

            {/* Mismatches List */}
            <div className="space-y-4">
                {loading ? (
                    Array.from({ length: 5 }).map((_, i) => (
                        <LoadingSkeleton key={i} className="h-32" />
                    ))
                ) : filteredMismatches.length === 0 ? (
                    <div className="glass-card p-12 text-center">
                        <AlertTriangle className="w-16 h-16 text-dark-600 mx-auto mb-4" />
                        <p className="text-dark-400 text-lg">No mismatches found</p>
                        <p className="text-dark-500 text-sm mt-2">Try adjusting your filters</p>
                    </div>
                ) : (
                    filteredMismatches.map((mismatch) => (
                        <div key={mismatch.id} className="glass-card-hover p-6">
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="p-3 rounded-lg bg-danger-light/20">
                                        <AlertTriangle className="w-6 h-6 text-danger-light" />
                                    </div>
                                    <div>
                                        <div className="flex items-center gap-2 mb-1">
                                            <h3 className="font-semibold text-dark-100">Mismatch {mismatch.id}</h3>
                                            <span className={getMismatchBadge(mismatch.mismatch_type)}>
                                                {mismatch.mismatch_type.replace('_', ' ')}
                                            </span>
                                        </div>
                                        <p className="text-sm text-dark-400">
                                            Transaction: <span className="font-mono text-primary-400">{mismatch.txn_id}</span>
                                        </p>
                                    </div>
                                </div>
                                <span className="text-xs text-dark-500">{formatDate(mismatch.detected_at)}</span>
                            </div>

                            <div className="bg-white/5 rounded-lg p-4 mb-4">
                                <p className="text-sm text-dark-200">{mismatch.details}</p>
                            </div>

                            <div className="flex gap-3">
                                <button className="btn-primary text-sm px-4 py-2">
                                    Investigate
                                </button>
                                <button className="btn-secondary text-sm px-4 py-2">
                                    Mark as Resolved
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};
