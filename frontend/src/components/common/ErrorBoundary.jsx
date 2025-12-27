import React, { Component } from 'react';
import { AlertTriangle } from 'lucide-react';

class ErrorBoundary extends Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        console.error('Error caught by boundary:', error, errorInfo);
        this.setState({
            error,
            errorInfo,
        });
    }

    handleReset = () => {
        this.setState({ hasError: false, error: null, errorInfo: null });
    };

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center p-4">
                    <div className="glass-card p-8 max-w-2xl w-full">
                        <div className="flex items-center gap-3 mb-6">
                            <AlertTriangle className="w-8 h-8 text-danger-light" />
                            <h1 className="text-2xl font-bold text-dark-100">Something went wrong</h1>
                        </div>

                        <p className="text-dark-300 mb-4">
                            We're sorry, but something unexpected happened. Please try refreshing the page.
                        </p>

                        {this.state.error && (
                            <details className="mb-6 bg-dark-900/50 rounded-lg p-4">
                                <summary className="cursor-pointer text-dark-200 font-medium mb-2">
                                    Error Details
                                </summary>
                                <pre className="text-xs text-danger-light overflow-auto custom-scrollbar">
                                    {this.state.error.toString()}
                                    {this.state.errorInfo?.componentStack}
                                </pre>
                            </details>
                        )}

                        <div className="flex gap-3">
                            <button
                                onClick={this.handleReset}
                                className="btn-primary"
                            >
                                Try Again
                            </button>
                            <button
                                onClick={() => window.location.href = '/'}
                                className="btn-secondary"
                            >
                                Go Home
                            </button>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
