# -*- coding: utf-8 -*-
"""
server.py
---------
6331 Sayılı İSG Kanunu Uyumlu Ziyaretçi ve Güvenlik Portalı.
Yerleşik SQLite veritabanı ile ziyaretçi kayıtlarını ve dijital İSG taahhütlerini depolar.
- Acil durum (yangın/deprem) bina tahliye listesi motoru (/api/acil-tahliye)
- Dijital İSG taahhütnamesi SHA-256 onay mührü ve SMS OTP kancası
"""

import http.server
import socketserver
import json
import sqlite3
import os
import sys
import random
from urllib.parse import urlparse, parse_qs

# Windows console UTF-8 desteği
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scripts.isg_digital_signature import (
    generate_isg_consent_hash,
    verify_isg_consent_hash,
    generate_sms_otp_code,
    get_evacuation_report
)

PORT = int(os.environ.get("PORT", 8089))
DB_FILE = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "isg_ziyaretciler.db"))

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_code TEXT UNIQUE,
            visitor_name TEXT,
            visitor_id TEXT,
            visitor_phone TEXT,
            visitor_company TEXT,
            visitor_email TEXT,
            host_employee TEXT,
            host_department TEXT,
            visit_reason TEXT,
            equipment_brought TEXT,
            vehicle_plate TEXT,
            hazard_class TEXT DEFAULT 'Az Tehlikeli',
            ppe_items TEXT DEFAULT '',
            digital_signature_hash TEXT DEFAULT '',
            digital_consent_verified INTEGER DEFAULT 1,
            check_in_time TEXT,
            check_out_time TEXT,
            status TEXT DEFAULT 'Tesis İçinde (Aktif)',
            created_at TEXT
        )
    """)
    # Dinamik kolon güncelleme
    cur.execute("PRAGMA table_info(visitors)")
    cols = [r[1] for r in cur.fetchall()]
    if "hazard_class" not in cols:
        cur.execute("ALTER TABLE visitors ADD COLUMN hazard_class TEXT DEFAULT 'Az Tehlikeli'")
    if "ppe_items" not in cols:
        cur.execute("ALTER TABLE visitors ADD COLUMN ppe_items TEXT DEFAULT ''")
    if "digital_signature_hash" not in cols:
        cur.execute("ALTER TABLE visitors ADD COLUMN digital_signature_hash TEXT DEFAULT ''")
    if "digital_consent_verified" not in cols:
        cur.execute("ALTER TABLE visitors ADD COLUMN digital_consent_verified INTEGER DEFAULT 1")
    conn.commit()
    conn.close()

class VisitorHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path in ("/", "/index.html"):
            self.send_file("index.html", "text/html; charset=utf-8")
        elif path in ("/admin", "/admin.html"):
            self.send_file("admin.html", "text/html; charset=utf-8")
        elif path == "/health":
            self.send_json({"status": "ok", "app": "kurumsal-isg-ziyaretci-kayit-scripti", "port": PORT})
        elif path == "/api/ziyaretciler":
            self.handle_get_visitors()
        elif path == "/api/acil-tahliye":
            self.handle_emergency_evacuation()
        elif path == "/api/generate-otp":
            self.send_json({"otp": generate_sms_otp_code()})
        elif path == "/api/isg-taahhut-dogrula":
            self.handle_verify_consent(qs)
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/ziyaretci-giris":
            self.handle_check_in()
        elif path == "/api/ziyaretci-cikis":
            self.handle_check_out()
        else:
            self.send_error(404, "Endpoint not found")

    def send_file(self, filename, content_type):
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        if not os.path.exists(filepath):
            self.send_error(404, f"File {filename} not found")
            return
        with open(filepath, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def handle_check_in(self):
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length)
        try:
            data = json.loads(post_data.decode("utf-8"))
            tracking_code = data.get("tracking_code") or f"ISG-2026-{random.randint(1000, 9999)}"
            hazard_class = data.get("hazard_class") or "Az Tehlikeli"
            ppe_items = data.get("ppe_items") or ""

            # Dijital İSG taahhüt hash'ini hesapla
            data["hazard_class"] = hazard_class
            data["ppe_items"] = ppe_items
            digital_hash = generate_isg_consent_hash(data)

            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO visitors (
                    tracking_code, visitor_name, visitor_id, visitor_phone,
                    visitor_company, visitor_email, host_employee, host_department,
                    visit_reason, equipment_brought, vehicle_plate,
                    hazard_class, ppe_items, digital_signature_hash, digital_consent_verified,
                    check_in_time, check_out_time, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tracking_code,
                data.get("visitor_name", ""),
                data.get("visitor_id", ""),
                data.get("visitor_phone", ""),
                data.get("visitor_company", ""),
                data.get("visitor_email", ""),
                data.get("host_employee", ""),
                data.get("host_department", ""),
                data.get("visit_reason", ""),
                data.get("equipment_brought", ""),
                data.get("vehicle_plate", ""),
                hazard_class,
                ppe_items,
                digital_hash,
                1 if data.get("digital_consent_verified", True) else 0,
                data.get("check_in_time", ""),
                "",
                data.get("status", "Tesis İçinde (Aktif)"),
                data.get("created_at", "")
            ))
            conn.commit()
            conn.close()

            self.send_json({
                "status": "success",
                "tracking_code": tracking_code,
                "digital_signature_hash": digital_hash,
                "hazard_class": hazard_class
            })
        except Exception as e:
            self.send_json({"status": "error", "message": str(e)}, status=500)

    def handle_get_visitors(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM visitors ORDER BY id DESC")
            rows = [dict(r) for r in cur.fetchall()]
            conn.close()
            self.send_json(rows)
        except Exception as e:
            self.send_json({"status": "error", "message": str(e)}, status=500)

    def handle_check_out(self):
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length)
        try:
            data = json.loads(post_data.decode("utf-8"))
            tracking_code = data.get("tracking_code")
            check_out_time = data.get("check_out_time")

            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("""
                UPDATE visitors
                SET status = 'Çıkış Yapıldı', check_out_time = ?
                WHERE tracking_code = ?
            """, (check_out_time, tracking_code))
            conn.commit()
            conn.close()

            self.send_json({"status": "success", "updated": tracking_code})
        except Exception as e:
            self.send_json({"status": "error", "message": str(e)}, status=500)

    def handle_emergency_evacuation(self):
        """Acil durum tahliye listesi JSON çıktısı"""
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM visitors WHERE status = 'Tesis İçinde (Aktif)' ORDER BY host_department ASC")
            active_rows = [dict(r) for r in cur.fetchall()]
            conn.close()

            report = get_evacuation_report(active_rows)
            self.send_json({"status": "success", "report": report})
        except Exception as e:
            self.send_json({"status": "error", "message": str(e)}, status=500)

    def handle_verify_consent(self, qs):
        """İSG taahhütname hash doğrulama kontrolü"""
        code = qs.get("code", [""])[0]
        if not code:
            self.send_json({"valid": False, "message": "Takip kodu girilmelidir."}, status=400)
            return

        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM visitors WHERE tracking_code = ?", (code,))
        row = cur.fetchone()
        conn.close()

        if not row:
            self.send_json({"valid": False, "message": "Ziyaretçi kaydı bulunamadı."}, status=404)
            return

        r_dict = dict(row)
        expected_hash = r_dict.get("digital_signature_hash", "")
        is_valid = verify_isg_consent_hash(r_dict, expected_hash)

        self.send_json({
            "valid": is_valid,
            "tracking_code": code,
            "visitor_name": r_dict.get("visitor_name"),
            "hazard_class": r_dict.get("hazard_class"),
            "ppe_items": r_dict.get("ppe_items"),
            "digital_signature_hash": expected_hash,
            "check_in_time": r_dict.get("check_in_time")
        })

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", PORT))
    print(f"🚀 ISG Ziyaretci Portali Baslatildi: http://localhost:{port}")
    print(f"🦺 Guvenlik Yonetim Paneli: http://localhost:{port}/admin")
    print(f"🚨 Acil Durum Tahliye API: http://localhost:{port}/api/acil-tahliye")
    with socketserver.TCPServer(("", port), VisitorHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nSunucu kapatildi.")
