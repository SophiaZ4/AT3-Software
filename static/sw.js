const CACHE_NAME = 'my-flask-pwa-cache-v49'; // Incremented version to force update
const STATIC_ASSETS = [
  '/', // Cache the root page for offline fallback
  '/static/style.css',
  '/static/app.js',
  '/static/images/icon.webp',
  '/manifest.json'
];

// Install event cache core static assets
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(cache => {
          return cache.startsWith('my-flask-pwa-cache-') && cache !== CACHE_NAME;
        }).map(cacheToDelete => {
          console.log('Service Worker: Deleting old cache:', cacheToDelete);
          return caches.delete(cacheToDelete);
        })
      );
    }).then(() => self.clients.claim())
  );
});


// CORRECTED FETCH LISTENER
self.addEventListener('fetch', event => {
  // Use a Network Only strategy for all navigation requests - preventing caching redirects
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .catch(() => {
          // If the network fails serves the cached root page
          return caches.match('/');
        })
    );
    return;
  }

  // For non-navigation requests use a Cache first strategy.
  // This serves assets quickly from the cache if they exist.
  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        // Return the cached response if found, otherwise go to the network
        return cachedResponse || fetch(event.request);
      })
  );
});