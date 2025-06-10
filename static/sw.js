const CACHE_NAME = 'my-flask-pwa-cache-v2';
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
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          // console.log('Service Worker: Found in cache', event.request.url);
          return response; // Serve from cache
        }
        // console.log('Service Worker: Not in cache, fetching from network', event.request.url);
        return fetch(event.request); // Fetch from network
        // Optional: Add logic here to cache new requests dynamically if needed
      })
      .catch(error => {
        console.error('Service Worker: Error fetching data', error);
        // might want to return a custom offline fallback page here
        // if (!event.request.url.startsWith('http')) return; // Skip non-http requests
        // return caches.match('/offline.html'); // Example: serve an offline.html page
      })
  );
});