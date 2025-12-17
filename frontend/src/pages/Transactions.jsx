import React, { useState, useEffect } from 'react';
import { Search, Filter, Download, ArrowUpDown } from 'lucide-react';
import { transactionAPI } from '../services/api';
import { LoadingSpinner, LoadingSkeleton } from '../components/common/LoadingSpinner';
import { formatCurrency, formatDate, getStatusBadge, getSourceColor } from '../utils/helpers';

export const Transactions = () => {
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [sourceFilter, setSourceFilter] = useState('all');
    const [statusFilter, setStatusFilter] = useState('all');

    useEffect(() => {
        loadTransactions();
    }, []);

    const loadTransactions = async () => {
        try {
            setLoading(true);
            // Mock data for now - replace with actual API call when backend is ready
            const mockTransactions = Array.from({ length: 20 }, (_, i) => ({
                txn_id: `TXN${String(i + 1).padStart(6, '0')}`,
                amount: Math.random() * 10000 + 100,
                status: ['success', 'pending', 'failed'][Math.floor(Math.random() * 3)],
                timestamp: new Date(Date.now() - Math.random() * 86400000).toISOString(),
                currency: 'USD',
                account_id: `ACC${Math.floor(Math.random() * 1000)}`,
                source: ['core', 'gateway', 'mobile'][Math.floor(Math.random() * 3)],
            }));
            setTransactions(mockTransactions);
        } catch (error) {
            console.error('Failed to load transactions:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredTransactions = transactions.filter((txn) => {
        const matchesSearch = txn.txn_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
            txn.account_id.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesSource = sourceFilter === 'all' || txn.source === sourceFilter;
        const matchesStatus = statusFilter === 'all' || txn.status === statusFilter;
        return matchesSearch && matchesSource && matchesStatus;
    });

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gradient mb-2">Transactions</h1>
                    <p className="text-dark-400">View and manage all transaction records</p>
                </div>
                <button className="btn-primary flex items-center gap-2">
                    <Download className="w-4 h-4" />
                    Export
                </button>
            </div>

            {/* Filters */}
            <div className="glass-card p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Search */}
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
                        <input
                            type="text"
                            placeholder="Search by ID or Account..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="input-field pl-10"
                        />
                    </div>

                    {/* Source Filter */}
                    <select
                        value={sourceFilter}
                        onChange={(e) => setSourceFilter(e.target.value)}
                        className="input-field"
                    >
                        <option value="all">All Sources</option>
                        <option value="core">Core Banking</option>
                        <option value="gateway">Payment Gateway</option>
                        <option value="mobile">Mobile App</option>
                    </select>

                    {/* Status Filter */}
                    <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        className="input-field"
                    >
                        <option value="all">All Status</option>
                        <option value="success">Success</option>
                        <option value="pending">Pending</option>
                        <option value="failed">Failed</option>
                    </select>
                </div>
            </div>

            {/* Transactions Table */}
            <div className="glass-card overflow-hidden">
                <div className="overflow-x-auto custom-scrollbar">
                    <table className="w-full">
                        <thead className="bg-white/5 border-b border-white/10">
                            <tr>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-dark-300 uppercase tracking-wider">
                                    Transaction ID
                                </th>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-dark-300 uppercase tracking-wider">
                                    Amount
                                </th>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-dark-300 uppercase tracking-wider">
                                    Status
                                </th>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-dark-300 uppercase tracking-wider">
                                    Source
                                </th>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-dark-300 uppercase tracking-wider">
                                    Account
                                </th>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-dark-300 uppercase tracking-wider">
                                    Timestamp
                                </th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/10">
                            {loading ? (
                                Array.from({ length: 5 }).map((_, i) => (
                                    <tr key={i}>
                                        <td colSpan="6" className="px-6 py-4">
                                            <LoadingSkeleton className="h-6" />
                                        </td>
                                    </tr>
                                ))
                            ) : filteredTransactions.length === 0 ? (
                                <tr>
                                    <td colSpan="6" className="px-6 py-8 text-center text-dark-400">
                                        No transactions found
                                    </td>
                                </tr>
                            ) : (
                                filteredTransactions.map((txn) => (
                                    <tr
                                        key={txn.txn_id}
                                        className="hover:bg-white/5 transition-colors cursor-pointer"
                                        onClick={() => window.location.href = `/transactions/${txn.txn_id}`}
                                    >
                                        <td className="px-6 py-4">
                                            <span className="font-mono text-sm text-primary-400">{txn.txn_id}</span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className="font-semibold text-dark-100">
                                                {formatCurrency(txn.amount, txn.currency)}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`${getStatusBadge(txn.status)} capitalize`}>
                                                {txn.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`${getSourceColor(txn.source)} font-medium capitalize`}>
                                                {txn.source}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className="text-sm text-dark-300">{txn.account_id}</span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className="text-sm text-dark-400">{formatDate(txn.timestamp)}</span>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination */}
                {!loading && filteredTransactions.length > 0 && (
                    <div className="px-6 py-4 border-t border-white/10 flex items-center justify-between">
                        <p className="text-sm text-dark-400">
                            Showing {filteredTransactions.length} of {transactions.length} transactions
                        </p>
                        <div className="flex gap-2">
                            <button className="btn-secondary px-4 py-2 text-sm">Previous</button>
                            <button className="btn-secondary px-4 py-2 text-sm">Next</button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
