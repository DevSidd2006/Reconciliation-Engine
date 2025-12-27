import React, { createContext, useState, useEffect } from 'react';
import authService from '../services/auth';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [authenticated, setAuthenticated] = useState(false);

    useEffect(() => {
        initAuth();
    }, []);

    const initAuth = async () => {
        try {
            const isAuth = await authService.init();
            setAuthenticated(isAuth);

            if (isAuth) {
                const userInfo = authService.getUserInfo();
                setUser(userInfo);
            }
        } catch (error) {
            console.error('Auth initialization failed:', error);
            setAuthenticated(false);
        } finally {
            setLoading(false);
        }
    };

    const login = async (username, password) => {
        try {
            // Pass credentials to auth service if needed (for mock auth, they're optional)
            await authService.login(username, password);
            const userInfo = authService.getUserInfo();
            setUser(userInfo);
            setAuthenticated(true);
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    };

    const logout = async () => {
        try {
            await authService.logout();
            setUser(null);
            setAuthenticated(false);
        } catch (error) {
            console.error('Logout failed:', error);
            throw error;
        }
    };

    const value = {
        user,
        authenticated,
        loading,
        login,
        logout,
        hasRole: (role) => authService.hasRole(role),
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};
