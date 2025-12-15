import React, { useState, useEffect } from 'react';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';

const icons = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info,
};

const styles = {
    success: 'bg-success-light/20 border-success-light text-success-light',
    error: 'bg-danger-light/20 border-danger-light text-danger-light',
    warning: 'bg-warning-light/20 border-warning-light text-warning-light',
    info: 'bg-primary-500/20 border-primary-500 text-primary-400',
};

export const Notification = ({ type = 'info', message, onClose, duration = 5000 }) => {
    const [isVisible, setIsVisible] = useState(true);
    const Icon = icons[type];

    useEffect(() => {
        if (duration > 0) {
            const timer = setTimeout(() => {
                setIsVisible(false);
                setTimeout(onClose, 300);
            }, duration);

            return () => clearTimeout(timer);
        }
    }, [duration, onClose]);

    if (!isVisible) return null;

    return (
        <div className={`${styles[type]} border rounded-lg p-4 shadow-lg backdrop-blur-sm animate-slide-in-right flex items-start gap-3 min-w-[300px] max-w-md`}>
            <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <p className="flex-1 text-sm font-medium">{message}</p>
            <button
                onClick={() => {
                    setIsVisible(false);
                    setTimeout(onClose, 300);
                }}
                className="flex-shrink-0 hover:opacity-70 transition-opacity"
            >
                <X className="w-4 h-4" />
            </button>
        </div>
    );
};

export const NotificationContainer = ({ notifications, removeNotification }) => {
    return (
        <div className="fixed top-4 right-4 z-50 flex flex-col gap-3">
            {notifications.map((notification) => (
                <Notification
                    key={notification.id}
                    type={notification.type}
                    message={notification.message}
                    duration={notification.duration}
                    onClose={() => removeNotification(notification.id)}
                />
            ))}
        </div>
    );
};

// Hook to manage notifications
export const useNotifications = () => {
    const [notifications, setNotifications] = useState([]);

    const addNotification = (type, message, duration = 5000) => {
        const id = Date.now() + Math.random();
        setNotifications((prev) => [...prev, { id, type, message, duration }]);
    };

    const removeNotification = (id) => {
        setNotifications((prev) => prev.filter((n) => n.id !== id));
    };

    return {
        notifications,
        addNotification,
        removeNotification,
        success: (message, duration) => addNotification('success', message, duration),
        error: (message, duration) => addNotification('error', message, duration),
        warning: (message, duration) => addNotification('warning', message, duration),
        info: (message, duration) => addNotification('info', message, duration),
    };
};
