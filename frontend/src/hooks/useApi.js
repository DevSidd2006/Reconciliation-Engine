import { useState, useEffect, useCallback } from 'react';

export const useApi = (apiFunction, immediate = true) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(immediate);
    const [error, setError] = useState(null);

    const execute = useCallback(async (...params) => {
        try {
            setLoading(true);
            setError(null);
            const result = await apiFunction(...params);
            setData(result);
            return result;
        } catch (err) {
            setError(err.response?.data?.message || err.message || 'An error occurred');
            throw err;
        } finally {
            setLoading(false);
        }
    }, [apiFunction]);

    useEffect(() => {
        if (immediate) {
            execute();
        }
    }, [execute, immediate]);

    const refetch = () => execute();

    return { data, loading, error, execute, refetch };
};
