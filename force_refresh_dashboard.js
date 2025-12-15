// Force refresh all dashboard panels by clearing browser cache and triggering refresh events

console.log('🔄 Forcing dashboard refresh...');

// Clear browser cache for this domain
if ('caches' in window) {
  caches.keys().then(function(names) {
    names.forEach(function(name) {
      caches.delete(name);
    });
  });
}

// Clear localStorage and sessionStorage
localStorage.clear();
sessionStorage.clear();

// Trigger dashboard refresh event
window.dispatchEvent(new CustomEvent('dashboardRefresh'));

// Force reload all components by adding timestamp to requests
const originalFetch = window.fetch;
window.fetch = function(...args) {
  if (args[0].includes('/api/')) {
    const url = new URL(args[0], window.location.origin);
    url.searchParams.set('_t', Date.now());
    args[0] = url.toString();
  }
  return originalFetch.apply(this, args);
};

// Refresh the page after a short delay
setTimeout(() => {
  console.log('✅ Cache cleared, refreshing page...');
  window.location.reload(true);
}, 1000);

console.log('✅ Dashboard refresh initiated!');