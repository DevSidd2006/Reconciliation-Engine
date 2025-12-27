import React, { useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext';
import { Layout } from './components/layout/Layout';
import Dashboard from './pages/Dashboard.jsx';
import { Transactions } from './pages/Transactions';
import TransactionDetails from './pages/TransactionDetails';
import { Mismatches } from './pages/Mismatches';
import { Reports } from './pages/Reports';
import { LiveStream } from './pages/LiveStream';
import { AIInsights } from './pages/AIInsights';
import { AuditLogs } from './pages/AuditLogs';
import { SystemHealth } from './pages/SystemHealth';
import { Settings } from './pages/Settings';
import ErrorBoundary from './components/common/ErrorBoundary';
import { NotificationContainer, useNotifications } from './components/common/Notification';
import './styles/index.css';

function ProtectedRoute({ element, authenticated, loading }) {
    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-dark-950 via-dark-900 to-dark-800">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
                    <p className="text-dark-300">Loading...</p>
                </div>
            </div>
        );
    }

    return authenticated ? element : <Navigate to="/" replace />;
}

function AppContent() {
    const authContext = useContext(AuthContext);
    const { authenticated, loading } = authContext || { authenticated: false, loading: true };
    const { notifications, removeNotification } = useNotifications();

    return (
        <>
            <NotificationContainer
                notifications={notifications}
                removeNotification={removeNotification}
            />
            <BrowserRouter>
                <Routes>
                    <Route 
                        path="/*" 
                        element={
                            <ProtectedRoute 
                                element={
                                    <Layout>
                                        <Routes>
                                            <Route path="/" element={<Dashboard />} />
                                            <Route path="transactions" element={<Transactions />} />
                                            <Route path="transactions/:id" element={<TransactionDetails />} />
                                            <Route path="mismatches" element={<Mismatches />} />
                                            <Route path="reports" element={<Reports />} />
                                            <Route path="live-stream" element={<LiveStream />} />
                                            <Route path="ai-insights" element={<AIInsights />} />
                                            <Route path="audit-logs" element={<AuditLogs />} />
                                            <Route path="system-health" element={<SystemHealth />} />
                                            <Route path="settings" element={<Settings />} />
                                        </Routes>
                                    </Layout>
                                }
                                authenticated={authenticated}
                                loading={loading}
                            />
                        }
                    />
                </Routes>
            </BrowserRouter>
        </>
    );
}

function App() {
    return (
        <ErrorBoundary>
            <AuthProvider>
                <AppContent />
            </AuthProvider>
        </ErrorBoundary>
    );
}

export default App;
