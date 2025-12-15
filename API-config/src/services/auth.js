import Keycloak from 'keycloak-js';
import { KEYCLOAK_CONFIG, ENABLE_KEYCLOAK } from '../utils/constants';

class AuthService {
    constructor() {
        this.keycloak = null;
        this.authenticated = false;
    }

    async init() {
        if (!ENABLE_KEYCLOAK) {
            console.log('Keycloak is disabled. Using mock authentication.');
            this.authenticated = true;
            return true;
        }

        try {
            this.keycloak = new Keycloak(KEYCLOAK_CONFIG);

            this.authenticated = await this.keycloak.init({
                onLoad: 'login-required',
                checkLoginIframe: false,
            });

            if (this.authenticated) {
                localStorage.setItem('token', this.keycloak.token);

                // Refresh token periodically
                setInterval(() => {
                    this.keycloak.updateToken(70).then((refreshed) => {
                        if (refreshed) {
                            localStorage.setItem('token', this.keycloak.token);
                        }
                    }).catch(() => {
                        console.error('Failed to refresh token');
                    });
                }, 60000);
            }

            return this.authenticated;
        } catch (error) {
            console.error('Keycloak initialization failed:', error);
            return false;
        }
    }

    login() {
        if (!ENABLE_KEYCLOAK) {
            this.authenticated = true;
            return Promise.resolve();
        }
        return this.keycloak?.login();
    }

    logout() {
        localStorage.removeItem('token');

        if (!ENABLE_KEYCLOAK) {
            this.authenticated = false;
            window.location.href = '/login';
            return Promise.resolve();
        }

        return this.keycloak?.logout();
    }

    getToken() {
        if (!ENABLE_KEYCLOAK) {
            return localStorage.getItem('token') || 'mock-token';
        }
        return this.keycloak?.token;
    }

    isAuthenticated() {
        if (!ENABLE_KEYCLOAK) {
            return this.authenticated;
        }
        return this.keycloak?.authenticated || false;
    }

    getUserInfo() {
        if (!ENABLE_KEYCLOAK) {
            return {
                name: 'Demo User',
                email: 'demo@reconciliation.com',
                roles: ['admin'],
            };
        }

        return this.keycloak?.tokenParsed || null;
    }

    hasRole(role) {
        if (!ENABLE_KEYCLOAK) {
            return true; // Mock user has all roles
        }

        return this.keycloak?.hasRealmRole(role) || false;
    }
}

// Create singleton instance
const authService = new AuthService();

export default authService;
