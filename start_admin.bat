@echo off
echo Starting CHIMERA with administrator privileges...
echo This will resolve port binding issues on Windows.
echo.
echo If you still get port errors, try:
echo 1. Run this as Administrator
echo 2. Disable Windows firewall temporarily
echo 3. Use different ports in chimera_autarch.py
echo.
pause
python chimera_autarch.py
pause
