const VERSION='ruheklang-v1.1.1';
const FILES=[
  './','./index.html','./seamless-player.js','./manifest.webmanifest','./icons/icon-180.png','./icons/icon-192.png','./icons/icon-512.png',
  './assets/rain.mp3','./assets/hardrain.mp3','./assets/thunder.mp3','./assets/sea.mp3',
  './assets/stream.mp3','./assets/wind.mp3','./assets/forest.mp3','./assets/fire.mp3',
  './assets/night.mp3','./assets/brown.mp3','./assets/pink.mp3','./assets/white.mp3',
  './assets/fan.mp3'
];
self.addEventListener('install',event=>{
  event.waitUntil(caches.open(VERSION).then(cache=>cache.addAll(FILES)).then(()=>self.skipWaiting()));
});
self.addEventListener('activate',event=>{
  event.waitUntil(Promise.all([
    caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('ruheklang-')&&k!==VERSION).map(k=>caches.delete(k)))),
    self.clients.claim()
  ]));
});
self.addEventListener('fetch',event=>{
  if(event.request.method!=='GET')return;
  const url=new URL(event.request.url);
  if(url.origin!==self.location.origin)return;
  event.respondWith((async()=>{
    const cached=await caches.match(event.request,{ignoreSearch:true,ignoreVary:true});
    if(cached){
      const range=event.request.headers.get('range');
      if(range&&/\.(mp3|wav|ogg)$/i.test(url.pathname)){
        const bytes=await cached.arrayBuffer();
        const match=/bytes=(\d+)-(\d*)/.exec(range);
        if(match){
          const start=Number(match[1]);
          const end=match[2]?Math.min(bytes.byteLength-1,Number(match[2])):bytes.byteLength-1;
          if(start>=bytes.byteLength||end<start)return new Response(null,{status:416,headers:{'Content-Range':'bytes */'+bytes.byteLength}});
          return new Response(bytes.slice(start,end+1),{status:206,headers:{'Content-Type':'audio/mpeg','Content-Range':`bytes ${start}-${end}/${bytes.byteLength}`,'Content-Length':String(end-start+1),'Accept-Ranges':'bytes'}});
        }
      }
      return cached;
    }
    return fetch(event.request);
  })());
});
