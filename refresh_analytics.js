// Force refresh analytics charts with new visualizations

console.log('🔄 Refreshing analytics charts...');

// Clear any cached chart data
if (window.localStorage) {
  Object.keys(localStorage).forEach(key => {
    if (key.includes('chart') || key.includes('analytics')) {
      localStorage.removeItem(key);
    }
  });
}

// Trigger analytics refresh event
window.dispatchEvent(new CustomEvent('dashboardRefresh'));

// Force reload analytics components
const analyticsElements = document.querySelectorAll('[class*="analytics"]');
analyticsElements.forEach(element => {
  if (element.style) {
    element.style.opacity = '0.5';
    setTimeout(() => {
      element.style.opacity = '1';
    }, 500);
  }
});

console.log('✅ Analytics charts refreshed with new visualizations!');
console.log('📊 New features available:');
console.log('  - Real SVG pie/donut charts');
console.log('  - Performance gauge charts');
console.log('  - Activity heatmaps');
console.log('  - Enhanced bar charts with animations');
console.log('  - Improved timeline visualizations');