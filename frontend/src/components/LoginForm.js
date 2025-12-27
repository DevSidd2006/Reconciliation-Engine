import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const LoginForm = () => {
 const [credentials, setCredentials] = useState({ username: '', password: '' });
 const [error, setError] = useState('');
 const [loading, setLoading] = useState(false);
 const { login } = useAuth();

 const handleSubmit = async (e) => {
 e.preventDefault();
 setLoading(true);
 setError('');

 const result = await login(credentials.username, credentials.password);
 
 if (!result.success) {
 setError(result.error);
 }
 
 setLoading(false);
 };

 const handleChange = (e) => {
 setCredentials({
 ...credentials,
 [e.target.name]: e.target.value
 });
 };

 // Demo user buttons
 const loginAsDemo = async (role) => {
 setLoading(true);
 setError('');

 const demoCredentials = {
 admin: { username: 'admin', password: 'admin123' },
 auditor: { username: 'auditor', password: 'auditor123' },
 operator: { username: 'operator', password: 'operator123' }
 };

 const result = await login(
 demoCredentials[role].username, 
 demoCredentials[role].password
 );
 
 if (!result.success) {
 setError(result.error);
 }
 
 setLoading(false);
 };

 return (
 <div className="App">
 <header className="header">
 <div className="header-content">
 <div>
 <h1>Banking Reconciliation</h1>
 <p className="header-subtitle">
 Secure Authentication Required
 </p>
 </div>
 </div>
 </header>

 <div className="container" style={{ maxWidth: '500px', marginTop: 'var(--space-12)' }}>
 <div className="card">
 <div className="card-header">
 <h3 className="card-title">
 
 Secure Login
 </h3>
 </div>

 <div className="card-body">
 <form onSubmit={handleSubmit}>
 {error && (
 <div className="alert alert-error" style={{ marginBottom: 'var(--space-6)' }}>
 <strong>
 <span className="icon">
   <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
     <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
     <line x1="12" y1="9" x2="12" y2="13"/>
     <line x1="12" y1="17" x2="12.01" y2="17"/>
   </svg>
 </span>
 Authentication Failed
 </strong>
 <p>{error}</p>
 </div>
 )}

 <div className="form-group">
 <label className="form-label">
 Username
 </label>
 <input
 type="text"
 name="username"
 value={credentials.username}
 onChange={handleChange}
 required
 className="form-input"
 placeholder="Enter your username"
 />
 </div>

 <div className="form-group">
 <label className="form-label">
 Password
 </label>
 <input
 type="password"
 name="password"
 value={credentials.password}
 onChange={handleChange}
 required
 className="form-input"
 placeholder="Enter your password"
 />
 </div>

 <button
 type="submit"
 disabled={loading}
 className="btn btn-primary"
 style={{ width: '100%' }}
 >
 <span className="icon">
   {loading ? (
     <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
       <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
       <path d="M21 3v5h-5"/>
       <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
       <path d="M3 21v-5h5"/>
     </svg>
   ) : (
     <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
       <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/>
       <polyline points="10,17 15,12 10,7"/>
       <line x1="15" y1="12" x2="3" y2="12"/>
     </svg>
   )}
 </span>
 {loading ? 'Authenticating...' : 'Secure Login'}
 </button>
 </form>
 </div>

 {/* Demo Users Section */}
 <div className="card-footer">
 <h4 className="text-center" style={{ marginBottom: 'var(--space-4)' }}>
 
 Demo Users
 </h4>
 
 <div className="grid grid-3" style={{ gap: 'var(--space-2)' }}>
 <button
 onClick={() => loginAsDemo('admin')}
 disabled={loading}
 className="btn btn-error btn-sm"
 >
 <span className="icon">
   <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
     <circle cx="12" cy="12" r="3"/>
     <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
   </svg>
 </span>
 Admin
 </button>
 
 <button
 onClick={() => loginAsDemo('auditor')}
 disabled={loading}
 className="btn btn-warning btn-sm"
 >
 <span className="icon">
   <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
     <path d="M9 12l2 2 4-4"/>
     <path d="M21 12c-1 0-3-1-3-3s2-3 3-3 3 1 3 3-2 3-3 3"/>
     <path d="M3 12c1 0 3-1 3-3s-2-3-3-3-3 1-3 3 2 3 3 3"/>
     <path d="M13 12h1"/>
   </svg>
 </span>
 Auditor
 </button>
 
 <button
 onClick={() => loginAsDemo('operator')}
 disabled={loading}
 className="btn btn-secondary btn-sm"
 >
 <span className="icon">
   <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
     <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
     <circle cx="9" cy="7" r="4"/>
     <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
     <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
   </svg>
 </span>
 Operator
 </button>
 </div>

 <div className="text-xs text-gray-600" style={{ marginTop: 'var(--space-4)' }}>
 <p><strong>Admin:</strong> Full system access, all operations</p>
 <p><strong>Auditor:</strong> Read-only access to all data</p>
 <p><strong>Operator:</strong> Limited operational access</p>
 </div>
 </div>
 </div>
 </div>
 </div>
 );
};

export default LoginForm;
