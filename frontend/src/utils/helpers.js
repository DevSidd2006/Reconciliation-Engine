// Format relative time (e.g., "2 minutes ago")
export const formatRelativeTime = (dateString) => {
  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) {
      return `${diffInSeconds}s ago`;
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return `${minutes}m ago`;
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return `${hours}h ago`;
    } else {
      const days = Math.floor(diffInSeconds / 86400);
      return `${days}d ago`;
    }
  } catch (error) {
    return 'Unknown';
  }
};

// Get mismatch badge styling
export const getMismatchBadge = (type) => {
  const baseClasses = 'px-2 py-1 rounded-full text-xs font-medium';
  
  switch (type) {
    case 'MISSING_IN_CORE':
      return `${baseClasses} bg-red-100 text-red-800`;
    case 'MISSING_IN_GATEWAY':
      return `${baseClasses} bg-orange-100 text-orange-800`;
    case 'MISSING_IN_MOBILE':
      return `${baseClasses} bg-purple-100 text-purple-800`;
    case 'MULTIPLE_MISMATCH':
      return `${baseClasses} bg-red-100 text-red-800`;
    default:
      return `${baseClasses} bg-gray-100 text-gray-800`;
  }
};

// Format currency
export const formatCurrency = (amount, currency = 'USD') => {
  try {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  } catch (error) {
    return `$${amount}`;
  }
};

// Format number with commas
export const formatNumber = (num) => {
  try {
    return new Intl.NumberFormat('en-US').format(num);
  } catch (error) {
    return num.toString();
  }
};

// Format percentage
export const formatPercentage = (value, decimals = 1) => {
  try {
    return `${value.toFixed(decimals)}%`;
  } catch (error) {
    return `${value}%`;
  }
};

// Get status badge styling
export const getStatusBadge = (status) => {
  const baseClasses = 'px-2 py-1 rounded-full text-xs font-medium';
  
  switch (status?.toLowerCase()) {
    case 'success':
      return `${baseClasses} bg-green-100 text-green-800`;
    case 'pending':
      return `${baseClasses} bg-yellow-100 text-yellow-800`;
    case 'failed':
      return `${baseClasses} bg-red-100 text-red-800`;
    default:
      return `${baseClasses} bg-gray-100 text-gray-800`;
  }
};

// Truncate text
export const truncateText = (text, maxLength = 50) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
};

// Debounce function
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

// Format date
export const formatDate = (dateString) => {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (error) {
    return 'Invalid Date';
  }
};

// Get source color
export const getSourceColor = (source) => {
  switch (source?.toLowerCase()) {
    case 'core':
      return 'text-blue-400';
    case 'gateway':
      return 'text-green-400';
    case 'mobile':
      return 'text-purple-400';
    default:
      return 'text-gray-400';
  }
};

// Get mismatch color
export const getMismatchColor = (type) => {
  switch (type) {
    case 'amount_mismatch':
      return 'text-red-400';
    case 'status_mismatch':
      return 'text-orange-400';
    case 'timestamp_mismatch':
      return 'text-yellow-400';
    case 'missing_transaction':
      return 'text-purple-400';
    default:
      return 'text-gray-400';
  }
};