import { useEffect, useState } from "react";
import { getTransactions } from "../services/transactions.service";

export default function useTransactions() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getTransactions();
        setTransactions(data);
      } catch (err) {
        setError(err.message || 'Failed to fetch transactions');
        console.error('Error fetching transactions:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchTransactions();
  }, []);

  return { transactions, loading, error, refetch: () => fetchTransactions() };
}