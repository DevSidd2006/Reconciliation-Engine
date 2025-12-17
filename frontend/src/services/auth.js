// Keycloak completely removed - using mock authentication only

class AuthService {
    constructor() {
        this.authenticated = false;
        this.token = 'mock-jwt-token';
        this.user = {
            name: 'Mock Admin',
            email: 'admin@reconciliation.com',
            preferred_username: 'admin',
            roles: ['admin', 'operator', 'auditor', 'viewer'],
            realm_access: {
                roles: ['admin', 'operator', 'auditor', 'viewer']
            },
            resource_access: {
                'reconciliation-api': {
                    roles: ['admin', 'operator', 'auditor', 'viewer']
                }
            }
        };
    }

    async init() {
        console.log('Using Mock Authentication');
        this.authenticated = true;
        // Store the mock token in localStorage so the API service can use it
        localStorage.setItem('token', this.token);
        return Promise.resolve(true);
    }

    login() {
        this.authenticated = true;
        // Store the mock token in localStorage
        localStorage.setItem('token', this.token);
        return Promise.resolve();
    }

    logout() {
        this.authenticated = false;
        // Remove token from localStorage
        localStorage.removeItem('token');
        window.location.href = '/login'; // Or just reload
        return Promise.resolve();
    }

    getToken() {
        return this.token;
    }

    isAuthenticated() {
        return this.authenticated;
    }

    getUserInfo() {
        return this.user;
    }

    hasRole(role) {
        return true; // Admin has all roles
    }
}

// Create singleton instance
const authService = new AuthService();

export default authService;
