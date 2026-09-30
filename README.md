# 📈 매크로 브리핑 웹 아카이브 & 뷰어

피터 나바로 매크로 인과체인 프레임워크 기반의 일일 브리핑 HTML 문서들을 모아서 한곳에서 열람, 검색, 관리할 수 있는 반응형 웹 뷰어 프로젝트입니다.

---

## 🚀 1. 최초 배포 설정 방법 (최초 1회만 진행)

### 단계 1: GitHub 원격 저장소 생성 및 푸시
1. [GitHub](https://github.com/)에 로그인 후 우측 상단 `+` -> **New repository** 클릭.
2. Repository name에 `macro-viewer` (또는 원하는 이름) 입력 후 **Create repository** 클릭. (Private/Public 무관)
3. 이 폴더(`c:\Users\moreb\Desktop\report`)에서 터미널을 열고 다음 명령어를 실행합니다:

```bash
git init
git add .
git commit -m "feat: initial commit for macro viewer"
git branch -M main
git remote add origin https://github.com/<본인아이디>/<저장소이름>.git
git push -u origin main
```

### 단계 2: Vercel 자동 배포 연동 (무료)
1. [Vercel](https://vercel.com/)에 접속하여 GitHub 계정으로 로그인합니다.
2. **Add New...** -> **Project**를 클릭합니다.
3. 방금 만든 GitHub 저장소(`macro-viewer`)의 **Import** 버튼을 클릭합니다.
4. 설정 화면에서:
   - **Framework Preset**: `Other` 선택
   - **Build and Output Settings** 확인:
     - **Build Command**: `node scripts/build-index.js` (또는 `npm run build`)
     - **Output Directory**: `public`
5. **Deploy** 버튼을 클릭합니다.
6. 약 30초 후 나만의 도메인 URL(예: `https://macro-viewer-xxx.vercel.app`)이 발급되며 배포가 완료됩니다!

---

## 📅 2. 매일 리포트 업데이트 방법 (일상 루틴)

매일 새로운 HTML 리포트가 생성되면 다음 **두 단계**만 진행하시면 됩니다:

1. 생성된 HTML 파일을 `public/reports/` 폴더 안에 복사/이동합니다.
2. 프로젝트 루트 폴더에 있는 **`update.bat` 파일을 더블클릭**합니다.
   - 자동으로 변경된 파일을 감지하여 GitHub로 푸시합니다.
   - 푸시 후 약 20~30초 이내에 Vercel에서 자동으로 인덱싱 및 배포가 완료됩니다.
   - 스마트폰이나 PC 브라우저에서 웹사이트를 새로고침하면 최신 리포트가 즉시 반영됩니다.

---

## 📁 프로젝트 구조

```text
macro-viewer/
├── package.json               # 프로젝트 설정 및 빌드 커맨드 정의
├── update.bat                 # 원클릭 자동 커밋 & GitHub 푸시 스크립트
├── README.md                  # 프로젝트 설명서 및 운영 가이드
├── scripts/
│   └── build-index.js         # public/reports 폴더 내 HTML을 분석하여 reports.json 생성
└── public/
    ├── index.html             # 반응형 메인 뷰어 UI (사이드바, 검색, iframe 격리 뷰어)
    ├── reports.json           # 빌드 시 자동 생성되는 리포트 메타데이터 색인 파일
    └── reports/               # 매일 생성된 원본 HTML 파일들이 저장되는 폴더
```

---

## 💡 주요 기능
- **반응형 UI**: PC 와이드 화면(좌측 사이드바 + 우측 본문)과 스마트폰 모바일 뷰(햄버거 드로어 메뉴)를 완벽 지원.
- **실시간 검색**: 제목이나 날짜(예: `2026-09`, `원자재`, `환율`) 입력 시 즉시 필터링.
- **최신 리포트 자동 열람**: 웹사이트 접속 시 가장 최신 날짜의 리포트가 메인 화면에 즉시 로드.
- **iframe 스타일 격리**: 개별 HTML 리포트 내부의 CSS/JS 스크립트가 메인 앱과 충돌하지 않도록 완벽 격리.
- **새 탭 원본 보기**: 상단의 [새 탭으로 열기] 버튼으로 리포트 원본 전체화면 열람 지원.
