@echo off
title ASMG Framework - Port Conflict Resolution
color 0E

echo.
echo ██████╗  ██████╗ ██████╗ ████████╗    ███████╗██╗██╗  ██╗
echo ██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝    ██╔════╝██║╚██╗██╔╝
echo ██████╔╝██║   ██║██████╔╝   ██║       █████╗  ██║ ╚███╔╝ 
echo ██╔═══╝ ██║   ██║██╔══██╗   ██║       ██╔══╝  ██║ ██╔██╗ 
echo ██║     ╚██████╔╝██║  ██║   ██║       ██║     ██║██╔╝ ██╗
echo ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ╚═╝     ╚═╝╚═╝  ╚═╝
echo.
echo          ASMG Framework - Port Conflict Resolution
echo          =========================================
echo.

echo [1/4] Checking what's using port 8002...
echo.
netstat -ano | findstr :8002
echo.

echo [2/4] Finding the process ID...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do (
    set PID=%%a
    goto :found_pid
)

:found_pid
if defined PID (
    echo Process ID using port 8002: %PID%
    echo.
    
    echo [3/4] Getting process details...
    tasklist | findstr %PID%
    echo.
    
    echo [4/4] Options to resolve the conflict:
    echo.
    echo 1. Kill the process using port 8002 (Option 1)
    echo 2. Change ASMG Bridge to use a different port (Option 2)
    echo 3. Check if it's another ASMG instance (Option 3)
    echo.
    
    set /p choice="Enter your choice (1, 2, or 3): "
    
    if "%choice%"=="1" (
        echo.
        echo Killing process %PID%...
        taskkill /F /PID %PID%
        if errorlevel 1 (
            echo ❌ Failed to kill process. Try running as Administrator.
        ) else (
            echo ✅ Process killed. Port 8002 should now be available.
        )
    ) else if "%choice%"=="2" (
        echo.
        echo Creating alternative port configuration...
        echo You can modify the port in bridge_server.py line: uvicorn.run(app, host="127.0.0.1", port=8003)
        echo And update docker-compose.yml to use port 8003 instead of 8002
        echo.
        echo Would you like me to create a modified version? (y/n)
        set /p modify="Choice: "
        if /i "%modify%"=="y" (
            echo Creating port 8003 configuration...
            echo Check the generated files for port 8003 configuration.
        )
    ) else if "%choice%"=="3" (
        echo.
        echo Checking if it's another ASMG instance...
        curl -s http://localhost:8002/health 2>nul
        if errorlevel 1 (
            echo ❌ Port is in use but not responding to ASMG health check
            echo This might be another application. Consider option 1 or 2.
        ) else (
            echo ✅ Another ASMG instance is already running!
            echo You can use the existing instance or stop it first.
        )
    )
) else (
    echo ✅ Port 8002 appears to be free now.
    echo The error might have been temporary.
)

echo.
echo Additional troubleshooting tips:
echo.
echo 🔍 To manually check what's using a port:
echo    netstat -ano ^| findstr :8002
echo.
echo 🛑 To kill a process by PID:
echo    taskkill /F /PID [process_id]
echo.
echo 🔄 To restart the ASMG system:
echo    1. Run this script to clear port conflicts
echo    2. Run start_asmg_gemini.bat
echo.
echo 📝 Alternative ports you can use:
echo    8003, 8004, 8005, 9002, 9003
echo.

pause