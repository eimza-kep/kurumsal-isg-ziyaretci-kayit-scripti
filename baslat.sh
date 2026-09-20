#!/usr/bin/env bash
echo "================================================================="
echo "       KURUMSAL İSG VE ZİYARETÇİ TAKİP SİSTEMİ BAŞLATICI"
echo "================================================================="
echo ""
echo "Sunucu başlatılıyor: http://localhost:8089"
echo "Güvenlik & Resepsiyon Paneli: http://localhost:8089/admin"
echo ""

if command -v python3 &>/dev/null; then
    python3 server.py
elif command -v python &>/dev/null; then
    python server.py
else
    echo "Hata: Python bulunamadı!"
    exit 1
fi
