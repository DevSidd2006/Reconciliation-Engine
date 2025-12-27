import React, { useState, useEffect } from 'react';
import { 
    Radio, 
    Pause, 
    Play, 
    Filter,
    AlertTriangle,
    CheckCircle,
    Clock,
    Zap
} from 'lucide-react';
import { useSocket } from '../hooks/useSocket';

const TransactionStream = ({ transaction, index }) => {
    const getSourceColor = (source) => {
        const colors = {
            'core': 'from-blue-600 to-blue-500',
            'gateway': 'from-green-600 to-green-500',
            'mobile': 'from-purple-600 to-purple-500'
        };
        return colors[source] || 'from-gray-600 to-gray-500';
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'matched': return <CheckCircle className="w-4 h-4 text-success-light" />;
            case 'mismatch': return <AlertTriangle className="w-4 h-4 text-danger-light" />;
            case 'pending': return <Clock className="w-4 h-4 text-warning-light" />;
            default: return <Zap className="w-4 h-4 text-primary-400" />;
        }
    };

    return (
        <div 
            className="flex items-center gap-4 p-4 glass-card mb-2 animate-slide-down"
            style={{ animationDelay: `${index * 0.1}s` }}
        >
            <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${getSourceColor(transaction.source)} animate-pulse`}></div>
            
            <div className="flex-1 grid grid-cols-1 md:grid-cols-6 gap-4 items-center">
                <div>
                    <p className="text-sm font-mono text-dark-100">{transaction.id}</p>
                    <p className="text-xs text-dark-400">{transaction.source}</p>
                </div>
                
                <div>
                    <p className="text-sm font-semibold text-dark-100">${transaction.amount}</p>
                </div>
                
                <div className="flex items-center gap-2">
                    {getStatusIcon(transaction.status)}
                    <span className="text-sm text-dark-200 capitalize">{transaction.status}</span>
                </div>
                
                <div>
                    <p className="text-xs text-dark-400">{transaction.timestamp}</p>
                </div>
                
                <div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        transaction.latency < 1000 ? 'bg-success-light/20 text-success-light' :
                        transaction.latency < 2000 ? 'bg-warning-light/20 text-warning-light' :
                        'bg-danger-light/20 text-danger-light'
                    }`}>
                        {transaction.latency}ms
                    </span>
                </div>
                
                <div>
                    {transaction.mismatch && (
                        <span className="px-2 py-1 bg-danger-light/20 text-danger-light rounded-full text-xs font-medium">
                            MISMATCH
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
};

export const LiveStream = () => {
    const [isStreaming, setIsStreaming] = useState(true);
    const [transactions, setTransactions] = useState([]);
    const [filters, setFilters] = useState({
        source: 'all',
        status: 'all',
        showMismatchesOnly: false
    });
    const [stats, setStats] = useState({
        totalEvents: 0,
        eventsPerMinute: 0,
        queueSize: 0,
        avgLatency: 0
    });

    const { socket } = useSocket();

    // Generate mock transaction stream
    useEffect(() => {
        if (!isStreaming) return;

        const generateTransaction = () => {
            const sources = ['core', 'gateway', 'mobile'];
            const statuses = ['matched', 'pending', 'mismatch'];
            const source = sources[Math.floor(Math.random() * sources.length)];
            
            return {
                id: `TXN${Date.now().toString().slice(-6)}`,
                source,
                amount: (Math.random() * 10000).toFixed(2),
                status: statuses[Math.floor(Math.random() * statuses.length)],
                timestamp: new Date().toLocaleTimeString(),
                latency: Math.floor(Math.random() * 3000) + 200,
                mismatch: Math.random() < 0.1 // 10% chance of mismatch
            };
        };

        const interval = setInterval(() => {
            const newTransaction = generateTransaction();
            setTransactions(prev => [newTransaction, ...prev.slice(0, 49)]); // Keep last 50
            
            // Update stats
            setStats(prev => ({
                totalEvents: prev.totalEvents + 1,
                eventsPerMinute: Math.floor(Math.random() * 200) + 50,
                queueSize: Math.floor(Math.random() * 100) + 10,
                avgLatency: Math.floor(Math.random() * 1000) + 500
            }));
        }, 1000 + Math.random() * 2000); // Random interval between 1-3 seconds

        return () => clearInterval(interval);
    }, [isStreaming]);

    // Listen for real-time updates via socket
    useEffect(() => {
        if (socket) {
            socket.on('new_transaction', (transaction) => {
                setTransactions(prev => [transaction, ...prev.slice(0, 49)]);
            });

            socket.on('new_mismatch', (mismatch) => {
                // Flash mismatch notification
                console.log('New mismatch detected:', mismatch);
            });

            return () => {
                socket.off('new_transaction');
                socket.off('new_mismatch');
            };
        }
    }, [socket]);

    const filteredTransactions = transactions.filter(transaction => {
        if (filters.source !== 'all' && transaction.source !== filters.source) return false;
        if (filters.status !== 'all' && transaction.status !== filters.status) return false;
        if (filters.showMismatchesOnly && !transaction.mismatch) return false;
        return true;
    });

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-dark-100 flex items-center gap-3">
                        <Radio className="w-8 h-8 text-primary-400" />
                        Live Transaction Stream
                    </h1>
                    <p className="text-dark-400 mt-2">Real-time monitoring of all transaction events</p>
                </div>
                
                <button
                    onClick={() => setIsStreaming(!isStreaming)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                        isStreaming 
                            ? 'bg-danger-600 hover:bg-danger-700 text-white' 
                            : 'bg-success-600 hover:bg-success-700 text-white'
                    }`}
                >
                    {isStreaming ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    {isStreaming ? 'Pause Stream' : 'Resume Stream'}
                </button>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div className="glass-card p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-dark-400 text-sm">Total Events</p>
                            <p className="text-2xl font-bold text-dark-100">{stats.totalEvents.toLocaleString()}</p>
                        </div>
                        <Zap className="w-8 h-8 text-primary-400" />
                    </div>
                </div>
                
                <div className="glass-card p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-dark-400 text-sm">Events/Min</p>
                            <p className="text-2xl font-bold text-dark-100">{stats.eventsPerMinute}</p>
                        </div>
                        <Radio className="w-8 h-8 text-success-light" />
                    </div>
                </div>
                
                <div className="glass-card p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-dark-400 text-sm">Queue Size</p>
                            <p className="text-2xl font-bold text-dark-100">{stats.queueSize}</p>
                        </div>
                        <Clock className="w-8 h-8 text-warning-light" />
                    </div>
                </div>
                
                <div className="glass-card p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-dark-400 text-sm">Avg Latency</p>
                            <p className="text-2xl font-bold text-dark-100">{stats.avgLatency}ms</p>
                        </div>
                        <AlertTriangle className="w-8 h-8 text-danger-light" />
                    </div>
                </div>
            </div>

            {/* Filters */}
            <div className="glass-card p-6 mb-6">
                <div className="flex items-center gap-4 mb-4">
                    <Filter className="w-5 h-5 text-primary-400" />
                    <h3 className="text-lg font-semibold text-dark-100">Stream Filters</h3>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-dark-300 mb-2">Source</label>
                        <select
                            value={filters.source}
                            onChange={(e) => setFilters(prev => ({ ...prev, source: e.target.value }))}
                            className="w-full bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-dark-100 focus:border-primary-500 focus:outline-none"
                        >
                            <option value="all">All Sources</option>
                            <option value="core">Core Banking</option>
                            <option value="gateway">Payment Gateway</option>
                            <option value="mobile">Mobile App</option>
                        </select>
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-dark-300 mb-2">Status</label>
                        <select
                            value={filters.status}
                            onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                            className="w-full bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-dark-100 focus:border-primary-500 focus:outline-none"
                        >
                            <option value="all">All Statuses</option>
                            <option value="matched">Matched</option>
                            <option value="pending">Pending</option>
                            <option value="mismatch">Mismatch</option>
                        </select>
                    </div>
                    
                    <div className="flex items-end">
                        <label className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                checked={filters.showMismatchesOnly}
                                onChange={(e) => setFilters(prev => ({ ...prev, showMismatchesOnly: e.target.checked }))}
                                className="rounded border-dark-600 bg-dark-800 text-primary-600 focus:ring-primary-500"
                            />
                            <span className="text-sm text-dark-300">Mismatches Only</span>
                        </label>
                    </div>
                </div>
            </div>

            {/* Transaction Stream */}
            <div className="glass-card p-6">
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-dark-100">Live Transaction Feed</h3>
                    <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${isStreaming ? 'bg-success-light animate-pulse' : 'bg-gray-500'}`}></div>
                        <span className="text-sm text-dark-300">{isStreaming ? 'Streaming' : 'Paused'}</span>
                    </div>
                </div>

                {/* Table Header */}
                <div className="grid grid-cols-1 md:grid-cols-6 gap-4 p-4 border-b border-white/10 mb-4">
                    <div className="text-sm font-medium text-dark-300">Transaction ID</div>
                    <div className="text-sm font-medium text-dark-300">Amount</div>
                    <div className="text-sm font-medium text-dark-300">Status</div>
                    <div className="text-sm font-medium text-dark-300">Time</div>
                    <div className="text-sm font-medium text-dark-300">Latency</div>
                    <div className="text-sm font-medium text-dark-300">Alerts</div>
                </div>

                {/* Transaction List */}
                <div className="max-h-96 overflow-y-auto custom-scrollbar">
                    {filteredTransactions.length > 0 ? (
                        filteredTransactions.map((transaction, index) => (
                            <TransactionStream key={transaction.id} transaction={transaction} index={index} />
                        ))
                    ) : (
                        <div className="text-center py-8">
                            <Radio className="w-12 h-12 text-dark-500 mx-auto mb-3" />
                            <p className="text-dark-400">No transactions match current filters</p>
                            <p className="text-dark-500 text-sm">Adjust filters or wait for new events</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};