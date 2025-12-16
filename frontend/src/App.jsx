import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Layout } from './components/layout/Layout';
import Dashboard from './pages/Dashboard.jsx';
import { Transactions } from './pages/Transactions';
import { Mismatches } from './pages/Mismatches';
import ErrorBoundary from './components/common/ErrorBoundary';
import { NotificationContainer, useNotifications } from './components/common/Notification';
import './styles/index.css';

function AppContent() {
    const { notifications, removeNotification } = useNotifications();

    return (
        <>
            <NotificationContainer
                notifications={notifications}
                removeNotification={removeNotification}
            />
            <BrowserRouter>
                <Layout>
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/transactions" element={<Transactions />} />
                        <Route path="/mismatches" element={<Mismatches />} />
                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </Layout>
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
