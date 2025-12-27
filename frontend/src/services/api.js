import axios from 'axios';
import { API_BASE_URL } from '../utils/constants';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Handle unauthorized access
            localStorage.removeItem('token');
            // window.location.href = '/login';
            console.warn("Unauthorized access - 401");
        }
        return Promise.reject(error);
    }
);

// Transaction API calls
export const transactionAPI = {
    getAll: async (params = {}) => {
        const response = await api.get('/transactions/', { params });
        return response.data;
    },

    getById: async (txnId) => {
        const response = await api.get(`/transactions/${txnId}`);
        return response.data;
    },

    getStats: async () => {
        const response = await api.get('/transactions/stats');
        return response.data;
    },
};

// Mismatch API calls
export const mismatchAPI = {
    getAll: async (params = {}) => {
        const response = await api.get('/mismatches/', { params });
        return response.data;
    },

    getById: async (id) => {
        const response = await api.get(`/mismatches/${id}`);
        return response.data;
    },

    getStats: async () => {
        const response = await api.get('/mismatches/stats');
        return response.data;
    },
};

export default api;
