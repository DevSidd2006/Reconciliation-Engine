import React, { useState } from 'react';
import { TransactionsTable, MismatchesTable, FiltersBar } from '../components/dashboard';
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

  const { transactions, loading: transactionsLoading, error: transactionsError, refetch: refetchTransactions } = useTransactions();
  const { mismatches, loading: mismatchesLoading, error: mismatchesError, refetch: refetchMismatches } = useMismatches();

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
      <h1 className="text-3xl font-bold text-dark-100 mb-6">
        Transaction Reconciliation Dashboard
      </h1>

      <FiltersBar filters={filters} setFilters={setFilters} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h2 className="text-xl font-semibold mb-4 text-dark-100">Recent Transactions</h2>
          {transactionsLoading ? (
            <LoadingSpinner />
          ) : transactionsError ? (
            <ErrorMessage message={transactionsError} onRetry={refetchTransactions} />
          ) : (
            <TransactionsTable transactions={filteredTransactions.slice(0, 10)} />
          )}
        </div>

        <div>
          <h2 className="text-xl font-semibold mb-4 text-dark-100">Recent Mismatches</h2>
          {mismatchesLoading ? (
            <LoadingSpinner />
          ) : mismatchesError ? (
            <ErrorMessage message={mismatchesError} onRetry={refetchMismatches} />
          ) : (
            <MismatchesTable mismatches={mismatches.slice(0, 10)} />
          )}
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-4 text-dark-100">All Transactions</h2>
        {transactionsLoading ? (
          <LoadingSpinner />
        ) : transactionsError ? (
          <ErrorMessage message={transactionsError} onRetry={refetchTransactions} />
        ) : (
          <TransactionsTable transactions={filteredTransactions} />
        )}
      </div>
    </div>
  );
}