import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
    LayoutDashboard, 
    ArrowLeftRight, 
    AlertTriangle, 
    X, 
    Menu,
    FileText,
    Radio,
    Brain,
    FileSearch,
    Activity,
    Settings,
    Shield
} from 'lucide-react';

const menuItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/transactions', icon: ArrowLeftRight, label: 'Transactions' },
    { path: '/mismatches', icon: AlertTriangle, label: 'Mismatches' },
    { path: '/reports', icon: FileText, label: 'Reports' },
    { path: '/live-stream', icon: Radio, label: 'Live Stream' },
    { path: '/ai-insights', icon: Brain, label: 'AI Insights' },
    { path: '/audit-logs', icon: FileSearch, label: 'Audit Logs' },
    { path: '/system-health', icon: Activity, label: 'System Health' },
    { path: '/settings', icon: Settings, label: 'Settings' },
];

export const Sidebar = ({ isOpen, onClose }) => {
    const location = useLocation();

    return (
        <>
            {/* Mobile overlay */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-dark-950/80 backdrop-blur-sm z-40 lg:hidden"
                    onClick={onClose}
                />
            )}

            {/* Sidebar */}
            <aside
                className={`
          fixed top-0 left-0 h-full w-64 glass-card border-r border-white/10 z-50
          transform transition-transform duration-300 ease-in-out
          lg:translate-x-0 lg:static
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
            >
                <div className="flex flex-col h-full">
                    {/* Logo */}
                    <div className="p-6 border-b border-white/10 flex items-center justify-between">
                        <div>
                            <h1 className="text-xl font-bold text-gradient">Reconciliation</h1>
                            <p className="text-xs text-dark-400 mt-1">Real-Time Engine</p>
                        </div>
                        <button
                            onClick={onClose}
                            className="lg:hidden text-dark-400 hover:text-dark-200"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Navigation */}
                    <nav className="flex-1 p-4 space-y-2">
                        {menuItems.map((item) => {
                            const Icon = item.icon;
                            const isActive = location.pathname === item.path;

                            return (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    onClick={onClose}
                                    className={`
                    flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200
                    ${isActive
                                            ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                                            : 'text-dark-300 hover:bg-white/5 hover:text-dark-100'
                                        }
                  `}
                                >
                                    <Icon className="w-5 h-5" />
                                    <span className="font-medium">{item.label}</span>
                                </Link>
                            );
                        })}
                    </nav>

                    {/* Footer */}
                    <div className="p-4 border-t border-white/10">
                        <div className="glass-card p-3">
                            <p className="text-xs text-dark-400">Version 1.0.0</p>
                            <p className="text-xs text-dark-500 mt-1">© 2025 Reconciliation Engine</p>
                        </div>
                    </div>
                </div>
            </aside>
        </>
    );
};
