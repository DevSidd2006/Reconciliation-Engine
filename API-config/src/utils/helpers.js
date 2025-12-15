import { format, formatDistanceToNow } from 'date-fns';

export const formatCurrency = (amount, currency = 'USD') => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency,
    }).format(amount);
};

export const formatDate = (date) => {
    if (!date) return 'N/A';
    return format(new Date(date), 'MMM dd, yyyy HH:mm:ss');
};

export const formatRelativeTime = (date) => {
    if (!date) return 'N/A';
    return formatDistanceToNow(new Date(date), { addSuffix: true });
};

export const getStatusColor = (status) => {
    const colors = {
        success: 'text-success-light',
        pending: 'text-warning-light',
        failed: 'text-danger-light',
    };
    return colors[status?.toLowerCase()] || 'text-dark-400';
};

export const getStatusBadge = (status) => {
    const badges = {
        success: 'badge-success',
        pending: 'badge-warning',
        failed: 'badge-danger',
    };
    return badges[status?.toLowerCase()] || 'badge-info';
};

export const getMismatchColor = (type) => {
    const colors = {
        amount_mismatch: 'text-danger-light',
        status_mismatch: 'text-warning-light',
        timestamp_mismatch: 'text-primary-400',
        missing_transaction: 'text-danger-light',
    };
    return colors[type] || 'text-dark-400';
};

export const getMismatchBadge = (type) => {
    const badges = {
        amount_mismatch: 'badge-danger',
        status_mismatch: 'badge-warning',
        timestamp_mismatch: 'badge-info',
        missing_transaction: 'badge-danger',
    };
    return badges[type] || 'badge-info';
};

export const truncateText = (text, maxLength = 50) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
};

export const getSourceColor = (source) => {
    const colors = {
        core: 'text-primary-400',
        gateway: 'text-success-light',
        mobile: 'text-warning-light',
    };
    return colors[source?.toLowerCase()] || 'text-dark-400';
};

export const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};
