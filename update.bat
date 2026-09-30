@echo off
chcp 65001 > nul
title 매크로 리포트 아카이브 자동 업데이터

echo ========================================================
echo   [1/3] 변경 및 추가된 리포트 파일 스캔 중...
echo ========================================================
git add public/reports/

:: 변경 사항이 있는지 확인
git diff --cached --quiet
if %errorlevel% equ 0 (
    echo.
    echo [안내] 새로 추가되거나 변경된 리포트 파일이 없습니다.
    echo public/reports/ 폴더에 새 HTML 파일을 넣고 다시 실행해 주세요.
    echo.
    pause
    exit /b
)

echo.
echo ========================================================
echo   [2/3] 변경 사항 자동 커밋 생성 중...
echo ========================================================
for /f "tokens=1-3 delims=-/. " %%a in ("%date%") do (
    set YYYY=%%a
    set MM=%%b
    set DD=%%c
)
git commit -m "Auto Update: %date% 리포트 업데이트"

echo.
echo ========================================================
echo   [3/3] GitHub 원격 저장소로 업로드 중...
echo ========================================================
git push origin main

if %errorlevel% neq 0 (
    echo.
    echo [주의] GitHub 푸시 도중 오류가 발생했습니다.
    echo 원격 저장소(origin)가 설정되어 있는지, 인터넷 연결이 정상인지 확인해 주세요.
    echo.
) else (
    echo.
    echo ========================================================
    echo   [성공] 업로드가 완료되었습니다!
    echo   약 20~30초 후 Vercel 사이트에 자동으로 반영됩니다.
    echo ========================================================
)

pause
