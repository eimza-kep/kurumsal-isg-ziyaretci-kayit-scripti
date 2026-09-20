@echo off
chcp 65001 >nul
echo =================================================================
echo        KURUMSAL İSG VE ZİYARETÇİ TAKİP SİSTEMİ BAŞLATICI
echo =================================================================
echo.
echo Sunucu hazırlanıyor ve başlatılıyor...
echo Port: 8089
echo.
start "" http://localhost:8089
python server.py
pause
