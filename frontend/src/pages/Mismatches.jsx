import React, { useState, useEffect } from 'react';
import { Search, AlertTriangle } from 'lucide-react';
import { mismatchAPI } from '../services/api';
import { LoadingSpinner, LoadingSkeleton } from '../components/common/LoadingSpinner';
import { formatDate, getMismatchBadge } from '../utils/helpers';

export const Mismatches = () => {
    // Data Loading State
    const [mismatches, setMismatches] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [typeFilter, setTypeFilter] = useState('all');

    // Resolution Modal State
    const [selectedMismatch, setSelectedMismatch] = useState(null);
    const [resolutionNotes, setResolutionNotes] = useState("");
    const [resolving, setResolving] = useState(false);

    useEffect(() => {
        loadMismatches();
    }, []);

    const loadMismatches = async () => {
        try {
            setLoading(true);
            const response = await mismatchAPI.getAll();
            // Backend returns wrapped response: { status: "success", data: [...] }
            setMismatches(response.data || []);
        } catch (error) {
            console.error('Failed to load mismatches:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleResolveClick = (mismatch) => {
        setSelectedMismatch(mismatch);
        setResolutionNotes("");
    };

    const confirmResolve = async () => {
        if (!selectedMismatch) return;
        try {
            setResolving(true);
            await mismatchAPI.resolve(selectedMismatch.id, { notes: resolutionNotes });

            // Optimistic update
            setMismatches(prev => prev.map(m =>
                m.id === selectedMismatch.id
                    ? { ...m, status: 'RESOLVED', resolution_notes: resolutionNotes }
                    : m
            ));

            setSelectedMismatch(null);
        } catch (error) {
            console.error("Failed to resolve:", error);
            alert("Failed to resolve mismatch. Please try again.");
        } finally {
            setResolving(false);
        }
    };

    const filteredMismatches = mismatches.filter((mismatch) => {
        const matchesSearch = String(mismatch.txn_id).toLowerCase().includes(searchTerm.toLowerCase()) ||
            String(mismatch.id).toLowerCase().includes(searchTerm.toLowerCase());
        const matchesType = typeFilter === 'all' || mismatch.mismatch_type === typeFilter;
        return matchesSearch && matchesType;
    });

    return (
        <div className="space-y-6 relative">
            {/* Resolution Modal */}
            {selectedMismatch && (
                <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
                    <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 max-w-md w-full">
                        <h3 className="text-xl font-bold text-white mb-4">Resolve Mismatch</h3>
                        <p className="text-gray-400 mb-2">ID: {selectedMismatch.id}</p>
                        <p className="text-gray-400 mb-4 text-sm">{selectedMismatch.details}</p>

                        <div className="mb-4">
                            <label className="block text-gray-300 mb-2 text-sm">Resolution Notes</label>
                            <textarea
                                className="w-full bg-gray-900 border border-gray-700 rounded p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                rows="3"
                                placeholder="Explain how this was resolved..."
                                value={resolutionNotes}
                                onChange={(e) => setResolutionNotes(e.target.value)}
                            />
                        </div>

                        <div className="flex justify-end gap-3">
                            <button
                                onClick={() => setSelectedMismatch(null)}
                                className="px-4 py-2 text-gray-300 hover:text-white"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={confirmResolve}
                                disabled={resolving}
                                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded font-medium flex items-center"
                            >
                                {resolving ? <LoadingSpinner className="w-4 h-4 mr-2" /> : null}
                                Confirm Resolution
                            </button>
                        </div>
                    </div>
                </div>
            )}

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
                                    <div className={`p-3 rounded-lg ${mismatch.status === 'RESOLVED' ? 'bg-green-900/20' : 'bg-red-900/20'}`}>
                                        <AlertTriangle className={`w-6 h-6 ${mismatch.status === 'RESOLVED' ? 'text-green-500' : 'text-red-500'}`} />
                                    </div>
                                    <div>
                                        <div className="flex items-center gap-2 mb-1">
                                            <h3 className="font-semibold text-dark-100">Mismatch {mismatch.id}</h3>
                                            <span className={getMismatchBadge(mismatch.mismatch_type)}>
                                                {mismatch.mismatch_type.replace('_', ' ')}
                                            </span>
                                            {mismatch.status === 'RESOLVED' && (
                                                <span className="px-2 py-0.5 rounded text-xs bg-green-900 text-green-400 border border-green-800">
                                                    RESOLVED
                                                </span>
                                            )}
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
                                {mismatch.resolution_notes && (
                                    <div className="mt-2 pt-2 border-t border-white/10 text-xs text-green-400">
                                        <span className="font-bold">Resolution:</span> {mismatch.resolution_notes}
                                    </div>
                                )}
                            </div>

                            <div className="flex gap-3">
                                <button className="btn-primary text-sm px-4 py-2">
                                    Investigate
                                </button>
                                {mismatch.status !== 'RESOLVED' && (
                                    <button
                                        onClick={() => handleResolveClick(mismatch)}
                                        className="btn-secondary text-sm px-4 py-2"
                                    >
                                        Mark as Resolved
                                    </button>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};
