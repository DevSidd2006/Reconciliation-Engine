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
 <span className="icon">WARN</span>
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
 <span className="icon">{loading ? 'REF' : ''}</span>
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
 
 Admin
 </button>
 
 <button
 onClick={() => loginAsDemo('auditor')}
 disabled={loading}
 className="btn btn-warning btn-sm"
 >
 
 Auditor
 </button>
 
 <button
 onClick={() => loginAsDemo('operator')}
 disabled={loading}
 className="btn btn-secondary btn-sm"
 >
 <span className="icon">CFG</span>
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
