// Authentication configuration
export const ENABLE_KEYCLOAK = false;

// Keycloak configuration
export const KEYCLOAK_CONFIG = {
  url: import.meta.env.VITE_KEYCLOAK_URL || 'http://localhost:8082',
  realm: import.meta.env.VITE_KEYCLOAK_REALM || 'reconciliation',
  clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || 'reconciliation-frontend',
};

// Chart configuration
export const CHART_DATA_POINTS = 12;

// API endpoints
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// WebSocket configuration
export const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000';
export const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:8000';
export const ENABLE_SOCKET = import.meta.env.VITE_ENABLE_SOCKET !== 'false';

// Refresh intervals (in milliseconds)
export const REFRESH_INTERVALS = {
  STATS: 30000,      // 30 seconds
  TRANSACTIONS: 60000, // 1 minute
  MISMATCHES: 30000,   // 30 seconds
};

// Pagination
export const DEFAULT_PAGE_SIZE = 50;
export const MAX_PAGE_SIZE = 1000;

// Status types
export const TRANSACTION_STATUSES = {
  SUCCESS: 'success',
  PENDING: 'pending',
  FAILED: 'failed',
};

export const MISMATCH_TYPES = {
  MISSING_IN_CORE: 'MISSING_IN_CORE',
  MISSING_IN_GATEWAY: 'MISSING_IN_GATEWAY', 
  MISSING_IN_MOBILE: 'MISSING_IN_MOBILE',
  MULTIPLE_MISMATCH: 'MULTIPLE_MISMATCH',
};

// Sources
export const TRANSACTION_SOURCES = {
  CORE: 'core',
  GATEWAY: 'gateway',
  MOBILE: 'mobile',
};

// WebSocket Events
export const EVENT_NEW_TRANSACTION = "new_transaction";
export const EVENT_NEW_MISMATCH = "new_mismatch";