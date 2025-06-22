const CACHE_NAME = 'chat-cifrado-cache-v1';
const urlsToCache = [
    '/',
    '/cli_ccy.html',
    
    '/static/icons/kicons32_192.png',
    '/static/icons/kicons32.png',
    '/static/icons/maskable_icon_x128.png',
    '/static/icons/maskable_icon_x512.png'
];

// Evento 'install': Se ejecuta cuando el Service Worker se instala.
// Aquí cacheamos los recursos estáticos de la aplicación.
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Service Worker: Cacheando archivos estáticos');
                return cache.addAll(urlsToCache);
            })
    );
});

// Evento 'fetch': Intercepta las solicitudes de red.
// Intentamos servir los recursos desde el caché primero, y si no están,
// vamos a la red.
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Si el recurso está en caché, lo devolvemos.
                if (response) {
                    return response;
                }
                // Si no, lo obtenemos de la red.
                return fetch(event.request).then(
                    function(response) {
                        // Comprobamos si recibimos una respuesta válida
                        if(!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }

                        // Clonamos la respuesta porque la respuesta es un Stream y solo se puede consumir una vez
                        const responseToCache = response.clone();

                        caches.open(CACHE_NAME)
                            .then(function(cache) {
                                cache.put(event.request, responseToCache);
                            });

                        return response;
                    }
                );
            })
    );
});

// Evento 'activate': Se ejecuta cuando el Service Worker se activa.
// Aquí gestionamos la limpieza de cachés antiguas.
self.addEventListener('activate', event => {
    const cacheWhitelist = [CACHE_NAME];
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheWhitelist.indexOf(cacheName) === -1) {
                        console.log('Service Worker: Eliminando caché antigua', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Manejo de notificaciones push (opcional, no solicitado explícitamente pero útil para PWAs)
self.addEventListener('push', event => {
    const data = event.data.json();
    const title = data.title || 'Chat Cifrado';
    const options = {
        body: data.body || 'Nuevo mensaje',
        icon: '/static/icons/icon-192x192.png'
    };
    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(
        clients.openWindow('/')
    );
});
