# 📈 매크로 브리핑 웹 아카이브 & 뷰어

일일 브리핑 HTML 문서들을 모아서 한곳에서 열람, 검색, 관리할 수 있는 반응형 웹 뷰어 프로젝트입니다.
구글 드라이브 → GitHub → Vercel 자동 동기화 구조입니다.

---

## 🔄 동작 방식

1. 구글 드라이브 폴더에 새 HTML 리포트가 올라옴
2. GitHub Actions (`deploy.yml`, 1일 3회: KST 09시 / 12시 / 21시)가 `sync_ci.py`로 변경분만 다운로드
3. `scripts/build-index.js`가 `public/reports.json` 색인 재생성
4. 변경 있으면 자동 커밋 → Vercel 재배포 (약 20~30초)
5. 로컬에서 직접 동기화하려면 **`update.bat` 더블클릭** (= `python sync.py` 실행)

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
     - **Build Command**: `npm run build`
     - **Output Directory**: `public`
5. **Deploy** 버튼을 클릭합니다.
6. 약 30초 후 나만의 도메인 URL(예: `https://macro-viewer-xxx.vercel.app`)이 발급되며 배포가 완료됩니다!

---

**평소에는 아무것도 안 해도 됩니다.** Actions 스케줄(매일 09시 / 12시 / 21시 KST)이 Drive를 자동으로 가져옵니다.

- 수동 즉시 반영이 필요하면: 구글 드라이브에 파일 업로드 후 Actions 탭 → `Auto Sync from Google Drive` → `Run workflow`
- 로컬 PC에서 직접 반영하려면: **`update.bat` 더블클릭** (Drive 다운로드 → 인덱싱 → Git 푸시까지 자동)
- 로컬 최초 1회만: `pip install -r requirements.txt`

주의:
- Drive에 없는 파일은 repo에서도 삭제됩니다 (미러 동기화).
- 파일명에 날짜(`2026.10.03` 등)가 없으면 빌드 시 파일 수정일 기준으로 날짜가 붙고, 빌드할 때마다 바뀔 수 있습니다. 가급적 파일명에 날짜 포함 권장.
- 동명 파일이 Drive 하위폴더에 중복되면 첫 번째만 반영되고 경고가 출력됩니다.

---

## 📁 프로젝트 구조

```text
macro-viewer/
├── package.json               # 빌드 커맨드 정의 (npm run build)
├── requirements.txt           # Python 의존성 (gdown)
├── update.bat                 # 로컬 원클릭 동기화 (python sync.py)
├── sync.py                    # 로컬용 Drive 동기화 + 인덱싱 + 푸시
├── sync_ci.py                 # Actions용 Drive 동기화 (경량)
├── .sync_cache.json           # 변경 감지용 해시 캐시 (추적됨, 삭제 금지)
├── vercel.json                # Vercel 빌드 설정
├── .github/workflows/deploy.yml  # 1일 3회 자동 동기화 워크플로
├── scripts/
│   └── build-index.js         # public/reports 내 HTML 분석 → reports.json 생성
└── public/
    ├── index.html             # 반응형 메인 뷰어 UI (사이드바, 검색, iframe 뷰어)
    ├── reports.json           # 빌드 시 자동 생성되는 색인 (커밋됨)
    └── reports/               # 동기화된 원본 HTML 저장 폴더
```

---

## 💡 주요 기능
- **반응형 UI**: PC 와이드 화면(좌측 사이드바 + 우측 본문)과 스마트폰 모바일 뷰(햄버거 드로어 메뉴) 지원.
- **실시간 검색**: 제목/파일명/날짜(예: `2026-09`, `원자재`, `환율`) 입력 시 즉시 필터링.
- **최신 리포트 자동 열람**: 접속 시 가장 최신 날짜의 리포트가 메인 화면에 로드.
- **iframe 격리**: 리포트에 `sandbox="allow-scripts allow-same-origin allow-popups"` 적용으로 메인 앱과 격리.
- **새 탭 원본 보기**: 상단의 [새 탭으로 열기] 버튼으로 원본 전체화면 열람 지원.
