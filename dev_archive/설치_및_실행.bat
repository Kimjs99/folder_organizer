@echo off
chcp 65001 >nul
echo ==============================================
echo       폴더정리 자동화 프로그램 설치
echo ==============================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] Python이 설치되어 있지 않습니다!
    echo 파이썬 홈페이지(https://www.python.org/downloads/)에서 먼저 파이썬을 설치해주세요.
    echo 설치 시 반드시 "Add Python to PATH"에 체크해야 합니다.
    pause
    exit /b
)

echo [1/3] 필요한 파이썬 라이브러리 설치 중...
pip install -r requirements.txt >nul
if %errorlevel% neq 0 (
    echo [오류] 라이브러리 설치 실패!
    pause
    exit /b
)

echo [2/3] 바탕화면에 클릭 실행 아이콘(바로가기) 생성 중...
python create_gui_shortcut.py >nul

echo [3/3] 설치가 완료되었습니다!
echo.
echo 이제 바탕화면의 [폴더정리 자동화 GUI] 아이콘을 더블클릭하여 실행해 주세요.
pause
