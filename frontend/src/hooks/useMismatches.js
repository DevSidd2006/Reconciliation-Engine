import { useEffect, useState } from "react";
import { getMismatches } from "../services/mismatches.service";

export default function useMismatches() {
  const [mismatches, setMismatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMismatches = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getMismatches();
        setMismatches(data);
      } catch (err) {
        setError(err.message || 'Failed to fetch mismatches');
        console.error('Error fetching mismatches:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMismatches();
  }, []);

  return { mismatches, loading, error, refetch: () => fetchMismatches() };
}