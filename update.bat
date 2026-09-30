@echo off
chcp 65001 > nul
title 매크로 리포트 아카이브 - 구글 드라이브 동기화 및 자동 배포

echo ========================================================
echo   [1/4] 구글 드라이브 공유 폴더에서 최신 리포트 다운로드 중...
echo ========================================================
python -m gdown --folder "https://drive.google.com/drive/folders/1LBzd_bb6UjL6fcAIW2B1cUmWFG6RBtQu" -O "public/reports"

:: 혹시 모를 docx 등 비-HTML 파일 정리
del /q "public\reports\*.docx" 2>nul

echo.
echo ========================================================
echo   [2/4] 리포트 목록 인덱싱(색인) 갱신 중...
echo ========================================================
node scripts/build-index.js

echo.
echo ========================================================
echo   [3/4] 변경 사항 감지 및 자동 커밋 생성 중...
echo ========================================================
git add public/reports/ public/reports.json

git diff --cached --quiet
if %errorlevel% equ 0 (
    echo.
    echo [안내] 새로 추가되거나 변경된 리포트 파일이 없습니다.
    echo 이미 모든 리포트가 최신 상태로 배포되어 있습니다.
    echo.
    pause
    exit /b
)

for /f "tokens=1-3 delims=-/. " %%a in ("%date%") do (
    set YYYY=%%a
    set MM=%%b
    set DD=%%c
)
git commit -m "Auto Update: %date% 구글 드라이브 리포트 동기화"

echo.
echo ========================================================
echo   [4/4] GitHub 및 Vercel 클라우드로 전송 중...
echo ========================================================
git push origin main

if %errorlevel% neq 0 (
    echo.
    echo [주의] GitHub 푸시 도중 오류가 발생했습니다.
    echo 인터넷 연결 또는 계정 권한을 확인해 주세요.
    echo.
) else (
    echo.
    echo ========================================================
    echo   [성공] 구글 드라이브 동기화 및 배포가 완료되었습니다!
    echo   약 20~30초 후 Vercel 웹사이트에서 확인하실 수 있습니다.
    echo ========================================================
)

pause
