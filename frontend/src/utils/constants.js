export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:8000';
export const ENABLE_KEYCLOAK = import.meta.env.VITE_ENABLE_KEYCLOAK === 'true';
export const ENABLE_SOCKET = import.meta.env.VITE_ENABLE_SOCKET !== 'false';

export const KEYCLOAK_CONFIG = {
    url: import.meta.env.VITE_KEYCLOAK_URL || 'http://localhost:8080',
    realm: import.meta.env.VITE_KEYCLOAK_REALM || 'reconciliation',
    clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || 'reconciliation-frontend',
};

export const TRANSACTION_SOURCES = {
    CORE: 'core',
    GATEWAY: 'gateway',
    MOBILE: 'mobile',
};

export const MISMATCH_TYPES = {
    AMOUNT: 'amount_mismatch',
    STATUS: 'status_mismatch',
    TIMESTAMP: 'timestamp_mismatch',
    MISSING: 'missing_transaction',
};

export const TRANSACTION_STATUS = {
    SUCCESS: 'success',
    PENDING: 'pending',
    FAILED: 'failed',
};

export const REFRESH_INTERVAL = 30000; // 30 seconds
export const CHART_DATA_POINTS = 20;
