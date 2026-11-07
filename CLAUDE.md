# 작업 안내 (Claude용)

「이의 있음!」 형법 OX 학습 게임. GitHub Pages(https://onlykor.github.io/xq7-study/)로 배포하는 PWA이고, 사용자 혼자 아이폰·안드로이드 홈 화면에 설치해 쓴다. 사용자와는 한국어로 대화한다.

## 구조
- `index.html`: 화면·스타일·게임 로직 전부 (빌드 도구 없음)
- `data.json`: 문제·판례·캐릭터 대사 데이터
- `a/`: 이미지(webp)·효과음(mp3). 캐릭터는 `이름.webp`, `이름_face.webp`, `이름_p.webp`, `이름_s.webp`
- `f/`: 글꼴, `icons/`: 앱 아이콘
- `sw.js`: 오프라인 캐시. **직접 고치지 말고** 생성 스크립트로 만든다
- `seed-save.json`: 기기에 기록이 없을 때 처음 불러오는 기록

## 고친 뒤 반드시
1. `python3 tools/build-sw.py` 실행 (파일 목록과 버전이 바뀌어야 폰이 새 버전을 받는다)
2. 휴대폰 크기로 Playwright 확인 (`python3 -m http.server`로 띄우고, 오프닝은 `opClose()`로 닫는다)
3. `main`에 커밋·푸시 → 1~2분 뒤 Pages에 반영

## 주의
- 기록은 localStorage 키 `pansorye`에 저장된다. 저장 구조(`fresh()`)를 바꾸면 기존 기록과 호환되게 한다.
- 이미지를 바꿀 때는 같은 파일명으로 덮어쓰고, 새 파일이면 webp로 넣는다. 큰 이미지는 줄여서 넣는다(캐릭터 전신 약 100~200KB).
- `a/garam_attack.webp`, `garam_awaken`, `garam_heal`, `garam_defeat`, `bg_boss2`는 없으면 기본 그림을 쓰는 선택 파일이다. 404가 나도 정상이다.
