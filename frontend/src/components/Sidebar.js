import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import ThemeToggle from './ThemeToggle';

const Sidebar = ({ activeTab, setActiveTab, selectedTransaction, onLogout }) => {
 const { user, isAdmin, isAuditor } = useAuth();
 const [isOpen, setIsOpen] = useState(false);

 const navigationItems = [
 {
 section: 'Main',
 items: [
 {
 id: 'overview',
 label: 'Overview',
 icon: 'OVR',
 description: 'Dashboard overview and KPIs'
 },
 {
 id: 'transactions',
 label: 'Transactions',
 icon: 'TXN',
 description: 'Live transaction monitoring'
 },
 {
 id: 'mismatches',
 label: 'Mismatches',
 icon: 'ERR',
 description: 'Reconciliation mismatches',
 badge: '5' // This could be dynamic
 },
 {
 id: 'analytics',
 label: 'Analytics',
 icon: 'ANA',
 description: 'Reports and analytics'
 },
 {
 id: 'system-health',
 label: 'System Health',
 icon: 'SYS',
 description: 'Infrastructure monitoring and system health'
 },
 {
 id: 'reconciliation',
 label: 'Transaction Reconciliation',
 icon: 'REC',
 description: 'Real-time transaction reconciliation dashboard'
 }
 ]
 },
 {
 section: 'Tools',
 items: [
 ...(selectedTransaction ? [{
 id: 'drilldown',
 label: 'Transaction Details',
 icon: 'DTL',
 description: 'Detailed transaction view'
 }] : []),
 ...(isAdmin() ? [{
 id: 'admin',
 label: 'Administration',
 icon: 'ADM',
 description: 'System administration'
 }] : [])
 ]
 }
 ];

 const handleItemClick = (itemId) => {
 setActiveTab(itemId);
 if (window.innerWidth <= 1024) {
 setIsOpen(false);
 }
 };

 const toggleSidebar = () => {
 setIsOpen(!isOpen);
 };

 const getUserInitials = (username) => {
 return username ? username.substring(0, 2).toUpperCase() : 'U';
 };

 return (
 <>
 {/* Mobile Toggle Button */}
 <button 
 className="sidebar-toggle"
 onClick={toggleSidebar}
 title="Toggle Navigation"
 >
 <span className="icon">≡</span>
 </button>

 {/* Overlay for mobile */}
 <div 
 className={`sidebar-overlay ${isOpen ? 'open' : ''}`}
 onClick={() => setIsOpen(false)}
 />

 {/* Sidebar */}
 <div className={`sidebar ${isOpen ? 'open' : ''}`}>
 {/* Header */}
 <div className="sidebar-header">
 <div className="sidebar-logo">
 <div className="sidebar-logo-icon">B</div>
 <div>
 <h1 className="sidebar-title">Banking Ops</h1>
 <p className="sidebar-subtitle">Reconciliation Engine</p>
 </div>
 </div>
 </div>

 {/* Navigation */}
 <nav className="sidebar-nav">
 {navigationItems.map((section, sectionIndex) => (
 <div key={sectionIndex} className="sidebar-nav-section">
 <div className="sidebar-nav-title">{section.section}</div>
 {section.items.map((item) => (
 <button
 key={item.id}
 onClick={() => handleItemClick(item.id)}
 className={`sidebar-nav-item ${activeTab === item.id ? 'active' : ''}`}
 title={item.description}
 >
 <span className="sidebar-nav-icon">{item.icon}</span>
 <span className="sidebar-nav-label">{item.label}</span>
 {item.badge && (
 <span className="sidebar-nav-badge">{item.badge}</span>
 )}
 </button>
 ))}
 </div>
 ))}
 </nav>

 {/* Footer */}
 <div className="sidebar-footer">
 {/* User Info */}
 <div className="sidebar-user">
 <div className="sidebar-user-avatar">
 {getUserInitials(user?.username)}
 </div>
 <div className="sidebar-user-info">
 <div className="sidebar-user-name">{user?.username || 'User'}</div>
 <div className="sidebar-user-role">
 {user?.roles?.join(', ') || 'Guest'}
 </div>
 </div>
 </div>

 {/* Controls */}
 <div className="sidebar-controls">
 <ThemeToggle />
 <button
 onClick={() => {
 if (window.confirm('Are you sure you want to logout?')) {
 onLogout();
 }
 }}
 className="btn btn-sm btn-error"
 title="Logout"
 style={{ flex: 1 }}
 >
 <span className="icon">×</span>
 Logout
 </button>
 </div>
 </div>
 </div>
 </>
 );
};

export default Sidebar;
