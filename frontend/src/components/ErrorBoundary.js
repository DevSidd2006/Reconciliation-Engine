import React from 'react';

class ErrorBoundary extends React.Component {
 constructor(props) {
 super(props);
 this.state = { hasError: false, error: null };
 }

 static getDerivedStateFromError(error) {
 return { hasError: true, error };
 }

 componentDidCatch(error, errorInfo) {
 console.error('Error caught by boundary:', error, errorInfo);
 }

 render() {
 if (this.state.hasError) {
 return (
 <div className="card" style={{ margin: '20px', padding: '20px' }}>
 <div className="alert alert-error">
 <h3>WARN COMPONENT ERROR</h3>
 <p>Something went wrong with this component.</p>
 <button 
 className="btn btn-primary" 
 onClick={() => this.setState({ hasError: false, error: null })}
 style={{ marginTop: '16px' }}
 >
 RETRY
 </button>
 </div>
 </div>
 );
 }

 return this.props.children;
 }
}

export default ErrorBoundary;
