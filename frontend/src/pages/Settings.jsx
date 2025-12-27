import React, { useState } from 'react';
import { 
    Settings as SettingsIcon, 
    User, 
    Bell, 
    Shield, 
    Database,
    Save,
    RefreshCw
} from 'lucide-react';

const SettingSection = ({ title, description, icon: Icon, children }) => (
    <div className="glass-card p-6 mb-6">
        <div className="flex items-center gap-3 mb-4">
            <Icon className="w-6 h-6 text-primary-400" />
            <div>
                <h3 className="text-lg font-semibold text-dark-100">{title}</h3>
                <p className="text-sm text-dark-400">{description}</p>
            </div>
        </div>
        {children}
    </div>
);

export const Settings = () => {
    const [settings, setSettings] = useState({
        // User Preferences
        theme: 'dark',
        language: 'en',
        timezone: 'UTC',
        
        // Notifications
        emailNotifications: true,
        pushNotifications: false,
        mismatchAlerts: true,
        systemAlerts: true,
        
        // Security
        sessionTimeout: 30,
        mfaEnabled: false,
        
        // System
        autoRefresh: true,
        refreshInterval: 30,
        maxLogEntries: 1000,
        
        // Dashboard
        defaultView: 'dashboard',
        chartsEnabled: true,
        realTimeUpdates: true
    });

    const [isSaving, setIsSaving] = useState(false);

    const handleSettingChange = (key, value) => {
        setSettings(prev => ({ ...prev, [key]: value }));
    };

    const saveSettings = () => {
        setIsSaving(true);
        setTimeout(() => {
            setIsSaving(false);
            // Show success message
        }, 1000);
    };

    const resetSettings = () => {
        setSettings({
            theme: 'dark',
            language: 'en',
            timezone: 'UTC',
            emailNotifications: true,
            pushNotifications: false,
            mismatchAlerts: true,
            systemAlerts: true,
            sessionTimeout: 30,
            mfaEnabled: false,
            autoRefresh: true,
            refreshInterval: 30,
            maxLogEntries: 1000,
            defaultView: 'dashboard',
            chartsEnabled: true,
            realTimeUpdates: true
        });
    };

    return (
        <div className="p-6 max-w-4xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-dark-100 flex items-center gap-3">
                    <SettingsIcon className="w-8 h-8 text-primary-400" />
                    System Settings
                </h1>
                <p className="text-dark-400 mt-2">Configure your reconciliation system preferences</p>
            </div>

            {/* User Preferences */}
            <SettingSection
                title="User Preferences"
                description="Customize your personal experience"
                icon={User}
            >
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                        <label className="block text-sm font-medium text-dark-300 mb-2">Theme</label>
                        <select
                            value={settings.theme}
                            onChange={(e) => handleSettingChange('theme', e.target.value)}
                            className="w-full bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-dark-100 focus:border-primary-500 focus:outline-none"
                        >
                            <option value="dark">Dark</option>
                            <option value="light">Light</option>
                            <option value="auto">Auto</option>
                        </select>
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-dark-300 mb-2">Language</label>
                        <select
                            value={settings.language}
                            onChange={(e) => handleSettingChange('language', e.target.value)}
                            className="w-full bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-dark-100 focus:border-primary-500 focus:outline-none"
                        >
                            <option value="en">English</option>
                            <option value="es">Spanish</option>
                            <option value="fr">French</option>
                            <option value="de">German</option>
                        </select>
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-dark-300 mb-2">Timezone</label>
                        <select
                            value={settings.timezone}
                            onChange={(e) => handleSettingChange('timezone', e.target.value)}
                            className="w-full bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-dark-100 focus:border-primary-500 focus:outline-none"
                        >
                            <option value="UTC">UTC</option>
                            <option value="EST">Eastern Time</option>
                            <option value="PST">Pacific Time</option>
                            <option value="GMT">Greenwich Mean Time</option>
                        </select>
                    </div>
                </div>
            </SettingSection>

            {/* Notifications */}
            <SettingSection
                title="Notifications"
                description="Configure alert and notification preferences"
                icon={Bell}
            >
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium text-dark-100">Email Notifications</p>
                            <p className="text-sm text-dark-400">Receive notifications via email</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={settings.emailNotifications}
                                onChange={(e) => handleSettingChange('emailNotifications', e.target.checked)}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-dark-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                        </label>
                    </div>
                    
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium text-dark-100">Push Notifications</p>
                            <p className="text-sm text-dark-400">Browser push notifications</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={settings.pushNotifications}
                                onChange={(e) => handleSettingChange('pushNotifications', e.target.checked)}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-dark-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                        </label>
                    </div>
                    
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium text-dark-100">Mismatch Alerts</p>
                            <p className="text-sm text-dark-400">Immediate alerts for transaction mismatches</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={settings.mismatchAlerts}
                                onChange={(e) => handleSettingChange('mismatchAlerts', e.target.checked)}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-dark-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                        </label>
                    </div>
                    
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium text-dark-100">System Alerts</p>
                            <p className="text-sm text-dark-400">Notifications for system health issues</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={settings.systemAlerts}
                                onChange={(e) => handleSettingChange('systemAlerts', e.target.checked)}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-dark-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                        </label>
                    </div>
                </div>
            </SettingSection>

            {/* Security */}
            <SettingSection
                title="Security"
                description="Manage security and authentication settings"
                icon={Shield}
            >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium text-dark-300 mb-2">Session Timeout (minutes)</label>
                        <input
                            type="number"
                            min="5"
                            max="480"
                            value={settings.sessionTimeout}
                            onChange={(e) => handleSettingChange('sessionTimeout', parseInt(e.target.value))}
                            className="w-full bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-dark-100 focus:border-primary-500 focus:outline-none"
                        />
                    </div>
                    
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium text-dark-100">Multi-Factor Authentication</p>
                            <p className="text-sm text-dark-400">Enable MFA for enhanced security</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={settings.mfaEnabled}
                                onChange={(e) => handleSettingChange('mfaEnabled', e.target.checked)}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-dark-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                        </label>
                    </div>
                </div>
            </SettingSection>

            {/* System Configuration */}
            <SettingSection
                title="System Configuration"
                description="Configure system behavior and performance"
                icon={Database}
            >
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium text-dark-100">Auto Refresh</p>
                            <p className="text-sm text-dark-400">Automatically refresh data</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={settings.autoRefresh}
                                onChange={(e) => handleSettingChange('autoRefresh', e.target.checked)}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-dark-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                        </label>
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-dark-300 mb-2">Refresh Interval (seconds)</label>
                        <input
                            type="number"
                            min="10"
                            max="300"
                            value={settings.refreshInterval}
                            onChange={(e) => handleSettingChange('refreshInterval', parseInt(e.target.value))}
                            className="w-full bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-dark-100 focus:border-primary-500 focus:outline-none"
                        />
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-dark-300 mb-2">Max Log Entries</label>
                        <input
                            type="number"
                            min="100"
                            max="10000"
                            value={settings.maxLogEntries}
                            onChange={(e) => handleSettingChange('maxLogEntries', parseInt(e.target.value))}
                            className="w-full bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-dark-100 focus:border-primary-500 focus:outline-none"
                        />
                    </div>
                </div>
            </SettingSection>

            {/* Save/Reset Buttons */}
            <div className="flex items-center justify-between">
                <button
                    onClick={resetSettings}
                    className="flex items-center gap-2 px-4 py-2 bg-dark-700 hover:bg-dark-600 text-dark-200 rounded-lg transition-colors"
                >
                    <RefreshCw className="w-4 h-4" />
                    Reset to Defaults
                </button>
                
                <button
                    onClick={saveSettings}
                    disabled={isSaving}
                    className="flex items-center gap-2 px-6 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white rounded-lg transition-colors"
                >
                    {isSaving ? (
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                        <Save className="w-4 h-4" />
                    )}
                    {isSaving ? 'Saving...' : 'Save Settings'}
                </button>
            </div>
        </div>
    );
};