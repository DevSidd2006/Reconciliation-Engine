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
    const body = document.body;
    
    // Add switching class to prevent transition flashing
    root.classList.add('theme-switching');
    
    // Remove existing theme classes
    body.classList.remove('light-theme', 'dark-theme');
    
    if (theme === 'light') {
      root.setAttribute('data-theme', 'light');
      body.classList.add('light-theme');
      // Use actual color values instead of CSS variables
      document.body.style.backgroundColor = '#ffffff';
      document.body.style.color = '#111827';
      root.style.setProperty('--bg-primary', '#ffffff');
      root.style.setProperty('--bg-secondary', '#f9fafb');
      root.style.setProperty('--text-primary', '#111827');
      root.style.setProperty('--text-secondary', '#4b5563');
      root.style.setProperty('--border-color', '#e5e7eb');
    } else {
      root.removeAttribute('data-theme');
      body.classList.add('dark-theme');
      // Use actual color values for dark theme
      document.body.style.backgroundColor = '#111827';
      document.body.style.color = '#ffffff';
      root.style.setProperty('--bg-primary', '#1f2937');
      root.style.setProperty('--bg-secondary', '#111827');
      root.style.setProperty('--text-primary', '#ffffff');
      root.style.setProperty('--text-secondary', '#d1d5db');
      root.style.setProperty('--border-color', '#374151');
    }
    
    // Force repaint
    body.style.display = 'none';
    body.offsetHeight; // Trigger reflow
    body.style.display = '';
    
    // Remove switching class after a brief delay
    setTimeout(() => {
      root.classList.remove('theme-switching');
    }, 100);
    
    // Save to localStorage
    localStorage.setItem('banking-dashboard-theme', theme);
    
    // Debug log
    console.log(`Theme switched to: ${theme}`, {
      dataTheme: root.getAttribute('data-theme'),
      bodyClasses: body.className,
      bodyBg: document.body.style.backgroundColor,
      bodyColor: document.body.style.color
    });
  };

  const toggleTheme = () => {
    const newTheme = isDark ? 'light' : 'dark';
    console.log(`Toggling theme from ${isDark ? 'dark' : 'light'} to ${newTheme}`);
    setIsDark(!isDark);
    applyTheme(newTheme);
    
    // Force a re-render of the entire app
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: newTheme } }));
  };

  return (
    <div 
      className={`theme-toggle ${isDark ? '' : 'active'}`}
      onClick={toggleTheme}
      title={`Switch to ${isDark ? 'light' : 'dark'} theme`}
      style={{
        padding: '8px 12px',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius)',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        backgroundColor: isDark ? 'var(--gray-800)' : 'var(--gray-100)',
        transition: 'all 0.2s ease',
        position: 'relative'
      }}
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
      
      <div 
        className="theme-toggle-switch"
        style={{
          width: '32px',
          height: '16px',
          backgroundColor: isDark ? 'var(--gray-600)' : 'var(--primary-blue)',
          borderRadius: '8px',
          position: 'relative',
          transition: 'background-color 0.2s ease'
        }}
      >
        <div
          style={{
            position: 'absolute',
            top: '2px',
            left: isDark ? '2px' : '16px',
            width: '12px',
            height: '12px',
            backgroundColor: 'white',
            borderRadius: '50%',
            transition: 'left 0.2s ease'
          }}
        />
      </div>
      
      <span className="theme-toggle-label" style={{ fontSize: '12px', fontWeight: '600' }}>
        {isDark ? 'Dark' : 'Light'}
      </span>
      
      {/* Test indicator */}
      <div style={{
        position: 'absolute',
        top: '-30px',
        left: '0',
        padding: '4px 8px',
        backgroundColor: isDark ? '#ff0000' : '#00ff00',
        color: 'white',
        fontSize: '10px',
        borderRadius: '4px',
        pointerEvents: 'none'
      }}>
        {isDark ? 'DARK' : 'LIGHT'}
      </div>
    </div>
  );
};

export default ThemeToggle;
