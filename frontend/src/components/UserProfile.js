import { useAuth } from '../contexts/AuthContext';

const UserProfile = () => {
 const { user, logout, isAdmin, isAuditor, isOperator } = useAuth();

 if (!user) return null;

 const getRoleColor = (role) => {
 switch (role) {
 case 'admin': return 'var(--error-red)';
 case 'auditor': return 'var(--accent-orange)';
 case 'operator': return 'var(--accent-cyan)';
 default: return 'var(--gray-800)';
 }
 };

 const getRoleIcon = (role) => {
 switch (role) {
 case 'admin': return 'Admin';
 case 'auditor': return 'Auditor';
 case 'operator': return 'Operator';
 default: return 'User';
 }
 };

 const getAccessLevel = () => {
 if (isAdmin()) return { level: 'FULL ACCESS', color: 'var(--error-red)' };
 if (isAuditor()) return { level: 'READ-only', color: 'var(--accent-orange)' };
 if (isOperator()) return { level: 'LIMITED', color: 'var(--accent-cyan)' };
 return { level: 'RESTRICTED', color: 'var(--gray-800)' };
 };

 const accessLevel = getAccessLevel();

 return (
 <div className="card" style={{ marginBottom: '32px' }}>
 <div className="card-header">
 <h3 className="card-title">User Profile</h3>
 </div>
 
 <div style={{ padding: '24px' }}>
 <div className="grid grid-2">
 {/* User Information */}
 <div>
 <h4 style={{ marginBottom: '16px', color: 'var(--primary-black)' }}>
 User Information
 </h4>
 
 <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem' }}>
 <div style={{ marginBottom: '12px' }}>
 <strong>Username:</strong> {user.username}
 </div>
 <div style={{ marginBottom: '12px' }}>
 <strong>Email:</strong> {user.email}
 </div>
 <div style={{ marginBottom: '12px' }}>
 <strong>User ID:</strong> 
 <span style={{ fontSize: '0.75rem', color: 'var(--gray-800)' }}>
 {user.user_id}
 </span>
 </div>
 <div style={{ marginBottom: '12px' }}>
 <strong>Access Level:</strong>
 <span style={{ 
 color: accessLevel.color, 
 fontWeight: '700',
 marginLeft: '8px'
 }}>
 {accessLevel.level}
 </span>
 </div>
 </div>
 </div>

 {/* Roles and Permissions */}
 <div>
 <h4 style={{ marginBottom: '16px', color: 'var(--primary-black)' }}>
 ROLES & PERMISSIONS
 </h4>
 
 {/* Roles */}
 <div style={{ marginBottom: '16px' }}>
 <strong style={{ fontSize: '0.875rem', marginBottom: '8px', display: 'block' }}>
 Assigned Roles:
 </strong>
 <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
 {user.roles.map(role => (
 <span
 key={role}
 style={{
 backgroundColor: getRoleColor(role),
 color: role === 'auditor' ? 'var(--primary-black)' : 'var(--primary-white)',
 padding: '4px 12px',
 border: '2px solid var(--primary-black)',
 fontSize: '0.75rem',
 fontWeight: '700',
 fontFamily: 'var(--font-mono)'
 }}
 >
 {getRoleIcon(role)} {role.toUpperCase()}
 </span>
 ))}
 </div>
 </div>

 {/* Permission Count */}
 <div style={{ 
 padding: '12px',
 backgroundColor: 'var(--gray-100)',
 border: '2px solid var(--primary-black)',
 fontFamily: 'var(--font-mono)',
 fontSize: '0.875rem'
 }}>
 <strong>Permissions:</strong> {user.permissions?.length || 0} granted
 </div>
 </div>
 </div>

 {/* Quick Actions */}
 <div style={{ 
 marginTop: '24px', 
 borderTop: '3px solid var(--primary-black)', 
 paddingTop: '16px' 
 }}>
 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
 <div>
 <h4 style={{ margin: 0, color: 'var(--primary-black)' }}>
 Security Status
 </h4>
 <p style={{ 
 margin: '4px 0 0 0', 
 fontSize: '0.875rem', 
 fontFamily: 'var(--font-mono)',
 color: 'var(--success-green)',
 fontWeight: '700'
 }}>
 AUTHENTICATED & AUTHORIZED
 </p>
 </div>
 
 <button
 onClick={logout}
 className="btn"
 style={{
 backgroundColor: 'var(--error-red)',
 color: 'var(--primary-white)',
 padding: '8px 16px'
 }}
 >
 Logout
 </button>
 </div>
 </div>

 {/* Permissions Details (for admins/auditors) */}
 {(isAdmin() || isAuditor()) && (
 <div style={{ 
 marginTop: '24px', 
 borderTop: '3px solid var(--primary-black)', 
 paddingTop: '16px' 
 }}>
 <h4 style={{ marginBottom: '12px', color: 'var(--primary-black)' }}>
 DETAILED PERMISSIONS
 </h4>
 <div style={{ 
 maxHeight: '150px', 
 overflowY: 'auto',
 fontSize: '0.75rem',
 fontFamily: 'var(--font-mono)'
 }}>
 {user.permissions?.map((permission, index) => (
 <div key={index} style={{ 
 padding: '4px 8px',
 backgroundColor: index % 2 === 0 ? 'var(--gray-100)' : 'transparent',
 border: '1px solid var(--gray-200)'
 }}>
 {permission}
 </div>
 ))}
 </div>
 </div>
 )}
 </div>
 </div>
 );
};

export default UserProfile;
