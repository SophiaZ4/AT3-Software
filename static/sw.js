const CACHE_NAME = 'my-flask-pwa-cache-v22';
const urlsToCache = [
  '/',
  '/rules', // Add the new route
  '/quiz',  // Add the new route
  '/manifest.json',
  '/sw.js',
  '/static/style.css',
  '/static/app.js',
  '/static/images/icon.png'
];

// Install event: cache core assets
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching app shell');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        console.log('Service Worker: App shell cached successfully');
        return self.skipWaiting(); // Force new SW to activate immediately
      })
      .catch(error => {
        console.error('Service Worker: Failed to cache app shell:', error);
      })
  );
});

// Activate event: clean up old caches
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
    }).then(() => {
        console.log('Service Worker: Activated successfully');
        return self.clients.claim(); // Take control of open clients
    })
  );
});

// Fetch event: serve from cache, fallback to network - contains optional console logs
self.addEventListener('fetch', event => {
  // console.log('Service Worker: Fetching', event.request.url);
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // If the network request is successful, clone it and cache it for offline use
            const responseToCache = response.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, responseToCache);
            });
            return response;
          })
          .catch(() => {
            // If the network fails, try to serve the page from the cache
            return caches.match(event.request)
              .then(response => response || caches.match('/')); // Fallback to cached root
          })
  );
  return;
  }
  // For non-navigation requests (CSS, JS, images), use the Cache First strategy
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});