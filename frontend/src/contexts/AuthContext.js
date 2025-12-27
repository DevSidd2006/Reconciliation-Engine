import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

// Configure axios base URL for all requests
axios.defaults.baseURL = 'http://localhost:8002';

const AuthContext = createContext();

export const useAuth = () => {
 const context = useContext(AuthContext);
 if (!context) {
 throw new Error('useAuth must be used within an AuthProvider');
 }
 return context;
};

export const AuthProvider = ({ children }) => {
 const [user, setUser] = useState(null);
 const [loading, setLoading] = useState(true);
 const [token, setToken] = useState(localStorage.getItem('auth_token'));

 // Configure axios defaults
 useEffect(() => {
 if (token) {
 axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
 } else {
 delete axios.defaults.headers.common['Authorization'];
 }
 }, [token]);

 // Check if user is authenticated on app load
 useEffect(() => {
 const checkAuth = async () => {
 console.log('Checking auth, token:', token ? 'exists' : 'none');
 
 if (token) {
 try {
 console.log('Validating existing token...');
 const response = await axios.get('/auth/me');
 console.log('Token valid, user:', response.data);
 setUser(response.data);
 } catch (error) {
 console.error('ERR Auth check failed:', error);
 logout();
 }
 }
 
 console.log('OK Auth check complete, loading set to false');
 setLoading(false);
 };

 checkAuth();
 }, [token]);

 const login = async (username, password) => {
 try {
 console.log(' Attempting login for:', username);
 
 const response = await axios.post('/auth/login', {
 username,
 password
 });

 console.log('OK Login response:', response.data);

 const { access_token, user_info } = response.data;
 
 setToken(access_token);
 setUser(user_info);
 localStorage.setItem('auth_token', access_token);
 
 console.log('OK Login successful, user set:', user_info);
 
 return { success: true };
 } catch (error) {
 console.error('ERR Login failed:', error);
 console.error('ERR Error response:', error.response?.data);
 return { 
 success: false, 
 error: error.response?.data?.detail || error.message || 'Login failed' 
 };
 }
 };

 const logout = () => {
 setToken(null);
 setUser(null);
 localStorage.removeItem('auth_token');
 delete axios.defaults.headers.common['Authorization'];
 };

 const hasRole = (role) => {
 return user?.roles?.includes(role) || false;
 };

 const hasPermission = (permission) => {
 return user?.permissions?.includes(permission) || false;
 };

 const isAdmin = () => hasRole('admin');
 const isAuditor = () => hasRole('auditor') || hasRole('admin');
 const isOperator = () => hasRole('operator') || hasRole('auditor') || hasRole('admin');

 const value = {
 user,
 token,
 loading,
 login,
 logout,
 hasRole,
 hasPermission,
 isAdmin,
 isAuditor,
 isOperator
 };

 return (
 <AuthContext.Provider value={value}>
 {children}
 </AuthContext.Provider>
 );
};
