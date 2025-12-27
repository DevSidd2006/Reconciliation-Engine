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
         icon: (
           <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
             <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
             <rect x="9" y="9" width="6" height="6"/>
             <path d="M9 1v6M15 1v6M9 17v6M15 17v6M1 9h6M1 15h6M17 9h6M17 15h6"/>
           </svg>
         ),
         description: 'Dashboard overview and KPIs'
       },
       {
         id: 'transactions',
         label: 'Transactions',
         icon: (
           <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
             <path d="M12 1v6M12 17v6"/>
             <circle cx="12" cy="12" r="4"/>
             <path d="M1 12h6M17 12h6"/>
           </svg>
         ),
         description: 'Live transaction monitoring'
       },
       {
         id: 'mismatches',
         label: 'Mismatches',
         icon: (
           <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
             <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
             <line x1="12" y1="9" x2="12" y2="13"/>
             <line x1="12" y1="17" x2="12.01" y2="17"/>
           </svg>
         ),
         description: 'Reconciliation mismatches',
         badge: '5' // This could be dynamic
       },
       {
         id: 'analytics',
         label: 'Analytics',
         icon: (
           <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
             <line x1="18" y1="20" x2="18" y2="10"/>
             <line x1="12" y1="20" x2="12" y2="4"/>
             <line x1="6" y1="20" x2="6" y2="14"/>
           </svg>
         ),
         description: 'Reports and analytics'
       },
       {
         id: 'system-health',
         label: 'System Health',
         icon: (
           <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
             <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
           </svg>
         ),
         description: 'Infrastructure monitoring and system health'
       },
       {
         id: 'reconciliation',
         label: 'Transaction Reconciliation',
         icon: (
           <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
             <path d="M9 11H1l2-2M1 13l2 2M23 11h-8l2-2M15 13l2 2"/>
             <path d="M11 12h2"/>
             <path d="M3 19h18"/>
             <path d="M5 21v-4M19 21v-4"/>
           </svg>
         ),
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
         icon: (
           <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
             <circle cx="11" cy="11" r="8"/>
             <path d="M21 21l-4.35-4.35"/>
             <circle cx="11" cy="11" r="3"/>
           </svg>
         ),
         description: 'Detailed transaction view'
       }] : []),
       ...(isAdmin() ? [{
         id: 'admin',
         label: 'Administration',
         icon: (
           <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
             <circle cx="12" cy="12" r="3"/>
             <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
           </svg>
         ),
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
 <span className="icon">
   <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
     <line x1="3" y1="6" x2="21" y2="6"/>
     <line x1="3" y1="12" x2="21" y2="12"/>
     <line x1="3" y1="18" x2="21" y2="18"/>
   </svg>
 </span>
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
 <span className="icon">
   <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
     <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
     <polyline points="16,17 21,12 16,7"/>
     <line x1="21" y1="12" x2="9" y2="12"/>
   </svg>
 </span>
 Logout
 </button>
 </div>
 </div>
 </div>
 </>
 );
};

export default Sidebar;
