@echo off
echo ============================================================
echo   REINICIO DE WebAI-to-API (Modo Cookies)
echo ============================================================
echo.

cd /d c:\Users\Admin\WebAI-to-API-master\WebAI-to-API-master

echo [1/2] Deteniendo servidor actual...
echo Presiona Ctrl+C en la otra terminal si aun esta corriendo
echo.
timeout /t 3 /nobreak >nul

echo [2/2] Iniciando servidor con nueva configuracion...
echo.
python src\run.py

pause
