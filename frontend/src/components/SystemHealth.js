import React, { useState, useEffect } from 'react';
import { Activity, Server, Database, Zap, Cpu, HardDrive, Wifi, AlertTriangle, CheckCircle, Clock, RefreshCw } from 'lucide-react';
import axios from 'axios';

const API_BASE = 'http://localhost:8002/api';

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

 // Map icon names to actual icon components
 const getIconComponent = (iconName) => {
 const iconMap = {
 'Server': Server,
 'Database': Database,
 'Zap': Zap,
 'Wifi': Wifi,
 'Activity': Activity
 };
 const IconComponent = iconMap[iconName] || Server;
 return IconComponent;
 };

 const IconComponent = typeof service.icon === 'string' ? getIconComponent(service.icon) : service.icon;

 return (
 <div className="flex items-center justify-between p-4 bg-dark-800/50 rounded-lg">
 <div className="flex items-center gap-4">
 <div className="w-10 h-10 rounded-lg bg-gradient-to-r from-primary-600 to-primary-500 flex items-center justify-center">
 <IconComponent className="w-5 h-5 text-white" />
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
 const [alerts, setAlerts] = useState([]);
 const [lastUpdated, setLastUpdated] = useState(new Date());
 const [isRefreshing, setIsRefreshing] = useState(false);
 const [loading, setLoading] = useState(true);
 const [error, setError] = useState(null);

 useEffect(() => {
 fetchHealthData();
 
 // Auto-refresh every 30 seconds
 const interval = setInterval(() => {
 fetchHealthData();
 }, 30000);

 return () => clearInterval(interval);
 }, []);

 const fetchHealthData = async () => {
 try {
 setError(null);
 
 // Fetch all health data in parallel
 const [overviewResponse, servicesResponse, alertsResponse] = await Promise.all([
 axios.get(`${API_BASE}/health/overview`),
 axios.get(`${API_BASE}/health/services`),
 axios.get(`${API_BASE}/health/alerts`)
 ]);

 const overview = overviewResponse.data;
 setHealthData(overview.metrics);
 setServices(servicesResponse.data.services);
 setAlerts(alertsResponse.data.alerts);
 setLastUpdated(new Date());
 setLoading(false);
 } catch (error) {
 console.error('Error fetching health data:', error);
 setError('Failed to fetch system health data');
 setLoading(false);
 
 // Fallback to mock data if API fails
 generateFallbackData();
 }
 };

 const generateFallbackData = () => {
 // Fallback data in case API is not available
 setHealthData({
 kafka: {
 status: 'unknown',
 eventsPerSecond: 0,
 details: [
 { label: 'Status', value: 'API Unavailable' }
 ]
 },
 backend: {
 status: 'unknown',
 cpu: 0,
 memory: 0,
 details: [
 { label: 'Status', value: 'API Unavailable' }
 ]
 },
 redis: {
 status: 'unknown',
 hitRate: 0,
 details: [
 { label: 'Status', value: 'API Unavailable' }
 ]
 },
 database: {
 status: 'unknown',
 queryTime: 0,
 storage: 0,
 details: [
 { label: 'Status', value: 'API Unavailable' }
 ]
 }
 });

 setServices([
 {
 name: 'System Health API',
 description: 'Health monitoring service',
 icon: Activity,
 status: 'down',
 uptime: 'N/A'
 }
 ]);

 setAlerts([
 {
 type: 'error',
 title: 'Health API Unavailable',
 message: 'Unable to connect to system health monitoring API'
 }
 ]);
 };

 const refreshData = async () => {
 setIsRefreshing(true);
 await fetchHealthData();
 setTimeout(() => {
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

 {/* Loading State */}
 {loading && (
 <div className="glass-card p-8 text-center">
 <RefreshCw className="w-8 h-8 animate-spin text-primary-400 mx-auto mb-4" />
 <p className="text-dark-200">Loading system health data...</p>
 </div>
 )}

 {/* Error State */}
 {error && (
 <div className="glass-card p-6 mb-8">
 <div className="flex items-center gap-3 text-danger-light">
 <AlertTriangle className="w-6 h-6" />
 <div>
 <h3 className="font-semibold">System Health Error</h3>
 <p className="text-sm text-dark-400 mt-1">{error}</p>
 </div>
 </div>
 </div>
 )}

 {/* System Health Cards */}
 {!loading && (
 <>
 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
 <HealthCard
 title="Kafka Cluster"
 status={healthData.kafka?.status}
 value={healthData.kafka?.eventsPerSecond || 0}
 unit="events/sec"
 icon={Wifi}
 details={healthData.kafka?.details}
 />
 <HealthCard
 title="Backend API"
 status={healthData.backend?.status}
 value={healthData.backend?.cpu || 0}
 unit="% CPU"
 icon={Server}
 details={healthData.backend?.details}
 />
 <HealthCard
 title="Redis Cache"
 status={healthData.redis?.status}
 value={healthData.redis?.hitRate || 0}
 unit="% hit rate"
 icon={Zap}
 details={healthData.redis?.details}
 />
 <HealthCard
 title="PostgreSQL"
 status={healthData.database?.status}
 value={healthData.database?.queryTime || 0}
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
 <span className="text-dark-100">{healthData.backend?.cpu || 0}%</span>
 </div>
 <div className="w-full bg-dark-700 rounded-full h-2">
 <div 
 className="bg-gradient-to-r from-primary-600 to-primary-500 h-2 rounded-full transition-all duration-300"
 style={{ width: `${healthData.backend?.cpu || 0}%` }}
 ></div>
 </div>
 </div>

 <div>
 <div className="flex justify-between items-center mb-2">
 <span className="text-dark-300">Memory Usage</span>
 <span className="text-dark-100">{healthData.backend?.memory || 0}%</span>
 </div>
 <div className="w-full bg-dark-700 rounded-full h-2">
 <div 
 className="bg-gradient-to-r from-success-600 to-success-500 h-2 rounded-full transition-all duration-300"
 style={{ width: `${healthData.backend?.memory || 0}%` }}
 ></div>
 </div>
 </div>

 <div>
 <div className="flex justify-between items-center mb-2">
 <span className="text-dark-300">Cache Hit Rate</span>
 <span className="text-dark-100">{healthData.redis?.hitRate || 0}%</span>
 </div>
 <div className="w-full bg-dark-700 rounded-full h-2">
 <div 
 className="bg-gradient-to-r from-warning-600 to-warning-500 h-2 rounded-full transition-all duration-300"
 style={{ width: `${healthData.redis?.hitRate || 0}%` }}
 ></div>
 </div>
 </div>

 <div>
 <div className="flex justify-between items-center mb-2">
 <span className="text-dark-300">Storage Usage</span>
 <span className="text-dark-100">{healthData.database?.storage || 0}%</span>
 </div>
 <div className="w-full bg-dark-700 rounded-full h-2">
 <div 
 className="bg-gradient-to-r from-blue-600 to-blue-500 h-2 rounded-full transition-all duration-300"
 style={{ width: `${healthData.database?.storage || 0}%` }}
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
 {alerts.map((alert, index) => (
 <div key={index} className={`p-4 rounded-lg border ${
 alert.type === 'success' ? 'bg-success-light/10 border-success-light/30' :
 alert.type === 'warning' ? 'bg-warning-light/10 border-warning-light/30' :
 alert.type === 'error' || alert.type === 'critical' ? 'bg-danger-light/10 border-danger-light/30' :
 'bg-dark-700/50 border-dark-600'
 }`}>
 <div className="flex items-center gap-3">
 {alert.type === 'success' ? <CheckCircle className="w-5 h-5 text-success-light" /> :
 alert.type === 'warning' ? <AlertTriangle className="w-5 h-5 text-warning-light" /> :
 <AlertTriangle className="w-5 h-5 text-danger-light" />}
 <div>
 <p className={`font-medium ${
 alert.type === 'success' ? 'text-success-light' :
 alert.type === 'warning' ? 'text-warning-light' :
 'text-danger-light'
 }`}>{alert.title}</p>
 <p className="text-sm text-dark-400">{alert.message}</p>
 </div>
 </div>
 </div>
 ))}
 </div>
 </div>
 </>
 )}
 </div>
 );
};

export default SystemHealth;
