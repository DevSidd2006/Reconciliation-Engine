import { useState, useEffect } from 'react';

const ThemeToggle = () => {
 const [isDark, setIsDark] = useState(true);

 // Initialize theme from localStorage or default to dark
 useEffect(() => {
 const savedTheme = localStorage.getItem('banking-dashboard-theme');
 const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
 
 const initialTheme = savedTheme || (prefersDark ? 'dark' : 'light');
 const isInitiallyDark = initialTheme === 'dark';
 
 setIsDark(isInitiallyDark);
 applyTheme(initialTheme);
 }, []);

 const applyTheme = (theme) => {
 const root = document.documentElement;
 
 // Add switching class to prevent transition flashing
 root.classList.add('theme-switching');
 
 if (theme === 'light') {
 root.setAttribute('data-theme', 'light');
 } else {
 root.removeAttribute('data-theme');
 }
 
 // Remove switching class after a brief delay
 setTimeout(() => {
 root.classList.remove('theme-switching');
 }, 50);
 
 // Save to localStorage
 localStorage.setItem('banking-dashboard-theme', theme);
 };

 const toggleTheme = () => {
 const newTheme = isDark ? 'light' : 'dark';
 setIsDark(!isDark);
 applyTheme(newTheme);
 };

 return (
 <div 
 className={`theme-toggle ${isDark ? '' : 'active'}`}
 onClick={toggleTheme}
 title={`Switch to ${isDark ? 'light' : 'dark'} theme`}
 >
 <span className="theme-toggle-icon">
 {isDark ? (
 <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
 <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
 </svg>
 ) : (
 <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
 <circle cx="12" cy="12" r="5"/>
 <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
 </svg>
 )}
 </span>
 
 <div className="theme-toggle-switch"></div>
 
 <span className="theme-toggle-label">
 {isDark ? 'Dark' : 'Light'}
 </span>
 </div>
 );
};

export default ThemeToggle;
