@echo off
REM Quick test script for Windows to verify both Member A and B

echo ======================================================================
echo Testing Integrated Fraud Detection System
echo ======================================================================
echo.

echo Installing dependencies...
python -m pip install -r requirements.txt --quiet
echo.

echo ======================================================================
echo Testing Member A (Graph Analysis)
echo ======================================================================
python test_member_a.py
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Member A tests failed!
    pause
    exit /b 1
)
echo.

echo ======================================================================
echo Testing Member B (ML Detection)
echo ======================================================================
python test_member_b.py
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Member B tests failed!
    pause
    exit /b 1
)
echo.

echo ======================================================================
echo ALL TESTS PASSED!
echo ======================================================================
echo.
echo Both Member A and Member B are working correctly!
echo.
echo To start the unified API:
echo   uvicorn api.unified_app:app --reload --port 8001
echo.
pause

