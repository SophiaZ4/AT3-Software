console.log("App.js loaded.");

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    // The path '/sw.js' will be handled by the route in app.py
    navigator.serviceWorker.register('/sw.js')
      .then(registration => {
        console.log('Service Worker registered with scope:', registration.scope);
      })
      .catch(error => {
        console.error('Service Worker registration failed:', error);
      });
  });
}