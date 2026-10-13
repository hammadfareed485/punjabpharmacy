@echo off
chcp 65001 > nul
title Punjab Pharmacy - Web Server Runner
echo ====================================================================
echo        PUNJAB PHARMACY (KOT SULTAN, LAYYAH) - ONLINE STORE
echo        Admin: 03045518658  ^|  Helpline: 03095518882
echo        Admin Gmail: hammadfareed876@gmail.com
echo ====================================================================
echo.
echo Checking Python dependencies...
python -m pip install -r requirements.txt --quiet
echo.
echo Starting Punjab Pharmacy Web Server on http://127.0.0.1:5000 ...
start http://127.0.0.1:5000
python app.py
pause
