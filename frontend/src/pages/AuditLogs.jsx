import React, { useState, useEffect } from 'react';
import { 
    FileSearch, 
    Filter, 
    Download, 
    Eye,
    User,
    Clock,
    Shield,
    AlertTriangle,
    CheckCircle,
    Search
} from 'lucide-react';

const LogEntry = ({ log, index }) => {
    const getActionIcon = (action) => {
        switch (action) {
            case 'login': return <User className="w-4 h-4 text-success-light" />;
            case 'logout': return <User className="w-4 h-4 text-dark-400" />;
            case 'mismatch_resolved': return <CheckCircle className="w-4 h-4 text-success-light" />;
            case 'mismatch_detected': return <AlertTriangle className="w-4 h-4 text-danger-light" />;
            case 'system_access': return <Shield className="w-4 h-4 text-primary-400" />;
            case 'data_export': return <Download className="w-4 h-4 text-warning-light" />;
            default: return <Eye className="w-4 h-4 text-dark-400" />;
        }
    };

    const getSeverityColor = (severity) => {
        switch (severity) {
            case 'high': return 'text-danger-light bg-danger-light/10 border-danger-light/30';
            case 'medium': return 'text-warning-light bg-warning-light/10 border-warning-light/30';
            case 'low': return 'text-blue-400 bg-blue-400/10 border-blue-400/30';
            default: return 'text-dark-400 bg-dark-700/50 border-dark-600';
        }
    };

    return (
        <div className="glass-card p-4 mb-3 hover:bg-white/5 transition-colors">
            <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1">
                    <div className="mt-1">
                        {getActionIcon(log.action)}
                    </div>
                    
                    <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                            <h4 className="font-medium text-dark-100">{log.description}</h4>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getSeverityColor(log.severity)}`}>
                                {log.severity?.toUpperCase() || 'INFO'}
                            </span>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                            <div>
                                <span className="text-dark-500">User:</span>
                                <span className="text-dark-200 ml-2">{log.user}</span>
                            </div>
                            <div>
                                <span className="text-dark-500">Role:</span>
                                <span className="text-dark-200 ml-2">{log.role}</span>
                            </div>
                            <div>
                                <span className="text-dark-500">IP:</span>
                                <span className="text-dark-200 ml-2 font-mono">{log.ip}</span>
                            </div>
                            <div>
                                <span className="text-dark-500">Time:</span>
                                <span className="text-dark-200 ml-2">{log.timestamp}</span>
                            </div>
                        </div>
                        
                        {log.details && (
                            <div className="mt-3 p-3 bg-dark-800/50 rounded-lg">
                                <p className="text-sm text-dark-300">{log.details}</p>
                            </div>
                        )}
                        
                        {log.metadata && (
                            <div className="mt-2 flex flex-wrap gap-2">
                                {Object.entries(log.metadata).map(([key, value]) => (
                                    <span key={key} className="px-2 py-1 bg-dark-700 text-xs text-dark-300 rounded">
                                        {key}: {value}
                                    </span>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
                
                <button className="text-dark-400 hover:text-dark-200 transition-colors">
                    <Eye className="w-4 h-4" />
                </button>
            </div>
        </div>
    );
};

export const AuditLogs = () => {
    const [logs, setLogs] = useState([]);
    const [filteredLogs, setFilteredLogs] = useState([]);
    const [filters, setFilters] = useState({
        user: '',
        action: 'all',
        severity: 'all',
        dateRange: 'today',
        searchTerm: ''
    });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        generateAuditLogs();
    }, []);

    useEffect(() => {
        applyFilters();
    }, [logs, filters]);

    const generateAuditLogs = () => {
        const sampleLogs = [
            {
                id: 'LOG001',
                action: 'login',
                description: 'User successfully authenticated',
                user: 'john.doe@bank.com',
                role: 'Admin',
                ip: '192.168.1.100',
                timestamp: '2025-12-17 14:23:15',
                severity: 'low',
                details: 'Multi-factor authentication completed successfully',
                metadata: { 'session_id': 'sess_abc123', 'device': 'Chrome/Windows' }
            },
            {
                id: 'LOG002',
                action: 'mismatch_detected',
                description: 'Amount mismatch detected in transaction TXN789',
                user: 'system',
                role: 'System',
                ip: '10.0.0.1',
                timestamp: '2025-12-17 14:20:33',
                severity: 'high',
                details: 'Core Banking: $1000.00, Gateway: $999.95, Difference: $0.05',
                metadata: { 'transaction_id': 'TXN789', 'mismatch_type': 'amount', 'auto_resolved': 'false' }
            },
            {
                id: 'LOG003',
                action: 'mismatch_resolved',
                description: 'Mismatch TXN456 resolved by operator',
                user: 'jane.smith@bank.com',
                role: 'Operator',
                ip: '192.168.1.105',
                timestamp: '2025-12-17 14:18:42',
                severity: 'medium',
                details: 'Manual investigation completed. Marked as acceptable rounding difference.',
                metadata: { 'transaction_id': 'TXN456', 'resolution_time': '15min', 'resolution_type': 'manual' }
            },
            {
                id: 'LOG004',
                action: 'data_export',
                description: 'Transaction report exported',
                user: 'audit.user@bank.com',
                role: 'Auditor',
                ip: '192.168.1.110',
                timestamp: '2025-12-17 14:15:28',
                severity: 'medium',
                details: 'Daily reconciliation report exported for date range 2025-12-16 to 2025-12-17',
                metadata: { 'report_type': 'daily_summary', 'records_count': '1247', 'file_size': '2.3MB' }
            },
            {
                id: 'LOG005',
                action: 'system_access',
                description: 'Unauthorized access attempt blocked',
                user: 'unknown',
                role: 'Unknown',
                ip: '203.0.113.45',
                timestamp: '2025-12-17 14:12:15',
                severity: 'high',
                details: 'Multiple failed login attempts from suspicious IP address. Account temporarily locked.',
                metadata: { 'attempts': '5', 'blocked_duration': '30min', 'threat_level': 'high' }
            },
            {
                id: 'LOG006',
                action: 'logout',
                description: 'User session terminated',
                user: 'operator.test@bank.com',
                role: 'Operator',
                ip: '192.168.1.102',
                timestamp: '2025-12-17 14:10:45',
                severity: 'low',
                details: 'Normal session logout after 2 hours of activity',
                metadata: { 'session_duration': '2h 15m', 'actions_performed': '23' }
            }
        ];
        
        setLogs(sampleLogs);
    };

    const applyFilters = () => {
        let filtered = [...logs];

        if (filters.user) {
            filtered = filtered.filter(log => 
                log.user.toLowerCase().includes(filters.user.toLowerCase())
            );
        }

        if (filters.action !== 'all') {
            filtered = filtered.filter(log => log.action === filters.action);
        }

        if (filters.severity !== 'all') {
            filtered = filtered.filter(log => log.severity === filters.severity);
        }

        if (filters.searchTerm) {
            filtered = filtered.filter(log =>
                log.description.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
                log.details?.toLowerCase().includes(filters.searchTerm.toLowerCase())
            );
        }

        setFilteredLogs(filtered);
    };

    const exportLogs = () => {
        setLoading(true);
        setTimeout(() => {
            const csvContent = [
                'ID,Action,Description,User,Role,IP,Timestamp,Severity,Details',
                ...filteredLogs.map(log => 
                    `${log.id},${log.action},${log.description},${log.user},${log.role},${log.ip},${log.timestamp},${log.severity},"${log.details}"`
                )
            ].join('\n');

            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `audit_logs_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            setLoading(false);
        }, 1000);
    };

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-dark-100 flex items-center gap-3">
                        <FileSearch className="w-8 h-8 text-primary-400" />
                        Audit Logs
                    </h1>
                    <p className="text-dark-400 mt-2">Complete system activity and security audit trail</p>
                </div>
                
                <button
                    onClick={exportLogs}
                    disabled={loading}
                    className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white rounded-lg transition-colors"
                >
                    {loading ? (
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                        <Download className="w-4 h-4" />
                    )}
                    Export Logs
                </button>
            </div>

            {/* Filters */}
            <div className="glass-card p-6 mb-6">
                <div className="flex items-center gap-4 mb-4">
                    <Filter className="w-5 h-5 text-primary-400" />
                    <h3 className="text-lg font-semibold text-dark-100">Filter Logs</h3>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-dark-300 mb-2">Search</label>
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-dark-400" />
                            <input
                                type="text"
                                placeholder="Search logs..."
                                value={filters.searchTerm}
                                onChange={(e) => setFilters(prev => ({ ...prev, searchTerm: e.target.value }))}
                                className="w-full pl-10 bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-dark-100 focus:border-primary-500 focus:outline-none"
                            />
                        </div>
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-dark-300 mb-2">User</label>
                        <input
                            type="text"
                            placeholder="Filter by user..."
                            value={filters.user}
                            onChange={(e) => setFilters(prev => ({ ...prev, user: e.target.value }))}
                            className="w-full bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-dark-100 focus:border-primary-500 focus:outline-none"
                        />
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-dark-300 mb-2">Action</label>
                        <select
                            value={filters.action}
                            onChange={(e) => setFilters(prev => ({ ...prev, action: e.target.value }))}
                            className="w-full bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-dark-100 focus:border-primary-500 focus:outline-none"
                        >
                            <option value="all">All Actions</option>
                            <option value="login">Login</option>
                            <option value="logout">Logout</option>
                            <option value="mismatch_detected">Mismatch Detected</option>
                            <option value="mismatch_resolved">Mismatch Resolved</option>
                            <option value="system_access">System Access</option>
                            <option value="data_export">Data Export</option>
                        </select>
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-dark-300 mb-2">Severity</label>
                        <select
                            value={filters.severity}
                            onChange={(e) => setFilters(prev => ({ ...prev, severity: e.target.value }))}
                            className="w-full bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-dark-100 focus:border-primary-500 focus:outline-none"
                        >
                            <option value="all">All Severities</option>
                            <option value="high">High</option>
                            <option value="medium">Medium</option>
                            <option value="low">Low</option>
                        </select>
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-dark-300 mb-2">Date Range</label>
                        <select
                            value={filters.dateRange}
                            onChange={(e) => setFilters(prev => ({ ...prev, dateRange: e.target.value }))}
                            className="w-full bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-dark-100 focus:border-primary-500 focus:outline-none"
                        >
                            <option value="today">Today</option>
                            <option value="week">This Week</option>
                            <option value="month">This Month</option>
                            <option value="all">All Time</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                <div className="glass-card p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-dark-400 text-sm">Total Logs</p>
                            <p className="text-2xl font-bold text-dark-100">{filteredLogs.length}</p>
                        </div>
                        <FileSearch className="w-8 h-8 text-primary-400" />
                    </div>
                </div>
                
                <div className="glass-card p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-dark-400 text-sm">High Severity</p>
                            <p className="text-2xl font-bold text-danger-light">
                                {filteredLogs.filter(log => log.severity === 'high').length}
                            </p>
                        </div>
                        <AlertTriangle className="w-8 h-8 text-danger-light" />
                    </div>
                </div>
                
                <div className="glass-card p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-dark-400 text-sm">Security Events</p>
                            <p className="text-2xl font-bold text-warning-light">
                                {filteredLogs.filter(log => log.action === 'system_access' || log.action === 'login').length}
                            </p>
                        </div>
                        <Shield className="w-8 h-8 text-warning-light" />
                    </div>
                </div>
                
                <div className="glass-card p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-dark-400 text-sm">Active Users</p>
                            <p className="text-2xl font-bold text-success-light">
                                {new Set(filteredLogs.map(log => log.user)).size}
                            </p>
                        </div>
                        <User className="w-8 h-8 text-success-light" />
                    </div>
                </div>
            </div>

            {/* Audit Log Entries */}
            <div className="glass-card p-6">
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-dark-100">Audit Trail</h3>
                    <p className="text-sm text-dark-400">
                        Showing {filteredLogs.length} of {logs.length} entries
                    </p>
                </div>

                <div className="space-y-0">
                    {filteredLogs.length > 0 ? (
                        filteredLogs.map((log, index) => (
                            <LogEntry key={log.id} log={log} index={index} />
                        ))
                    ) : (
                        <div className="text-center py-8">
                            <FileSearch className="w-12 h-12 text-dark-500 mx-auto mb-3" />
                            <p className="text-dark-400">No audit logs match current filters</p>
                            <p className="text-dark-500 text-sm">Try adjusting your search criteria</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};