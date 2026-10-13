# Punjab Pharmacy Server Launcher for PowerShell
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "       PUNJAB PHARMACY (KOT SULTAN, LAYYAH) - ONLINE STORE          " -ForegroundColor Green
Write-Host "       Admin: 03045518658  |  Helpline: 03095518882                 " -ForegroundColor Yellow
Write-Host "       Admin Gmail: hammadfareed876@gmail.com                       " -ForegroundColor Magenta
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Installing dependencies if needed..." -ForegroundColor Gray
python -m pip install -r requirements.txt --quiet

Write-Host "Launching Browser at http://127.0.0.1:5000 ..." -ForegroundColor Cyan
Start-Process "http://127.0.0.1:5000"

Write-Host "Starting Flask App..." -ForegroundColor Green
python app.py
