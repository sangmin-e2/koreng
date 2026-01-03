@echo off
REM IME Caret Indicator 실행 파일 빌드 스크립트

echo PyInstaller로 실행 파일 생성 중...

pyinstaller --onefile --noconsole --name="koreng" main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo 빌드 완료!
    echo 실행 파일 위치: dist\koreng.exe
) else (
    echo.
    echo 빌드 실패. PyInstaller가 설치되어 있는지 확인하세요.
    echo 설치: pip install pyinstaller
)

pause

