#!/usr/bin/env python3
"""claude.ai 아티팩트의 index.html을 앱(PWA) 버전으로 바꾼다.

사용법: python3 tools/port-artifact.py <아티팩트에서 받은 index.html> [출력 경로=index.html]

하는 일
1. <head>를 앱용으로 교체 (manifest, 아이콘, 홈 화면 설정, 검색 노출 금지)
2. Claude 해설 버튼과 코드 제거
3. Claude 계정 저장(db/user)을 기기 저장(localStorage) + 첫 실행 시 seed-save.json 불러오기로 교체
4. 기록 백업/불러오기 버튼 추가
5. 오프라인용 서비스 워커 등록
아티팩트 코드가 바뀌어 기준 문구를 못 찾으면 멈추고 어느 단계인지 알려 준다.
"""
import sys

src = sys.argv[1]
dst = sys.argv[2] if len(sys.argv) > 2 else 'index.html'
s = open(src, encoding='utf8').read().replace('\r\n', '\n')


def cut(start, end, repl, what):
    global s
    a = s.find(start)
    b = s.find(end, a + 1) if a >= 0 else -1
    if a < 0 or b < 0:
        sys.exit(f'[멈춤] {what}: 기준 문구를 찾지 못했어요')
    s = s[:a] + repl + s[b:]


def sub(old, new, what):
    global s
    if old not in s:
        sys.exit(f'[멈춤] {what}: 기준 문구를 찾지 못했어요')
    s = s.replace(old, new, 1)


# 1. head
HEAD = '''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>이의 있음!</title>
<link rel="manifest" href="manifest.webmanifest">
<meta name="robots" content="noindex,nofollow">
<meta name="theme-color" content="#15131C">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="이의 있음!">
<link rel="apple-touch-icon" href="icons/icon-180.png">
<link rel="icon" href="icons/icon-192.png">
<style>:root{color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}html{scroll-padding-top:env(safe-area-inset-top,0px)}body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#fff;color:#000;-webkit-tap-highlight-color:transparent;-webkit-touch-callout:none}img{max-width:100%;-webkit-user-drag:none}[hidden]:not([hidden=until-found i]){display:none!important}</style>
</head><body>
'''
cut('', '<style>\n@font-face', HEAD, 'head 교체')

# 2. Claude 해설
sub('<button class="btn" id="ask">Claude 해설</button>', '', '해설 버튼')
sub('  $("ask").onclick=()=>askClaude(x,openSheet("Claude 해설 · 소리 내어 듣기 좋게"),$("ask"));\n', '', '해설 버튼 동작')
cut('/* ---------- Claude 해설 ---------- */', '/* ---------- 동료와 카드 ---------- */', '', '해설 코드')

# 3. 저장
cut('async function initStore(){', 'function save(){', '''async function initStore(){
  let loaded=null;
  try{const t=localStorage.getItem("pansorye");if(t)loaded=JSON.parse(t);}catch(e){}
  if(!loaded){try{const r=await fetch("seed-save.json");if(r.ok){loaded=await r.json();try{localStorage.setItem("pansorye",JSON.stringify(loaded));}catch(e){}}}catch(e){}}
  S=Object.assign(fresh(),loaded||{});
  Object.keys(S.chars).forEach(k=>{if(!CH[k])delete S.chars[k];});if(S.lead&&!CH[S.lead])S.lead=null;
  if(!S.court)S.court={};
  try{if(navigator.storage&&navigator.storage.persist)navigator.storage.persist();}catch(e){}
  $("save-note").textContent="기록은 이 기기에 저장돼요.";
}
''', '저장 불러오기')
sub('  if(store.mode!=="db")return;clearTimeout(store.timer);store.timer=setTimeout(flush,1200);\n', '', '계정 저장 호출')
cut('async function flush(){', '/* ---------- 화면 ---------- */', '', '계정 저장 함수')

# 4. 백업 버튼
sub('<div class="row"><button class="btn" id="op-replay">',
    '<div class="row"><button class="btn" id="bk-out">기록 백업</button><button class="btn" id="bk-in">기록 불러오기</button>'
    '<input type="file" id="bk-file" accept=".json,application/json,text/plain" hidden></div>\n    '
    '<div class="row"><button class="btn" id="op-replay">', '백업 버튼')
BACKUP = '''
/* ---------- 기록 백업 ---------- */
function bkName(){const d=new Date();return `이의있음-기록-${d.getFullYear()}${String(d.getMonth()+1).padStart(2,"0")}${String(d.getDate()).padStart(2,"0")}.json`;}
$("bk-out").onclick=async()=>{
  const text=JSON.stringify(S);const file=new File([text],bkName(),{type:"application/json"});
  try{if(navigator.canShare&&navigator.canShare({files:[file]})){await navigator.share({files:[file],title:"이의 있음! 기록"});flashNote("기록 파일을 보냈어요.");return;}}
  catch(e){if(e&&e.name==="AbortError")return;}
  const a=document.createElement("a");a.href=URL.createObjectURL(file);a.download=file.name;document.body.appendChild(a);a.click();
  setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},1000);flashNote("기록 파일을 저장했어요.");
};
$("bk-in").onclick=()=>{$("bk-file").value="";$("bk-file").click();};
$("bk-file").onchange=async()=>{
  const f=$("bk-file").files[0];if(!f)return;
  let st;try{st=JSON.parse(await f.text());}catch(e){flashNote("기록 파일을 읽지 못했어요.");return;}
  if(!st||typeof st!=="object"||!st.chars||!st.review){flashNote("이 게임의 기록 파일이 아니에요.");return;}
  if(!confirm("지금 기록을 이 파일의 기록으로 바꿀까요? 지금 기록은 사라져요."))return;
  try{localStorage.setItem("pansorye",JSON.stringify(st));}catch(e){}
  location.reload();
};
'''
sub('/* ---------- 화면 ---------- */', BACKUP + '/* ---------- 화면 ---------- */', '백업 코드')

# 5. 서비스 워커
s = s.rstrip()
if s.endswith('</body></html>'):
    s = s[:-len('</body></html>')].rstrip()
s += '\n<script>if("serviceWorker" in navigator)addEventListener("load",()=>navigator.serviceWorker.register("sw.js").catch(()=>{}));</script>\n</body></html>\n'

left = [w for w in ('claude.use', 'sampleFn', 'store.ref') if w in s]
if left:
    sys.exit(f'[멈춤] Claude 전용 코드가 남아 있어요: {left}')
open(dst, 'w', encoding='utf8').write(s)
print('완료:', dst)
