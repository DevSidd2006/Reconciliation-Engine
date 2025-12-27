import React from 'react';
import { Menu, Bell, User, LogOut, Wifi, WifiOff } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { useSocket } from '../../hooks/useSocket';

export const Header = ({ onMenuClick }) => {
    const { user, logout } = useAuth();
    const { isConnected } = useSocket();
    const [showUserMenu, setShowUserMenu] = React.useState(false);

    return (
        <header className="glass-card border-b border-white/10 sticky top-0 z-30">
            <div className="flex items-center justify-between px-6 py-4">
                {/* Left side */}
                <div className="flex items-center gap-4">
                    <button
                        onClick={onMenuClick}
                        className="lg:hidden text-dark-300 hover:text-dark-100 transition-colors"
                    >
                        <Menu className="w-6 h-6" />
                    </button>

                    <div className="hidden lg:block">
                        <h2 className="text-lg font-semibold text-dark-100">
                            Transaction Reconciliation Dashboard
                        </h2>
                        <p className="text-xs text-dark-400">Monitor real-time transaction mismatches</p>
                    </div>
                </div>

                {/* Right side */}
                <div className="flex items-center gap-4">
                    {/* Connection Status */}
                    <div className="flex items-center gap-2">
                        {isConnected ? (
                            <>
                                <Wifi className="w-4 h-4 text-success-light" />
                                <span className="text-xs text-success-light hidden sm:inline">Connected</span>
                            </>
                        ) : (
                            <>
                                <WifiOff className="w-4 h-4 text-danger-light" />
                                <span className="text-xs text-danger-light hidden sm:inline">Disconnected</span>
                            </>
                        )}
                    </div>

                    {/* Notifications */}
                    <button className="relative p-2 text-dark-300 hover:text-dark-100 transition-colors">
                        <Bell className="w-5 h-5" />
                        <span className="absolute top-1 right-1 w-2 h-2 bg-danger-light rounded-full"></span>
                    </button>

                    {/* User Menu */}
                    <div className="relative">
                        <button
                            onClick={() => setShowUserMenu(!showUserMenu)}
                            className="flex items-center gap-2 p-2 rounded-lg hover:bg-white/5 transition-colors"
                        >
                            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-primary-600 to-primary-500 flex items-center justify-center">
                                <User className="w-4 h-4 text-white" />
                            </div>
                            <span className="text-sm text-dark-200 hidden sm:inline">{user?.name || 'User'}</span>
                        </button>

                        {/* Dropdown */}
                        {showUserMenu && (
                            <>
                                <div
                                    className="fixed inset-0 z-40"
                                    onClick={() => setShowUserMenu(false)}
                                />
                                <div className="absolute right-0 mt-2 w-48 glass-card border border-white/10 rounded-lg shadow-xl z-50 animate-slide-down">
                                    <div className="p-3 border-b border-white/10">
                                        <p className="text-sm font-medium text-dark-100">{user?.name || 'Demo User'}</p>
                                        <p className="text-xs text-dark-400">{user?.email || 'demo@reconciliation.com'}</p>
                                    </div>
                                    <button
                                        onClick={() => {
                                            setShowUserMenu(false);
                                            logout();
                                        }}
                                        className="w-full flex items-center gap-2 px-3 py-2 text-sm text-danger-light hover:bg-danger-light/10 transition-colors"
                                    >
                                        <LogOut className="w-4 h-4" />
                                        Logout
                                    </button>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </header>
    );
};
