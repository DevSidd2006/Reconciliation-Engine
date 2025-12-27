import React, { useState, useEffect } from 'react';
import { 
    Activity, 
    Server, 
    Database, 
    Zap,
    Cpu,
    HardDrive,
    Wifi,
    AlertTriangle,
    CheckCircle,
    Clock,
    RefreshCw
} from 'lucide-react';

const HealthCard = ({ title, status, value, unit, icon: Icon, details }) => {
    const getStatusColor = (status) => {
        switch (status) {
            case 'healthy': return 'text-success-light bg-success-light/10 border-success-light/30';
            case 'warning': return 'text-warning-light bg-warning-light/10 border-warning-light/30';
            case 'critical': return 'text-danger-light bg-danger-light/10 border-danger-light/30';
            default: return 'text-dark-400 bg-dark-700/50 border-dark-600';
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'healthy': return <CheckCircle className="w-4 h-4 text-success-light" />;
            case 'warning': return <AlertTriangle className="w-4 h-4 text-warning-light" />;
            case 'critical': return <AlertTriangle className="w-4 h-4 text-danger-light" />;
            default: return <Clock className="w-4 h-4 text-dark-400" />;
        }
    };

    return (
        <div className="glass-card p-6 hover:scale-105 transition-transform duration-200">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <Icon className="w-6 h-6 text-primary-400" />
                    <h3 className="font-semibold text-dark-100">{title}</h3>
                </div>
                <div className={`px-3 py-1 rounded-full border ${getStatusColor(status)} flex items-center gap-2`}>
                    {getStatusIcon(status)}
                    <span className="text-sm font-medium capitalize">{status}</span>
                </div>
            </div>
            
            <div className="mb-4">
                <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-bold text-dark-100">{value}</span>
                    {unit && <span className="text-dark-400">{unit}</span>}
                </div>
            </div>
            
            {details && (
                <div className="space-y-2">
                    {details.map((detail, index) => (
                        <div key={index} className="flex justify-between text-sm">
                            <span className="text-dark-400">{detail.label}:</span>
                            <span className="text-dark-200">{detail.value}</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

const ServiceStatus = ({ service }) => {
    const getStatusColor = (status) => {
        switch (status) {
            case 'running': return 'text-success-light';
            case 'degraded': return 'text-warning-light';
            case 'down': return 'text-danger-light';
            default: return 'text-dark-400';
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'running': return <CheckCircle className="w-5 h-5 text-success-light" />;
            case 'degraded': return <AlertTriangle className="w-5 h-5 text-warning-light" />;
            case 'down': return <AlertTriangle className="w-5 h-5 text-danger-light" />;
            default: return <Clock className="w-5 h-5 text-dark-400" />;
        }
    };

    return (
        <div className="flex items-center justify-between p-4 bg-dark-800/50 rounded-lg">
            <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-r from-primary-600 to-primary-500 flex items-center justify-center">
                    <service.icon className="w-5 h-5 text-white" />
                </div>
                <div>
                    <h4 className="font-medium text-dark-100">{service.name}</h4>
                    <p className="text-sm text-dark-400">{service.description}</p>
                </div>
            </div>
            
            <div className="text-right">
                <div className="flex items-center gap-2 mb-1">
                    {getStatusIcon(service.status)}
                    <span className={`font-medium capitalize ${getStatusColor(service.status)}`}>
                        {service.status}
                    </span>
                </div>
                <p className="text-xs text-dark-400">Uptime: {service.uptime}</p>
            </div>
        </div>
    );
};

export const SystemHealth = () => {
    const [healthData, setHealthData] = useState({});
    const [services, setServices] = useState([]);
    const [lastUpdated, setLastUpdated] = useState(new Date());
    const [isRefreshing, setIsRefreshing] = useState(false);

    useEffect(() => {
        generateHealthData();
        generateServiceData();
        
        // Auto-refresh every 30 seconds
        const interval = setInterval(() => {
            generateHealthData();
            generateServiceData();
            setLastUpdated(new Date());
        }, 30000);

        return () => clearInterval(interval);
    }, []);

    const generateHealthData = () => {
        setHealthData({
            kafka: {
                status: 'healthy',
                lag: Math.floor(Math.random() * 100),
                eventsPerSecond: Math.floor(Math.random() * 500) + 100,
                producerHealth: 'healthy',
                consumerHealth: 'healthy',
                details: [
                    { label: 'Partitions', value: '12' },
                    { label: 'Replicas', value: '3' },
                    { label: 'Topics', value: '3' }
                ]
            },
            backend: {
                status: Math.random() > 0.8 ? 'warning' : 'healthy',
                cpu: Math.floor(Math.random() * 40) + 20,
                memory: Math.floor(Math.random() * 30) + 40,
                errors: Math.floor(Math.random() * 10),
                details: [
                    { label: 'Requests/min', value: '1,247' },
                    { label: 'Avg Response', value: '156ms' },
                    { label: 'Active Connections', value: '23' }
                ]
            },
            redis: {
                status: 'healthy',
                hitRate: Math.floor(Math.random() * 10) + 90,
                size: (Math.random() * 500 + 100).toFixed(1),
                connections: Math.floor(Math.random() * 50) + 10,
                details: [
                    { label: 'Keys', value: '15,432' },
                    { label: 'Expired Keys', value: '1,234' },
                    { label: 'Memory Usage', value: '67%' }
                ]
            },
            database: {
                status: 'healthy',
                connections: Math.floor(Math.random() * 20) + 5,
                queryTime: Math.floor(Math.random() * 50) + 10,
                storage: Math.floor(Math.random() * 20) + 60,
                details: [
                    { label: 'Tables', value: '8' },
                    { label: 'Indexes', value: '24' },
                    { label: 'Transactions/sec', value: '45' }
                ]
            }
        });
    };

    const generateServiceData = () => {
        const serviceList = [
            {
                name: 'FastAPI Backend',
                description: 'Main reconciliation API server',
                icon: Server,
                status: 'running',
                uptime: '99.9%'
            },
            {
                name: 'PostgreSQL Database',
                description: 'Primary data storage',
                icon: Database,
                status: 'running',
                uptime: '99.8%'
            },
            {
                name: 'Redis Cache',
                description: 'In-memory caching layer',
                icon: Zap,
                status: 'running',
                uptime: '99.7%'
            },
            {
                name: 'Kafka Cluster',
                description: 'Message streaming platform',
                icon: Wifi,
                status: Math.random() > 0.9 ? 'degraded' : 'running',
                uptime: '99.5%'
            },
            {
                name: 'Traefik Proxy',
                description: 'Load balancer and reverse proxy',
                icon: Activity,
                status: 'running',
                uptime: '99.9%'
            }
        ];
        
        setServices(serviceList);
    };

    const refreshData = () => {
        setIsRefreshing(true);
        setTimeout(() => {
            generateHealthData();
            generateServiceData();
            setLastUpdated(new Date());
            setIsRefreshing(false);
        }, 1000);
    };

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-dark-100 flex items-center gap-3">
                        <Activity className="w-8 h-8 text-primary-400" />
                        System Health Monitor
                    </h1>
                    <p className="text-dark-400 mt-2">Real-time infrastructure monitoring and performance metrics</p>
                </div>
                
                <div className="flex items-center gap-4">
                    <div className="text-right">
                        <p className="text-sm text-dark-400">Last Updated:</p>
                        <p className="text-sm text-dark-200">{lastUpdated.toLocaleTimeString()}</p>
                    </div>
                    <button
                        onClick={refreshData}
                        disabled={isRefreshing}
                        className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white rounded-lg transition-colors"
                    >
                        <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                        Refresh
                    </button>
                </div>
            </div>

            {/* System Health Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <HealthCard
                    title="Kafka Cluster"
                    status={healthData.kafka?.status}
                    value={healthData.kafka?.eventsPerSecond}
                    unit="events/sec"
                    icon={Wifi}
                    details={healthData.kafka?.details}
                />
                
                <HealthCard
                    title="Backend API"
                    status={healthData.backend?.status}
                    value={healthData.backend?.cpu}
                    unit="% CPU"
                    icon={Server}
                    details={healthData.backend?.details}
                />
                
                <HealthCard
                    title="Redis Cache"
                    status={healthData.redis?.status}
                    value={healthData.redis?.hitRate}
                    unit="% hit rate"
                    icon={Zap}
                    details={healthData.redis?.details}
                />
                
                <HealthCard
                    title="PostgreSQL"
                    status={healthData.database?.status}
                    value={healthData.database?.queryTime}
                    unit="ms avg"
                    icon={Database}
                    details={healthData.database?.details}
                />
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-8">
                {/* Service Status */}
                <div className="glass-card p-6">
                    <h3 className="text-xl font-semibold text-dark-100 mb-6 flex items-center gap-3">
                        <Server className="w-6 h-6 text-primary-400" />
                        Service Status
                    </h3>
                    
                    <div className="space-y-4">
                        {services.map((service, index) => (
                            <ServiceStatus key={index} service={service} />
                        ))}
                    </div>
                </div>

                {/* Performance Metrics */}
                <div className="glass-card p-6">
                    <h3 className="text-xl font-semibold text-dark-100 mb-6 flex items-center gap-3">
                        <Activity className="w-6 h-6 text-primary-400" />
                        Performance Metrics
                    </h3>
                    
                    <div className="space-y-6">
                        <div>
                            <div className="flex justify-between items-center mb-2">
                                <span className="text-dark-300">CPU Usage</span>
                                <span className="text-dark-100">{healthData.backend?.cpu}%</span>
                            </div>
                            <div className="w-full bg-dark-700 rounded-full h-2">
                                <div 
                                    className="bg-gradient-to-r from-primary-600 to-primary-500 h-2 rounded-full transition-all duration-300"
                                    style={{ width: `${healthData.backend?.cpu}%` }}
                                ></div>
                            </div>
                        </div>
                        
                        <div>
                            <div className="flex justify-between items-center mb-2">
                                <span className="text-dark-300">Memory Usage</span>
                                <span className="text-dark-100">{healthData.backend?.memory}%</span>
                            </div>
                            <div className="w-full bg-dark-700 rounded-full h-2">
                                <div 
                                    className="bg-gradient-to-r from-success-600 to-success-500 h-2 rounded-full transition-all duration-300"
                                    style={{ width: `${healthData.backend?.memory}%` }}
                                ></div>
                            </div>
                        </div>
                        
                        <div>
                            <div className="flex justify-between items-center mb-2">
                                <span className="text-dark-300">Cache Hit Rate</span>
                                <span className="text-dark-100">{healthData.redis?.hitRate}%</span>
                            </div>
                            <div className="w-full bg-dark-700 rounded-full h-2">
                                <div 
                                    className="bg-gradient-to-r from-warning-600 to-warning-500 h-2 rounded-full transition-all duration-300"
                                    style={{ width: `${healthData.redis?.hitRate}%` }}
                                ></div>
                            </div>
                        </div>
                        
                        <div>
                            <div className="flex justify-between items-center mb-2">
                                <span className="text-dark-300">Storage Usage</span>
                                <span className="text-dark-100">{healthData.database?.storage}%</span>
                            </div>
                            <div className="w-full bg-dark-700 rounded-full h-2">
                                <div 
                                    className="bg-gradient-to-r from-blue-600 to-blue-500 h-2 rounded-full transition-all duration-300"
                                    style={{ width: `${healthData.database?.storage}%` }}
                                ></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* System Alerts */}
            <div className="glass-card p-6">
                <h3 className="text-xl font-semibold text-dark-100 mb-6 flex items-center gap-3">
                    <AlertTriangle className="w-6 h-6 text-warning-light" />
                    System Alerts
                </h3>
                
                <div className="space-y-3">
                    {healthData.backend?.status === 'warning' && (
                        <div className="p-4 bg-warning-light/10 border border-warning-light/30 rounded-lg">
                            <div className="flex items-center gap-3">
                                <AlertTriangle className="w-5 h-5 text-warning-light" />
                                <div>
                                    <p className="font-medium text-warning-light">High CPU Usage Detected</p>
                                    <p className="text-sm text-dark-400">Backend CPU usage is above normal threshold</p>
                                </div>
                            </div>
                        </div>
                    )}
                    
                    {services.some(s => s.status === 'degraded') && (
                        <div className="p-4 bg-warning-light/10 border border-warning-light/30 rounded-lg">
                            <div className="flex items-center gap-3">
                                <AlertTriangle className="w-5 h-5 text-warning-light" />
                                <div>
                                    <p className="font-medium text-warning-light">Service Performance Degraded</p>
                                    <p className="text-sm text-dark-400">Kafka cluster showing reduced performance</p>
                                </div>
                            </div>
                        </div>
                    )}
                    
                    {!healthData.backend?.status === 'warning' && !services.some(s => s.status === 'degraded') && (
                        <div className="p-4 bg-success-light/10 border border-success-light/30 rounded-lg">
                            <div className="flex items-center gap-3">
                                <CheckCircle className="w-5 h-5 text-success-light" />
                                <div>
                                    <p className="font-medium text-success-light">All Systems Operational</p>
                                    <p className="text-sm text-dark-400">No active alerts or performance issues detected</p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};