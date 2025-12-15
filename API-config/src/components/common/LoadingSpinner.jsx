import React from 'react';

export const LoadingSpinner = ({ size = 'md', className = '' }) => {
    const sizes = {
        sm: 'w-4 h-4',
        md: 'w-8 h-8',
        lg: 'w-12 h-12',
        xl: 'w-16 h-16',
    };

    return (
        <div className={`flex items-center justify-center ${className}`}>
            <div className={`${sizes[size]} border-4 border-primary-500/30 border-t-primary-500 rounded-full animate-spin`}></div>
        </div>
    );
};

export const LoadingOverlay = ({ message = 'Loading...' }) => {
    return (
        <div className="fixed inset-0 bg-dark-950/80 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="glass-card p-8 flex flex-col items-center gap-4">
                <LoadingSpinner size="lg" />
                <p className="text-dark-200 text-lg">{message}</p>
            </div>
        </div>
    );
};

export const LoadingSkeleton = ({ className = '', count = 1 }) => {
    return (
        <>
            {Array.from({ length: count }).map((_, index) => (
                <div
                    key={index}
                    className={`shimmer bg-white/5 rounded-lg ${className}`}
                ></div>
            ))}
        </>
    );
};
