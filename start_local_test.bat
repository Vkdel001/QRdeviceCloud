@echo off
echo ============================================================
echo Body and Soul POS - Local Testing
echo ============================================================
echo.
echo This will start both services for local testing:
echo   - Local Service (ESP32): Port 8080
echo   - Cloud Service (Web): Port 5000
echo.
echo Make sure you have created .env file with:
echo   LOCAL_SERVICE_URL=http://localhost:8080
echo   LOCAL_API_KEY=test-key-12345
echo   COM_PORT=COM3
echo.
echo Press Ctrl+C to stop both services
echo ============================================================
echo.

REM Start local service in new window
start "Body & Soul - Local Service" cmd /k python body_soul_local_enhanced.py

REM Wait a bit for local service to start
timeout /t 5 /nobreak

REM Start cloud service in new window
start "Body & Soul - Cloud Service" cmd /k python body_soul_cloud_enhanced.py

REM Wait a bit for cloud service to start
timeout /t 5 /nobreak

REM Open browser
start http://localhost:5000

echo.
echo ============================================================
echo Both services started!
echo ============================================================
echo   Local Service: http://localhost:8080
echo   Cloud Service: http://localhost:5000
echo   Browser opened automatically
echo ============================================================
echo.
echo Close this window when done testing
echo (The service windows will remain open)
echo ============================================================
pause
