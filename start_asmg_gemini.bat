@echo off
title ASMG Framework - Starting with Gemini 2.5 Pro
color 0A

echo.
echo ███████╗████████╗ █████╗ ██████╗ ████████╗██╗███╗   ██╗ ██████╗ 
echo ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝██║████╗  ██║██╔════╝ 
echo ███████╗   ██║   ███████║██████╔╝   ██║   ██║██╔██╗ ██║██║  ███╗
echo ╚════██║   ██║   ██╔══██║██╔══██╗   ██║   ██║██║╚██╗██║██║   ██║
echo ███████║   ██║   ██║  ██║██║  ██║   ██║   ██║██║ ╚████║╚██████╔╝
echo ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝ 
echo.
echo                ASMG Framework - Gemini 2.5 Pro
echo                ==============================
echo.

REM Check if required files exist
echo [1/5] Checking required files...
if not exist .env (
    echo ❌ ERROR: .env file not found!
    echo Please create .env file with your configuration
    pause
    exit /b 1
)
if not exist docker-compose.yml (
    echo ❌ ERROR: docker-compose.yml not found!
    echo Please create docker-compose.yml file
    pause
    exit /b 1
)
echo ✅ Required files found

REM Start Plant Simulation Bridge
echo [2/5] Starting Plant Simulation Bridge...
cd plant-sim-bridge
start /B cmd /c "bridge-env\Scripts\activate && python bridge_server.py"
cd ..
echo ✅ Bridge starting in background

REM Wait for bridge
echo [3/5] Waiting for services to initialize...
timeout /t 8 /nobreak >nul

REM Start Docker services
echo [4/5] Starting Docker services...
docker-compose up -d --build
if errorlevel 1 (
    echo ❌ ERROR: Docker services failed to start
    echo Please check Docker Desktop is running
    pause
    exit /b 1
)

REM Wait for all services
echo [5/5] Waiting for all services to be ready...
timeout /t 20 /nobreak >nul

REM Health check
echo Checking service health...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️ API service still starting up...
) else (
    echo ✅ API service ready
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo                    🚀 ASMG FRAMEWORK RUNNING!
echo ═══════════════════════════════════════════════════════════════
echo.
echo 🌐 Web Interface: http://localhost:3000
echo 📡 API Documentation: http://localhost:8000/docs
echo 🔍 System Health: http://localhost:8000/health
echo 🔌 Bridge Status: http://localhost:8002/health
echo 🗄️ ChromaDB: http://localhost:8001
echo.

REM Open web interface
echo Opening web interface...
start http://localhost:3000

echo.
echo System is now running! Press any key to return to prompt...
pause >nul