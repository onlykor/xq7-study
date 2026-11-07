#!/usr/bin/env python3
"""게임 파일 목록과 버전으로 sw.js를 다시 만든다. 파일을 바꾼 뒤 저장소 최상위에서 실행: python3 tools/build-sw.py"""
import hashlib, json, os
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
files = ['./', 'index.html', 'manifest.webmanifest', 'data.json', 'seed-save.json']
for d in ('a', 'f', 'icons'):
    files += [f'{d}/{x}' for x in sorted(os.listdir(d))]
h = hashlib.sha256()
for f in files[1:]:
    h.update(open(f, 'rb').read())
ver = h.hexdigest()[:10]
sw = f'''// 이의 있음! 오프라인 캐시. 자동 생성 파일: tools/build-sw.py
const VERSION="{ver}";
const FILES={json.dumps(files, ensure_ascii=False)};
self.addEventListener("install",e=>{{e.waitUntil(caches.open(VERSION).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting()));}});
self.addEventListener("activate",e=>{{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==VERSION).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));}});
self.addEventListener("fetch",e=>{{
  if(e.request.method!=="GET")return;
  e.respondWith(caches.match(e.request,{{ignoreSearch:true}}).then(r=>r||fetch(e.request)));
}});
'''
open('sw.js', 'w', encoding='utf8').write(sw)
print('sw.js', ver, len(files), 'files')
