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
        <div className="container">
          <h1>🏦 BANKING RECONCILIATION</h1>
          <p style={{ fontFamily: 'var(--font-mono)', fontSize: '1rem', margin: 0 }}>
            SECURE AUTHENTICATION REQUIRED
          </p>
        </div>
      </header>

      <div className="container">
        <div className="card" style={{ maxWidth: '500px', margin: '0 auto' }}>
          <div className="card-header">
            <h3 className="card-title">🔐 SECURE LOGIN</h3>
          </div>

          <form onSubmit={handleSubmit} style={{ padding: '24px' }}>
            {error && (
              <div className="alert alert-error" style={{ marginBottom: '24px' }}>
                <strong>❌ Authentication Failed</strong>
                <p>{error}</p>
              </div>
            )}

            <div style={{ marginBottom: '20px' }}>
              <label style={{ 
                display: 'block', 
                marginBottom: '8px', 
                fontWeight: '700',
                fontFamily: 'var(--font-mono)'
              }}>
                USERNAME
              </label>
              <input
                type="text"
                name="username"
                value={credentials.username}
                onChange={handleChange}
                required
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '3px solid var(--primary-black)',
                  backgroundColor: 'var(--primary-white)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '1rem',
                  boxSizing: 'border-box'
                }}
                placeholder="Enter your username"
              />
            </div>

            <div style={{ marginBottom: '24px' }}>
              <label style={{ 
                display: 'block', 
                marginBottom: '8px', 
                fontWeight: '700',
                fontFamily: 'var(--font-mono)'
              }}>
                PASSWORD
              </label>
              <input
                type="password"
                name="password"
                value={credentials.password}
                onChange={handleChange}
                required
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '3px solid var(--primary-black)',
                  backgroundColor: 'var(--primary-white)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '1rem',
                  boxSizing: 'border-box'
                }}
                placeholder="Enter your password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{ width: '100%', marginBottom: '24px' }}
            >
              {loading ? '🔄 AUTHENTICATING...' : '🔐 SECURE LOGIN'}
            </button>
          </form>

          {/* Demo Users Section */}
          <div style={{ 
            borderTop: '3px solid var(--primary-black)', 
            padding: '24px',
            backgroundColor: 'var(--gray-100)'
          }}>
            <h4 style={{ 
              marginBottom: '16px', 
              fontFamily: 'var(--font-mono)',
              textAlign: 'center'
            }}>
              🎭 DEMO USERS
            </h4>
            
            <div className="grid grid-3">
              <button
                onClick={() => loginAsDemo('admin')}
                disabled={loading}
                className="btn"
                style={{
                  backgroundColor: 'var(--error-red)',
                  color: 'var(--primary-white)',
                  fontSize: '0.875rem',
                  padding: '8px 12px'
                }}
              >
                👑 ADMIN
              </button>
              
              <button
                onClick={() => loginAsDemo('auditor')}
                disabled={loading}
                className="btn"
                style={{
                  backgroundColor: 'var(--warning-orange)',
                  color: 'var(--primary-black)',
                  fontSize: '0.875rem',
                  padding: '8px 12px'
                }}
              >
                🔍 AUDITOR
              </button>
              
              <button
                onClick={() => loginAsDemo('operator')}
                disabled={loading}
                className="btn"
                style={{
                  backgroundColor: 'var(--accent-cyan)',
                  color: 'var(--primary-black)',
                  fontSize: '0.875rem',
                  padding: '8px 12px'
                }}
              >
                ⚙️ OPERATOR
              </button>
            </div>

            <div style={{ 
              marginTop: '16px', 
              fontSize: '0.75rem', 
              fontFamily: 'var(--font-mono)',
              color: 'var(--gray-800)'
            }}>
              <p><strong>ADMIN:</strong> Full system access, all operations</p>
              <p><strong>AUDITOR:</strong> Read-only access to all data</p>
              <p><strong>OPERATOR:</strong> Limited operational access</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;