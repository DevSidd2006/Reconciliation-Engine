import React, { useState, useEffect } from 'react';
import { TransactionsTable, MismatchesTable, FiltersBar } from '../components/dashboard';
import MismatchHeatmap from '../components/dashboard/MismatchHeatmap';
import { KPICards } from '../components/dashboard/KPICards';
import { RealTimeChart } from '../components/dashboard/RealTimeChart';
import { AIInsightPanel } from '../components/dashboard/AIInsightPanel';
import { useTransactions, useMismatches } from '../hooks';

const LoadingSpinner = () => (
  <div className="flex justify-center items-center py-8">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
  </div>
);

const ErrorMessage = ({ message, onRetry }) => (
  <div className="bg-danger-light/20 border border-danger-light/30 rounded-lg p-4">
    <div className="flex items-center justify-between">
      <p className="text-danger-light">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-3 py-1 text-sm bg-danger-light/20 text-danger-light rounded hover:bg-danger-light/30 transition-colors"
        >
          Retry
        </button>
      )}
    </div>
  </div>
);

export default function Dashboard() {
  const [filters, setFilters] = useState({
    date: '',
    source: '',
    status: ''
  });

  const [stats, setStats] = useState({
    totalTransactions: 0,
    matchedTransactions: 0,
    mismatches: 0,
    pendingTransactions: 0,
    highRiskAlerts: 0
  });

  const { transactions, loading: transactionsLoading, error: transactionsError, refetch: refetchTransactions } = useTransactions();
  const { mismatches, loading: mismatchesLoading, error: mismatchesError, refetch: refetchMismatches } = useMismatches();

  // Calculate stats from transactions and mismatches
  useEffect(() => {
    if (transactions.length > 0) {
      const totalTransactions = transactions.length;
      const matchedTransactions = transactions.filter(t => t.status === 'matched').length;
      const pendingTransactions = transactions.filter(t => t.status === 'pending').length;
      const mismatchCount = mismatches.length;
      const highRiskAlerts = mismatches.filter(m => m.severity === 'high').length;

      setStats({
        totalTransactions,
        matchedTransactions,
        mismatches: mismatchCount,
        pendingTransactions,
        highRiskAlerts
      });
    }
  }, [transactions, mismatches]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      refetchTransactions();
      refetchMismatches();
    }, 30000);

    return () => clearInterval(interval);
  }, [refetchTransactions, refetchMismatches]);

  // Filter transactions based on current filters
  const filteredTransactions = transactions.filter(transaction => {
    if (filters.source && transaction.source !== filters.source) {
      return false;
    }
    if (filters.status && transaction.status !== filters.status) {
      return false;
    }
    if (filters.date && !transaction.timestamp?.startsWith(filters.date)) {
      return false;
    }
    return true;
  });

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-dark-100">
            Banking Reconciliation Dashboard
          </h1>
          <p className="text-dark-400 mt-2">Real-time transaction monitoring and mismatch detection</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-dark-400">Last sync:</p>
          <p className="text-sm text-dark-200">{new Date().toLocaleString()}</p>
        </div>
      </div>

      {/* KPI Summary Cards */}
      <KPICards stats={stats} />

      {/* Real-Time Streaming Chart */}
      <RealTimeChart />

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-8">
        {/* Recent Transactions */}
        <div className="xl:col-span-1">
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4 text-dark-100">Recent Transactions</h3>
            {transactionsLoading ? (
              <LoadingSpinner />
            ) : transactionsError ? (
              <ErrorMessage message={transactionsError} onRetry={refetchTransactions} />
            ) : (
              <TransactionsTable transactions={filteredTransactions.slice(0, 5)} compact={true} />
            )}
          </div>
        </div>

        {/* Recent Mismatches */}
        <div className="xl:col-span-1">
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4 text-dark-100">Recent Mismatches</h3>
            {mismatchesLoading ? (
              <LoadingSpinner />
            ) : mismatchesError ? (
              <ErrorMessage message={mismatchesError} onRetry={refetchMismatches} />
            ) : (
              <MismatchesTable mismatches={mismatches.slice(0, 5)} compact={true} />
            )}
          </div>
        </div>

        {/* AI Insights Panel */}
        <div className="xl:col-span-1">
          <AIInsightPanel />
        </div>
      </div>

      {/* Mismatch Heatmap */}
      <div className="mb-8">
        <MismatchHeatmap data={mismatches} />
      </div>

      {/* Filters and Full Tables */}
      <FiltersBar filters={filters} setFilters={setFilters} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4 text-dark-100">All Transactions</h3>
          {transactionsLoading ? (
            <LoadingSpinner />
          ) : transactionsError ? (
            <ErrorMessage message={transactionsError} onRetry={refetchTransactions} />
          ) : (
            <TransactionsTable transactions={filteredTransactions} />
          )}
        </div>

        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4 text-dark-100">All Mismatches</h3>
          {mismatchesLoading ? (
            <LoadingSpinner />
          ) : mismatchesError ? (
            <ErrorMessage message={mismatchesError} onRetry={refetchMismatches} />
          ) : (
            <MismatchesTable mismatches={mismatches} />
          )}
        </div>
      </div>
    </div>
  );
}